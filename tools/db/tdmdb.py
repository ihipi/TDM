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
from tools import IMG, DB, ROOTDB


class TDMDB():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.root = ROOTDB
        self.dbfile = DB
        self.db = sqlite3.connect(DB)
        self.c = self.db.cursor()

        self.c.execute('CREATE TABLE IF NOT EXISTS '
                       'series ('
                       'imdb INTEGER PRIMARY KEY not NULL,'
                       'tvmazeID INTEGER, '
                       'name TEXT, '
                       'image TEXT, '
                       'rating TEXT, '
                       'sinopsis TEXT)')
        self.c.execute('CREATE TABLE IF NOT EXISTS '
                       'mycollection ('
                       'imdb INTEGER PRIMARY KEY not NULL,'
                       'tviso_id INTEGER, '
                       'media INTEGER, '
                       'name TEXT, '
                       'plot TEXT, '
                       'estat TEXT, '
                       'imatge TEXT, seasons INTEGER )')
        self.c.execute('create table if not exists '
                       'capitols ('
                       'idm INTEGER PRIMARY KEY not NULL, '
                       'tviso_id INTEGER, '
                       'season INTEGER, '
                       'capitol INTEGER, '
                       'titol TEXT, '
                       'sinopsis TEXT,'
                       'estat INTEGER , '
                       'date TEXT)')
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
        # print("La ultima actualitzacio: {}\nFrequencia d'actualitzacio: {}"(self.lastUpdate,str(tools.getconfig()['actualitzacio_freq'])))
        if deltaTime.days>=tools.getconfig()['actualitzacio_freq']:
            print("Fa {} dies de la ultima actualitzacio de la DB".format(deltaTime.days))
            self.updateUserMedia()
        else:
            print('-'*50,'\nBase de dades actualitzada a dia: {}\n'.format(self.lastUpdate),'-'*50)

    def settime(self):
#         f = open(self.root+'confb', mode='w')
        last = {'lastUpdate':time.strftime(self.format)}
#         j = json.dump(last, f )
#         f.close()
        tools.setconfig(lastUpdate = time.strftime(self.format))
        return tools.getconfig()

    def dbstart(self):
        self.db = sqlite3.connect(self.dbfile)
        self.c = self.db.cursor()
        return self.db.cursor()

    def dbstop(self):
        self.db.close()

    def __dbquery(self, query,*args):
        q = self.dbstart()
        response = None
        try:
            print((query, args))
            response = [row for row in self.c.execute(query, args)]
        except Exception as e:
            return False, print(e)

        # self.dbstop()
        return response

    # TODO canviar per un query que retorni la id mes alta
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
        sortida = False
        while   sortida == False:
            # Si el primer argument és un Queue definim @param fil i cua
            if isinstance(args[1],queue.Queue):
                fil, cua = args
                # aconseguim la serie i el tipus del seguent element de la cua
                serie, tipus = cua.get()
            else: # si el primer argument no es Queue assignem serie i tipus directament
                fil, cua= None, None
                serie, tipus = args

            tviso =  TViso()
            print('##'*60,'\nFil numero : {},\t codi: {},\t tipus:{}\n'.format(fil,serie, tipus),'##'*60)
            res = tviso.getFullInfo(serie, tipus)

            try:
                if isinstance(res['images'], dict):
                    posterFile = ROOTDB+'/imatges/'+serie+"_"+ res['imdb'] +"_poster.jpg"
                    backdropFile = ROOTDB+'/imatges/'+serie+"_"+ res['imdb'] +"_back.jpg"


                    if not os.path.exists(posterFile) and not os.path.exists(backdropFile):
                        backurl = 'https://img.tviso.com'+'/{}{}{}'.format(res['images']['country'] or 'XX', IMG['fonsL'],res['images']['poster'])
                        posterurl = 'https://img.tviso.com'+'/{}{}{}'.format(res['images']['country'] or 'XX', IMG['posterL'],res['images']['backdrop'])
                        print(posterurl, posterFile )
                        print(backurl, backdropFile )
                        #descarreguem la imatge amb un WGET de consola normal i corrent
                        print('descarregant poster i back per la serie {}'.format(serie))
                        os.system("wget -O {0} {1}".format(posterFile, posterurl))
                        os.system("wget -O {0} {1}".format(backdropFile, backurl))
                        if fil != None:
                            cua.task_done()
                        else:
                            sortida = True
                    elif not os.path.exists(posterFile):
                        posterurl = 'https://img.tviso.com'+'/{}{}{}'.format(res['images']['country'], IMG['posterL'],res['images']['poster'])
                        print(posterurl, posterFile )
                        print(backurl, backdropFile )
                        #descarreguem la imatge amb un WGET de consola normal i corrent
                        print('descarregant poster pe la serie {}'.format(serie))
                        os.system("wget -O {0} {1}".format(posterFile, posterurl))
                        if fil != None:
                            cua.task_done()
                        else:
                            sortida = True
                    if not os.path.exists(backdropFile):
                        backurl = 'https://img.tviso.com'+'/{}{}{}'.format(res['images']['country'] or 'ES', IMG['fonsL'],res['images']['backdrop'])
                        print(posterurl, posterFile )
                        print(backurl, backdropFile )
                        #descarreguem la imatge amb un WGET de consola normal i corrent
                        print('descarregant background pe la serie {}'.format(serie))
                        os.system("wget -O {0} {1}".format(backdropFile, backurl))
                        if fil != None:
                            cua.task_done()
                        else:
                            sortida = True
                    else:
                        print('La imatge ja esta descarregada')
                        if fil != None:
                            cua.task_done()
                        else:
                            sortida = True


                else:
                    cua.task_done()
                    print('sense imatge')
                    return False
            except Exception as e:
                print('ERROR: ', e)
                if fil != None:
                    cua.task_done()
                else:
                    sortida = True

    def addSerie(self, idm, media_type):

        tviso =  TViso()
        res = tviso.getFullInfo( idm, media_type)
        try:
            # posem la imatge en que teoricament existeix
            imageFile = ROOTDB + "/imatges/{}_{}_poster.jpg".format(res['idm'],res['imdb'])

            if not os.path.isfile(imageFile):
                imageFile = ""

            seasons = 0
            if res['mediaType']== 1:
                for k in res['seasons'].keys():
                    if int(k) > seasons:
                        seasons = int(k)
            values = (int(res['imdb'][2:]),     # 1 imdb
                      int(res['idm']),          # 2 idm
                      int(res['mediaType']),    # 3 media
                      str(res['name']),         # 4 name
                      str(res['plot']),
                      str(res['status']),       # 5 estat
                      imageFile,                # 6 imatge
                      seasons)                  # 7 seasons
            self.c.execute("INSERT OR REPLACE into mycollection values (?,?,?,?,?,?,?,?)",values)
            self.db.commit()
            print("{}({}) s'ha afegit correctament".format(res['name'], res['idm']))

        except Exception as e:

            print('error:\t'+str(e)+'...  \no no existeix...\n')


        #afegim els episodis a la taula capitols


        if res['mediaType'] == 1:
            for season in res['seasons'].keys():
                for e in res['seasons'][str(season)]:
                    estat =0
                    values = (int(e['idm']),int(e['media']['idm']),
                              int(e['season']), int(e['num']),
                              str(e['name']),
                              str(e['plot']),
                              estat,
                              '')

                    print('-'*60)
                    ordre = """INSERT OR replace into capitols values (?,?,?,?,?,?,?,?) """
                    try:
                        self.c.execute(ordre,values)
                        self.db.commit()

                    except sqlite3.IntegrityError:
                        print("couldn't add episode twice")
                    except Exception as e :
                        print("epic fail: {}  ".format(e),ordre)

    def updateUserMedia(self):
        tviso = TViso()
        res = tviso.getUserSumary()
        image_dict = dict()
        #busquem totes les imatges que tenim guardades
        for file in os.listdir(ROOTDB+'/imatges/'):
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


        img_file =  open(ROOTDB+'/imatges/imatges_dict', mode='w+')
        json.dump(image_dict,img_file)
        img_file.close()
        image_file = open(ROOTDB+'/imatges/imatges_dict', mode='r+')
        images = json.load(image_file)
        for media in res['collection']['medias'].keys():
            tipus, idm = media.split('-')
            idms = images.keys()
            dbexist = self.__dbquery('SELECT * FROM mycollection WHERE tviso_id= ?', idm)
            print('query de la serie a mycollection', dbexist)
            if str(idm) not in idms:
                print(idm, idms)
                print('Queuing:', idm, tipus)
                self.wgetImage(idm, tipus)
                # per fer servir la cua de descarregues
                # self.get_image_queue.put((idm,tipus))
            if dbexist == []:
                self.addSerie(idm, tipus)
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
                    ordre = """INSERT OR REPLACE into series values (?,?,?,?,?,?)"""

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

    def getCollectionList(self, table, filtre=None, *tipus ):
        extra = ' ORDER BY name DESC'
        ordre = "SELECT * FROM " + table
        ordretipus = ordrefiltre =None
        if isinstance(filtre, str) and len(filtre) > 1:
            ordrefiltre = "instr(UPPER(name) , UPPER('{}'))>0".format(filtre)

        # filtrar el tipus de video per a la llista
        print("tipus:",tipus[0])

        if len(tipus[0]) > 0:
            tip=""
            for t in tipus[0]:
                print(t)
                tip+=str(t) + ","
            print(tip)
            ordretipus= "media IN (" + tip[:-1] + ")"

        if ordrefiltre:
            ordre += " WHERE " + ordrefiltre
            if ordretipus:
                ordre += " AND " + ordretipus
        else:
            if ordretipus:
                ordre += " WHERE " + ordretipus

        print(ordre)
        self.c.execute(ordre)
        llista = []
        for row in self.c:
            llista.append(tools.Media(**{'imdb' : row[0],'idm' : row[1],'mediaType' : row[2],'name' : row[3],'plot' : row[4],'estat' : row[5],'seasons' : row[6]}))
        print(llista)

        return llista

    def getCollectionShowId(self, idm):
        """
        Aconsegueix la serie amb la id de tvmaze
        """
        return self.__dbquery('SELECT * FROM mycollection WHERE idm=?',(idm,))

    def getEpisodes(self,tviso_id):
        num_temp = self.c.execute('SELECT max(season) FROM capitols WHERE tviso_id=?',(tviso_id,))
        print('NUMERO DE TEMPORADES: ')
        episodis = dict()
        for season in range(num_temp.fetchone()[0]):
            res = self.c.execute('SELECT * FROM capitols WHERE tviso_id=? AND season = ?' , (tviso_id,season))
            episodis[season]=[row for row in res]
        return episodis


# db =TDMDB()
# for m in db.getCollectionList('mycollection','',*[1,2,3]):
#     if isinstance(m,tools.Media):
#         print('info: ',m.info())
#     else:
#         print('No')
# print(db.dbquery('SELECT * FROM mycollection WHERE tviso_id=?', 69))
#db.settime()
# print(db.getEpisodes(67))
# pprint(db.getCollectionList([tools.Media(**{'imdb' : row[0],'idm' : row[1],'mediaType' : row[2],'name' : row[3],'plot' : row[4],'estat' : row[5],'seasons' : row[6]})row for row in self.c]'mycollection'))
#db.updatedb()
# db.c.execute('INSERT OR REPLACE into series values (756,4455,"jhon nieve","imatge")')
#db.db.commit()
# db.addSerie(613,1)
# db.updateUserMedia()
#db.addSerie(23)
#db.addSerie(643)

#db.c.execute("SELECT * FROM capitols")
#print(db.c.fetchone())

