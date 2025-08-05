from .otel_global_attributes import get_global_attributes

class OutgoingHttpMetricsManager:
    """
    A manager class for handling outgoing HTTP metrics using OpenTelemetry.

    Attributes:
        meter: The OpenTelemetry meter used for creating and recording metrics.
    """

    def __init__(self, meter, app_name: str, service_name: str):
        """
        Initializes the OutgoingHttpMetricsManager with the provided OpenTelemetry meter.

        Args:
            meter: An OpenTelemetry meter instance for creating metrics.
        """
        self.meter = meter
        self.app_name = app_name
        self.service_name = service_name
        self._setup()

    def _setup(self):
        """
        Sets up the various metrics for monitoring outgoing HTTP requests.

        This method creates counters, histograms, and gauges for tracking outgoing HTTP requests.
        """
        self.outgoing_http_requests_sent_count = self.meter.create_counter(
            name="outgoing_http_requests_sent_count",
            description="Total count of outgoing HTTP requests by method and path.",
        )

        self.outgoing_http_requests_duration_milliseconds = self.meter.create_histogram(
            name="outgoing_http_requests_duration_milliseconds",
            description="Histogram of outgoing HTTP request processing time by path (in milliseconds).",
        )

    def _get_attributes(self, method: str, path: str, extra_attributes: dict = {}) -> dict:
        """
        Constructs the attributes dictionary for a given request.

        Args:
            request (Request): The incoming HTTP request.
            extra_attributes (dict): Additional attributes to include.

        Returns:
            dict: A dictionary of attributes for the metrics.
        """
        attributes = get_global_attributes()
        attributes.update({
            "method": method,
            "path": path,
            "app_name": self.app_name,
            "service_name": self.service_name
        })
        attributes.update(extra_attributes)
        return attributes

    def increment_outgoing_http_requests_sent_count(self, method: str, path: str, extra_attributes: dict = {}):
        """
        Increments the outgoing HTTP requests sent count.
        """
        self.outgoing_http_requests_sent_count.add(1, self._get_attributes(method, path, extra_attributes))

    def record_outgoing_http_requests_duration_milliseconds(self, method: str, path: str, status_code: int, duration: float, extra_attributes: dict = {}):
        """
        Records the outgoing HTTP requests duration milliseconds.
        """
        extra_attributes["status_code"] = status_code
        self.outgoing_http_requests_duration_milliseconds.record(
            duration,
            self._get_attributes(method, path, extra_attributes)
        )
