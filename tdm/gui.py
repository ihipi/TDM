
import sys, os, multiprocessing
from threading import Thread

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QBrush
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QTreeWidgetItem, QFileDialog, QSplitter, QHBoxLayout, QFrame
from urllib.request import Request, urlopen
from tools import torrentsearch,IMG, GUI, setconfig,getconfig, MEDIATYPE, ROOTDB, transmision as tr, tviso as tv, SERIESTATE,PELISTATE
import tools
from tdm.dialegs import TVisoLogin, TransmissionConf
# from tools.torrentsearch import  BUSCADORS
from tools.db.tdmdb import TDMDB



# Clase heredada de QMainWindow (Constructor de ventanas)
class Ventana(QMainWindow):
    #Metode constructor de la classe
    def __init__(self, bd='/db/'):
        # Iniciar el objeto QMainWindow
        QMainWindow.__init__(self)
        # Carregar la configuracio de l'arxiu .ui en el objeto
        self.dialog_03 = TransmissionConf()
        self.dialog_02 = TVisoLogin()
        uic.loadUi(GUI, self)

        # self.setWindowTitle("Cambiando el título de la ventana")
        self.db = TDMDB()
        print(TDMDB)
        self.tv = tv.TViso()
        self.tabs_ = []
        for motor in torrentsearch.BUSCADORS.keys():
            self.comboMotors.addItem(motor)
        self.index =0
        ###
        ###Configuracio de l'arbre episodis
        ###
        self.treeEpisodis.setHeaderHidden(False)
        self.listShows.setHeaderHidden(False)


#         self.db.addSerie(32)



        ###########################################################
        ###                    ACCIONS                        #####
        ###                                                   #####
        ###                                                   #####
        ###########################################################

        ###########################################################
        ###            PESTANYA CONFIGURACIO                  #####
        ###########################################################
        self.btn_dirSeries.setText(getconfig()['dir_series'])
        self.btn_dirPelis.setText(getconfig()['dir_pelis'])
        self.btn_dirSeries.clicked.connect(lambda: self.setmediadirectory(1))
        self.btn_dirPelis.clicked.connect(lambda: self.setmediadirectory(2))
        self.btn_tviso.clicked.connect(self.callTvisoLogin)
        self.btn_transmission.clicked.connect(self.callTransmissionConf)
        self.conf_radio_series.toggled.connect(self._pobla_folders)
        self.conf_radio_pelis.toggled.connect(self._pobla_folders)


        ###########################################################
        ###            PESTANYA TORRENTS                      #####
        ###########################################################

        torrent_spliter = QSplitter(Qt.Horizontal)
        torrent_spliter.addWidget(self.treeResultat)
        torrent_spliter.addWidget(self.torrent_info)
        self.frameBaix.layout().addWidget(torrent_spliter)
        # self.wBaix.setLayout(QHBoxLayout)
        # f.addWidget(torrent_spliter)
        self.buto_busqueda.clicked.connect(self.buscaEvent)
        self.btnDownload.clicked.connect(lambda: self.download(self.treeResultat.currentItem()))
        self.comboMotors.currentIndexChanged.connect(self.setTorrentOptions)
        self.treeResultat.itemSelectionChanged.connect(lambda: self.set_torrent_info(self.treeResultat.currentItem()))
        self.torrent_temp =[]

        ###########################################################
        ###            PESTANYA SERIES                        #####
        ###########################################################


        hsplit= QSplitter(Qt.Horizontal)
        hsplit.addWidget(self.listShowsW)
        hsplit.addWidget(self.mediaInfo)
        self.mediaBaix.layout().addWidget(hsplit)
        vsplt= QSplitter(Qt.Vertical)
        vsplt.addWidget(self.mediaInfoUp)
        vsplt.addWidget(self.mediaInfoDown)
        self.mediaInfo.layout().addWidget(vsplt)

        self.media_temp = []
        #global\Local
        self.radioLocal.toggled.connect(self.get_items)
        self.radioGlobal.toggled.connect(self.get_items)
        self.cb_1.toggled.connect(self.feed_list)
        self.cb_2.toggled.connect(self.feed_list)
        self.cb_3.toggled.connect(self.feed_list)
        self.cb_4.toggled.connect(self.feed_list)
        #afegir borrar series de la llista
        #   add        lambda: self.db.addSerie(self.listShows.currentItem().text(0))
        #   delete     lambda: self.db.deleteSerie(self.listShows.currentItem().text(0))
        self.btnAddShow.clicked.connect(self.add_show)
        self.btnDeleteShow.clicked.connect(self.deleteShow)

        #filtra resultats
        self.lineFiltra.textChanged.connect(lambda: self.get_items(self.lineFiltra.text()))
        #mostra informacio
        self.listShows.clicked.connect(lambda: self.set_show_info(self.listShows.currentItem()))
        self.listShows.itemSelectionChanged.connect(lambda: self.set_show_info(self.listShows.currentItem()))
        #mostra info capitol
        self.treeEpisodis.clicked.connect(lambda: self.set_episodi_info(self.treeEpisodis.currentItem().text(1)))
        #al seleccionar un capitol
        # self.treeEpisodis.itemChanged.connect(self.seleccioCapitol)
        self.radioLocal.setChecked(True)
        # busca a tviso
        self.btn_busca_media.clicked.connect(lambda: self.get_search(self.line_busca_media.text()))
        # busca un torrent
        self.search_torrent.clicked.connect(lambda: self.searchMediaTorrent(self.listShows.currentItem()))

    def closeEvent(self, event):
        resultat = QMessageBox.question(self,"sortir...","Vols sortir de l'aplicacio?",QMessageBox.Yes | QMessageBox.No)
        if resultat == QMessageBox.Yes:
            self.db.dbstop()
            event.accept()
        else: event.ignore()

        ###########################################################
        #                        CONFIGURACIO                     #
        ###########################################################
    def callTvisoLogin(self):

        self.dialog_02.show()
        self.dialog_02.raise_()

    def callTransmissionConf(self):

        self.dialog_03.show()
        self.dialog_03.raise_()

    def _pobla_folders(self):
        if self.conf_radio_series.toggled:
            for f in tools.localmedia('dir_series'):
                self.treeFolder.insertTopLevelItems(0, [QTreeWidgetItem(self.listShows, f)])

    def setmediadirectory(self, tipus):
        media_dir = None
        if tipus == 1:
            media_dir = 'dir_series'
        elif tipus == 2:
            media_dir = 'dir_pelis'
        fileName = QFileDialog.getExistingDirectory(self, 'Dialog Title')
        if fileName:
            print(fileName)

            if tipus == 1:
                self.line_series.setText(fileName)
                setconfig(dir_series = fileName)
                print(tools.localmedia(media_dir))

            elif tipus == 2:
                self.line_pelis.setText(fileName)
                setconfig(dir_pelis = fileName)
                print(tools.localmedia(media_dir))

        ###########################################################
        #                        TORRENTS                         #
        ###########################################################

    def download(self, item):
        print(item.text(1))
        tr.addtorrent(item.text(1))

    def poblaListShow(self,):
        self.listShows.clear()
        tipus = [(1,self.cb_1.isChecked()),(2,self.cb_2.isChecked()),(3,self.cb_3.isChecked()),(4,self.cb_4.isChecked())]
        tip_checked = [tip[0] for tip in tipus if tip[1] !=False]
        for row in self.media_temp:
            fila = [str(row.idm),'{} '.format(row.name), str(row.tipus)]
            # afegim item
            # Seleccio deltreeWidget afegir a dalt(columna,[objecte])
            if len(tip_checked) > 0:
                if int(fila[-1]) in tip_checked:
                    self.listShows.insertTopLevelItems(0, [QTreeWidgetItem(self.listShows, fila)])
            else:
                self.listShows.insertTopLevelItems(0, [QTreeWidgetItem(self.listShows, fila)])

    def buscaEvent(self, motor=None, paraula=None,divixserie=None, imdb=None):
#         busqueda = DivixTotal().busca(str(self.text_busqueda.text()),self.check_series.isChecked())
        m = motor or self.comboMotors.currentText()
        p = paraula or str(self.text_busqueda.text())
        s = divixserie or self.check_series.isChecked()
        i = imdb or self.opt_kick_imdb.isChecked()

        self.torrent_temp = torrentsearch.busca(m, p, divixserie=s,imdb=i)
        print(m, self.text_busqueda.text(),i)
        self.treeResultat.clear()
        for tor in self.torrent_temp:
            row = tor.getList()[:-2]
        # for k in busqueda[0].keys():
            # row = [k,str(busqueda[k][0])]
            print(row)
            if len(self.amb.text()) > 1:
                if self.amb.text() in tor.name:
                    self.treeResultat.insertTopLevelItems(0,[QTreeWidgetItem(self.treeResultat, row)])
            else:
                self.treeResultat.insertTopLevelItems(0,[QTreeWidgetItem(self.treeResultat, row)])

    def set_torrent_info(self, item):
        for t in self.torrent_temp:
            if t.name == item.text(0):
                self.tor_info_name.setText(t.name)
                if t.info[:13] == 'http://kat.cr':
                    k = torrentsearch.KickAss()
                    self.tor_info_extra.setText(k.getInfo(t.info))
                else:
                    self.tor_info_extra.setText(t.info)

    def setTorrentOptions(self):
        motor = self.comboMotors.currentText()
        if motor == 'divixtotal':
            self.box_dvx.hide()
            self.box_kick.hide()
            self.box_dvx.show()
        elif motor == 'elitetorrent':
            self.box_dvx.hide()
            self.box_kick.hide()
            self.box_elite.show()
        elif motor == 'kickass':
            self.box_dvx.hide()
            self.box_elite.hide()
            self.box_kick.show()
        ###########################################################
        #                           SERIES                        #
        ###########################################################

    def deleteShow(self):
        """
        crida la bd per BORRAR una serie de myseries
        """
        num = self.listShows.currentItem().text(0)
        self.db.deleteSerie(num)
        self.get_items()
        print(num)

    def add_show(self):
        """
        crida la bd per AFEGIR una serie de myseries
        """

        num = int(self.listShows.currentItem().text(0))

        self.db.addSerie(num, None)
        print(num)

    def feed_list(self):
        if self.radioLocal.isChecked():
            self.get_items()
        elif self.radioGlobal.isChecked():
            self.poblaListShow()

    def get_items(self, filtra=''):
        """
        Busca i mostra series a la llista lateral
        @param filtra: Text de filtratge pe a la busqueda
        """

        self.listShows.clear()

        if isinstance(filtra,   bool):
            filtra =''
        table = None
        # comprovem quina llista esta seleccionada Local/Global
        if self.radioLocal.isChecked():
            table = 'mycollection'
            #  Iterem per poblar||
            # --------- crida base dades --- (GLOB/LOC,TEXT)
            tipus = [(1,self.cb_1.isChecked()),(2,self.cb_2.isChecked()),(3,self.cb_3.isChecked()),(4,self.cb_4.isChecked())]
            self.media_temp = self.db.getCollectionList(table, filtra, [tip[0] for tip in tipus if tip[1] !=False])
            self.poblaListShow()
#             print(row)

    def get_search(self, text):

        self.listShows.clear()
        self.media_temp = self.tv.searchTitle(text)
        rows = []

        self.poblaListShow()

    def set_image(self, idm, tipus = None):
        """
        donada una url assigna la imatge de la serie
        """
        data=None
        pixmap = QPixmap()
        dir =ROOTDB+'/imatges/'

        # en cas de ser de la coleccio local
        #nomes cal dfer servir Load
        try:
            found =False
            for f in os.listdir(dir):

                if idm == f.split('_')[0] and 'poster.jpg' == f.split('_')[-1]:
                    print(dir + f)
                    found = True
                    pixmap.load(dir + f)
            if not found:
                self.db.get_image_queue(idm,tipus)


            #creem i assignem la
            # Objecte label ---------- imatge - escalem (tamany definit de Label), Mante l'aspecte, ???)

            self.labelImatge.setPixmap(pixmap.scaled(self.labelImatge.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            return True
        except:

            self.labelImatge.setText('Sense imatge')
            return False

    def set_show_info(self, item):
        """
        Emplena el quadre de Informacio
        @param item: linia de la llista lateral
        """

        for media in self.media_temp:
             if int(media.idm) == int(item.text(0)):
                print('OK! ','item seleccionat: ', item.text(1), item.text(2))
                self.labelTitol.setText(media.name)
                self.set_image(item.text(0), str(media.tipus))
                self.setSinopsy(media.plot)
                print()
                if item.text(2) == '1':
                    if self.radioLocal.isChecked():
                        self.labelRating.setText(SERIESTATE[str(media.estat)])
                    else:
                        tviso = tv.TViso()
                        pixmap = QPixmap()
                        res = tviso.getFullInfo(item.text(0), str(media.tipus))
                        url = 'https://img.tviso.com'+'/{}{}{}'.format(res['images']['country'] or 'XX', IMG['posterL'],res['images']['backdrop'])
                        print(url)
                        data = request.urlretrieve(url)
                        pixmap.load(data)
                        self.labelImatge.setPixmap(pixmap.scaled(self.labelImatge.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

                    self.extrainfo.hide()
                    self.treeEpisodis.show()
                    self.addEpisodis(media.idm)
                else:
                    if self.radioLocal.isChecked():
                        self.labelRating.setText(PELISTATE[str(media.estat)])
                    else:
                        tviso = tv.TViso()
                        pixmap = QPixmap()
                        res = tviso.getFullInfo(item.text(0), str(media.tipus))
                        country = 'ES'
                        try:
                            country = res['images']['country']
                        except:
                            pass
                        url = 'https://img.tviso.com'+'/{}{}{}'.format( country, IMG['posterM'],res['images']['poster'])
                        print(url)
                        req = Request(url,  headers={'User-Agent': 'Mozilla/5.0'})
                        data = urlopen(req).read()
                        pixmap.loadFromData(data)
                        self.labelImatge.setPixmap(pixmap.scaled(self.labelImatge.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

                    self.extrainfo.show()
                    self.treeEpisodis.hide()

    def set_episodi_info(self, item):
        try:
            print([item.text(0),item.text(1),item.text(2)])
            self.db.c.execute('SELECT sinopsis, titol FROM capitols WHERE titol=?', (item.text(2),))
            self.db.commit()
            sin, tit = self.db.c.fetchone()
            self.setSinopsy(sin)
            self.labelTitol.setText(tit)
        except Exception as e:
            print('Episodi info no actualitzat')
            print('ERROR: {}'.format(e))

    def setSinopsy(self, text= 'Sinopsis....'):
        self.labelSinopsi.setText(text)

    def addEpisodis(self, tviso_id):
        """
        Emplena l'arbre de capitols i detecta quins estan vistos
        :param tviso_id:  idm(tviso) per buscar a la base de dades local
        :return:
        """
        # neteja l'arbre d'episodis i el prepara per repoblarlo
        self.treeEpisodis.clear()

        parent =self.treeEpisodis.invisibleRootItem()
        col =0
        # cridem la base de dades per aconseguir un diccionari {'season':[episodis,...]}
        seasons = self.db.getEpisodes(tviso_id)
        # comencem a poblar l'arbre
        for k in seasons.keys():
            # per cada temporada (k) creem una entrada "pare"
            s = QTreeWidgetItem(parent, ['Season '+ str(k)])
            s.setData(col, Qt.UserRole, 'Temporada')
            # per cada episodi de la temporada una entrada associada a l'anterior
            for e in seasons[k]:

                row = QTreeWidgetItem(s, ['', str(e[3]), e[4]])
                row.setData(1, Qt.UserRole, 'Episodi')
                # comprovem l'estat i marquem si esta vista o no
                if e[-1] != '':
                    row.setBackground(0,QBrush(Qt.darkBlue))    # la pintem de color
                    row.setCheckState(0, Qt.Checked)            # la marquem

                else:
                    row.setCheckState(0, Qt.Unchecked)

        print("Arbre d'episodis acyualitzat")

    def seleccioCapitol(self, item, column):
        print(item.text(column), column)
        try:
            if item.checkState(column) == Qt.Checked:
                self.db.c.execute('UPDATE capitols SET estat=? WHERE titol=?', (1, item.text(2)))
                self.db.db.commit()
                self.db.c.execute('SELECT estat FROM capitols WHERE titol=?', (item.text(2), ))
                self.db.db.commit()
                print('ESTAT:',self.db.c.fetchone())

                print("checked", item, item.text(2))
            if item.checkState(column) == Qt.Unchecked:

                self.db.c.execute('UPDATE capitols SET estat=? WHERE titol=?', (0,item.text(2)))
                self.db.db.commit()
                self.db.c.execute('SELECT estat FROM capitols WHERE titol=?', (item.text(2),))
                self.db.db.commit()
                print('ESTAT:', self.db.c.fetchone()[-1])
                print("unchecked", item, item.text(2))
        except Exception as e:
            print('seleccio capitol fallada : {}'.format(e))

    def searchMediaTorrent(self, item):
        idm, name, tipus = item.text(0),item.text(1),int(item.text(2))
        self.text_busqueda.setText(name)
        self.tabs.setCurrentIndex(1)
        self.db.c.execute('select imdb from mycollection where idm={}'.format(idm))
        imdb = self.db.c.fetchone()[0]
        motor =  'kickass' # self.comboMotors.currentText()
        self.buscaEvent(motor,name, imdb= imdb)

        # if tipus > 1:
        #     self.buscaEvent(motor, name, )
        # else:
        #     self.buscaEvent(motor, name, divixserie = True )

def start():
    #Instancia para iniciar una aplicación
    app = QApplication(sys.argv)
    #Crear un objeto de la clase
    _ventana = Ventana()
    #Mostra la ventana
    _ventana.show()
    #Ejecutar la aplicación
    app.exec_()