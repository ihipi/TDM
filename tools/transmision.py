import transmissionrpc as tr, requests as r, os


class Trans():
    def __init__(self):
        self.session = tr.Session()
        self.session._client
def addtorrent(url):
    t = tr.Client('localhost', port=9091, user='ihipi', password='1q2w4r')
    t.add_torrent(torrent= url)

    # print(t.get_torrents())

# addtorrent('magnet:?xt=urn:btih:y43mormfjucwr7sd6s5xqokhtpx66sxm&dn=La+Gran+Estafa+%28DVDRip%29+%28EliteTorrent.net%29&tr=http://tpb.tracker.thepiratebay.org:80/announce')