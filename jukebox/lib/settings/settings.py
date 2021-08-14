import yaml
import uuid
from dataclasses import dataclass, asdict
from marshmallow import Schema, fields, pre_load, EXCLUDE, post_load

@dataclass
class DeezerSetings:
    user_id:int = 0
    arl:str = ''

class DeezerSetingsSchema(Schema):
    user_id:int = fields.Integer()
    arl:str = fields.String()

    @post_load
    def post_load_func(self, data: dict, **kwargs):
        return DeezerSetings(**data)

    class Meta:
        unknown = EXCLUDE


@dataclass
class TidalKey:
    device_code:str = ''
    user_code:str = ''
    verification_url:str = ''
    auth_check_timeout:int = 0
    auth_check_interval:int = 0
    access_token:str = ''
    refresh_token:str = ''
    expires_in:int = 0
    country_code:str = ''

class TidalKeySchema(Schema):
    device_code:str = fields.String()
    user_code:str = fields.String()
    verification_url:str = fields.String()
    auth_check_timeout:int = fields.Integer()
    auth_check_interval:int = fields.Integer()
    access_token:str = fields.String()
    refresh_token:str = fields.String()
    expires_in:int = fields.Integer()
    country_code:str = fields.String()

    @post_load
    def post_load_func(self, data: dict, **kwargs):
        return TidalKey(**data)
    class Meta:
        unknown = EXCLUDE

@dataclass
class TidalSetings:
    user_id:int = 0
    key:TidalKey = TidalKey()

class TidalSetingsSchema(Schema):
    user_id:int = fields.Integer()
    key:TidalKey = fields.Nested(TidalKeySchema())

    @post_load
    def post_load_func(self, data: dict, **kwargs):
        return TidalSetings(**data)
    class Meta:
        unknown = EXCLUDE

@dataclass
class ClientManagerSettings:
    deezer_settings:DeezerSetings = DeezerSetings()
    tidal_settings:TidalSetings = TidalSetings()

class ClientManagerSettingsSchema(Schema):
    deezer_settings:DeezerSetings = fields.Nested(DeezerSetingsSchema())
    tidal_settings:TidalSetings = fields.Nested(TidalSetingsSchema())

    @post_load
    def post_load_func(self, data: dict, **kwargs):
        return ClientManagerSettings(**data)
    class Meta:
        unknown = EXCLUDE

@dataclass
class JukeBoxUserSettings:
    uuid:str = uuid.uuid4()
    accept_language:str = ''
    client_manager_settings:ClientManagerSettings = ClientManagerSettings()

    @property
    def dict(self) -> dict:
        data = asdict(self)
        data['uuid'] = str(data['uuid'])
        return data

    def save(self, file_path:str):
        with open(file_path, mode='w') as f:
            yaml.dump(self.dict,f)

    @classmethod
    def load(cls, file_path:str):
        with open(file_path, mode='r') as f: 
            settings = yaml.load(f, Loader=yaml.SafeLoader)
            schema = JukeBoxUserSettingsSchema()
            user_settings:JukeBoxUserSettings = schema.load(settings)
            return user_settings

class JukeBoxUserSettingsSchema(Schema):
    uuid:str = fields.UUID()
    accept_language:str = fields.String()
    client_manager_settings:ClientManagerSettings = fields.Nested(ClientManagerSettingsSchema())

    @post_load
    def post_load_func(self, data: dict, **kwargs):
        return JukeBoxUserSettings(**data)
    class Meta:
        unknown = EXCLUDE

@dataclass
class JukeBoxSettings:
    pass