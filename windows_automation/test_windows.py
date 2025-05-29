import os
import time
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import our Windows automation components using full package path
from windows_automation.windows_driver_factory import create_windows_driver
from windows_automation.windows_client import WindowsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_windows.log')
    ]
)
logger = logging.getLogger(__name__)

# Test configuration for WinForms App
TEST_CONFIG = {
    'desktopDevice': {
        'appPath': r'C:\Code\New folder\WinFormsApp2\bin\ARM32\Debug\net8.0-windows\WinFormsApp2.exe',
        'grid': {
            # hubUrl will default to 'http://127.0.0.1:4723' in the driver factory
        },
        'desiredCapabilities': {
            'platformName': 'Windows',
            'automationName': 'Windows',
            'deviceName': 'WindowsPC',
            'app': r'C:\\Code\\New folder\\WinFormsApp2\\bin\\ARM32\\Debug\\net8.0-windows\\WinFormsApp2.exe'
        }
    },
    'testCase': {
        'name': 'WinForms App Test',
        'description': 'Test WinForms application using Appium Windows Driver'
    }
}

def create_test_object(locators: list) -> Dict[str, Any]:
    """
    Create a test object with the given locators.
    
    Args:
        locators: List of locator dictionaries with 'type' and 'value' keys
        
    Returns:
        Dictionary representing a test object
    """
    return {
        'id': f"element_{int(time.time())}",
        'name': 'Test Element',
        'propertyMap': json.dumps({
            'locators': locators
        })
    }

def test_winforms_app():
    """
    Test the WinForms application using the Windows driver.
    """
    logger.info("Starting WinForms application test...")
    driver = None
    
    try:
        # 1. Create Windows driver
        logger.info("1. Creating Windows driver...")
        driver = create_windows_driver(TEST_CONFIG)
        
        # 2. Interact with the WinForms app
        logger.info("2. Interacting with WinForms application...")
        
        # Wait for the application to be fully loaded
        time.sleep(2)  # Give the app time to initialize
        
        # 3. Find and click the "Click Me" button
        logger.info("3. Finding and clicking 'Click Me' button...")
        try:
            # Using find_element with AppiumBy.NAME for the button
            button = driver.driver.find_element(AppiumBy.NAME, "Click Me")
            button.click()
            logger.info("Successfully clicked 'Click Me' button")
        except Exception as e:
            logger.error(f"Failed to find or click button: {e}")
            logger.info("Available page source:")
            logger.info(driver.driver.page_source)
            raise
        
        # 4. Verify the label text
        logger.info("4. Verifying label text...")
        try:
            # Using find_element with AppiumBy.ACCESSIBILITY_ID for the label
            label = driver.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "lblMessage")
            actual_text = label.text
            expected_text = "Hello from WinForms!"
            
            logger.info(f"Label text: '{actual_text}'")
            
            if actual_text == expected_text:
                logger.info("Label text verification successful!")
            else:
                logger.error(f"Label text verification failed. Expected: '{expected_text}', Got: '{actual_text}'")
                raise AssertionError(f"Label text verification failed. Expected: '{expected_text}', Got: '{actual_text}'")
                
        except Exception as e:
            logger.error(f"Failed to verify label: {e}")
            raise
        
        logger.info("5. Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        return False
        
    finally:
        # Clean up
        if driver:
            try:
                logger.info("Cleaning up...")
                driver.quit()
                logger.info("Driver closed successfully")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    # Run the test
    success = test_winforms_app()
    
    # Exit with appropriate status code
    exit(0 if success else 1)