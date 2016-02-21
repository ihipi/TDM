import transmissionrpc as tr, requests as r, os


class Trans():
    def __init__(self):
        self.session = tr.Session()
        self.session._client
def addtorrent(url):
    t = tr.Client('localhost', port=9091, user='ihipi', password='1q2w4r')
    t.add_torrent(torrent= url)

    # print(t.get_torrents())

addtorrent('http://torcache.net/torrent/61CED7D1D51E6EF05BB8BDD398ED32CF03112E5B.torrent')