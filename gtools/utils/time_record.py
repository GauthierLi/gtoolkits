import time


def print_run_time(func):
    """count function time

    Usages:
    ---
    >>>    @print_run_time
    >>>    def add(a: int, b: int) -> int:
    >>>        return a + b
    """

    def wrapper(*args, **kw):
        local_time = time.time()
        result = func(*args, **kw)
        print(
            f"""\rCurrent Function: [{func.__name__}(args={[type(arg) for arg in args]},\
kwargs={[(k, type(v)) for k, v in kw.items()]})];\
run time is {time.time() - local_time:.5f}""",
            end="",
        )
        return result

    return wrapper
