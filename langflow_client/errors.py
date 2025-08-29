class LangflowError(Exception):
    def __init__(self, message: str, response):
        super().__init__(message)
        self.cause = response


class LangflowRequestError(Exception):
    def __init__(self, message: str, error: Exception | None = None):
        super().__init__(message)
        self.cause = error 