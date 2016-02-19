'''
Created on 14 gen. 2016

@author: albert
'''
import time

#import webview
import requests, getpass, pprint
#Per llegir parameetres de una url
from urllib.parse import urlparse, parse_qs
from tools import API_ID, SECRET, TVISOURL
import tools
from tdm import dialegs

class TViso:
    '''
    classdocs
    '''

    

    def __init__(self, id_api=None, secret=None):
        '''
        Constructor
        '''
        #aconseguim el token d'autoritzacio 
        self.id_api = id_api or API_ID
        self.secret = secret or SECRET
        self.actualTime = time.time()
        self.auth_token = tools.getconfig()['auth_token']
        self.auth_expires = tools.getconfig()['auth_expires_date']
        self.user_token = tools.getconfig()['user_token']
        print(int(self.actualTime) , self.auth_expires)

        if int(time.time()) > int(tools.getconfig()['auth_expires_date']):

            try:
                print('actualitzant tokens...')
                self.getAuthToken()
                self.getUserToken()
            except Exception as e:
                print(e)
        if 'usuari' not in tools.getconfig().keys():
            pass

        #aconseguim el user token
#        webbrowser.open('https://api.tviso.com/user/user_token?auth_token='+self.auth_token+'&redirect_url=me')
#        webbrowser.open('https://api.tviso.com/user/user_login?auth_token='+self.auth_token+'&username=ihipi&password=1234567')

    def getAuthToken(self):
        """
        aconsegueix el token i l'expiracio. Ho prova des del fitxer sino o agafa de
        :return:
        """
        conf = tools.getconfig()
        auth, expires = conf['auth_token'], conf['auth_expires_date']

        if auth == None or expires == None or self.actualTime > expires:
            getauthurl= 'https://api.tviso.com/auth_token?id_api=' + self.id_api + '&secret=' + self.secret
            getAuthToken = requests.get(getauthurl).json()
            print('auth_token: ',getAuthToken['auth_token'],'\expira: ',getAuthToken['auth_expires_date'])
            tools.setconfig(auth_expires_date = getAuthToken['auth_expires_date'], auth_token = getAuthToken['auth_token'])
            return True, getAuthToken['auth_expires_date'], getAuthToken['auth_token']
        else:
            auth, expires = conf['auth_token'],conf['auth_expires_date']
            print('getauthtoken....',auth, expires)
            return True, expires, auth


    def getUserToken(self):
        usuari = contrasenya = None

        if tools.getconfig()['usuari'] != None and tools.getconfig()['password'] != None:
            usuari = tools.getconfig()['usuari']
            contrasenya =tools.getconfig()['password']
        else:
            tools.setconfig(usuari=str(input('usuari de TViso ')))
            tools.setconfig(password=str(getpass.getpass()))
            usuari = tools.getconfig()['usuari']
            contrasenya =tools.getconfig()['password']
        # if time.time()> float(self.auth_expires):
        urluser = 'https://api.tviso.com/user/user_login?auth_token={}&username={}&password={}'.format(self.auth_token, usuari, contrasenya)
        response = requests.get(urluser)
        if response.history:
            print("Esperant el token d'usuari...")
            
            print(response.status_code, response.url)
            #creem un objecte url parse per trobar el usertoken
            resp = urlparse(response.url)
            query = parse_qs(resp.query)
            if query.get('user_token'):

                tools.setconfig(user_token = query.get('user_token')[0])
                print("token d'usuari: {}".format(query.get('user_token')[0]))
                return True, query.get('user_token')[0]
            else:
                respj = response.json()
                print("Hi ha hagut un problema: {}".format(respj))
                return False, None

    def getuid(self):
        gets={'auth_token':self.auth_token,'user_token':self.user_token}
        req = requests.get('https://api.tviso.com/user/me?', params = gets).json()
        # tools.setconfig(uid = req['results']['uid'])
        print
        return req['result']['uid']

    def searchTitle(self, title):
        """
        Busca videos per titol
        :param self:
        :param title: text a buscar
        :return: una llista amb objectes media
        """
        gets = {'auth_token': self.auth_token,
                'q':title,
                'country':'ES'}
        llista = []
        j = requests.get('https://api.tviso.com/media/search?',params =gets).json()
        for k in j.keys():
            if isinstance(j[k], dict):
                print(j)
                llista.append(tools.Media(**{'idm' : j[k]['idm'],'imdb' : j[k]['imdb'],'name' : j[k]['name'],
                                             'plot' : j[k]['plot'],
                                             'image' : j[k]['images']['poster'],
                                             'year' : j[k]['year'],
                                             'mediaType': j[k]['mediaType']}))
        print(llista)
        return llista

    # TODO mirar de que funcioni i crear la base de dades general
    def getAllMediaList(self):
        """
        :param self:
        :return:
        """
        gets = {'auth_token':self.auth_token}
        return requests.get(TVISOURL + '/media/list/all?',params = gets).json()

    def getFollowing(self):
        gets={'auth_token':self.auth_token,'user_token':self.user_token}
        print((TVISOURL+'/user/following?',gets))
        return requests.get(TVISOURL+'/user/following?', params = gets).json()

    def getUserCollection(self):
        gets={'auth_token':self.auth_token,'user_token':self.user_token}
        return requests.get(TVISOURL+'/user/media/collection?', params = gets).json()

    def getUserMedia(self,media = False):
        """
        Recull la biblioteca actual de tviso. Serveix per poblar la taula mycollection de la base de dades
        :param media: si nomes vols un tipus de video
        :return: json amb el llistat
        """
        gets={'auth_token':self.auth_token,'user_token':self.user_token}

        return requests.get(TVISOURL + '/user/media?', params = gets).json()
    # TODO buscar sense "mediaType"
    def getFullInfo(self, idm,media_type = None):
        """
        Busca la informacio de un video
        :param idm:  'necessari' id de tviso
        :param mediaType: tipus de media "teoricament" no necessari
        :return: json amb la info
        """
        gets = {'auth_token': self.auth_token,'idm':idm }
        if media_type:
            print('media: ',media_type)
            gets['mediaType']=media_type
        return requests.get(TVISOURL+'/media/full_info?', params = gets).json()

    def getUserPending(self):
        """

        :return:
        """
        gets={'auth_token':self.auth_token,'user_token':self.user_token}
        return requests.get(TVISOURL+'/user/media/pending/:mediaType?', params = gets).json()

    def getUserSumary(self):
        """
        Busca un resum de tot el que tens vist i seguint al tviso
        :return: json amb un resum( inclos capitols vistos i les dates)
        """

        gets={'auth_token':self.auth_token,'user_token':self.user_token}
        req = requests.get(TVISOURL+'/user/media/collection_summary?', params = gets).json()
        print(req)
        return req

    def llistatviso(self):
        gets = {'auth_token':self.auth_token,'user_token':self.user_token,}
        llistes =  requests.post('https://api.tviso.com/user/media/lists?auth_token={auth_token}&user_token={user_token}', gets).json()['own']
        print(llistes)
        for ll in llistes:
            if ll['title'] == 'TDManta':
                return ll
        return {}

    def addMedia(self, idm, mediaType):
        llista = self.llistatviso()
        print(llista)
        try:

            tdmlistid = llista['id']
            # posts = (self.auth_token, self.user_token, tdmlistid, idm, mediaType)
            # res = requests.post('https://api.tviso.com/media/list/add_media?auth_token={}&user_token={}&id={}&idm={}&mediaType={}'.format(self.auth_token, self.user_token, tdmlistid, idm, mediaType)).json()
            posts = {'auth_token' :self.auth_token,'user_token': self.user_token,'id' : tdmlistid,'idm': idm,'mediaType': mediaType}
            res = requests.post('https://api.tviso.com/media/list/add_media?',posts ).json()
            print('resultat: ' , res)
            if res['error'] == 0:
                return True
            else:
                print('adding...',res['errorMessage'])
        except Exception as e:
            print('Escept' ,e)




# tv = TViso()
# print(tv.addMedia(69,1))
# al = tv.getUserSumary()
# print(al)
# for k in al:
#     print("{}:".format(k.info()))
#
# print(al)

# al=tv.getAllMediaList()
# tv.getUserToken()
# print(tv.getUserSumary())
#pprint(Tv.getUserCollection().json(),depth = 5)
#pprint(Tv.getUserMedia().json(),depth = 5)
#
# full = tv.getFullInfo(2078,1)



# full = tv.getUserSumary()
# for k in full.keys():
#     print("{}:\n{}".format(k,full[k]))
#     if isinstance(full[k],dict):
#         for kk in full[k].keys():
#             print("\t{}:\n\t{}".format(kk,full[k][kk]))

# pprint(Tv.getUserSumary(),depth =4)

