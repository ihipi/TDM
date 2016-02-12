'''
Created on 16 gen. 2016

@author: albert
'''
import json
import multiprocessing
import os
import queue
import sqlite3
import threading
import time
from datetime import datetime
from math import floor


from tools.tviso import TViso
import tools
from tools import IMG


class TDMDB():
    '''
    classdocs
    '''


    def __init__(self, lloc=''):
        '''
        Constructor
        '''
        self.root = lloc
        self.dbname = 'sicruc.db'
        self.db = sqlite3.connect(lloc +self.dbname)
        self.c = self.db.cursor()

        self.c.execute('CREATE TABLE IF NOT EXISTS series (imdb INTEGER PRIMARY KEY not NULL,tvmazeID INTEGER, name TEXT, image TEXT, rating TEXT, sinopsis TEXT)')
        self.c.execute('CREATE TABLE IF NOT EXISTS mycollection (imdb INTEGER PRIMARY KEY not NULL,tviso_id INTEGER, media INTEGER, name TEXT, estat TEXT, imatge TEXT )')
        self.c.execute('create table if not exists capitols (idm INTEGER PRIMARY KEY not NULL, tviso_id INTEGER, season INTEGER, capitol INTEGER, titol TEXT, sinopsis TEXT,estat INTEGER , date TEXT)')
        self.lastId = self.getLastID()
        self.format = '%Y-%M-%d'
        ###
        ###Implementing multiples threads
        ###
        self.cpu_cores = multiprocessing.cpu_count()
        self.get_image_queue = queue.Queue()
        for i in range(self.cpu_cores):
            worker = threading.Thread(target=self.wgetImage, args=(i, self.get_image_queue,))
            worker.setDaemon(True)
            worker.start()



        ###
        ### COMPROVAR ULTIMA ACTUALITZACIó
        ###
        self.lastUpdate = self.gettime()
        deltaTime = datetime.strptime(time.strftime(self.format),self.format)-datetime.strptime(self.lastUpdate , self.format)
        print(self.lastUpdate)
        if deltaTime.days>=tools.getconfig()['actualitzacio_freq']:
            print(deltaTime.days)
            self.updateUserMedia()
        else:
            print('-'*50,'\nBase de dades actualitzada a dia: {}\n'.format(self.lastUpdate),'-'*50)

    def settime(self):
#         f = open(self.root+'conf.json', mode='w')
        last = {'lastUpdate':time.strftime(self.format)}
#         j = json.dump(last, f )
#         f.close()
        tools.setconfig(lastUpdate = time.strftime(self.format))
        return tools.getconfig()

    def dbstart(self):
        self.db = sqlite3.connect(self.dbname)
        self.c = self.db.cursor()
        return self.db.cursor()

    def dbstop(self):
        self.db.close()

    def __dbquery(self, query,*args):
        q = self.dbstart()
        try:
            print((query, args))
            response = [row for row in self.c.execute(query, args[0])]
        except Exception as e:
            return False, print(e)

        self.dbstop()
        return response

    def getLastID(self):

        self.c.execute('select * from series')
        lastId = 0
        for row in self.c:
            if row[0]>lastId:
                lastId = row[0]
        print('Last TVMaze id: ',lastId)
        return lastId

    def gettime(self):

        print(tools.getconfig()['lastUpdate'])
        return tools.getconfig()['lastUpdate']

    def wgetImage(self, *args):
        """
        aconsegueix les imatges del "media seleccionat
        @params media_json: json de TVISO amb la informacio del media
        """
        print(args)

        while True:
            # Si el primer argument és un Queue definim @param fil i cua
            if isinstance(args[1],queue.Queue):
                fil, cua = args
                # aconseguim la serie i el tipus del seguent element de la cua
                serie, tipus = cua.get()
            else: # si el primer argument no es Queue assignem serie i tipus directament
                fil, cua= None
                serie, tipus = args

            tviso =  TViso()
            print('##'*60,'\nFil numero : {},\t codi: {},\t tipus:{}\n'.format(fil,serie, tipus),'##'*60)
            res = tviso.getFullInfo(serie, tipus).json()
            try:
                if isinstance(res['images'], dict):
                    posterFile = self.root+'imatges/'+serie+"_"+ res['imdb'] +"_poster.jpg"
                    backdropFile = self.root+'imatges/'+serie+"_"+ res['imdb'] +"_back.jpg"


                    if not os.path.exists(posterFile) and not os.path.exists(backdropFile):
                        backurl = 'https://img.tviso.com'+'/{}{}{}'.format(res['images']['country'] or 'ES', IMG['fonsL'],res['images']['poster'])
                        posterurl = 'https://img.tviso.com'+'/{}{}{}'.format(res['images']['country'] or 'ES', IMG['posterL'],res['images']['backdrop'])
                        print(posterurl, posterFile )
                        print(backurl, backdropFile )
                        #descarreguem la imatge amb un WGET de consola normal i corrent
                        print('descarregant imatges pe la serie {}'.format(serie))
                        os.system("wget -O {0} {1}".format(posterFile, posterurl))
                        os.system("wget -O {0} {1}".format(backdropFile, backurl))
                        cua.task_done()
                    elif not os.path.exists(posterFile):
                        posterurl = 'https://img.tviso.com'+'/{}{}{}'.format(res['images']['country'], IMG['posterL'],res['images']['poster'])
                        print(posterurl, posterFile )
                        print(backurl, backdropFile )
                        #descarreguem la imatge amb un WGET de consola normal i corrent
                        print('descarregant imatges pe la serie {}'.format(serie))
                        os.system("wget -O {0} {1}".format(posterFile, posterurl))
                        cua.task_done()
                    if not os.path.exists(backdropFile):
                        backurl = 'https://img.tviso.com'+'/{}{}{}'.format(res['images']['country'] or 'ES', IMG['fonsL'],res['images']['backdrop'])
                        print(posterurl, posterFile )
                        print(backurl, backdropFile )
                        #descarreguem la imatge amb un WGET de consola normal i corrent
                        print('descarregant imatges pe la serie {}'.format(serie))
                        os.system("wget -O {0} {1}".format(backdropFile, backurl))
                        cua.task_done()
                    else:
                        print('La imatge ja esta descarregada')
                        cua.task_done()


                else:
                    cua.task_done()
                    print('sense imatge')
                    return False
            except Exception as e:
                print('ERROR: ', e)
                cua.task_done()

    def addSerie(self, idm, media_type):

        tviso =  TViso()
        res = tviso.getFullInfo( idm, media_type).json()
        try:

            imageFile = self.root+'imatges/'+res['imdb']+"_poster.jpg"
            values = (int(res['imdb'][2:]),int(res['idm']), int(res['mediaType']), str(res['name']), str(res['status']), imageFile)
            self.c.execute("""insert into mycollection values (?,?,?,?,?,?)""",values)


        except sqlite3.IntegrityError:
            print("couldn't add serie  twice")

        except Exception as e:

            print('error:\t'+str(e)+'...  \no no existeix...\n')


        #afegim els episodis a la taula capitols


        if res['mediaType'] == 1:
            for season in res['seasons'].keys():
                for e in res['seasons'][str(season)]:
                    estat =1
                    values = (int(e['idm']),int(e['media']['idm']), int(e['season']), int(e['num']),str(e['name']),str(e['plot']),estat, '')

                    print('-'*60)
                    ordre = """insert into capitols values (?,?,?,?,?,?,?,?)"""
                    try:
                        self.c.execute(ordre,values)
                    except sqlite3.IntegrityError:
                        print("couldn't add episode twice")
                    except Exception as e :
                        print("epic fail: {}  ".format(e),ordre)
                    self.db.commit()

    def updateUserMedia(self):
        tviso = TViso()
        res = tviso.getUserSumary()
        image_dict = dict()
        #busquem totes les imatges que tenim guardades
        for file in os.listdir(os.path.dirname(__file__)+'/imatges/'):
            if file[-5:] != "_dict":
                idm, imdb, tipe = file.split('_')
                # si no existeix la entrada la creem
                if not idm in image_dict.keys():
                    image_dict[idm]= dict()
                    image_dict[idm]['imdb']=imdb
                    image_dict[idm][tipe[:-4]]=file
                # si ja existeix i afegim l'altre tipus de fotografia
                else:
                    image_dict[idm]['imdb']=imdb
                    image_dict[idm][tipe[:-4]]=file


        img_file =  open(os.path.dirname(__file__)+'/imatges/imatges_dict', mode='w+')
        json.dump(image_dict,img_file)
        img_file.close()
        image_file = open(os.path.dirname(__file__)+'/imatges/imatges_dict', mode='r+')
        images = json.load(image_file)
        for media in res['collection']['medias'].keys():
            tipus, idm = media.split('-')
            idms = images.keys()
            if str(idm) not in idms:
                print(idm, idms)

                print('Queuing:', idm, tipus)
                self.get_image_queue.put((idm,tipus))
        self.get_image_queue.join()
#            self.wgetImage(media.split('-')[1],media.split('-')[0])
        for episodi in res['collection']['episodes'].keys():
            data = datetime.fromtimestamp(res['collection']['episodes'][episodi]).strftime('%Y-%m-%d')
            print(data, episodi)
            self.c.execute("""UPDATE capitols SET date=? WHERE idm=?""", (str(data), int(episodi)))
            self.db.commit()





        self.settime()

    def deleteSerie(self,tvmazeID):
        self.c.execute('SELECT image FROM myseries WHERE tvmazeID=?',(tvmazeID,))
        os.remove(self.c.fetchone()[0])
        self.c.execute('DELETE FROM myseries WHERE tvmazeID=?',(tvmazeID,))
        self.db.commit()
        self.c.execute('DELETE FROM capitols WHERE tvmazeID=?',(tvmazeID,))
        self.db.commit()

    def updatedb(self):
        i = floor(self.lastId/250)
        print('Pagina:',i)
        info = Info()
        while True:
            r = info.tvShowList(i)
            if r ==[]:
                break


            i += 1
            if r:
                for show in r:

                    nom = str(show['name'])
                    idtvmaze = show['id']

                    imatge = ''
                    try:
                        imatge = show['image']['original']
                        print(imatge)
                    except TypeError:
                        imatge = 'None'
                        print(show['image'])

                    try:
                        sino = show['summary']
                    except:
                        sino =''

                    imdb = show['externals']['imdb']
                    if thetvdb == None:
                        thetvdb =0
                    rating = show['rating']['average']
                    if rating ==None:
                        rating = 0
#                     titol = nom
#                     idKey = idtvmaze
#                     tvdb = thetvdb
#                     print('-'*60)
#                     print('Nom', '\t', nom)
#                     print('TVMazeId','\t',idtvmaze)
#                     print('imatge','\t',imatge)
#                     print('thetvdb','\t',thetvdb)
#                     print('Rate', '\t',rating)
                    row =( int(imdb[2:]), str(idtvmaze), str(nom), str(imatge),str(rating),sino)
                    ordre = """insert into series values (?,?,?,?,?,?)"""

                    print(ordre)
                    try:
                        self.c.execute(ordre,row)

                    except sqlite3.IntegrityError:
                        print('"could not add "'+row[2]+'" twice')

                    except :
                        print('No ha funcionat',row)
                    self.db.commit()

        for serie in self.getCollectionList('myseries'):
            self.addSerie(int(serie[0]))

        self.settime()

    def getCollectionList(self, table, filtre=None, *tipus):
        extra = ' ORDER BY name DESC'
        ordre = "SELECT name, media, tviso_id FROM " + table
        if isinstance(filtre, str) and len(filtre) > 2:
                ordre = ordre + " WHERE instr(UPPER(name) , UPPER('{}'))>0".format(filtre)

#         ordre += extra
#         print(filtre)
        print(ordre)
        # filtrar el tipus de video per a la llista
        if len(tipus[0]) != 0:
            # print(tipus[0])
            ordre += " WHERE media = " + str(tipus[0][0])
            if len(tipus[0]) > 1:
                for tip in tipus[0][1:]:
                    ordre += " OR media = " + str(tip)
        print(ordre)
        self.c.execute(ordre)
        return [[str(row[2]),str(row[0]),str(row[1])] for  row in self.c]

    def getShowId(self,id):
        """
        Aconsegueix la serie amb la id de tvmaze
        """
        return self.__dbquery('SELECT * FROM mycollection WHERE tvmazeID=?',id)

    def getEpisodes(self,tviso_id):
        num_temp = self.c.execute('SELECT max(season) FROM capitols WHERE tviso_id=?',(tviso_id,))
        print('NUMERO DE TEMPORADES: ')
        episodis = dict()
        for season in range(num_temp.fetchone()[0]):
            res = self.c.execute('SELECT * FROM capitols WHERE tviso_id=? AND season = ?' , (tviso_id,season))
            episodis[season]=[row for row in res]
        return episodis


# db =SickRucDB()
# print(db.dbquery('SELECT * FROM mycollection WHERE tviso_id=?', 69))
#db.settime()
# print(db.getEpisodes(67))
# pprint(db.getCollectionList('mycollection'))
#db.updatedb()
# db.c.execute('insert into series values (756,4455,"jhon nieve","imatge")')
#db.db.commit()
# db.addSerie(613,1)
# db.updateUserMedia()
#db.addSerie(23)
#db.addSerie(643)

#db.c.execute("SELECT * FROM capitols")
#print(db.c.fetchone())

