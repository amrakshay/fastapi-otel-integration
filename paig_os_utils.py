import os

def ensure_log_files_exist():
    """
    Ensures that the logs directory and required log files exist.
    Creates them if they don't exist.
    """
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Create log files if they don't exist
    log_files = ["app.log", "access.log"]
    for log_file in log_files:
        log_path = os.path.join(logs_dir, log_file)
        if not os.path.exists(log_path):
            open(log_path, 'w').close()  # Create empty file

