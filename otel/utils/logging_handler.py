import logging
import os
from logging import Logger


def setup_otel_logging_handler(
        logger: Logger,
        service_name: str,
        service_instance_id: str = os.environ.get("HOSTNAME", "UNKNOWN"),
        deployment_environment: str = os.environ.get("GLOBAL_ENV", "UNKNOWN"),
        service_namespace: str = os.environ.get("GLOBAL_NAMESPACE", "UNKNOWN"),
        otlp_endpoint: str = None
) -> None:
    """
    Set up the OpenTelemetry logging handler for the given logger.

    This method configures the logger to use the OpenTelemetry logging handler,
    which exports log records to an OTLP (OpenTelemetry Protocol) endpoint.

    Args:
        logger (Logger): The logger to set up the handler for.
        service_name (str): The name of the service.
        service_instance_id (str, optional): The instance ID of the service.
            Defaults to the value of the "HOSTNAME" environment variable or "UNKNOWN".
        deployment_environment (str, optional): The deployment environment of the service.
            Defaults to the value of the "GLOBAL_ENV" environment variable or "UNKNOWN".
        service_namespace (str, optional): The namespace of the service.
            Defaults to the value of the "GLOBAL_NAMESPACE" environment variable or "UNKNOWN".
        otlp_endpoint (str, optional): The OTLP endpoint to export log records to.
            If not provided, the default exporter configuration is used.

    Raises:
        ImportError: If the required OpenTelemetry libraries are not installed.
    """

    # Check for required libraries
    try:
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    except ImportError as e:
        missing_package = str(e).split("'")[-2]
        raise ImportError(
            f"The required library '{missing_package}' is not installed. "
            f"Please install it using the following command:\n\n"
            f"pip install opentelemetry-sdk opentelemetry-exporter-otlp"
        ) from e

    # Create a resource with the service metadata
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.instance.id": service_instance_id,
            "deployment.environment": deployment_environment,
            "service.namespace": service_namespace
        }
    )

    # Set up the OTLP logging handler with or without a custom endpoint
    exporter = OTLPLogExporter(endpoint=otlp_endpoint) if otlp_endpoint else OTLPLogExporter()
    provider = LoggerProvider(resource=resource)
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=provider)
    logger.addHandler(handler)
