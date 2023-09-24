import random
from PIL import Image,ImageDraw
import numpy as np
import matplotlib.pyplot as plt

# Funciones auxiliares:

def generar_punto_fijo(ancho_imagen, alto_imagen): # función auxiliar para generar un punto aleatorio
    x = random.randint(0, ancho_imagen - 1) 
    y = random.randint(0, alto_imagen - 1)
    radio =3
    return (x, y, radio) # devuelve una tupla con las coordenadas del punto

def generar_poblacion_secuencial(tam_poblacion, num_puntos, ancho_imagen, alto_imagen): # función auxiliar para generar una población inicial
    distancia = int(np.sqrt(ancho_imagen * alto_imagen / num_puntos)) # distancia entre puntos
    poblacion = [] # lista de individuos
 
    for _ in range(tam_poblacion): # para cada individuo
        individuo = [] # lista de puntos
        for x in range(0, ancho_imagen, distancia): # para cada punto
            for y in range(0, alto_imagen, distancia): # para cada punto
                punto = (x, y, 3)  # genera un punto aleatorio
                color = color_aleatorio() # genera un color aleatorio
                individuo.append((punto, color)) # añade el punto y el color a la lista de puntos
        poblacion.append(individuo) # añade el individuo a la población

    return poblacion # devuelve la población

def color_aleatorio(): # función auxiliar para generar un color aleatorio
    r = random.randint(0, 255) 
    g = random.randint(0, 255) 
    b = random.randint(0, 255)
    return (r, g, b) # devuelve una tupla con los valores RGB


def generar_individuo(num_puntos, ancho_imagen, alto_imagen): # función auxiliar para generar un individuo
    puntos_fijos = [generar_punto_fijo(ancho_imagen, alto_imagen) for _ in range(num_puntos)] # genera una lista de puntos aleatorios
    colores = [color_aleatorio() for _ in range(num_puntos)] # genera una lista de colores aleatorios
    return list(zip(puntos_fijos, colores)) # devuelve una lista de tuplas con los puntos y los colores

def generar_poblacion(tam_poblacion, num_puntos, ancho_imagen, alto_imagen): # función auxiliar para generar una población inicial
    return [generar_individuo(num_puntos, ancho_imagen, alto_imagen) for _ in range(tam_poblacion)] # devuelve una lista de individuos

def individuo_a_imagen(individuo, ancho_imagen, alto_imagen): # función auxiliar para convertir un individuo en una imagen
    imagen = Image.new('RGB', (ancho_imagen, alto_imagen)) # crea una imagen en blanco
    draw = ImageDraw.Draw(imagen) # crea un objeto para dibujar sobre la imagen
    #fondo blanco 
    for punto_fijo, color in individuo: # para cada punto y color del individuo
        x, y, radio = punto_fijo # extrae las coordenadas y el radio del punto
        draw.ellipse([(x-radio, y-radio), (x+radio, y+radio)], fill=color) # dibuja un círculo en la imagen
    return imagen # devuelve la imagen

def calcular_fitness_envoltura(args): # función auxiliar para calcular el fitness de un individuo
    return fitness(*args) # devuelve el fitness del individuo

def calcular_diferencia(imagen1, imagen2): # función auxiliar para calcular la diferencia entre dos imágenes
    # Convertir las imágenes a arrays de numpy
    arr1 = np.asarray(imagen1) 
    arr2 = np.asarray(imagen2)
    diferencia = np.sum(np.abs(arr1 - arr2)) # calcular la diferencia entre los arrays
    return diferencia   # devuelve la diferencia

def fitness(individuo, imagen_objetivo): # función auxiliar para calcular el fitness de un individuo
    imagen_generada = individuo_a_imagen(individuo, *imagen_objetivo.size) # convierte el individuo en una imagen
    return calcular_diferencia(imagen_generada, imagen_objetivo) # devuelve la diferencia entre la imagen generada y la imagen objetivo

def seleccion_torneo(poblacion, imagen_objetivo, tam_torneo=3): # función auxiliar para seleccionar un individuo mediante torneo
    seleccionados = random.sample(poblacion, tam_torneo) # selecciona aleatoriamente un subconjunto de la población
    seleccionados.sort(key=lambda ind: fitness(ind, imagen_objetivo)) # ordena los individuos del subconjunto por su fitness
    return seleccionados[0] # devuelve el individuo con menor fitness

def cruzar(padre1, padre2): # función auxiliar para cruzar dos individuos
    punto_corte = random.randint(0, len(padre1)) # elige un punto de corte aleatorio
    hijo1 = padre1[:punto_corte] + padre2[punto_corte:] # crea el primer hijo
    hijo2 = padre2[:punto_corte] + padre1[punto_corte:] # crea el segundo hijo
    return hijo1, hijo2 # devuelve los dos hijos

def mutar(individuo, probabilidad_mutacion): # función auxiliar para mutar un individuo
    if random.random() < probabilidad_mutacion:  # si se cumple la probabilidad de mutación
        indice = random.randint(0, len(individuo) - 1) # elige un punto de corte aleatorio
        _, color_actual = individuo[indice] # extrae el color del punto
        nuevo_color = color_aleatorio() # genera un nuevo color aleatorio
        if color_actual != nuevo_color: # si el color es distinto
            individuo[indice] = (individuo[indice][0], nuevo_color) # cambia el color del punto

def algoritmo_genetico( imagen_objetivo_path, tam_poblacion, num_puntos,
                        num_generaciones, 
                        probabilidad_mutacion, tam_torneo,update_callback=None, 
                        generation_callback=None): # función principal del algoritmo genético
    print(probabilidad_mutacion)
    print(tam_torneo)
    print(num_generaciones)
    imagen_objetivo = Image.open(imagen_objetivo_path) # abre la imagen objetivo
    ancho_imagen, alto_imagen = imagen_objetivo.size # extrae el ancho y el alto de la imagen objetivo

    poblacion  = generar_poblacion_secuencial(tam_poblacion, num_puntos, ancho_imagen, alto_imagen) # genera una población inicial


    mejor_individuo = min(poblacion, key=lambda ind: fitness(ind, imagen_objetivo)) # encuentra el individuo con menor fitness
    mejor_fitness = fitness(mejor_individuo, imagen_objetivo) # calcula el fitness del mejor individuo
    generacion = 0  # Introduce una variable para contar las generaciones



    #infinito loop
    while True:
        nueva_poblacion = [] # crea una nueva población vacía

        while len(nueva_poblacion) < tam_poblacion: # mientras la nueva población no esté llena
            padre1 = seleccion_torneo(poblacion, imagen_objetivo, tam_torneo) # selecciona el primer padre
            padre2 = seleccion_torneo(poblacion, imagen_objetivo, tam_torneo) # selecciona el segundo padre

            hijo1, hijo2 = cruzar(padre1, padre2) # cruza los padres para crear dos hijos

            mutar(hijo1, probabilidad_mutacion) # muta los hijos
            mutar(hijo2, probabilidad_mutacion) # muta los hijos

            nueva_poblacion.append(hijo1) # añade los hijos a la nueva población
            nueva_poblacion.append(hijo2) # añade los hijos a la nueva población

        poblacion = nueva_poblacion # la nueva población pasa a ser la población actual

        individuo_actual = min(poblacion, key=lambda ind: fitness(ind, imagen_objetivo)) # encuentra el individuo con menor fitness
        fitness_actual = fitness(individuo_actual, imagen_objetivo) # calcula el fitness del mejor individuo

        if fitness_actual < mejor_fitness: # si el fitness del mejor individuo es menor que el fitness del mejor individuo hasta ahora
            mejor_fitness = fitness_actual # actualiza el fitness del mejor individuo
            mejor_individuo = individuo_actual # actualiza el mejor individuo



        if generacion % 5 == 0:  # cada 5 generaciones
            resultado_temp_np = np.array(individuo_a_imagen(individuo_actual, ancho_imagen, alto_imagen)) # convierte el individuo en una imagen
            if update_callback: # si se ha pasado una función de callback
                update_callback(resultado_temp_np) # llama a la función de callback

        if generation_callback: 
            generation_callback(generacion, mejor_fitness) # llama a la función de callback

        generacion += 1  # Incrementa la cuenta de generaciones



