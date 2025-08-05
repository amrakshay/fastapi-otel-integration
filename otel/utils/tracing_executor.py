import asyncio
from typing import Callable, Any


async def run_in_executor_with_otel_tracing(func: Callable[[], Any]) -> Any:
    """
    Run the given function within the OpenTelemetry tracing context in an asynchronous executor.

    This method ensures that the provided function is executed in a separate thread while preserving the current tracing context.

    Args:
        func (Callable[[], Any]): The function to run. It should not require any arguments.

    Returns:
        Any: The result of the function execution.

    Raises:
        ImportError: If the required OpenTelemetry libraries are not installed.
    """
    # Check for required libraries
    try:
        from opentelemetry.context import attach, detach, get_current
    except ImportError as e:
        missing_package = str(e).split("'")[-2]
        raise ImportError(
            f"The required library '{missing_package}' is not installed. "
            f"Please install it using the following command:\n\n"
            f"pip install opentelemetry-api"
        ) from e

    # Capture the current tracing context
    context = get_current()

    def wrapper() -> Any:
        """
        Wrapper function to attach the captured context to the current thread
        and execute the provided function.

        Returns:
            Any: The result of the function execution.
        """
        token = attach(context)
        try:
            return func()
        finally:
            detach(token)

    # Run the wrapper function in an executor within the current event loop
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, wrapper)
