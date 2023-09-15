import random
import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim

# Define the number of points (p), maximum radius, width, and height
p = 10000
n = 5
m = 50
radius = 5
tasaMutacion = 0.1  # Tasa de mutación (ajusta según sea necesario)
population = []
images = []

# Ruta de la imagen
path_img = 'Test2.jpg'
# Leer la imagen
img = cv2.imread(path_img)

height, width, _ = img.shape
print('height ', height)
print('width ', width)

# Funcion de evalucion de la poblacion
def evaluacionPoblacion():
    max = 0
    best = 0
    for i in range(len(images)):
        percentage = fitness(images[i])
        if(percentage > max):
            max = percentage
            best = i
    return best

# Gen de la población
class Point:
    def __init__(self, radius, red, green, blue, x, y):
        self.radius = radius
        self.red = red
        self.green = green
        self.blue = blue
        self.x = x
        self.y = y

    def __str__(self):
        return f"Punto {self.x}, {self.y} (Rojo={self.red}, Verde={self.green}, Azul={self.blue}) radio {self.radius}"

    def set_radius(self, new_radius):
        self.radius = new_radius

    def set_red(self, new_red):
        self.red = new_red

    def set_green(self, new_green):
        self.green = new_green

    def set_blue(self, new_blue):
        self.blue = new_blue

    def set_x(self, new_x):
        self.x = new_x

    def set_y(self, new_y):
        self.y = new_y

# Generamos las listas con los puntos, de forma aleatoria.
def generate_population(array_points):
  for i in range(p):
    array_points.append(
      Point(
          radius = radius,
          x = random.randint(0, width),
          y = random.randint(0, height),
          red = random.randint(0, 255),
          green = random.randint(0, 255),
          blue = random.randint(0, 255)
          )
    )
  return array_points

# Meter poblacion inicial
def poblacionInicial():
    for i in range(n) :
        population.append(generate_population([]))

# Leemos los puntos realizados
def read_points(array):
  for point in array:
      print(point)

# Lista con las imagenes generadas de los Points, generados.
def generate_images(population):
  for i in range(len(population)):
    # Crea una imagen en blanco
    new_img = np.zeros((height, width, 3), dtype=np.uint8)

    # Dibuja los puntos en la imagen
    for point in population[i]:
        color = tuple((int(point.blue), int(point.green), int(point.red)))  # OpenCV usa BGR en lugar de RGB
        cv2.circle(new_img, (point.x, point.y), point.radius, color, -1)  # Dibuja un círculo lleno
    images.append(new_img)
  return images

# Calcular el fitness del similitud de las imagenes
def fitness(image):
  # Imagen original
  img_grace1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  # Imagen a testear
  img_grace2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  index_ssim = ssim(img_grace1, img_grace2)
  percentage = index_ssim * 100
  #print('percentage: ', percentage)
  return percentage

# Sacar los n padres 
def seleccionPadres(population):
    totalFitness = 0
    probabilidades = []
    listaFitness = []
    # Calcular fitness total
    for i in range(len(images)):
        individuoFitness = fitness(images[i])
        totalFitness += individuoFitness
        listaFitness.append(individuoFitness)
    # Calcular probabilidad de cada individuo 
    for i in listaFitness:
        probabilidad = i / totalFitness
        probabilidades.append(probabilidad)
    # Sacar de forma aleatoria los padres
    padres = []
    for i in range(len(population)):
         # Seleccionar un padre aleatoriamente usando las probabilidades calculadas
        padre = random.choices(population, weights=probabilidades)[0]
        padres.append(padre)
    return padres

# Función para realizar el crossover entre dos padres y crear un gen de hijo
def crossover(padre1, padre2):
    # Tomar el promedio de los valores de los padres.
    hijo_radius = radius
    hijo_x = int((padre1.x + padre2.x) / 2)
    hijo_y = int((padre1.y + padre2.y) / 2)
    hijo_red = int((padre1.red + padre2.red) / 2)
    hijo_green = int((padre1.green + padre2.green) / 2)
    hijo_blue = int((padre1.blue + padre2.blue) / 2)
    # Crear un nuevo punto (hijo) con los valores combinados
    hijo = Point(hijo_radius, hijo_red, hijo_green, hijo_blue, hijo_x, hijo_y)
    return hijo

# Creamos los nuevos hijo
def crearHijos(padres):
    newPopulation = []
    newChild = []
    for i in range(n):
        # Seleccionar dos padres aleatorios
        padre1 = random.choice(padres)
        padre2 = random.choice(padres)
        for y in range(p):
            newPoint = crossover(padre1[y],padre2[y])
            newChild.append(newPoint)
        newPopulation.append(newChild)
        newChild = []
    return newPopulation

import random

# Función de mutación para un punto
def mutate_point(point, mutation_rate):
    if random.random() < mutation_rate:
        # Realizar una mutación en el componente rojo del color (cambiar su valor)
        point.set_red(random.randint(0, 255))
    
    if random.random() < mutation_rate:
        # Realizar una mutación en el componente verde del color (cambiar su valor)
        point.set_green(random.randint(0, 255))
    
    if random.random() < mutation_rate:
        # Realizar una mutación en el componente azul del color (cambiar su valor)
        point.set_blue(random.randint(0, 255))
    
    if random.random() < mutation_rate:
        # Realizar una mutación en las coordenadas x e y (mover el punto)
        point.set_x(int(point.x + random.uniform(-1, 1)))
        point.set_y(int(point.y + random.uniform(-1, 1)))

# Mutar a la pobalcion nueva
def mutacionPoblacion(newPopulation, mutation_rate):
    for individuo in newPopulation:
        if random.random() < mutation_rate:
            for y in range(p):
                mutate_point(individuo[y], mutation_rate)
    return newPopulation

def algoritmoGenetico():
    global population, images
    poblacionInicial()
    for i in range(1000):
        generate_images(population)
        best = evaluacionPoblacion()
        padres = seleccionPadres(population)
        newPopulation = crearHijos(padres)
        newPopulation = mutacionPoblacion(newPopulation, tasaMutacion)
        population = newPopulation
        images = []
        print(i)
    plt.imshow(cv2.cvtColor(images[best], cv2.COLOR_BGR2RGB))  # Convierte de BGR a RGB
    plt.axis('off')  # Oculta los ejes
    plt.show()
    #generate_images(population)
    #best = evaluacionPoblacion()
    #padres = seleccionPadres(population)
    #newPopulation = crearHijos(padres)
    #newPopulation = mutacionPoblacion(newPopulation, tasaMutacion)
    #population = newPopulation
    #for i in population:
    #    read_points(i)
    
algoritmoGenetico()
