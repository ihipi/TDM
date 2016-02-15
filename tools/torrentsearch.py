import requests
from tools import get_bs




def busca(motor, paraula, divixserie = False):
    print('torrentsearch:',motor,paraula, divixserie)
    motorB = BUSCADORS[motor]

    if motor == 'divixtotal':
        return motorB.busca(paraula,divixserie)
    elif motor == 'elitetorrent':
        return motorB.busca(paraula)
    elif motor == 'kickass':
        pass


class Eliterorrent():
    def __init__(self):

        self.url = "http://www.elitetorrent.net"

        self.CATEGORIA = {'series':''+self.url+'/categoria/4/series',
                     'pelicules':''+self.url+'/categoria/2/peliculas',
                     'seriesVOSE':''+self.url+'/categoria/16/series-vose',
                     'peliculesVOSE':''+self.url+'/categoria/14/peliculas-vose',
                     'peliculesHDRIP':''+self.url+ '/categoria/13/peliculas-hdrip',}

    def busca(self, busqueda = ''):
        torrents={}
        url =''+self.url+'/busqueda/'+ busqueda
        resp = requests.get(''+self.url+'/busqueda/'+ busqueda)

        text = resp.text

        soup = get_bs(url)
        lis = soup.find_all('li')
        for li in lis:
            torrents[li.div.a.get('title')]= self.url+li.a.get('href')
        print(torrents)
        for n in torrents.keys():
            torrents[n] = self.getTorrent(torrents[n])
        return torrents

        print('ended')

    def getTorrent(self, url):

        soup = get_bs(url)
        links = soup.find('div', attrs={'class':'enlace_descarga'})
        descarga =[]
        print(links)
        try:
            for a in links.find_all('a'):

                if a.get('href')[:6] != 'magnet':
                    descarga.append(self.url+a.get('href'))
                else:
                    descarga.append(a.get('href'))
        except Exception == 'NoneType':
            print('sense resposta')
        except Exception as e:
            print("error: {}\n Al aconseguir els links de elitetorrent".format(e))
        return descarga

class DivixTotal(object):
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
        print('divixtotal:', serie)
        for p in soup.find_all('p', attrs={'class':'seccontnom'}):

            if serie: # si esta activat serie
                if 'Series' in p.next_sibling.next_sibling.a.get(('title')):
                    #comprova que estigui catalogat com a serie i retorna la pagina de la serie
                    seriebs = get_bs(self.url + p.a.get('href'))


                    for capitol in seriebs.find_all('td', attrs={"class":'capitulonombre'}):
                        torrents[str(capitol.a.text)] = self.url+capitol.a.get('href')
                        print(capitol.a.text, '\t'+ self.url+capitol.a.get('href'))
                return torrents
            else:
                torrents[str(p.a.text)] = ''+self.url+p.a.get('href')
            #print(p.a.get('title'),'\t\t',''+self.url+p.a.get('href'))
        print(torrents)
        return torrents

    # TODO arreglar la busqueda per series de divixtotal
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

BUSCADORS = {'divixtotal':DivixTotal(),
                  'elitetorrent':Eliterorrent(),
                  'kickass':''}

# e =Eliterorrent()
# e.busca('gran estafa')
#dvx = DivixTotal()
#dvx.llistaSeries('B')
# dvx.busca('fargo')
# print('ended')
