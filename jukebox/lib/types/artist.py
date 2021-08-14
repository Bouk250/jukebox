from dataclasses import dataclass
from .types import Services
from datetime import date, datetime
from marshmallow import Schema, fields, post_load, pre_load, EXCLUDE
from .types import Services, Types
from jukebox.utils.logs import JukeBoxLogger as logger

key_map = {
    'id' : ['ART_ID'],
    'name': ['ART_NAME'],
    'picture': ['ART_PICTURE'],
    'bummy': ['ARTIST_IS_DUMMY']
}

@dataclass
class Artist:
    id:int = 0
    name:str = ''
    picture:str = ''
    bummy:bool = False

class ArtistSchema(Schema):
    id:int              = fields.Integer(missing=0)
    name:str            = fields.String(missing='')
    picture:str         = fields.String(missing='')
    bummy:bool          = fields.Boolean(missing=False)


    @pre_load
    def pre_load_func(self, data:dict, **kwargs):
        data_key = list(data.keys())
        for k,v in key_map.items():
            intersection = list(set(data_key).intersection(v))
            if len(intersection)>1:
                raise ValueError(intersection)
            data[k] = data.pop(intersection[0])
        return data
    
    @post_load
    def post_load_func(self, data:dict, **kwargs):
        return Artist(**data)
    
    class Meta:
        unknown = EXCLUDE
        ordered = True
    
