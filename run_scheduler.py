#!/usr/bin/env python3
"""
Script to run the reminder scheduler.
This script starts the scheduler and keeps it running.
"""

import sys
import os
import signal
import logging

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scheduler import run_scheduler
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main function to run the scheduler."""
    logger.info("Starting reminder scheduler...")
    logger.info(f"Database path: {Config.DATABASE_PATH}")
    logger.info(f"Log level: {Config.LOG_LEVEL}")
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run the scheduler
        run_scheduler(Config.DATABASE_PATH)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Error running scheduler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 