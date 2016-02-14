import transmissionrpc as tr, requests as r, os


class Trans():
    def __init__(self):
        self.session = tr.Session()
        self.session._client
def addtorrent(url):
    t = tr.Client('localhost', port=9091, user='ihipi', password='1q2w4r')
    t.add_torrent(torrent= url)
    # print(t.get_torrents())

# addtorrent('http://www.divxtotal.com//torrents_tor/Fargo.2x01.HDTV.XviD.%5Bwww.DivxTotaL.com%5D.t50337.torrent')