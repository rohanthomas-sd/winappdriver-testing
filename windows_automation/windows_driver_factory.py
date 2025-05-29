import os
import time
import logging
from typing import Dict, Any, Optional

from appium import webdriver
from appium.options.windows import WindowsOptions
from appium.webdriver.appium_service import AppiumService

# Use full package path for imports
from windows_automation.windows_driver import WindowsDriver
from windows_automation.windows_client import WindowsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('windows_driver.log')
    ]
)
logger = logging.getLogger(__name__)

# Constants
IMPLICIT_WAIT = 60  # seconds

def get_windows_capabilities(req):
    """
    Get Windows capabilities from the test request.
    
    Args:
        req (dict): Test configuration
        
    Returns:
        tuple: (capabilities, hub_url) where capabilities is a dict and hub_url is a string
    """
    # Get the hub URL with a default value
    hub_url = req.get('desktopDevice', {}).get('grid', {}).get('hubUrl', 'http://127.0.0.1:4721')
    
    # Get app path and capabilities
    app_path = req.get('desktopDevice', {}).get('appPath', '')
    capabilities = req.get('desktopDevice', {}).get('desiredCapabilities', {})
    
    # Create Windows options
    options = WindowsOptions()
    
    # Set app path if provided - this is required
    if app_path:
        logger.info(f"Setting app path: {app_path}")
        options.app = app_path
    
    # Set additional capabilities
    for key, value in capabilities.items():
        # Remove any 'appium:' prefix as we'll handle it properly
        clean_key = key.replace('appium:', '')
        
        # Special handling for appTopLevelWindow
        if clean_key == 'appTopLevelWindow':
            logger.info(f"Setting appTopLevelWindow: {value}")
            options.set_capability('appTopLevelWindow', value)
        # Handle ms: prefixed capabilities
        elif clean_key.startswith('ms:'):
            logger.info(f"Setting {clean_key}: {value}")
            options.set_capability(clean_key, value)
        # Standard capabilities
        else:
            logger.info(f"Setting capability {clean_key}: {value}")
            options.set_capability(clean_key, value)
    
    # Set default capabilities if not provided
    if not any('automationName' in k for k in options.capabilities):
        logger.info("Setting default automationName: Windows")
        options.set_capability('automationName', 'Windows')
    
    if 'platformName' not in options.capabilities:
        logger.info("Setting default platformName: Windows")
        options.set_capability('platformName', 'Windows')
    
    if not any('deviceName' in k for k in options.capabilities):
        logger.info("Setting default deviceName: WindowsPC")
        options.set_capability('deviceName', 'WindowsPC')
    
    # Ensure we have either app or appTopLevelWindow
    has_app = any('app' in k.lower() for k in options.capabilities)
    has_app_top_level = any('apptoplevelwindow' in k.lower() for k in options.capabilities)
    
    if not has_app and not has_app_top_level:
        if app_path:
            logger.info("Setting app capability from appPath")
            options.app = app_path
        else:
            logger.warning("Neither 'app' nor 'appTopLevelWindow' capability is set")
    
    logger.debug(f"Final capabilities: {options.capabilities}")
    return options, hub_url

def create_windows_driver(req):
    """
    Create a Windows driver instance.
    
    Args:
        req (dict): Test configuration
        
    Returns:
        WindowsDriver: Initialized Windows driver instance
    """
    try:
        logger.info("Creating Windows driver...")
        
        # Get capabilities and hub URL
        options, hub_url = get_windows_capabilities(req)
        
        logger.info(f"Connecting to Appium Windows Driver at {hub_url}")
        logger.debug(f"Using capabilities: {options.capabilities}")
        
        # Create the driver
        driver = create_remote_windows_driver(req, options, hub_url)
        
        if not driver or not hasattr(driver, 'driver') or not driver.driver:
            raise Exception("Failed to create Windows driver")
            
        logger.info("Successfully created Windows driver")
        return driver
        
    except Exception as e:
        logger.error(f"Failed to create Windows driver: {e}")
        raise

def create_remote_windows_driver(req, options, hub_url):
    """
    Create a remote Windows driver instance.
    
    Args:
        req (dict): Test configuration
        options: WebDriver options
        hub_url (str): URL of the Appium server
        
    Returns:
        WindowsDriver: Initialized Windows driver instance
    """
    try:
        # Create the remote WebDriver
        appium_driver = webdriver.Remote(
            command_executor=hub_url,
            options=options
        )
        
        # Create and return the WindowsDriver instance
        return WindowsDriver(
            req=req,
            driver=appium_driver,
            service=None,  # No service needed for remote driver
            driver_type='WindowsDriver',
            implicit_wait=IMPLICIT_WAIT
        )
        
    except Exception as e:
        logger.error(f"Failed to create remote Windows driver: {e}")
        raise

def start_windows_appium_service(port=4723):
    """
    Starts the Appium service for Windows automation.
    
    Args:
        port (int): Port number to start the Appium service on
        
    Returns:
        AppiumService: The Appium service instance
    """
    appium_service = AppiumService()
    appium_service.start(args=['--port', str(port)])
    return appium_service