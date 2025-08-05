class CustomMetricsManager:
    """
    A manager class for handling custom OpenTelemetry metrics, including metrics for FastAPI applications

    This class is implemented as a singleton, ensuring that metrics are only initialized once per application.

    Attributes:
        _initialized (bool): Indicates whether the manager has been initialized.
        _meter (Optional[Meter]): The OpenTelemetry meter used to record metrics.
        _fastapi_metrics_manager (Optional[FastAPIMetricsManager]): The metrics manager for FastAPI applications.
        _outgoing_http_metrics_manager (Optional[OutgoingHttpMetricsManager]): The metrics manager for outgoing HTTP requests.
    """
    _instance = None
    _lock = None

    def __new__(cls):
        if cls._instance is None:
            import threading
            if cls._lock is None:
                cls._lock = threading.Lock()
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CustomMetricsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = False
            self._meter = None
            self._fastapi_metrics_manager = None
            self._outgoing_http_metrics_manager = None
            self.app_name = None

    def init(self, application_name: str) -> None:
        """
        Initialize the CustomMetricsManager with a specific application name.

        This method sets up the OpenTelemetry meter provider and creates a meter
        for recording metrics. It must be called before any other methods in this class.

        Args:
            application_name (str): The name of the application, used to create the meter.

        Raises:
            ImportError: If the required OpenTelemetry libraries are not installed.
        """
        if not self._initialized:
            try:
                from opentelemetry import metrics
                from opentelemetry.sdk.metrics import MeterProvider
            except ImportError as e:
                missing_package = str(e).split("'")[-2]
                raise ImportError(
                    f"The required library '{missing_package}' is not installed. "
                    f"Please install it using the following command:\n\n"
                    f"pip install opentelemetry-sdk"
                ) from e

            metrics.set_meter_provider(MeterProvider())
            self.app_name = application_name
            self._meter = metrics.get_meter(application_name)
            self._initialized = True

    def get_meter(self):
        """
        Get the meter instance.
        """
        return self._meter
    
    def get_or_create_outgoing_http_metrics_manager(self):
        """
        Get the outgoing HTTP metrics manager instance.
        """
        if not self._initialized:
            raise RuntimeError("CustomMetricsManager is not initialized. Call init first.")

        if self._outgoing_http_metrics_manager is None:
            self.register_outgoing_http_metrics(self.app_name, self.app_name)

        return self._outgoing_http_metrics_manager

    def register_fastapi_metrics(self, app, service_name: str) -> None:
        """
        Register a FastAPI application for metrics collection.

        This method sets up a FastAPI metrics manager and registers the provided
        FastAPI application for metric collection.

        Args:
            app: The FastAPI application instance to register.
            service_name (str): The name of the service to associate with the metrics.

        Raises:
            RuntimeError: If the manager has not been initialized.
            ImportError: If the required FastAPI metrics manager module is not installed.
        """
        if not self._initialized:
            raise RuntimeError("CustomMetricsManager is not initialized. Call init first.")

        if self._fastapi_metrics_manager is None:
            from .fastapi_metrics_manager import FastAPIMetricsManager

            self._fastapi_metrics_manager = FastAPIMetricsManager(self._meter)
            self._fastapi_metrics_manager.register_for_metrics(app, service_name)

    def register_outgoing_http_metrics(self, app_name: str, service_name: str) -> None:
        """
        Register a FastAPI application for metrics collection.
        """
        if not self._initialized:
            raise RuntimeError("CustomMetricsManager is not initialized. Call init first.")

        if self._outgoing_http_metrics_manager is None:
            from .outgoing_http_metrics_manager import OutgoingHttpMetricsManager
            self._outgoing_http_metrics_manager = OutgoingHttpMetricsManager(self._meter, app_name, service_name)