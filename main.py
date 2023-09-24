#pyqt6 call .ui file

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt6.QtCore import QFile,QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from PyQt6 import uic
from algoritmoGenetico import algoritmoGenetico
import cv2
import matplotlib.pyplot as plt
import numpy as np
class GeneticAlgorithmThread(QThread):
    update_signal = pyqtSignal(np.ndarray)

    def run(self):
        def update_callback(image):
            self.update_signal.emit(image)

        algoritmoGenetico(update_callback=update_callback)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/main_window.ui', self)
        self.startButton.clicked.connect(self.startButtonClicked)
        self.uploadImageButton.clicked.connect(self.uploadImageButtonClicked)
        self.finishButton.clicked.connect(self.finishButtonClicked)

        self.genetic_thread = GeneticAlgorithmThread()
        self.genetic_thread.update_signal.connect(self.updateImage)
    def uploadImageButtonClicked(self):
        imagePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        print(imagePath)
        if imagePath:
            self.targetImageLabel.setPixmap(QPixmap(imagePath))
            self.targetImageLabel.setScaledContents(True)

    def updateImage(self, image):
        height, width, channel = image.shape
        bytesPerLine = 3 * width
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setScaledContents(True)
                    

    def startButtonClicked(self):
        if not self.genetic_thread.isRunning():
            self.genetic_thread.start()
    
    def finishButtonClicked(self):
        print('Finish Button Clicked')




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')
# En main.py
