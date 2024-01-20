import matplotlib.pyplot as plt
import numpy as np
# Puntos de datos
import skfuzzy as fuzz

def imprimir_todas_las_graficas(values, nombres):
    timestamps = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    for i in range(0, len(values)):
        plt.plot(timestamps, values[i], marker='o', linestyle='-', label=nombres[i])
    plt.xlabel('Timestamps')
    plt.ylabel('Valores')
    plt.title('Evolución de fatiga')
    plt.legend()

    # Mostrar el gráfico
    plt.show()

import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz

def plot_fuzzy_sets():
    x = np.arange(0, 101, 1)

    mf1 = fuzz.trapmf(x, [0, 0, 15, 30])
    mf2 = fuzz.trimf(x, [15, 30, 40])
    mf3 = fuzz.trimf(x, [30, 40, 60])
    mf4 = fuzz.trapmf(x, [40, 60, 100, 100])

    plt.figure(figsize=(8, 6))
    plt.plot(x, mf1, 'darkblue', linewidth=1.5, label='15% underperform')
    plt.plot(x, mf2, 'darkgreen', linewidth=1.5, label='15-40% underperform')
    plt.plot(x, mf3, 'darkred', linewidth=1.5, label='30-60% underperform')
    plt.plot(x, mf4, 'darkcyan', linewidth=1.5, label='40-100% underperform')
    plt.title('Fuzzy Sets', fontsize=15)
    plt.xlabel('Value', fontsize=13)
    plt.ylabel('Membership', fontsize=13)
    plt.legend(loc='upper right', fontsize=10)
    plt.grid(True, color='gray', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()

# Example of use
plot_fuzzy_sets()





timestamps = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

values_miguel = [0.317, 0.0, 1.0, 0.855, 0.798, 0.845, 0.937, 0.774, 0.414, 0.529] #miguel
values_miguel_fatigado = [0.086, 0.0, 0.584, 0.785, 0.85, 0.912, 1.0, 0.942, 0.688, 0.632] #miguel con acumulacion de fatiga

values_mohamed = [0.599, 0.103, 0.046, 0.0, 0.213, 0.222, 0.976, 1.0, 0.85, 0.319] #mohamed
values_mohamed_fatigado = [0.133, 0.0, 0.054, 0.054, 0.177, 0.244, 0.713, 0.962, 1.0, 0.712] 
values_mohamed_fatigado2 = [0.006, 0.0, 0.016, 0.085, 0.149, 0.278, 0.463, 0.642, 0.794, 1.0]

values_siham = [0.29, 0.0, 0.008, 0.098, 0.912, 1.0, 0.673, 0.817, 0.82, 0.843] #siham
values_siham_fatigado = [0.0, 0.081, 0.126, 0.19, 0.644, 0.916, 0.885, 0.943, 0.973, 1.0]

values_raul_fatigado = [0.0, 0.47, 0.75, 0.815, 0.758, 0.806, 0.813, 0.655, 0.642, 1.0] #raul_fatigado
values_raul = [0.722, 0.514, 0.619, 0.446, 0.237, 0.414, 0.375,0.0, 0.154, 1.0]

values_daniel_fatigado = [0.0, 0.009, 0.335, 0.257, 0.332, 0.327, 0.177, 0.121, 0.723, 1.0]
values_daniel = [0.655, 0.0, 0.491, 0.123, 0.297, 0.233, 0.008, 0.035, 1.0, 0.963]



#imprimir_todas_las_graficas([values_mohamed, values_mohamed_fatigado, values_mohamed_fatigado2], ["sin_acumulacion", "acumulando v1", "acumulando v2"])

