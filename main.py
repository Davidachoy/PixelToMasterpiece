import sys
from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt6.QtCore import QFile, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from PyQt6 import uic
from algoritmoGenetico import algoritmo_genetico
import cv2
import numpy as np


class GeneticAlgorithmThread(QThread):
    update_signal = pyqtSignal(np.ndarray)

    def __init__(self, population_size,image_path):
        super().__init__()
        self.population_size = population_size
        self.image_path = image_path


    def run(self):
        algoritmo_genetico(self.image_path, self.population_size, 1000, 20000, 0.1, 3, update_callback=self.updateImageSignal)

    def updateImageSignal(self, image):
        self.update_signal.emit(image)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/main_window.ui', self)
        
        # Suponiendo que el slider se llama 'populationSlider' en tu archivo .ui
        self.populationSlider = self.horizontalSlider_2  
        self.populationSlider.valueChanged.connect(self.sliderValueChanged)
        self.label_5.setText(str(self.populationSlider.value()))
        self.image_path = ""  # O la ruta de una imagen por defecto



        self.startButton.clicked.connect(self.startButtonClicked)
        self.uploadImageButton.clicked.connect(self.uploadImageButtonClicked)
        self.finishButton.clicked.connect(self.finishButtonClicked)

        self.genetic_thread = GeneticAlgorithmThread(self.populationSlider.value(), self.image_path)
        self.genetic_thread.update_signal.connect(self.updateImage)

    def uploadImageButtonClicked(self):
        imagePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if imagePath:
            self.targetImageLabel.setPixmap(QPixmap(imagePath))
            self.targetImageLabel.setScaledContents(True)
            self.image_path = imagePath  # Guardar la ruta de la imagen

    def updateImage(self, image):
        height, width, channel = image.shape
        bytesPerLine = 3 * width
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setScaledContents(True)

    def startButtonClicked(self):
        if not self.genetic_thread.isRunning():
            population_size = self.populationSlider.value()
            self.genetic_thread = GeneticAlgorithmThread(population_size, self.image_path)
            self.genetic_thread.update_signal.connect(self.updateImage)
            self.genetic_thread.start()

    def finishButtonClicked(self):
        print('Finish Button Clicked')

    def sliderValueChanged(self):
        value = self.populationSlider.value()
        # Si quieres realizar acciones adicionales al mover el slider, hazlo aquí. 
        # Por ejemplo, mostrar el valor en un QLabel.
        self.label_5.setText(str(value))

        print(f"Population Size set to: {value}")
        # Actualizar el tamaño de la población en el hilo antes de empezarlo
        self.genetic_thread.population_size = value


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')
