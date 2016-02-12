import json,  requests, os  # transmissionrpc
from bs4 import BeautifulSoup


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
        else:
            conf[k] ={kargs[k]}
            print("La clau '{}' s'ha afegit a la configuració amb valor '{}'".format(k,kargs[k]))

    f = open(CONFIGFILE, mode='w')
    json.dump(conf, f)
    f.close()
    print(conf)
    return True


# ###########################################
#  GLOBALS                                  #
# ###########################################

BASE_DIR = os.path.dirname(__file__)
CONFIGFILE = BASE_DIR + os.path.abspath('/conf.json')
GUI = os.path.abspath('./tdm/gui.ui')
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

TVISO_USER = ''
TVISO_PASS = ''

# ############################################
# ############################################