from pprint import pprint
import unittest
import  sys
import time
from jukebox.lib.client import  DeezerClient, TidalClient
from jukebox.utils.result import ResultCode


class TestServicesLogin(unittest.TestCase):

    def setUp(self):
        self.dz = DeezerClient()

    def test_deezer_login(self):
        """
        Test that it can login to deezer
        """
        
        arl = "d32c00a1b79a5e8e4267b333cd9dcf72aa2c294ab425c57ebf630af79d44dc8f798b922bfdf91a73eb4996513984941854a5330fdfa4c4c6dc1ec5b844380109ef0a682d9e613d0b4604c7b1233343f4bbd2fa7105df4132635f71c05fedc4ce"
        result = self.dz.login(arl=arl)
        self.assertEqual(result.result_code,ResultCode.SUCCESS)
        print(result.data)

    def test_get_track(self):
        result = self.dz.api.get_track_with_fallback('118986142')
        pprint(result.data)
        self.assertEqual(result.result_code,ResultCode.SUCCESS)


    def test_tidal_login(self):
        td = TidalClient()
        result = td.login()
        self.assertEqual(result.result_code,ResultCode.SUCCESS)


if __name__ == '__main__':
    unittest.main()
