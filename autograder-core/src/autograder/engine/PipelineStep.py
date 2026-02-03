from abc import ABC, abstractmethod

from autograder.data import GradingContext

class PipelineStep(ABC):
    @abstractmethod
    def run(self, ctx: GradingContext, config: dict):
        pass

