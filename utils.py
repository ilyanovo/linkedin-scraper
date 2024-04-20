import time

def retry_func(n_times: int = 5, sleep_time: int = 20):
    def decorator(func):
        def wrapper(*args, **kwargs):
            counter = 0
            for i in range(n_times):
                if counter > n_times:
                    raise Exception("Failed to get data")
                try:
                    resp = func(*args, **kwargs)
                    return resp
                except Exception as e:
                    time.sleep(sleep_time)
                    counter += 1
        return wrapper
    return decorator