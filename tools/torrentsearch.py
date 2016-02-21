import requests
from tools import get_bs, Torrent




def busca(motor, paraula, **Kargs):
    print('torrentsearch:',motor,paraula, Kargs)
    motorB = BUSCADORS[motor]

    if motor == 'divixtotal':
        return motorB.busca(paraula,Kargs['divixserie'])
    elif motor == 'elitetorrent':
        return motorB.busca(paraula)
    elif motor == 'kickass' or motor == None:
        if isinstance(Kargs['imdb'],int):
            paraula =str(Kargs['imdb'])
        print(paraula,Kargs)
        res = motorB.busca(paraula,Kargs['imdb'],True)
        if res == []:
            res =motorB.busca(paraula,Kargs['imdb'])
        return res
class Eliterorrent():
    def __init__(self):

        self.url = "http://www.elitetorrent.net"

        self.CATEGORIA = {'series':''+self.url+'/categoria/4/series',
                     'pelicules':''+self.url+'/categoria/2/peliculas',
                     'seriesVOSE':''+self.url+'/categoria/16/series-vose',
                     'peliculesVOSE':''+self.url+'/categoria/14/peliculas-vose',
                     'peliculesHDRIP':''+self.url+ '/categoria/13/peliculas-hdrip',}

    def busca(self, busqueda = ''):
        torrents=[]
        url =''+self.url+'/busqueda/'+ busqueda
        resp = requests.get(''+self.url+'/busqueda/'+ busqueda)

        text = resp.text

        soup = get_bs(url)
        lis = soup.find_all('li')
        for li in lis:
            torrents.append(Torrent(name=li.div.a.get('title'), url=self.url+li.a.get('href')))
        print(torrents)
        for t in torrents:
            tor, mag = self.getTorrent(t.url)
            t.url =tor
            t.magnet = mag
        return torrents

        print('ended')

    def getTorrent(self, url):

        soup = get_bs(url)
        links = soup.find('div', attrs={'class':'enlace_descarga'})
        descarga =[]
        # print(links)
        try:
            for a in links.find_all('a'):

                if a.get('href')[:6] != 'magnet':
                    descarga.append(self.url+a.get('href'))
                else:
                    descarga.append(a.get('href'))

        except Exception as e:
            print("error: {}\n Al aconseguir els links de elitetorrent".format(e))
        return descarga

class DivixTotal():
    """
    DIVIXTOTAL
    """

    def __init__(self):
        '''
        Constructor
        '''
        self.url = "http://www.divxtotal.com/"

        self.cat = {'busca' : '' + self.url + 'buscar.php?busqueda=',
                          'series':''+self.url+'series/',
                          'pelicules':''+self.url+'peliculas/'}

    def busca(self,busqueda, serie = False):
        '''
        Busca llistat de torrents
        @param busqueda: torrent que busques
        @param serie: si estas buscant una serie

        '''


        soup = get_bs(self.cat['busca'] + busqueda)
#         print(soup.prettify())
        #recull els resultats de la busqueda i els itera
        torrents = {}
        torList = []
        print('divixtotal:', serie)
        for p in soup.find_all('p', attrs={'class':'seccontnom'}):

            if serie: # si esta activat serie
                if 'Series' in p.next_sibling.next_sibling.a.get(('title')):
                    #comprova que estigui catalogat com a serie i retorna la pagina de la serie
                    seriebs = get_bs(self.url + p.a.get('href'))


                    for capitol in seriebs.find_all('td', attrs={"class":'capitulonombre'}):
                        t = Torrent(name = str(capitol.a.text),url = self.url+capitol.a.get('href'))
                        torList.append(t)
                        torrents[str(capitol.a.text)] = self.url+capitol.a.get('href')
                        print(capitol.a.text, '\t'+ self.url+capitol.a.get('href'))
                return torrents
            else:
                if '/series/' not in p.a.get('href'):
                    bsoup = get_bs(self.url+p.a.get( 'href'))
                    torrent = bsoup.find('div', {'class':'ficha_link_det'})
                    info = bsoup.find('div', {'class' : 'fichatxt'}).text
                    # print(info)
                    torList.append(Torrent(name = p.a.text, url = self.url+torrent.h3.a.get('href')[1:], info = info))
                    # torrents[str(p.a.text)] = (self.url+torrent.h3.a.get('href')[1:], info)

            #print(p.a.get('title'),'\t\t',''+self.url+p.a.get('href'))
        print(torList)
        return torList

    def gettorrent(self):
        pass

    def llistaSeries(self, inicial=None):
        '''
        Busca el llistat sencer de series de divixtotal

        '''
        soup = get_bs(self.cat['series'])
        lis = soup.find('li', {'class':'li_listadoseries'})
        print(lis)
        for li in lis:
            lletra = None
            if li.font:
                lletra= li.font.text
                print(lletra)
            for a in li.find_all('a'):
                if inicial:
                    if lletra in inicial:
                        print(a.get('title'),'\t\t\t',''+self.url+a.get( 'href'))

                else:
                    print(a.get('title'),'\t\t\t',''+self.url+a.get( 'href'))

class KickAss():
    def __init__(self, domain='kat.cr'):
        self.domain = domain

        self.url= {  'BASE' : "http://"+domain,
                    'SEARCH' : "http://"+domain+"/usearch/",
                    'LATEST' : "http://"+domain+"/new/",
                    'USER' : "http://"+domain+"/user/"}
        self.categories = {'MOVIES' : "movies",
                    'TV' : "tv",
                    'MUSIC' : "music",
                    'BOOKS' : "books",
                    'GAMES' : "games",
                    'APPLICATIONS' : "applications",
                    'XXX' : "xxx"}
        self.order = {'SIZE' : "size",
                'FILES_COUNT' : "files_count",
                'AGE' : "time_add",
                'SEED' : "seeders",
                'LEECH' : "leechers",
                'ASC' : "asc",
                'DESC' : "desc"}

    def makeurl(self,query,imdb,lang):
        url = self.url['SEARCH']
        if imdb:
            url += 'imdb:'+str(query)
            print(url)
        elif lang:
            url += ' lang_id:14'
        elif not lang and not imdb:
            url += str(query)
        print(url)
        return  url
    def busca(self, query, imdb=False, lang = False):
        intents =0
        soup = get_bs(self.makeurl(query,imdb,lang))
        taula = soup.find_all('tr',{'class': 'odd', 'class' : 'even'})
        torrents =[]
        for tr in taula:
            # print('tr:{}:'.format(type(tr)))
            if tr is not '':
                tds = tr.find_all('td')
                name = tr.find('a',{'class' : 'cellMainLink'}).text
                magnet = tr.find('a', {'title' : 'Torrent magnet link'}).get('href')
                tor = 'http:'+tr.find('a', {'title' : 'Download torrent file'}).get('href')
                info = self.url['BASE']+tr.find('a',{'class' : 'cellMainLink'}).get('href')

                torrents.append(Torrent(name=name, url=tor.split('?')[0], magnet=magnet, info=info))
                # print(name,info)
                # print(magnet)
                # print(tor)
        print('torrents list\n',torrents)
        return torrents
    def getInfo(self,url):
        info = url
        try:
            infosoup = get_bs(url)
            infodiv = infosoup.find('div',{'class': 'dataList'})
            print( infodiv)
            info = infodiv.text
        except:
            print('el torrent no te info')
        return info

BUSCADORS = {'divixtotal':DivixTotal(),
                  'elitetorrent':Eliterorrent(),
                  'kickass':KickAss()}

# k = KickAss()
# k.getsearch('ladrona')
# for t in busca('kickass', 'ida', imdb=1714206):
#     print(t.getList)
# e =Eliterorrent()
# e.busca('gran estafa')
#dvx = DivixTotal()
#dvx.llistaSeries('B')
# dvx.busca('fargo')
# print('ended')
