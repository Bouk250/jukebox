from dataclasses import dataclass, replace
from enum import Enum, IntEnum
from typing import Union, Any

class Types(Enum):
    NOT_RECOGNIZED  = 'null'
    ISRC            = 'isrc'
    TRACK           = 'track'
    PLAYLIST        = 'playlist'
    ALBUM           = 'album'
    ARTIST          = 'artist'
    PODCASTS        = 'podcasts'
    VIDEO           = 'video'

class Services(Enum):
    NOT_RECOGNIZED = 'null'
    DEEZER = 'deezer'
    TIDAL = 'tidal'

class TrackFormats(bytes, Enum):

    HI_RES = (5, {
        Services.TIDAL:{
            'service_format': 'HI_RES',
            'extentions': {
                'audio/flac' : '.flac',
            },
        },
    })
    
    HI_FI = (4, {
        Services.DEEZER:{
            'service_format': 'FLAC',
            'extentions': {
                'FLAC' : '.flac',
            },
        },
        Services.TIDAL:{
            'service_format': 'LOSSLESS',
            'extentions': {
                'audio/flac' : '.flac',
            },
        },
    })
    
    LOSSY_320 = (3,{
        Services.DEEZER:{
            'service_format': 'MP3_320',
            'extentions': {
                'MP3_320' : '.mp3',
            },
        },
        Services.TIDAL:{
            'service_format': 'HIGH',
            'extentions': {
                'audio/mp4' : '.mp4',
            },
        },
    })
    
    LOSSY_256 = (2,{
        Services.DEEZER:{
            'service_format': 'MP3_256',
            'extentions': {
                'MP3_256' : '.mp3',
            },
        },
        Services.TIDAL:{
            'service_format': 'LOW',
            'extentions': {
                'audio/mp4' : '.mp4',
            },
        },
    })
    
    LOSSY_128 = (1, {
        Services.DEEZER:{
            'service_format': 'MP3_128',
            'extentions': {
                'MP3_128' : '.mp3',
            },
        },
    })

    UNKNOW = (0, {})
    
    def __new__(cls, key:int, services:dict):
        obj = bytes.__new__(cls,[key])
        obj._value_ = key
        obj.services = services
        return obj

    @classmethod
    def get_service_formats(cls, service:Services):
        formats = []
        for track_format in cls:
            if track_format.check_service_compatible(service):
                formats.append(track_format)
        return formats

    @classmethod
    def get_format_from_name(cls, service:Services, formate:str):
        formats = TrackFormats.get_service_formats(service)
        for track_format in formats:
            if track_format.services[service]['service_format'] == formate:
                return track_format
        return TrackFormats.UNKNOW

    def check_service_compatible(self, service:Services):
        return self.services.get(service) is not None

@dataclass
class Uri:
    service:Services
    type:Types
    id:str

    def __init__(self, service:Services, type:Types, id:Union[str,int]):
        self.service = service
        self.type = type
        self.id = str(id)

    def copy(self):
        return replace(self)

    def __str__(self):
        return f"{self.service.value}_{self.type.value}_{self.id}"

    def __hash__(self) -> int:
        return hash(str(self))

@dataclass
class StreamUrl:
    stream_track_format:TrackFormats
    stream_file_size:int = 0
    stream_url:str = ''
    stream_file_decrypter:Any = None
    stream_file_extention: str = ''

class FormatMap:
    def __init__(self):
        self._format_map = {}
    
    def set(self, service:Services, formate:TrackFormats):
        self._format_map[service] = formate

    def get(self, service:Services) -> TrackFormats:
        return self._format_map.get(service)