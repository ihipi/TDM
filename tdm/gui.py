
import sys, os

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QBrush
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QFileDialog

from tools import torrentsearch, GUI, setconfig,getconfig, MEDIATYPE, ROOTDB
import tools
from tdm.dialegs import TVisoLogin
# from tools.torrentsearch import  BUSCADORS
from tools.db.tdmdb import TDMDB



# Clase heredada de QMainWindow (Constructor de ventanas)
class Ventana(QMainWindow):
    #Metode constructor de la classe
    def __init__(self, bd='/db/'):
        # Iniciar el objeto QMainWindow
        QMainWindow.__init__(self)
        # Carregar la configuracio de l'arxiu .ui en el objeto
        uic.loadUi(GUI, self)

        # self.setWindowTitle("Cambiando el título de la ventana")
        self.db = TDMDB()
        print(TDMDB)
        self.tabs = []
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
        ###########################################################
        ###            PESTANYA TORRENTS                      #####
        ###########################################################
        self.buto_busqueda.clicked.connect(self.buscaEvent)
        self.btnDownload.clicked.connect(lambda: self.download(self.treeResultat.currentItem()))


        ###########################################################
        ###            PESTANYA SERIES                        #####
        ###########################################################


        #global\Local
        self.radioLocal.toggled.connect(self.get_items)
        self.radioGlobal.toggled.connect(self.get_items)
        self.cb_1.toggled.connect(self.get_items)
        self.cb_2.toggled.connect(self.get_items)
        self.cb_3.toggled.connect(self.get_items)
        self.cb_4.toggled.connect(self.get_items)
        #afegir borrar series de la llista
        #   add        lambda: self.db.addSerie(self.listShows.currentItem().text(0))
        #   delete     lambda: self.db.deleteSerie(self.listShows.currentItem().text(0))
        self.btnAddShow.clicked.connect(self.add_show)
        self.btnDeleteShow.clicked.connect(self.deleteShow)

        #filtra resultats
        self.lineFiltra.textChanged.connect(lambda: self.get_items(self.lineFiltra.text()))
        #mostra informacio
        self.listShows.clicked.connect(lambda: self.set_show_info(self.listShows.currentItem()))
        #mostra info capitol
        self.treeEpisodis.clicked.connect(lambda: self.set_episodi_info(self.treeEpisodis.currentItem().text(1)))
        #al seleccionar un capitol
        # self.treeEpisodis.itemChanged.connect(self.seleccioCapitol)
        self.radioLocal.setChecked(True)





#     def closeEvent(self, event):
#         resultat = QMessageBox.question(self,"sortir...","Vols sortir de l'aplicacio?",QMessageBox.Yes | QMessageBox.No)
#         if resultat == QMessageBox.Yes:
#             self.db.dbstop()
#             event.accept()
#         else: event.ignore()
#
        ###########################################################
        #                        CONFIGURACIO                     #
        ###########################################################
    def callTvisoLogin(self):
        self.dialog_02 = TVisoLogin()
        self.dialog_02.show()
        self.dialog_02.raise_()

        ###########################################################
        #                        TORRENTS                         #
        ###########################################################
    def download(self, item):
        # TODO agafar un torrent i passarlo al transmission
        pass

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


    def buscaEvent(self):
#         busqueda = DivixTotal().busca(str(self.text_busqueda.text()),self.check_series.isChecked())

        busqueda = torrentsearch.busca(motor=self.comboMotors.currentText(), paraula=str(self.text_busqueda.text()), divixserie=self.check_series.isChecked())
        print(self.comboMotors.currentText(), self.text_busqueda.text(), self.check_series.isChecked())
        #busqueda = DivixTotal().busca('fargo',True)
        self.treeResultat.clear()
        for k in busqueda.keys():
            row = [k,busqueda[k]]
            print(row)
            self.treeResultat.insertTopLevelItems(0,[QTreeWidgetItem(self.treeResultat, row)])

#             item = QListWidgetItem(k)
#             self.list_resultat.addItem(item)

    def setTorrentInfo(self):
        motor = self.comoMotors
        if motor == 'divixtotal':

            pass
        elif motor == 'elitetorrent':
            pass
        elif motor == 'kickass':
            pass

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
        if self.radioGlobal.isChecked():
            table = 'series'



        #  Iterem per poblar||
        # --------- crida base dades --- (GLOB/LOC,TEXT)
        tipus = [(1,self.cb_1.isChecked()),(2,self.cb_2.isChecked()),(3,self.cb_3.isChecked()),(4,self.cb_4.isChecked())]
        print([tip[0] for tip in tipus if tip[1] !=False])
        for row in self.db.getCollectionList(table, filtra, [tip[0] for tip in tipus if tip[1] !=False]):

            # afegim item
            # Seleccio deltreeWidget afegir a dalt(columna,[objecte])
            self.listShows.insertTopLevelItems(0, [QTreeWidgetItem(self.listShows, row)])

#             print(row)

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
        local = self.radioLocal.isChecked()
        if local:
            print(item.text(0))

            tviso_id = item.text(0)
            # info =self.db.getShowId(tvmaID)[0]
            self.db.c.execute('SELECT tviso_id, media,seasons, imatge, plot, name FROM mycollection WHERE tviso_id=?', (item.text(0), ))
            idm,media, seasons, imatge , plot, name = self.db.c.fetchone()
            print('local:\n', idm,media, seasons, imatge , plot, name)
#             self.labelTitol.setText(info[0][2])
#             self.labelRating.setText(info[0][4])
#             self.setImage(info[0][3])
#             self.setSinopsy(info[0][5])
#             self.addEpisodis(tvmaID)
        else:
            tviso_id = item.text(0)
            info =self.db.getCollectionShowId(tviso_id)[0]
            # self.db.c.execute('SELECT * FROM myseries WHERE tvmazeID=?',[item.text(0),])
            # info =[row for  row in self.db.c]
            print('Global:\n', info)

        self.labelTitol.setText(name)
        self.labelRating.setText(str(seasons))
        self.set_image(item.text(0), str(media))
        self.setSinopsy(plot)
        print('item seleccionat: ', item.text(1), item.text(2))
        if item.text(2) == '1':
            self.addEpisodis(tviso_id)

    def set_episodi_info(self, item):
        try:
            print([item.text(0),item.text(1),item.text(2)])
            self.db.c.execute('SELECT sinopsis, titol FROM capitols WHERE titol=?', (item.text(2),))
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
                print('ESTAT:',self.db.c.fetchone())

                print("checked", item, item.text(2))
            if item.checkState(column) == Qt.Unchecked:

                self.db.c.execute('UPDATE capitols SET estat=? WHERE titol=?', (0,item.text(2)))
                self.db.db.commit()
                self.db.c.execute('SELECT estat FROM capitols WHERE titol=?', (item.text(2),))
                print('ESTAT:', self.db.c.fetchone()[-1])
                print("unchecked", item, item.text(2))
        except Exception as e:
            print('seleccio capitol fallada : {}'.format(e))

def start():
    #Instancia para iniciar una aplicación
    app = QApplication(sys.argv)
    #Crear un objeto de la clase
    _ventana = Ventana()
    #Mostra la ventana
    _ventana.show()
    #Ejecutar la aplicación
    app.exec_()