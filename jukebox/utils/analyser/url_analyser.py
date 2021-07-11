from typing import Union
import string
from jukebox.lib.types import Types, Services
import re


def get_url_from_sti(service:Services, url_type:Types, id:Union[str,int]) -> str:
    if service == Services.NOT_RECOGNIZED:
        raise ValueError()
    if url_type == Types.NOT_RECOGNIZED:
        raise ValueError()
    if id == None or int(id) == 0:
        raise ValueError()
    
    if service == Services.DEEZER:
       return f"https://www.deezer.com/{type.value}/{id}"
        
def url_analizer(url:str) -> tuple:
    service = Services.NOT_RECOGNIZED
    url_type = Types.NOT_RECOGNIZED
    id = 0
    
    url = url.lower()
    m = re.search('(?P<service>tidal|deezer).+(?P<type>track|album|artist|video)\/(?P<id>\d+)', url)
    if m is not None:
        service = Services(m.group('service'))
        url_type = Types(m.group('type'))
        id = int(m.group('id'))

    return service, url_type, id