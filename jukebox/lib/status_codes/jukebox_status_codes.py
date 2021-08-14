from enum import Enum, Flag, auto
from dataclasses import dataclass
from typing import Any

class JukeBoxStatusCode(Flag):
    Unknown = auto()
    Success = auto()
    ApiRequestError = auto()
    UriServiceNotCompatible = auto()
    GotLowerAudioQuality = auto()
    GotHigherAudioQuality = auto()
    FormatMapDontHaveTrackService = auto()
    ClientNotLoggedIn = auto()
    
    #? Deezer Status Code
    DeezerApiError = auto()
    DeezerApiDataNotFound = auto()
    DeezerLoginFaile = auto()

    
    #? Tidal Status Code
    TidalApiError = auto()
    TidalDeviceAuthorizationFailed = auto()
    TidalAuthorizationCheckStatus = auto()
    TidalAuthorizationCheckTimeout = auto()

@dataclass
class JukeBoxStatus:
    status_code:JukeBoxStatusCode = JukeBoxStatusCode.Unknown
    msg:Any = None
