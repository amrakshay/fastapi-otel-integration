import os

def get_global_attributes():
    if os.getenv("SET_GLOBAL_OTEL_ATTRIBUTES") is not None and os.getenv("SET_GLOBAL_OTEL_ATTRIBUTES") == "true":
        return {
            "k8s_namespace_name": os.getenv("K8S_NAMESPACE_NAME", "unknown"),
            "k8s_pod_name": os.getenv("K8S_POD_NAME", "unknown"),
            "tenant_id": os.getenv("TENANT_ID", "unknown"),
        }
    
    return {}