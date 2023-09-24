import sys
from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt6.QtCore import QFile, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from PyQt6 import uic
from algoritmoGenetico import algoritmo_genetico
import numpy as np


class GeneticAlgorithmThread(QThread): # Clase para ejecutar el algoritmo genético en un hilo
    update_signal = pyqtSignal(np.ndarray) # Señal para actualizar la imagen
    generation_signal = pyqtSignal(int, float)  # Señal para las generaciones y el fitness


    def __init__(self, population_size,mutation_rate,tournament_size,num_puntos,image_path): # Constructor de la clase
        super().__init__() # Inicializar la clase padre
        self.population_size = population_size # Tamaño de la población
        self.image_path = image_path # Ruta de la imagen
        self.mutation_rate = mutation_rate  # Probabilidad de mutación
        self.tournament_size = tournament_size  # Nuevo valor para el tamaño del torneo
        self.num_puntos = num_puntos  # Nuevo valor para el número de puntos


    def run(self): # Función que se ejecuta al iniciar el hilo
        algoritmo_genetico(self.image_path, self.population_size, self.num_puntos, 20000, self.mutation_rate, self.tournament_size, update_callback=self.updateImageSignal, generation_callback=self.updateGenerationSignal)
        

    def updateImageSignal(self, image): # Función para emitir la señal de actualización de la imagen
        self.update_signal.emit(image) # Emitir la señal de actualización de la imagen

    def updateGenerationSignal(self, generation, fitness):
        self.generation_signal.emit(generation, fitness)



class MainWindow(QWidget): #  Clase para la ventana principal
    def __init__(self): # Constructor de la clase
        super().__init__() # Inicializar la clase padre
        uic.loadUi('ui/main_window.ui', self) # Cargar la interfaz gráfica desde el archivo .ui
        

        self.populationSlider = self.horizontalSlider_2   # Slider para el tamaño de la población
        self.populationSlider.valueChanged.connect(self.sliderValueChanged) # Conectar la señal de cambio de valor del slider a la función sliderValueChanged
        self.label_5.setText(str(self.populationSlider.value())) # Mostrar el valor del slider en un QLabel
        self.image_path = "" # Ruta de la imagen


        self.mutationRateSlider = self.horizontalSlider_3 # Slider para la probabilidad de mutación
        self.mutationRateSlider.valueChanged.connect(self.mutationSliderValueChanged) # Conectar la señal de cambio de valor del slider a la función mutationSliderValueChanged
        self.label_6.setText(str(self.mutationRateSlider.value() / 100.0)) # Mostrar el valor del slider en un QLabel

        self.tournamentSizeSlider = self.horizontalSlider     # Slider para el tamaño del torneo
        self.tournamentSizeSlider.valueChanged.connect(self.tournamentSliderValueChanged)       
        self.label_7.setText(str(self.tournamentSizeSlider.value()))  # Mostrar el valor del slider en un QLabel
        
        self.pointsSlider = self.horizontalSlider_4  
        self.pointsSlider.valueChanged.connect(self.pointsSliderValueChanged)
        self.label_8.setText(str(self.pointsSlider.value())) 
        
        self.generationLabel = self.genlabel
        self.fitnessLabel = self.label_10
        



        self.startButton.clicked.connect(self.startButtonClicked) # Conectar el botón de inicio a la función startButtonClicked
        self.uploadImageButton.clicked.connect(self.uploadImageButtonClicked) # Conectar el botón de subir imagen a la función uploadImageButtonClicked
        self.finishButton.clicked.connect(self.finishButtonClicked) # Conectar el botón de finalizar a la función finishButtonClicked

        self.genetic_thread = GeneticAlgorithmThread(self.populationSlider.value(), self.mutationRateSlider.value() / 100.0, self.tournamentSizeSlider.value(), self.pointsSlider.value(), self.image_path)
        self.genetic_thread.update_signal.connect(self.updateImage) # Conectar la señal de actualización de la imagen a la función updateImage

    def uploadImageButtonClicked(self): # Función para manejar el click en el botón de subir imagen
        imagePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)") # Abrir un diálogo para seleccionar una imagen
        if imagePath: # Si se ha seleccionado una imagen
            self.targetImageLabel.setPixmap(QPixmap(imagePath)) # Mostrar la imagen en un QLabel
            self.targetImageLabel.setScaledContents(True) # Escalar la imagen para que se ajuste al tamaño del QLabel
            self.image_path = imagePath  # Guardar la ruta de la imagen
            

    def updateImage(self, image):   # Función para actualizar la imagen
        height, width, channel = image.shape # Extraer el alto, el ancho y el número de canales de la imagen
        bytesPerLine = 3 * width # Calcular el número de bytes por línea
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format.Format_RGB888) # Crear una QImage a partir de la imagen
        pixmap = QPixmap.fromImage(qImg) # Crear un QPixmap a partir de la QImage
        self.imageLabel.setPixmap(pixmap) # Mostrar la imagen en un QLabel
        self.imageLabel.setScaledContents(True) # Escalar la imagen para que se ajuste al tamaño del QLabel

    def startButtonClicked(self): # Función para manejar el click en el botón de inicio
        if not self.genetic_thread.isRunning(): # Si el hilo no está ejecutándose
            population_size = self.populationSlider.value() # Tamaño de la población
            mutation_rate = self.mutationRateSlider.value() / 100.0 # Probabilidad de mutación
            tournament_size = self.tournamentSizeSlider.value() # Nuevo valor para el tamaño del torneo
            num_puntos = self.pointsSlider.value()

            self.genetic_thread = GeneticAlgorithmThread(population_size, mutation_rate, tournament_size, num_puntos, self.image_path)
            self.genetic_thread.update_signal.connect(self.updateImage) # Conectar la señal de actualización de la imagen a la función updateImage
            self.genetic_thread.generation_signal.connect(self.updateGenerationLabel)
            self.genetic_thread.start() # Iniciar el hilo

    def updateGenerationLabel(self, generation,fitness):
        self.generationLabel.setText(f"Generación: {generation}")
        self.fitnessLabel.setText(f"Mejor Fitness: {fitness}")



    def finishButtonClicked(self):
        print('Finish Button Clicked')

    def sliderValueChanged(self): # Función para manejar el cambio de valor en el slider de tamaño de la población
        value = self.populationSlider.value() # Valor del slider
        self.label_5.setText(str(value)) # Mostrar el valor del slider en un QLabel
        self.genetic_thread.population_size = value # Actualizar el tamaño de la población en el hilo

    def mutationSliderValueChanged(self): # Función para manejar el cambio de valor en el slider de probabilidad de mutación
        mutation_value = self.mutationRateSlider.value() / 100.0 # Valor del slider
        self.label_6.setText(str(mutation_value)) # Mostrar el valor del slider en un QLabel
        self.genetic_thread.mutation_rate = mutation_value # Actualizar la probabilidad de mutación en el hilo 

    def tournamentSliderValueChanged(self):
        tournament_value = self.tournamentSizeSlider.value()
        self.label_7.setText(str(tournament_value))
        self.genetic_thread.tournament_size = tournament_value
    def pointsSliderValueChanged(self):
        points_value = self.pointsSlider.value()
        self.pointsLabel.setText(str(points_value))
        self.genetic_thread.num_puntos = points_value


if __name__ == '__main__': # Función principal
    app = QApplication(sys.argv) # Crear una aplicación
    window = MainWindow() # Crear una ventana
    window.show() # Mostrar la ventana
    try: 
        sys.exit(app.exec()) # Ejecutar la aplicación
    except SystemExit:
        print('Closing Window...')
