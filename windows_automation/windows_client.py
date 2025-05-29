import os
import time
import json
import logging
import base64
import cv2
import numpy as np
from typing import Dict, Any, Optional, List, Union
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.keys import Keys
from PIL import Image
from io import BytesIO

# Constants
POINTER_MOUSE = "mouse"
POINTER_TOUCH = "touch"
POINTER_PEN = "pen"

class WindowsClient:
    """
    WindowsClient provides low-level interaction with Windows applications
    using Appium's Windows driver.
    """
    
    def __init__(self, driver: WebDriver, data_container: Optional[Any] = None, 
                 automation_engine: str = "Windows", wait_time: int = 30, 
                 executor_port: Optional[int] = None, s3_client: Optional[Any] = None):
        """
        Initialize the Windows client.
        
        Args:
            driver: WebDriver instance
            data_container: Container for test data (optional)
            automation_engine: Type of automation engine (default: "Windows")
            wait_time: Default wait time in seconds
            executor_port: Port for the executor (optional)
            s3_client: S3 client for file operations (optional)
        """
        self.driver = driver
        self.data_container = data_container
        self.automation_engine = automation_engine
        self.wait_time = wait_time
        self.executor_port = executor_port
        self.s3_client = s3_client
        self.window_handles = {}
        self.current_window = None
        self.logger = logging.getLogger(__name__)
    
    # Core Element Interaction Methods
    # ===============================
    
    def find_element(self, property_map: Dict[str, Any], object_image: Optional[bytes] = None) -> WebElement:
        """
        Find a UI element using the provided property map.
        
        Args:
            property_map: Dictionary containing element locators
            object_image: Optional image of the object (for visual matching)
            
        Returns:
            WebElement: The found element
            
        Raises:
            NoSuchElementException: If the element cannot be found
        """
        locators = property_map.get('locators', [])
        
        for locator in locators:
            locator_type = locator.get('type', '').lower()
            locator_value = locator.get('value')
            
            if not locator_value:
                continue
                
            try:
                if locator_type == 'name':
                    return self.driver.find_element(AppiumBy.NAME, locator_value)
                elif locator_type == 'id':
                    return self.driver.find_element(AppiumBy.ID, locator_value)
                elif locator_type == 'xpath':
                    return self.driver.find_element(AppiumBy.XPATH, locator_value)
                elif locator_type == 'class_name':
                    return self.driver.find_element(AppiumBy.CLASS_NAME, locator_value)
                elif locator_type == 'accessibility_id':
                    return self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, locator_value)
            except Exception as e:
                self.logger.debug(f"Failed to find element by {locator_type}: {locator_value}. Error: {e}")
                continue
                
        raise NoSuchElementException(f"Element not found using locators: {locators}")
    
    def click(self, obj: Dict[str, Any]) -> None:
        """
        Click on a UI element.
        
        Args:
            obj: Dictionary containing element properties
        """
        element = self.find_element(json.loads(obj["propertyMap"]))
        element.click()
    
    def enter_text(self, obj: Dict[str, Any], text: str) -> None:
        """
        Enter text into a UI element.
        
        Args:
            obj: Dictionary containing element properties
            text: Text to enter
        """
        element = self.find_element(json.loads(obj["propertyMap"]))
        element.clear()
        element.send_keys(text)
    
    def get_text(self, obj: Dict[str, Any]) -> str:
        """
        Get text from a UI element.
        
        Args:
            obj: Dictionary containing element properties
            
        Returns:
            str: The text content of the element
        """
        element = self.find_element(json.loads(obj["propertyMap"]))
        return element.text
    
    def is_visible(self, obj: Dict[str, Any]) -> bool:
        """
        Check if a UI element is visible.
        
        Args:
            obj: Dictionary containing element properties
            
        Returns:
            bool: True if the element is visible, False otherwise
        """
        try:
            element = self.find_element(json.loads(obj["propertyMap"]))
            return element.is_displayed()
        except Exception:
            return False
    
    # Window Management
    # ================
    
    def switch_to_window(self, window_name: str) -> None:
        """
        Switch to a specific window.
        
        Args:
            window_name: Name or title of the window to switch to
        """
        if window_name in self.window_handles:
            self.driver.switch_to.window(self.window_handles[window_name])
        else:
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                if window_name.lower() in self.driver.title.lower():
                    self.window_handles[window_name] = handle
                    self.current_window = window_name
                    return
            raise NoSuchWindowException(f"Window with title containing '{window_name}' not found")
    
    # Advanced Interactions
    # ====================
    
    def right_click(self, obj: Dict[str, Any]) -> None:
        """
        Perform a right-click on a UI element.
        
        Args:
            obj: Dictionary containing element properties
        """
        element = self.find_element(json.loads(obj["propertyMap"]))
        actions = ActionChains(self.driver)
        actions.context_click(element).perform()
    
    def double_click(self, obj: Dict[str, Any]) -> None:
        """
        Perform a double-click on a UI element.
        
        Args:
            obj: Dictionary containing element properties
        """
        element = self.find_element(json.loads(obj["propertyMap"]))
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
    
    def hover(self, obj: Dict[str, Any]) -> None:
        """
        Hover over a UI element.
        
        Args:
            obj: Dictionary containing element properties
        """
        element = self.find_element(json.loads(obj["propertyMap"]))
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
    
    # Screenshot and Visual Testing
    # ============================
    
    def take_screenshot(self, filename: str = "screenshot.png") -> str:
        """
        Take a screenshot of the current window.
        
        Args:
            filename: Name of the file to save the screenshot as
            
        Returns:
            str: Path to the saved screenshot
        """
        screenshot_path = os.path.join(os.getcwd(), "screenshots", filename)
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        self.driver.save_screenshot(screenshot_path)
        return screenshot_path
    
    # Helper Methods
    # ==============
    
    def wait_for_element(self, obj: Dict[str, Any], timeout: Optional[int] = None) -> WebElement:
        """
        Wait for an element to be present.
        
        Args:
            obj: Dictionary containing element properties
            timeout: Maximum time to wait in seconds (default: self.wait_time)
            
        Returns:
            WebElement: The found element
            
        Raises:
            TimeoutException: If the element is not found within the timeout
        """
        if timeout is None:
            timeout = self.wait_time
            
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        locators = json.loads(obj["propertyMap"]).get('locators', [])
        
        for locator in locators:
            locator_type = locator.get('type', '').lower()
            locator_value = locator.get('value')
            
            if not locator_value:
                continue
                
            try:
                if locator_type == 'name':
                    return WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((AppiumBy.NAME, locator_value))
                    )
                elif locator_type == 'id':
                    return WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((AppiumBy.ID, locator_value))
                    )
                elif locator_type == 'xpath':
                    return WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((AppiumBy.XPATH, locator_value))
                    )
                elif locator_type == 'class_name':
                    return WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((AppiumBy.CLASS_NAME, locator_value))
                    )
                elif locator_type == 'accessibility_id':
                    return WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, locator_value))
                    )
            except Exception as e:
                self.logger.debug(f"Failed to find element by {locator_type}: {locator_value}. Error: {e}")
                continue
                
        raise NoSuchElementException(f"Element not found using locators: {locators}")


class NoSuchElementException(Exception):
    """Raised when an element cannot be found."""
    pass


class NoSuchWindowException(Exception):
    """Raised when a window cannot be found."""
    pass