from typing import Any


class JukeBoxMessageInterface:
    def send(self, result:Any):
        """Implement this class to process updates and messages from the core"""
        pass
