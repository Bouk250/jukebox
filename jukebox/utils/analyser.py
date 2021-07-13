import re

from typing import Union

from jukebox.lib.types import Types, Services, Uri
import eventlet

urlopen = eventlet.import_patched('urllib.request').urlopen


def get_url_from_sti(service:Services, url_type:Types, id:Union[str,int]) -> str:
    if service == Services.NOT_RECOGNIZED:
        raise ValueError()
    if url_type == Types.NOT_RECOGNIZED:
        raise ValueError()
    if id == None or int(id) == 0:
        raise ValueError()
    
    if service == Services.DEEZER:
       return f"https://www.deezer.com/{type.value}/{id}"
        
def url_uri_analizer(url_uri:str) -> Uri:    
    if 'deezer.page.link' in url_uri: url_uri = urlopen(url_uri).url
    
    m = re.search('(^https:\/\/)?(?(1).*(?P<url_service>deezer|tidal).+(?P<url_type>track|album|artist|video|playlist|isrc)\/(?P<url_id>\w+)|^(?P<uri_service>deezer|tidal):(?P<uri_type>track|album|artist|video|playlist|isrc):(?P<uri_id>\w+))', url_uri, flags=re.IGNORECASE)
    if m is not None:
        return Uri(service=Services(m.group('url_service') or m.group('uri_service')), type=Types(m.group('url_type') or m.group('uri_type')), id=m.group('url_id') or m.group('uri_id'))
    return None