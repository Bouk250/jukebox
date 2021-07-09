from pathlib import Path
import sys
import os

homedata = Path.home()
config_folder = ""


if os.getenv("JUKEBOX_DATA_DIR"):
    config_folder = Path(os.getenv("JUKEBOX_DATA_DIR"))
elif os.getenv("XDG_CONFIG_HOME"):
    config_folder = Path(os.getenv("XDG_CONFIG_HOME")) / 'jukebox'
elif os.getenv("APPDATA"):
    config_folder = Path(os.getenv("APPDATA")) / "jukebox"
elif sys.platform.startswith('darwin'):
    config_folder = homedata / 'Library' / 'Application Support' / 'jukebox'
else:
    config_folder = homedata / '.config' / 'jukebox'

def getConfigFolder():
    return config_folder