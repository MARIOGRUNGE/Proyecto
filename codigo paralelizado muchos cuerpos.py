#Nota de Brayan: la implementacion de muchos cuerpos la hice  en el secuencial y funciona, y como el secuencial y el paralelo arrojan las mismas trayectorias que se puede probar con poquitos cuerpos  entonces eso quiere decir que el codigo funciona, el problema es que si se corre con muchos cuerpos y mucho tiempo va a tardar una eternidad, pero lo paralelicé como dijo y lo mejor que pude :v #

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
from multiprocessing import Pool
from multiprocessing import Manager
numero_planetas = 8
numero_asteroides = 0
n_cuerpos = numero_planetas + numero_asteroides + 1

entidades_orbitales = np.zeros( ( numero_planetas+1 , 7) )

# el sol será la primera entidad orbital
# se pone lo de los asteroides por si acaso

entidades_orbitales[0, :] = np.array([ 0.0,0.0,0.0,        0.0,0.0,0.0,      1.989e30 ]) # un cuerpo similar al sol
entidades_orbitales[1, :] = np.array([ 57.909e9,0.0,0.0,   0.0,47.36e3,0.0,  0.33011e24 ]) # un cuerpo similar a mercurio
entidades_orbitales[2, :] = np.array([ 108.209e9,0.0,0.0,  0.0,35.02e3,0.0,  4.8675e24 ])  # un cuerpo similar a venus
entidades_orbitales[3, :] = np.array([ 149.596e9,0.0,0.0,  0.0,29.78e3,0.0,  5.9724e24 ])  # un cuerpo similar a la tierra
entidades_orbitales[4, :] = np.array([ 227.923e9,0.0,0.0,  0.0,24.07e3,0.0,  0.64171e24 ]) # un cuerpo similar a marte
entidades_orbitales[5, :] = np.array([ 778.570e9,0.0,0.0,  0.0,13e3,0.0,     1898.19e24 ]) # un cuerpo similar a jupiter
entidades_orbitales[6, :] = np.array([ 1433.529e9,0.0,0.0, 0.0,9.68e3,0.0,   568.34e24 ])  # un cuerpo similar a saturno
entidades_orbitales[7, :] = np.array([ 2872.463e9,0.0,0.0, 0.0,6.80e3,0.0,   86.813e24 ])  # un cuerpo similar a urano
entidades_orbitales[8, :] = np.array([ 4495.060e9,0.0,0.0, 0.0,5.43e3,0.0,   102.413e24 ]) # un cuerpo similar a neptuno
def generar_asteroide():
    # Suponiendo valores aleatorios para la posición, velocidad y masa del asteroide
    posicion_x = np.random.uniform(-10000e9, 10000e9)
    posicion_y = np.random.uniform(-10000e9, 10000e9)  # Agregamos coordenada y aleatoria
    velocidad_x = np.random.uniform(-100e3, 100e3)
    velocidad_y = np.random.uniform(-100e3, 100e3)  # Agregamos velocidad en el eje y aleatoria
    masa = np.random.uniform(1e15, 1e21)  # Masa en kg, asumiendo un rango para asteroides
    
    return np.array([posicion_x, posicion_y, 0.0, velocidad_x, velocidad_y, 0.0, masa])
   
# Generar 100 asteroides y agregarlos a la matriz
for i in range(9, 9 + numero_asteroides):
    entidades_orbitales = np.vstack((entidades_orbitales, generar_asteroide()))


# variables de control
t_0 = 0
t = t_0
dt = 86400 *2
t_fin = 86400 * 50  # aproximadamente una decada en segundos
G = 6.67e-11 # constante gravitacional


# truco muy chulo para graficar, temporal
trayectorias = []

def calcular_fuerzas(t, entidades_orbitales, n_cuerpos, G):   
     
     for m1 in range(n_cuerpos): # for para recorrer cada cuerpo, m1 quiere decir, indice de masa 1
        a_g = np.array([0,0,0]) # aceleración para la masa m1, cabe recordar que cada masa será tenida en cuenta, luego este vector va a representar diferentes masas a medida que el for avanza
        for m2 in range(n_cuerpos): # for para recorrer cada cuerpo, esta vez para ser la masa 2
            # recordar que acá se va a medir la "influencia" de cada cuerpo m2 en m1. m1 y m2 no pueden ser iguales
            if m2 != m1:
                
                
                vector_r = entidades_orbitales[m1, :3] - entidades_orbitales[m2, :3]
                # norma del vector dirección entre las dos masas
                mag_r = np.sqrt(np.dot(vector_r, vector_r))
                # print(mag_r)
                # cálculo de la aceleración, basicamente se omite la masa de m1
                aceleracion = (-1.0 * G * (entidades_orbitales[m2, 6])) / (mag_r**2)
                # cálculo de los vectores unitarios y las proyecciones de la aceleración
                vector_ru = vector_r / mag_r
                # acá se acumulan los valores de acelaciones, recordar que a_g es del nivel del primer for, entonces se acumulan valores para cada paso del segundo for
                a_g = a_g + aceleracion * vector_ru
                # fin del if
            # fin del segundo for
        # acá se calculan las velocidades para el paso t
        entidades_orbitales[m1, 3:6] = entidades_orbitales[m1, 3:6] + a_g * dt 
     for m1 in range(n_cuerpos):
            
        # calculo de las posiciones para el tiempo t
         entidades_orbitales[m1, :3] = entidades_orbitales[m1, :3] + entidades_orbitales[m1, 3:6] * dt        
         
     return entidades_orbitales



if __name__ == '__main__':
   
    m1= range(n_cuerpos)
    m2= range(n_cuerpos)
    
    while t < t_fin:    
        with Pool(processes=8) as pool:
        
        # Definimos una lista de tuplas que contienen los argumentos
            arguments_list = [(t, entidades_orbitales, n_cuerpos, G),]
                        
            entidades_orbitales_a = pool.starmap(calcular_fuerzas, arguments_list)
            entidades_orbitales[:] = entidades_orbitales_a[0][:]
            pool.close()
            pool.join() 
            #print(entidades_orbitales)
        
        # salvar puntos para trayectorias de los planetas y el sol. Que no se note que ya estaba cansado
        if t % (86400*10) == 0:
            for i in range(n_cuerpos):
                trayectoria_actual = [entidades_orbitales[i, 0], entidades_orbitales[i, 1]]
                trayectorias.append(trayectoria_actual)
           

             

        t += dt


trayectorias = np.array(trayectorias)    

plt.figure(figsize=(10, 6))
plt.title("Trayectorias de cuerpos en el sistema solar")
plt.xlabel("Posición X (metros)")
plt.ylabel("Posición Y (metros)")


# Trayectoria del Sol (cuerpo 0)
plt.plot(trayectorias[0::n_cuerpos, 0], trayectorias[0::n_cuerpos, 1], label="Sol", color="yellow", linewidth=2)

# Trayectorias de los planetas (cuerpos 1 al 9)
colores_planetas = ["gray", "orange", "red", "blue", "green", "cyan", "brown", "purple", "pink"]
for i in range(1, 9):
    plt.plot(trayectorias[i::n_cuerpos, 0], trayectorias[i::n_cuerpos, 1], label=f"Planeta {i}", color=colores_planetas[i - 1])

# Trayectorias de los asteroides (cuerpos 10 en adelante)
for i in range(9, n_cuerpos):
    plt.plot(trayectorias[i::n_cuerpos, 0], trayectorias[i::n_cuerpos, 1], ".", color="black", markersize=1)

plt.legend()
plt.grid(True)
plt.show()


