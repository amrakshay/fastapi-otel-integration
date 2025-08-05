import os
from functools import lru_cache

from fastapi import FastAPI
import logging


@lru_cache
def is_app_tracing_enabled():
    return os.environ.get("APP_TRACING_ENABLED", "false").lower() == "true"

@lru_cache
def is_otel_log_export_enabled():
    return is_app_tracing_enabled() and \
        os.environ.get("OTEL_ENABLE_LOG_EXPORT", "false").lower() == "true"

def setup_otel(service_name: str, logger: logging.Logger, app: FastAPI) -> None:
    """
    Sets up OpenTelemetry (OTEL) configurations including log export, custom metrics, FastAPI metrics, and Pyroscope profiling.

    Args:
        service_name (str): The name of the service to be used for OTEL configurations.
        logger (logging.Logger): The logger instance to be used for setting up OTEL logging.
        app (FastAPI): The FastAPI application instance to register metrics with.

    Returns:
        None
    """

    logger.info(f"Setting up OTEL configurations for service: {service_name}")

    # Enable OTEL log export if configured
    enable_log_export = os.environ.get("OTEL_ENABLE_LOG_EXPORT", "false").lower() == "true"
    if enable_log_export:
        logger.info("OTEL log export is enabled. Setting up OTEL logging handler.")
        from otel.utils.logging_handler import setup_otel_logging_handler
        setup_otel_logging_handler(logger, service_name)
    else:
        logger.info("OTEL log export is disabled.")

    # Enable custom metrics if configured
    enable_custom_metrics = os.environ.get("OTEL_ENABLE_CUSTOM_METRICS", "false").lower() == "true"
    if enable_custom_metrics:
        logger.info("Custom metrics are enabled. Initializing CustomMetricsManager.")
        from otel.metrics.custom_metrics_manager import CustomMetricsManager
        custom_metrics_manager = CustomMetricsManager()
        custom_metrics_manager.init(service_name)

        # Enable FastAPI metrics if configured
        enable_fastapi_metrics = os.environ.get("OTEL_ENABLE_FASTAPI_METRICS", "false").lower() == "true"
        if enable_fastapi_metrics:
            logger.info("FastAPI metrics are enabled. Registering FastAPI metrics.")
            custom_metrics_manager.register_fastapi_metrics(app, service_name)
        else:
            logger.info("FastAPI metrics are disabled.")

        # Enable Outgoing Request Metrics if configured
        enable_outgoing_http_metrics = os.environ.get("OTEL_ENABLE_OUTGOING_HTTP_METRICS", "false").lower() == "true"
        if enable_outgoing_http_metrics:
            logger.info("Outgoing request metrics are enabled. Initializing OutgoingRequestMetricsManager.")
            custom_metrics_manager.register_outgoing_http_metrics(service_name, service_name)
        else:
            logger.info("Outgoing request metrics are disabled.")
    else:
        logger.info("Custom metrics are disabled.")

    # Enable Pyroscope profiling if configured
    enable_pyroscope = os.environ.get("OTEL_ENABLE_PYROSCOPE", "false").lower() == "true"
    if enable_pyroscope:
        logger.info("Pyroscope profiling is enabled. Setting up Pyroscope collector.")
        from otel.utils.pyroscope_collector import enable_pyroscope
        pyroscope_server_address = os.environ.get("OTEL_PYROSCOPE_SERVER_ADDRESS", "http://localhost:4040")
        enable_pyroscope(service_name, pyroscope_server_address)
    else:
        logger.info("Pyroscope profiling is disabled.")

    logger.info("OTEL setup completed.")

