from abc import ABC, abstractmethod


# create an interface for providers (abstract class)
# create an interface for providers (abstract class)
class ProviderInterface(ABC):

    def __init__(self):
        """
        Initializes the Provider with the necessary API key and client.
        """
        # experiment constants
        self.min_tokens = 10000
        self.system_prompt = (
            f"Please provide a detailed response of MORE THAN {self.min_tokens} words"
        )

        # metrics
        self.metrics = {
            "response_times": {},
            "timetofirsttoken": {},
            "totaltokens": {},
            "tps": {},
            "timebetweentokens": {},
            "timebetweentokens_median": {},
            "timebetweentokens_p95": {},
        }

    def log_metrics(self, model_name, metric, value):
        """
        Logs metrics
        """
        if metric not in self.metrics:
            raise ValueError(f"Metric type '{metric}' is not defined.")
        if model_name not in self.metrics[metric]:
            self.metrics[metric][model_name] = []

        if metric == "timebetweentokens":
            self.metrics[metric][model_name].extend(value)
        else:
            self.metrics[metric][model_name].append(value)

    @abstractmethod
    def perform_inference(self, model, prompt):
        """
        perform_inference
        """
        pass

    @abstractmethod
    def perform_inference_streaming(self, model, prompt):
        """
        perform_inference_streaming
        """
        pass

    @abstractmethod
    def get_model_name(self, model):
        """
        get model names
        """
        pass
