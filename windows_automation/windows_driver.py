import os
import time
import logging
import base64
import cv2
import numpy as np
from typing import Dict, Any, Optional, List, Union

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

# Use full package path for imports
from windows_automation.windows_client import WindowsClient

# Configure logging
logger = logging.getLogger(__name__)


class WindowsDriver:
    """
    WindowsDriver provides a high-level interface for Windows application automation.
    """
    
    def __init__(self, req, driver, service, driver_type, implicit_wait=30):
        """
        Initialize the WindowsDriver.
        
        Args:
            req: Test configuration
            driver: WebDriver instance
            service: Appium service instance
            driver_type: Type of driver (e.g., 'WindowsDriver')
            implicit_wait: Implicit wait time in seconds
        """
        self.driver = driver
        self.service = service
        self.driver_type = driver_type
        self.req = req
        self.client = WindowsClient(self.driver)
        
        # Set implicit wait
        self.driver.implicitly_wait(implicit_wait)
        logger.info(f"Initialized WindowsDriver with implicit wait: {implicit_wait}s")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
    
    def quit(self):
        """Quit the driver and clean up resources."""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
                logger.info("Successfully quit WebDriver")
            except Exception as e:
                logger.error(f"Error quitting WebDriver: {e}")
        
        if hasattr(self, 'service') and self.service:
            try:
                self.service.stop()
                logger.info("Successfully stopped Appium service")
            except Exception as e:
                logger.error(f"Error stopping Appium service: {e}")
    
    def click(self, element, timeout=10):
        """
        Click on an element.
        
        Args:
            element: Element to click
            timeout: Maximum time to wait for the element to be clickable
            
        Returns:
            bool: True if click was successful, False otherwise
        """
        return self.client.click(element, timeout)
    
    def enter_text(self, element, text, clear_first=True, timeout=10):
        """
        Enter text into an input field.
        
        Args:
            element: Input element
            text: Text to enter
            clear_first: Whether to clear the field first
            timeout: Maximum time to wait for the element to be present
            
        Returns:
            bool: True if text was entered successfully, False otherwise
        """
        return self.client.enter_text(element, text, clear_first, timeout)
    
    def get_text(self, element, timeout=10):
        """
        Get text from an element.
        
        Args:
            element: Element to get text from
            timeout: Maximum time to wait for the element to be present
            
        Returns:
            str: Text content of the element
        """
        return self.client.get_text(element, timeout)
    
    def is_visible(self, element, timeout=10):
        """
        Check if an element is visible.
        
        Args:
            element: Element to check
            timeout: Maximum time to wait for the element
            
        Returns:
            bool: True if element is visible, False otherwise
        """
        return self.client.is_visible(element, timeout)
    
    def take_screenshot(self, filename=None):
        """
        Take a screenshot of the current window.
        
        Args:
            filename: Optional filename to save the screenshot
            
        Returns:
            str: Path to the saved screenshot or the image data if no filename provided
        """
        return self.client.take_screenshot(filename)