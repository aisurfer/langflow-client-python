class UploadResponse:
    def __init__(self, response: dict):
        self.flow_id: str = response.get("flowId")
        self.file_path: str = response.get("file_path") 