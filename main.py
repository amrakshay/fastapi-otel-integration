
import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from otel.metrics.custom_metrics_manager import CustomMetricsManager
import otel_utils
from paig_os_utils import ensure_log_files_exist
from otel.metrics.outgoing_http_metrics_manager import OutgoingHttpMetricsManager

# Setup Logger
import logging.config
logging.config.fileConfig("default-logging-config.ini")

IQ_LOGGER_NAME = "trust3_iq"
ACCESS_LOGGER_NAME = "trust3_iq_access"

def get_iq_logger():
    return logging.getLogger(IQ_LOGGER_NAME)


def get_access_logger():
    return logging.getLogger(ACCESS_LOGGER_NAME)


logger = get_iq_logger()
access_logger = get_access_logger()


def load_configs():
    # Ensure log files exist
    ensure_log_files_exist()

    if otel_utils.is_app_tracing_enabled():
        logger.info("APP Tracing is enabled so setting up OTEL configurations")
        service_name = os.environ.get("APP_NAME", "trust3_iq")
        otel_utils.setup_otel(service_name, logger, app)
    else:
        logger.info("APP Tracing is disabled, skipping OTEL configurations")


# Setup FastAPI App
app = FastAPI()

# Load configuration
load_configs()

custom_metrics_manager = CustomMetricsManager()
outgoing_http_metrics_manager = custom_metrics_manager.get_or_create_outgoing_http_metrics_manager()

def log_access_request(request: Request, response, request_process_start_time):
    routes_to_ignore = ["/"]
    if request.url.path in routes_to_ignore:
        return

    headers = request.headers

    # record the access logs
    tenant_id = headers.get('x-tenant-id', 'N/A')
    host = headers.get('Host', 'N/A')
    end_time = time.time()
    elapsed_time_ms = (end_time - request_process_start_time) * 1000

    access_log_message = (f"[{host}] -- [{tenant_id}] \"{request.method} {request.url.path}\" {response.status_code} "
                          f"{elapsed_time_ms:.3f} ms")
    access_logger.info(access_log_message)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_start_time = time.time()
    path, method = request.url.path, request.method
    headers = request.headers
    tenant_id = headers.get('x-tenant-id', 'N/A')
    if not path.startswith('/api/healthcheck') and (path.startswith("/public/api") or path.startswith("/api")) and tenant_id == 'N/A':
        return JSONResponse(status_code=400, content={"error": "Bad Request", "message": f"Missing 'x-tenant-id' header in the request: {path}"})
    response = None

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"[{tenant_id}] Error processing request: {e}")
        response = JSONResponse(
            status_code=500,
            content={
                "error_code": 500,
                "success": False,
                "message": "An unexpected error occurred. Please try again later."
            }
        )

    log_access_request(request, response, request_start_time)
    return response


@app.get("/", tags=["HealthCheck"])
@app.get("/api/healthcheck/status", tags=["HealthCheck"])
def healthcheck():
    return "PAIG Guardrails Running..."

@app.get("/hello", tags=["Hello"])
async def hello():
    return {"message": "Hello World"}

@app.get("/trust3", tags=["Trust3"])
async def trust3():
    outgoing_http_metrics_manager.increment_outgoing_http_requests_sent_count("GET", "/trust3")
    outgoing_http_metrics_manager.record_outgoing_http_requests_duration_milliseconds("GET", "/trust3", 200, 100)
    return {"message": "Trust3 Called"}

@app.get("/snowflake", tags=["Snowflake"])
async def snowflake():
    outgoing_http_metrics_manager.increment_outgoing_http_requests_sent_count("GET", "/snowflake")
    outgoing_http_metrics_manager.record_outgoing_http_requests_duration_milliseconds("GET", "/snowflake", 200, 150)
    return {"message": "Snowflake Called"}

@app.get("/salesforce", tags=["Salesforce"])
async def salesforce():
    outgoing_http_metrics_manager.increment_outgoing_http_requests_sent_count("GET", "/salesforce")
    outgoing_http_metrics_manager.record_outgoing_http_requests_duration_milliseconds("GET", "/salesforce", 200, 200)
    return {"message": "Salesforce Called"}

@app.get("/exception", tags=["Exception"])
async def exception():
    outgoing_http_metrics_manager.increment_outgoing_http_requests_sent_count("GET", "/exception")
    outgoing_http_metrics_manager.record_outgoing_http_requests_duration_milliseconds("GET", "/exception", 500, 250)
    raise Exception("Exception")

@app.get("/bad-request", tags=["BadRequest"])
async def bad_request():
    """Endpoint that returns 400 status code"""
    outgoing_http_metrics_manager.increment_outgoing_http_requests_sent_count("GET", "/bad-request")
    outgoing_http_metrics_manager.record_outgoing_http_requests_duration_milliseconds("GET", "/bad-request", 400, 100)
    return JSONResponse(
        status_code=400,
        content={
            "error": "Bad Request",
            "message": "This endpoint intentionally returns a 400 status code",
            "code": 400
        }
    )

@app.post("/create-resource", tags=["CreateResource"])
async def create_resource():
    """Endpoint that returns 201 status code"""
    outgoing_http_metrics_manager.increment_outgoing_http_requests_sent_count("POST", "/create-resource")
    outgoing_http_metrics_manager.record_outgoing_http_requests_duration_milliseconds("POST", "/create-resource", 201, 100)
    return JSONResponse(
        status_code=201,
        content={
            "message": "Resource created successfully",
            "resource_id": "12345",
            "status": "created"
        }
    )
