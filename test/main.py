from jukebox.lib.item import JukeBoxItem
from jukebox.lib.user import JukeBoxUser
from jukebox.lib.types import TrackFormats, Services

user = JukeBoxUser()

user.dz_cl.login(arl='d32c00a1b79a5e8e4267b333cd9dcf72aa2c294ab425c57ebf630af79d44dc8f798b922bfdf91a73eb4996513984941854a5330fdfa4c4c6dc1ec5b844380109ef0a682d9e613d0b4604c7b1233343f4bbd2fa7105df4132635f71c05fedc4ce')

iteam = JukeBoxItem(user=user, bitrate=TrackFormats.LOSSY_320_MP3, uri="deezer:album:236554602")

print(iteam.url, iteam.type, iteam.service,iteam.id, iteam.uuid)

print(TrackFormats.getServiceFormats(Services.DEEZER))
