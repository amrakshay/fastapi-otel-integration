import uvicorn

from paig_os_utils import ensure_log_files_exist


def main():
    """
    Main function to start the server

    :return: None
    """
    # Ensure log files exist
    ensure_log_files_exist()

    # Retrieve the host address from the configuration, defaulting to "0.0.0.0" if not specified
    host = "0.0.0.0"

    # Retrieve the port number from the configuration, defaulting to 8080 if not specified
    port = 8000

    # Retrieve the number of Uvicorn workers from the configuration, defaulting to 1 if not specified
    workers = 1

    print("Starting server...")
    # Run the Uvicorn server with the specified app, host, port, and number of workers
    uvicorn.run(
        app="main:app",
        host=host,
        port=port,
        workers=workers,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error starting server: {e}")
