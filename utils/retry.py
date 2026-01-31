import time
import functools
from typing import Callable, Type, Tuple, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)


def retry_on_exception(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable = None
):
    """
    Decorator to retry a function on exception.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry (1.0 = constant)
        exceptions: Tuple of exception types to catch
        on_retry: Optional callback function called on each retry
    
    Example:
        @retry_on_exception(max_attempts=3, delay=1, backoff=2)
        def unreliable_function():
            # might fail
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.debug(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
                    result = func(*args, **kwargs)
                    
                    if attempt > 1:
                        logger.info(f"✓ {func.__name__} succeeded on attempt {attempt}")
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts:
                        logger.warning(
                            f"✗ {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}"
                        )
                        
                        if on_retry:
                            on_retry(attempt, e)
                        
                        logger.info(f"Retrying in {current_delay:.1f}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"✗ {func.__name__} failed after {max_attempts} attempts"
                        )
            
            # All attempts exhausted
            raise last_exception
        
        return wrapper
    return decorator


class RetryContext:
    """
    Context manager for manual retry logic.
    
    Example:
        with RetryContext(max_attempts=3, delay=1) as retry:
            for attempt in retry:
                try:
                    result = do_something()
                    break
                except SomeError as e:
                    if not retry.should_retry(e):
                        raise
    """
    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 1.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.initial_delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
        self.current_attempt = 0
        self.current_delay = delay
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False  # Don't suppress exceptions
    
    def __iter__(self):
        for attempt in range(1, self.max_attempts + 1):
            self.current_attempt = attempt
            yield attempt
    
    def should_retry(self, exception: Exception) -> bool:
        """Check if we should retry after this exception."""
        if not isinstance(exception, self.exceptions):
            return False
        
        if self.current_attempt >= self.max_attempts:
            return False
        
        logger.warning(
            f"Attempt {self.current_attempt}/{self.max_attempts} failed: {exception}"
        )
        logger.info(f"Retrying in {self.current_delay:.1f}s...")
        time.sleep(self.current_delay)
        self.current_delay *= self.backoff
        
        return True


def retry_function(
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Any:
    """
    Retry a function without using a decorator.
    
    Args:
        func: Function to retry
        args: Positional arguments for func
        kwargs: Keyword arguments for func
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries
        backoff: Delay multiplier after each retry
        exceptions: Exception types to catch
    
    Returns:
        Result of successful function call
    
    Raises:
        Last exception if all attempts fail
    """
    if kwargs is None:
        kwargs = {}
    
    current_delay = delay
    last_exception = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            
            if attempt < max_attempts:
                logger.warning(
                    f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}"
                )
                time.sleep(current_delay)
                current_delay *= backoff
    
    raise last_exception


if __name__ == "__main__":
    # Test retry decorator
    attempt_count = 0
    
    @retry_on_exception(max_attempts=3, delay=0.5, backoff=2)
    def flaky_function():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError("Not yet!")
        return "Success!"
    
    try:
        result = flaky_function()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed: {e}")
    
    # Test RetryContext
    print("\nTesting RetryContext:")
    with RetryContext(max_attempts=3, delay=0.5) as retry:
        for attempt in retry:
            try:
                if attempt < 2:
                    raise RuntimeError("Not ready")
                print("Success with context manager!")
                break
            except RuntimeError as e:
                if not retry.should_retry(e):
                    raise
