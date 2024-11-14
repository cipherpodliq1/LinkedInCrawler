import json
import time

from logger.logger import Logger
from functools import wraps

retry_logger = Logger("Retry")
catch_logger = Logger('ExceptionsHandler')
__exceptions = (
    Exception,
    json.decoder.JSONDecodeError
)


def catch_exceptions(func, exceptions: tuple = __exceptions):
    """ decorator for catching selenium exceptions """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try: return func(*args, **kwargs)
        except exceptions as e:
            catch_logger.exception(f'function "{func.__name__}" with parameters: "{args, kwargs}" failed with exception {e}')
            return False

    return wrapper


def retry(
        func,
        times: int = 3,
        interval: int = 5,
        exceptions: tuple = __exceptions):
    """ decorator for retrying a function after failure """
    @wraps(func)
    def wrapper(*args, **kwargs):
        for _ in range(times):
            try:
                response = func(*args, **kwargs)
                if response is False:
                    retry_logger.error(f'function "{func.__name__}" with parameters: "{args, kwargs}" failed with bad response "{response}" retying after {interval} seconds.')
                    continue
                return response
            except exceptions as e:
                retry_logger.exception(f'function "{func.__name__}" with parameters: "{args, kwargs}" failed with exception "{e}" retrying after {interval} seconds.')
                time.sleep(interval)
        return False

    return wrapper
