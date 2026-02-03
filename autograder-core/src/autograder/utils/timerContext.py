import time
from contextlib import contextmanager

from autograder.data.StepLatency import StepLatency

@contextmanager
def step_timer(stepLatencyData: StepLatency, name: str, numSubmissions: int):
    try:
        start = time.perf_counter()
        yield
        cumulativeLatency = getattr(stepLatencyData, name) * (numSubmissions - 1)
        curLatency = (time.perf_counter() - start) * 1000
        setattr(stepLatencyData, name, (cumulativeLatency + curLatency) // numSubmissions)
    except Exception as e   :
        print(e)
        print(f"Exception occurred during timing of step: {name}", str(e))
        raise Exception(f"Exception occurred during timing of step: {name}", str(e))
