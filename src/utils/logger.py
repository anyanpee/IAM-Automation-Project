"""
Logging configuration for IAM automation tool
"""

import logging
import os
# from colorama import init, Fore, Style  # Not available in Lambda
# init()  # Disabled for Lambda

def setup_logger():
    """Setup logging configuration"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create custom formatter with colors
    class ColoredFormatter(logging.Formatter):
        # Simplified formatter for Lambda (no colors)
        def format(self, record):
            return super().format(record)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Simple console handler for Lambda
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Get root logger and replace handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    return root_logger