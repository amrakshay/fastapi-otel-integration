export OTEL_SERVICE_NAME=trust3_iq
export OTEL_TRACES_EXPORTER=otlp
export OTEL_METRICS_EXPORTER=otlp
export OTEL_LOGS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_RESOURCE_ATTRIBUTES="deployment.environment=local,service.namespace=akshay,service.instance.id=localhost"
export OTEL_EXTRA_OPTS=""

export APP_TRACING_ENABLED=true
export OTEL_ENABLE_LOG_EXPORT=true
export OTEL_ENABLE_CUSTOM_METRICS=true
export OTEL_ENABLE_FASTAPI_METRICS=true
export OTEL_ENABLE_OUTGOING_HTTP_METRICS=true
export OTEL_ENABLE_PYROSCOPE=false
export OTEL_PYROSCOPE_SERVER_ADDRESS=http://localhost:4040

export SET_GLOBAL_OTEL_ATTRIBUTES=true
export K8S_NAMESPACE_NAME=akshay
export K8S_POD_NAME=trust3_iq_local
export TENANT_ID=1234567890

export OTEL_LOG_LEVEL=DEBUG
export OTEL_PYTHON_LOG_LEVEL=DEBUG

opentelemetry-instrument \
    --service_name ${OTEL_SERVICE_NAME:=${APP_NAME}} \
    --traces_exporter ${OTEL_TRACES_EXPORTER:="otlp"} \
    --metrics_exporter ${OTEL_METRICS_EXPORTER:="otlp"} \
    --logs_exporter ${OTEL_LOGS_EXPORTER:="otlp"} \
    --exporter_otlp_protocol ${OTEL_EXPORTER_OTLP_PROTOCOL:="http/protobuf"} \
    --exporter_otlp_endpoint ${OTEL_EXPORTER_OTLP_ENDPOINT:="http://opentelemetry-collector.monitoring.svc.cluster.local:4318"} \
    --resource_attributes ${OTEL_RESOURCE_ATTRIBUTES:="deployment.environment=${GLOBAL_ENV:="UNKNOWN"},service.namespace=${GLOBAL_NAMESPACE:="UNKNOWN"},service.instance.id=${HOSTNAME:="UNKNOWN"}"} ${OTEL_EXTRA_OPTS} \
    python3 server.py

