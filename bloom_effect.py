# Ignacio Díaz Lara
# Modelación y Computación Gráfica para Ingenier@s
#
# Esto programa recibe una imagen y difumina un color según la ecuación de la luz.
# Recibe nombre de la imagen, un N de distancia del difuminado, y los números R, G y B
# que representan el color a difuminar.
# Crea una archivo con la imagen difuminada.

import sys
import PIL
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve

if __name__ == "__main__":

    # Recolectar variables de la llamada

    Nn = int(sys.argv[2])  # N pixeles de distancia de alcance del difuminado

    # Valores de colores en codificación RGB
    R = int(sys.argv[3])
    G = int(sys.argv[4])
    B = int(sys.argv[5])
    image = sys.argv[1]  # Nombre de la imagen

    # Abrir la imagen con PIL y pasarla a un arreglo de numpy
    img = Image.open(image)
    I = np.asarray(PIL.Image.open(image))

    # Varibles de tamaño de la imagen
    H = len(I) - 1  # ancho o cantidad de pixeles verticalmente
    W = len(I[0]) - 1  # alto o cantidad de pixeles horizontalmente
    N = H * W  # cantidad de pixeles

    # Diccionarios que serán de utilidad para guardar coordenadas de la imagen
    D1 = {}  # Guarda el número de aparición de la incógnita como valor y con clave su coordenada
    D2 = {}  # Guarda la coordenada de la incógnita como valor y con clave el número de aparición
    D3 = {}  # Guarda las coordenadas que coinciden con el valor de RGB que se quiere difuminar (como clave)

    count = 0  # Cuenta la cantidad incógnitas que se encuentran

    # Iterar por toda la matriz para encontrar los valores que coincidan con el color que queremos difuminar
    # y establecer las incógnitas
    for i in range(0, H):  # Recorrer el alto
        for j in range(0, W):  # Recorrer el ancho
            # Encontrar el color que se busca difuminar
            if I[i][j][0] == R and I[i][j][1] == G and I[i][j][2] == B:
                D3[(i, j)] = 1  # Guarda la coordenada en D3. Dado que no se usa el valor, podría cambiarse a una lista

                # Busca todas las combinaciones que estén dentro de la distancia de difusión establecida
                # y guarda las incógnitas
                for n in range(0, Nn + 1):
                    for m in range(0, Nn + 1):

                        # Variables que tiene las coordenadas ya establecidas como incógnitas para no duplicar
                        dict_keys = D2.keys()

                        # Cada uno de los siguientes ifs chequea que la coordenada que intenta determinar como incógnita
                        # esté dentro de la imagen, que no haya sido registrada ya como incógnita, que esté a una
                        # distancia de radio Nn de la coordenada (i,j) y que no tenga el color que se busca difuminar
                        if n ** 2 + m ** 2 <= Nn ** 2:
                            # Busca incógnitas en el cuadrante superior izquierdo
                            # (tomando como origen la coordenada (i,j))
                            if H >= i - n >= 0 and W >= j - m >= 0 and not (i - n, j - m) in dict_keys \
                                    and (I[i - n][j - m][0] != R or I[i - n][j - m][1] != G or I[i - n][j - m][2] != B):
                                D1[count] = (i - n, j - m)
                                D2[(i - n, j - m)] = count
                                count += 1

                            # Busca incógnitas en el cuadrante inferior izquierdo
                            # (tomando como origen la coordenada (i,j))
                            if H >= i - n >= 0 and W >= j + m >= 0 and not (i - n, j + m) in dict_keys \
                                    and (I[i - n][j + m][0] != R or I[i - n][j + m][1] != G or I[i - n][j + m][2] != B):
                                D1[count] = (i - n, j + m)
                                D2[(i - n, j + m)] = count
                                count += 1

                            # Busca incógnitas en el cuadrante superior derecho
                            # (tomando como origen la coordenada (i,j))
                            if H >= i + n >= 0 and W >= j - m >= 0 and not (i + n, j - m) in dict_keys \
                                    and (I[i + n][j - m][0] != R or I[i + n][j - m][1] != G or I[i + n][j - m][2] != B):
                                D1[count] = (i + n, j - m)
                                D2[(i + n, j - m)] = count
                                count += 1

                            # Busca incógnitas en el cuadrante inferior izquierdo
                            # (tomando como origen la coordenada (i,j))
                            if H >= i + n >= 0 and W >= j + m >= 0 and not (i + n, j + m) in dict_keys \
                                    and (I[i + n][j + m][0] != R or I[i + n][j + m][1] != G or I[i + n][j + m][2] != B):
                                D1[count] = (i + n, j + m)
                                D2[(i + n, j + m)] = count
                                count += 1

    # Crear la matriz sparse que tendrá los coeficientes de las incógnitas en las ecuaciones a resolver
    A = csc_matrix((count, count))  # A = np.zeros((count, count))
    # Crear los Vectores que tendrán los resultados de las ecuaciones a resolver
    B1 = np.zeros((count,))
    B2 = np.zeros((count,))
    B3 = np.zeros((count,))

    # Por cada coordenada guardad como incógnita se crea el stencil de 5 puntos para resolver la EDP
    for (a, b) in D2:
        # Centro del stencil de 5 puntos
        A[D2[(a, b)], D2[(a, b)]] = -4.0

        dict_keys = D2.keys()  # lista de coordenadas de las incógnitas
        dict_keys2 = D3.keys()  # lista de coordenadas de los pixeles que tienen el color que se quiere difuminar

        # A la derecha del stencil de 5 puntos
        if (a + 1, b) in dict_keys:
            A[D2[(a, b)], D2[(a + 1, b)]] = 1.0  # se agrega el coeficiente en caso que sea una incógnita

        # A la izquierda del stencil de 5 puntos
        if (a - 1, b) in dict_keys:
            A[D2[(a, b)], D2[(a - 1, b)]] = 1.0  # se agrega el coeficiente en caso que sea una incógnita

        # Abajo en el stencil de 5 puntos
        if (a, b + 1) in dict_keys:
            A[D2[(a, b)], D2[(a, b + 1)]] = 1.0  # se agrega el coeficiente en caso que sea una incógnita

        # Arriba en el stencil de 5 puntos
        if (a, b - 1) in dict_keys:
            A[D2[(a, b)], D2[(a, b - 1)]] = 1.0  # se agrega el coeficiente en caso que sea una incógnita

        # En el caso que uno de los puntos del stencil sea una coordenada del color que se busca difuminar
        # se le resta el color los vectores b de soluciones en la fila que corresponde
        if (a + 1, b) in dict_keys2 or (a, b - 1) in dict_keys2 or (a, b + 1) in dict_keys2 or (a - 1, b) in dict_keys2:
            B1[D2[(a, b)]] = - R
            B2[D2[(a, b)]] = - G
            B3[D2[(a, b)]] = - B

    # Resolver los sistemas de ecuaciones, uno por cada color
    # Con matrices sparse  # Sin matrices sparse
    x1 = spsolve(A, B1)    # x1 = np.linalg.solve(A, B1)
    x2 = spsolve(A, B2)    # x2 = np.linalg.solve(A, B2)
    x3 = spsolve(A, B3)    # x3 = np.linalg.solve(A, B3)

    # Generar una copia de la matriz para poder modificarla
    I2 = I.copy()

    # Sumar los resultados por color con la matriz copiada. Con un mínimo para no pasarse del máximo color aceptado
    for i in range(0, count):
        I2[D1[i]][0] = min(I2[D1[i]][0] + x1[i], 255)
        I2[D1[i]][1] = min(I2[D1[i]][1] + x2[i], 255)
        I2[D1[i]][2] = min(I2[D1[i]][2] + x3[i], 255)

    # Descomentar para visualizar
    # imgplot = plt.imshow(I2)
    # plt.show()

    # Pasar la matriz a imagen
    Ifinal = PIL.Image.fromarray(np.uint8(I2))
    if '.png' in image:
        # Quitar a extensión del archivo
        image = image.replace('.png', '')
        # Guardar la imagen con el nombre original finalizado con un '_out.jpg'
        Ifinal = Ifinal.save(image + "_out.png")
    else:
        # Quitar a extensión del archivo
        image = image.replace('.jpg', '')
        # Guardar la imagen con el nombre original finalizado con un '_out.jpg'
        Ifinal = Ifinal.save(image + "_out.jpg")
