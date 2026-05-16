from utils.logger import logging

if __name__ == "__main__":
    logging.info("This is a log message from an external module.")
    try:
        a = 1 / 0
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    
    print("Testing complete. Check the logs folder.")
