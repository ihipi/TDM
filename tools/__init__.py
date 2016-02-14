import json,  requests, os, getpass  , re # transmissionrpc , re
from bs4 import BeautifulSoup
# from tdm.dialegs import dialegdirector
import PyQt5.QtWidgets

def get_bs(url):
    res = requests.get(url)
    return BeautifulSoup(res.text, 'html.parser')


def getconfig():
    f = open(CONFIGFILE, mode='r')
    conf = json.load(f)
    return conf


def setconfig(**kargs):
    conf = getconfig()
    print(kargs)
    for k in kargs.keys():
        if k in conf.keys():

            conf[k] = kargs[k]
            print("La clau '{}' s'ha actualitzat a la configuració amb valor '{}'".format(k,kargs[k]))

        else:
            conf[k] =kargs[k]
            print("La clau '{}' s'ha afegit a la configuració amb valor '{}'".format(k,kargs[k]))

    f = open(CONFIGFILE, mode='w')
    json.dump(conf, f)
    f.close()
    return True


def filtra_torrents(**kargs):
    print(kargs)
    if kargs['tipus']==1:
        serie =  re.compile(r'([\w]+)(([st]\d{1,2})([ecx]\d{1,2}))',re.IGNORECASE)
        busca = serie.findall(kargs['nom'])
        print(busca)
        if busca:
            for m in busca:
                print('Match: ', m)
        else:
            print('No match')


def localmedia(tipus):
    """
    retorna els directoris que hi ha a la carpeta multimedia seleccionada
    :param tipus: "dir_series" per la carpeta de series/"dir_pelis per la de peliciles
    :return: llista de tuplas amb (nom, ruta) dels directoris
    """
    dir = getconfig()[tipus]
    return [(f,os.path.join(dir,f)) for f in os.listdir(dir) if not os.path.isfile(os.path.join(dir, f))]


# ###########################################
#  GLOBALS                                  #
# ###########################################

BASE_DIR = os.path.dirname(__file__)
CONFIGFILE = BASE_DIR + os.path.abspath('/conf.json')
GUI = os.path.abspath('./tdm/gui.ui')
ROOTDB = BASE_DIR + os.path.abspath('/db/')
DB = BASE_DIR + os.path.abspath('/db/tdmDB.sqlite')
print(DB)

DIR_SERIES = ''
DIR_PELIS = ''

# ###########################################
# TVISO                                     #
# ###########################################
MEDIATYPE= {'1': 'Serie',
            '2': 'Movie',
            '3': 'Documentary',
            '4': 'TV Show',
            '5': 'Episode'}
SERIE = 1
PELI = 2
DOCU = 3
TV = 4
EPISODI = 5

SERIESTATE = {'1': 'Following',
              '2': 'Pending',
              '3': 'Watched'}

PELISTATE = {'1': 'Watched',
             '2': 'Favorite',
             '3': 'Pending'}

IMG =  {'fonsL': '/backdrop/w600',
        'fonsS': '/backdrop/w300',
        'posterL': '/poster/w430',
        'posterM': '/poster/w200',
        'posterS': '/poster/w50'}
PAIS = ('ES', 'XX')
TVISOURL = 'https://api.tviso.com'
API_ID = '3452'
SECRET="t33eHYzzay9np3nugyzv"

AUTH_TOKEN= None
EXPIRES_TOKEN = None


TVISO_USER = ''
TVISO_PASS = ''

# ############################################
# Proves
# ############################################

# print([dir[0] for dir in localmedia('dir_pelis')])

# filtra_torrents(tipus = 1, nom = 'la cosa nstrasS20E34')
# setconfig(usuari=str(input('usuari de TViso ')))
# setconfig(password=str(getpass.getpass()))