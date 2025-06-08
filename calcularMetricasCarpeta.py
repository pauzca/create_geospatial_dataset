import json
import glob

# Ruta donde están los JSON
archivos_json = glob.glob("Resultados/MetricasPiedecuesta/*.json")  # Cambia esto por la ruta de tus archivos

# Diccionario para acumular las métricas
suma_metricas = {
    "Accuracy": 0.0,
    "Precision": 0.0,
    "Recall": 0.0,
    "F1_Score": 0.0,
    "IoU": 0.0
}

conteo = 0

for archivo in archivos_json:
    with open(archivo, 'r') as f:
        data = json.load(f)
        for key in suma_metricas:
            suma_metricas[key] += data[key]
        conteo += 1

# Calcular promedio
promedios = {key: (suma_metricas[key] / conteo) for key in suma_metricas}

# Guardar el promedio en un archivo JSON
with open("promedio_metricas_Piedecuesta.json", "w") as f_out:
    json.dump(promedios, f_out, indent=4)

# Mostrar resultado en formato JSON
print(json.dumps(promedios, indent=4))