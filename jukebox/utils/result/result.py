from enum import Enum, auto, Flag
from typing import Any

class ResultCode(Flag):
    IN_PROCESS = auto()
    SUCCESS = auto()
    FAILED = auto()
    ERROR = auto()
    API_ERROR = auto()

class ExceptionCode(Flag):
    ITEMS_LIMIT_EXCEEDED_EXCEPTION = auto()
    PERMISSION_EXCEPTION = auto()
    INVALID_TOKEN_EXCEPTION = auto()
    WRONG_PARAMETER_EXCEPTION = auto()
    MISSING_PARAMETER_EXCEPTION = auto()
    INVALID_QUERY_EXCEPTION = auto()
    DATA_EXCEPTION = auto()
    INDIVIDUAL_ACCOUNT_CHANGED_NOT_ALLOWED_EXCEPTION = auto()
    ARL_LOGIN_EXCEPTION = auto()
    API_EXCEPTION = auto()
    EXCEPTION = auto()

class SuccessCode(Flag):
    ARL_LOGIN_SUCCESS = auto()
    SUCCESS = auto()

class Result:

    def __init__(self,result_code:Flag, value:Any=None):
        self.result_code = result_code
        self.value = value