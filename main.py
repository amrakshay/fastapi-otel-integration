
import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import otel_utils
from paig_os_utils import ensure_log_files_exist

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
