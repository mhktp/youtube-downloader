from PyQt5.QtCore import QDateTime, Qt, QTimer, QSettings
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget,QFormLayout,QTextEdit,
        QVBoxLayout, QWidget)


import os , sys, configparser, json
import youtube_dl


class WidgetGallery(QDialog):       
    def createOptions(self,directory):
        options = {}
        if self.isThumbnail.isChecked():
            options['writethumbnail'] = True
        if self.isThumbnail.isChecked():
            options["allsubtitles"] = True
        if self.both.isChecked():
            options['format'] = "{}[ext={}]+{}[ext={}]/best[ext=mp4]/best".format(str(self.videoFormatCB.currentText()),
                                                                                        str(self.videoFileCB.currentText()),
                                                                                      str(self.audioFormatCB.currentText()),
                                                                                        str(self.audioFileCB.currentText()))
        elif self.audioOnly.isChecked():
            options['format'] = str(self.audioFormatCB.currentText())+"[ext={}]/bestaudio[ext=wav]/bestaudio".format(str(self.audioFileCB.currentText()))
            options['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': str(self.audioFileCB.currentText()),
                'preferredquality': '192',}]
        elif self.videoOnly.isChecked():
            options['format'] = str(self.videoFormatCB.currentText()) + "[ext={}]/bestvideo[ext=mp4]/bestvideo".format(str(self.videoFileCB.currentText()))
        options["outtmpl"] = directory + "/%(title)s.%(ext)s"
        options["socket_timeout"] = 1
        options["retries"] = 10000000
        print("Options are :\n",options)
        return options

    def download_process(self,video,options):
        if len(self.youtubeURL.text()) == 0:
            self.outputs.append("ERROR : No Youtube URL.")
            return False
        try:
            with youtube_dl.YoutubeDL(options) as ydl:
                info_dict = ydl.extract_info(video, download=False)
                ydl.download([video])
        except youtube_dl.utils.DownloadError as error:
            self.outputs.append("\n********************\n{}\n********************".format(error))
            return False
        self.outputs.append("Started a new prompt.")
        self.outputs.append("Done downloading : {} ".format(info_dict['title']))   

    def download(self):
        self.downloadButton.setEnabled(False)
        directory = self.dirinput.text().replace("\\","/")
        if len(directory) == 0 or not os.path.isdir(directory):
            self.outputs.append("ERROR : Invalid Directory.")
            self.downloadButton.setEnabled(True)
            return
        youtubeURL = self.youtubeURL.text().replace(" ","").split(";")
        results = []
        options = self.createOptions(directory)
        for video in youtubeURL:
            results.append(self.download_process(video,options))
        if False in results:
            self.outputs.append("!----------------\nEnded with {} error(s).".format(results.count(False)))
        else:
            self.outputs.append("-----------------\nEnded successfully.")
        self.downloadButton.setEnabled(True)


    def closeEvent(self, e):
        # Write window size and position to config file
        self.settings.setValue( "windowScreenGeometry", self.saveGeometry() )
        self.config["DEFAULT"]["email"] = self.emailText.text()
        self.config["DEFAULT"]["dirinput"] = self.dirinput.text()
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        e.accept()
        
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        
        self.settings = QSettings("yt_downloader", "TOMHK")
        self.setWindowIcon(QIcon('icon.png'))

        # Accounts layout

        self.accountbox = QGroupBox("Youtube Account")
        self.accountbox.setCheckable(True)

        self.emailText = QLineEdit('')
        self.pwText = QLineEdit('')
        self.pwText.setEchoMode(QLineEdit.Password)
        self.authText = QLineEdit('')
        
        logLayout = QFormLayout()
        logLayout.addRow("Email :",self.emailText)
        logLayout.addRow("Password :",self.pwText)
        logLayout.addRow("Auth :",self.authText)

        self.accountbox.setLayout(logLayout)
        #logLayout.addStretch(1)

        # Top Layout
        pixmap = QPixmap('grand_logo.png')
        pixmap.scaled(64,64)
        pixlabel = QLabel()
        pixlabel.setPixmap(pixmap)

        self.createrow1()
        self.createrow2()
        self.createrow3()
        
        topLayout = QHBoxLayout()
        topLayout.addWidget(pixlabel)
        topLayout.addWidget(self.accountbox)
        #topLayout.addStretch()

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 1)
        mainLayout.addWidget(self.row1, 1, 0)
        mainLayout.addWidget(self.row2, 2, 0)
        mainLayout.addWidget(self.row3, 3, 0)

        mainLayout.setRowStretch(1, 0)
        mainLayout.setRowStretch(2, 2)
        mainLayout.setRowStretch(3, 1)
        #mainLayout.setColumnStretch(1, 1)
        #mainLayout.setColumnStretch(0, 1)
        self.setLayout(mainLayout)

        self.config = configparser.ConfigParser()
        try:
            self.config.read('config.ini')
        except:
            self.outputs.append("ERROR : Config deleted, recreated one.")
            self.config['DEFAULT'] = {"email": "","geometry":[100,100,500,600],"dirinput":""}
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

        self.emailText.setText(self.config["DEFAULT"]["email"])
        self.dirinput.setText(self.config["DEFAULT"]["dirinput"])
        self.setWindowTitle("Youtube Downloader - TOMHK")
        QApplication.setStyle(QStyleFactory.create('windowsvista'))
        geometry = json.loads(self.config.get("DEFAULT","geometry"))
        self.setGeometry(int(geometry[0]),
                         int(geometry[1]),
                         int(geometry[2]),
                         int(geometry[3]))

        self.accountbox.setChecked(False)

    def createrow1(self):
        self.row1 = QGroupBox("Youtube Link")

        label = QLabel("Enter a youtube link here :")
        self.youtubeURL = QLineEdit()


        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.youtubeURL)
        layout.addStretch(1)
        self.row1.setLayout(layout)

        
    def createrow2(self):            
        self.row2 = QGroupBox("Options")

        self.both = QRadioButton("Both")
        self.audioOnly = QRadioButton("Audio Only")
        self.videoOnly = QRadioButton("Video Only")

        self.videoFormatCB = QComboBox()
        self.videoFormatCB.addItems(["bestvideo","worstvideo"])
        videoLabel = QLabel("&Video Quality:")
        videoLabel.setBuddy(self.videoFormatCB)
        
        self.audioFormatCB = QComboBox()
        self.audioFormatCB.addItems(["bestaudio","worstaudio"])
        audioLabel = QLabel("&Audio Quality:")
        audioLabel.setBuddy(self.audioFormatCB)
        
        self.isSubtitles = QCheckBox("&Download Subtitles")
        self.isSubtitles.setChecked(False)

        self.isThumbnail = QCheckBox("&Download Thumbnail")
        self.isThumbnail.setChecked(False)

        audiofLabel = QLabel("Audio Formats:")
        self.audioFileCB = QComboBox()
        self.audioFileCB.addItems(["mp3","wav"])
        videofLabel = QLabel("Video Quality:")
        self.videoFileCB = QComboBox()
        self.videoFileCB.addItems(["mp4","webm"])


        propertiesGB = QGroupBox("Video Properties")
        propertiesGBLayout = QGridLayout()
        propertiesGBLayout.addWidget(self.both, 0, 0)
        propertiesGBLayout.addWidget(self.audioOnly, 1, 0)
        propertiesGBLayout.addWidget(self.videoOnly, 2 ,0)
        propertiesGBLayout.addWidget(audioLabel, 0 ,1)
        propertiesGBLayout.addWidget(self.audioFormatCB, 0 ,2)
        propertiesGBLayout.addWidget(videoLabel, 1 ,1)
        propertiesGBLayout.addWidget(self.videoFormatCB, 1 ,2)
        propertiesGB.setLayout(propertiesGBLayout)

        otherLayout = QGridLayout()
        otherLayout.addWidget(self.isSubtitles,1,0)
        otherLayout.addWidget(self.isThumbnail,1,1)
        otherLayout.addWidget(audiofLabel,2,0)
        otherLayout.addWidget(self.audioFileCB,3,0)
        otherLayout.addWidget(videofLabel,2,1)
        otherLayout.addWidget(self.videoFileCB,3,1)
        
        layout = QGridLayout()
        layout.addWidget(propertiesGB, 1, 1)
        layout.addLayout(otherLayout,1,0)
        #layout.addStretch(1)
        self.row2.setLayout(layout)

        #activations

        self.both.setChecked(True)

        
    def createrow3(self):
        self.row3 = QGroupBox("Processing")

        dirlabel = QLabel("Enter dir input :")
        self.dirinput = QLineEdit()

        dirlayout = QVBoxLayout()
        dirlayout.addWidget(dirlabel)
        dirlayout.addWidget(self.dirinput)
        dirlayout.addStretch(1)
        
        self.downloadButton = QPushButton("Download")
        self.downloadButton.setDefault(True)

        self.outputs = QTextEdit()
        self.outputs.setPlainText("Outputs :\n")
        self.outputs.setReadOnly(True)

        
        
        layout = QVBoxLayout()
        layout.addLayout(dirlayout)
        layout.addWidget(self.outputs)
        layout.addWidget(self.downloadButton)
        layout.addStretch(1)
        self.row3.setLayout(layout)
        self.downloadButton.clicked.connect(self.download)


sys._excepthook = sys.excepthook 
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback) 
    sys.exit(1) 
sys.excepthook = exception_hook 

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())



