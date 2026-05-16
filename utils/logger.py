import logging
import os
from datetime import datetime

# Define the log file name with timestamp for uniqueness
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Create a 'logs' directory in the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_path = os.path.join(project_root, "logs", LOG_FILE)
os.makedirs(os.path.dirname(logs_path), exist_ok=True)

# Configure the logging
logging.basicConfig(
    filename=logs_path,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Example usage/testing block
if __name__ == "__main__":
    logging.info("Logging has started successfully.")
    print(f"Logs are being saved to: {logs_path}")
