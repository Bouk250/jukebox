from datetime import date
from pprint import pprint
from dateutil.parser import parse
from dataclasses import asdict, dataclass, field
from marshmallow import Schema, fields, post_load, pre_load, EXCLUDE

from .types import Services, Uri
from .artist import Artist, ArtistSchema

from jukebox.utils.logs import JukeBoxLogger as logger
from jukebox.utils.utils import dict_recursive_get

key_map = {
    'id': {
        'key': {
            Services.DEEZER.value : ['SNG_ID'],
            Services.TIDAL.value : ['id'],
        },
        'convertor': lambda x: str(x)
    },
    'isrc': {
        'key': {
            Services.DEEZER.value : ['ISRC'],
            Services.TIDAL.value : ['isrc'],
        },
        'convertor': lambda x: str(x)
    },
    'title': {
        'key': {
            Services.DEEZER.value : ['SNG_TITLE'],
            Services.TIDAL.value : ['title'],
        },
        'convertor': lambda x: str(x)
    },
    'duration': {
        'key': {
            Services.DEEZER.value : ['DURATION'],
            Services.TIDAL.value : ['duration'],
        },
        'convertor': lambda x: int(x)
    },
    'md5': {
        'key': {
            Services.DEEZER.value : ['MD5_ORIGIN'],
        },
        'convertor': lambda x: str(x)
    },
    'media_version': {
        'key': {
            Services.DEEZER.value : ['MEDIA_VERSION'],
        },
        'convertor': lambda x: int(x)
    },
    'artists': {
        'key': {
            Services.DEEZER.value : ['ARTISTS'],
        },
        'convertor': lambda x: x
    },
    'date': {
        'key': {
            Services.DEEZER.value : ['PHYSICAL_RELEASE_DATE'],
            Services.TIDAL.value : ['streamStartDate'],
        },
        'convertor': lambda x: str(parse(x).date())
    },
    'artist_id': {
        'key': {
            Services.DEEZER.value : ['ART_ID'],
            Services.TIDAL.value : ['artist', 'id'],
        },
        'convertor': lambda x: str(x)
    },
    'artist_name': {
        'key': {
            Services.DEEZER.value : ['ART_NAME'],
            Services.TIDAL.value : ['artist', 'name'],
        },
        'convertor': lambda x: str(x)
    },
    'track_token': {
        'key': {
            Services.DEEZER.value : ['TRACK_TOKEN'],
        },
        'convertor': lambda x: str(x)
    },
    'allow_streaming':{        
        'key': {
            Services.TIDAL.value : ['allowStreaming'],
        },
        'convertor': lambda x: x
    }
}


@dataclass
class Track:
    service: Services = Services.NOT_RECOGNIZED
    stream_urls: list = field(default_factory=list)
    uri:Uri = None
    api_data: dict = None
    id: str = ''
    isrc: str = ''
    title: str = ''
    duration: int = 0
    md5: str = ''
    media_version: int = 0
    artist_id: int = 0
    artist_name: str = ''
    artists: list = None
    date: date = None
    track_token: str = ''
    allow_streaming: bool = False

    def dict(self) -> dict:
        return asdict(self)


class TrackSchema(Schema):
    service: str = fields.String()
    id: str = fields.String()
    api_data: dict = fields.Dict()
    isrc: str = fields.String()
    title: str = fields.String()
    duration: int = fields.Integer()
    md5: str = fields.String()
    media_version: int = fields.Integer()
    artist_id: int = fields.Integer()
    artist_name: str = fields.String()
    #artists:list        = fields.List(fields.Nested(ArtistSchema))
    
    date: date = fields.Date()
    track_token: str = fields.String()
    allow_streaming: bool = fields.Boolean()

    @pre_load
    def pre_load_func(self, data: dict, **kwargs):
        new_data = {'service': data['service']}
        
        for k, v in key_map.items():

            key = v['key'].get(new_data['service'])
            convertor = v['convertor']
            if key:
                result = dict_recursive_get(data, key)
                new_data[k] = convertor(result)

        new_data['api_data'] = data.copy()
        return new_data

    @post_load
    def post_load_func(self, data: dict, **kwargs):
        if 'service' in data:
            data['service'] = Services(data['service'])
        return Track(**data)

    class Meta:
        unknown = EXCLUDE
        ordered = True
