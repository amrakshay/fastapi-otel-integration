import os


def enable_pyroscope(
        service_name: str,
        server_address: str = "http://localhost:4040",
        service_instance_id: str = os.environ.get("HOSTNAME", "UNKNOWN"),
        deployment_environment: str = os.environ.get("GLOBAL_ENV", "UNKNOWN"),
        service_namespace: str = os.environ.get("GLOBAL_NAMESPACE", "UNKNOWN"),
):
    """
    Configures Pyroscope for profiling with the specified service name and server address.

    Args:
        service_name (str): The name of the service to profile.
        server_address (str): The address of the Pyroscope server.

    Raises:
        ImportError: If the Pyroscope library is not installed, prompts the user to install it.
    """
    try:
        import pyroscope
    except ImportError:
        raise ImportError(
            "The 'pyroscope' library is not installed. Please install it using the following command:\n"
            "pip install pyroscope-io"
        )

    pyroscope.configure(
        application_name=service_name,
        server_address=server_address,
        enable_logging=True,
        report_pid=True,
        report_thread_id=True,
        report_thread_name=True,
        tags={
            "service_instance_id": service_instance_id,
            "deployment_environment": deployment_environment,
            "service_namespace": service_namespace
        }
    )
