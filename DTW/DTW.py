from matplotlib.patches import ConnectionPatch
import matplotlib.pyplot as plt
import numpy as np
import scipy.spatial.distance as dist


def plot_inicial(x, y):
    plt.figure(figsize=(6, 4))
    plt.plot(np.arange(x.shape[0]), x + 1.5, "-o", c="C3")
    plt.plot(np.arange(y.shape[0]), y - 1.5, "-o", c="C0")
    plt.axis("off")
    plt.savefig("fig/signals_a_b.pdf")

def plot_final(path, cost_mat, dist_mat):
    plt.figure(figsize=(6, 4))
    plt.subplot(121)
    plt.title("Distance matrix")
    plt.imshow(dist_mat, cmap=plt.cm.binary, interpolation="nearest", origin="lower")
    plt.subplot(122)
    plt.title("Cost matrix")
    plt.imshow(cost_mat, cmap=plt.cm.binary, interpolation="nearest", origin="lower")
    x_path, y_path = zip(*path)
    plt.plot(y_path, x_path)
    plt.savefig("fig/cost_distance_matrix.pdf")

    plt.figure()
    
    for x_i, y_j in path:
        plt.plot([x_i, y_j], [x[x_i] + 1.5, y[y_j] - 1.5], c="C7")
    plt.plot(np.arange(x.shape[0]), x + 1.5, "-o", c="C3")
    plt.plot(np.arange(y.shape[0]), y - 1.5, "-o", c="C0")
    plt.axis("off")
    plt.savefig("fig/signals_a_b_align.pdf")
    

def calculo_distancia(x, y):
    # Distance matrix
    N = x.shape[0]
    M = y.shape[0]
    dist_mat = np.zeros((N, M))
    for i in range(N):
        for j in range(M):
            dist_mat[i, j] = abs(x[i] - y[j])
    return dist_mat


def dp(x, y):
    dist_mat = calculo_distancia(x, y)

    N, M = dist_mat.shape
    
    cost_mat = np.zeros((N + 1, M + 1))
    for i in range(1, N + 1):
        cost_mat[i, 0] = np.inf
    for i in range(1, M + 1):
        cost_mat[0, i] = np.inf

    traceback_mat = np.zeros((N, M)) #Almacenamos la dirección a la que ira cada casilla (la de menor coste). Se almacena un 0 (abajo izquierda), 1 (abajo) o 2 (izquierda)
    for i in range(N):
        for j in range(M):
            penalty = [
                cost_mat[i, j],      # match (0)
                cost_mat[i, j + 1],  # insertion (1)
                cost_mat[i + 1, j]]  # deletion (2)
            i_penalty = np.argmin(penalty)
            cost_mat[i + 1, j + 1] = dist_mat[i, j] + penalty[i_penalty]
            traceback_mat[i, j] = i_penalty

    # Traceback from bottom right
    #Inicializamos los indices a la esquina superior derecha de la matriz
    i = N - 1
    j = M - 1
    path = [(i, j)] #Añadiremos las coordenadas del camino a seguir
    while i > 0 or j > 0:
        tb_type = traceback_mat[i, j]  #Por cada coordenada en la que nos situemos veremos cual es la dirección a la que debemos ir
        if tb_type == 0:
            # Match
            i = i - 1
            j = j - 1
        elif tb_type == 1:
            # Insertion
            i = i - 1
        elif tb_type == 2:
            # Deletion
            j = j - 1
        path.append((i, j))

    # Strip infinity edges from cost_mat before returning
    cost_mat = cost_mat[1:, 1:]
    return (path[::-1], cost_mat, dist_mat)


def DTW(x, y):
    plot_inicial(x, y)

    path, cost_mat, dist_mat = dp(x, y)
    N, M = cost_mat.shape
    print("Alignment cost: {:.4f}".format(cost_mat[N - 1, M - 1]))
    print("Normalized alignment cost: {:.4f}".format(cost_mat[N - 1, M - 1]/(N + M)))

    plot_final(path, cost_mat, dist_mat)


if __name__ == '__main__':
    #EJEMPLO
    x = np.array([0, 0, 1, 1, 0, 0, -1, 0, 0, 0, 0])
    y = np.array([0, 0, 0, 0, 1, 1, 0, 0, 0, -1, -0.5, 0, 0])

    # DTW
    DTW(x, y)

