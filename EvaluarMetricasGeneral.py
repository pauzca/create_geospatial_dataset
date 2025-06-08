import torch
import numpy as np
from PIL import Image
import json
import os
from glob import glob
from torchmetrics.classification import (
    BinaryAccuracy, BinaryPrecision, BinaryRecall,
    BinaryF1Score, BinaryJaccardIndex
)

# Función para cargar imagen binaria como tensor aplanado
def cargar_mascara(path):
    return torch.tensor(np.array(Image.open(path).convert("1"))).flatten().int()

# Rutas
carpeta_gt = "ground_truth_binaryMask"
carpeta_pred = "prediccionVDVI"
carpeta_Resultados = "Resultados_groundTruthBinaryMask_vs_prediccionVDVI"
os.makedirs(carpeta_Resultados, exist_ok=True)

# Inicializar acumulador de métricas
suma_metricas = {
    "Accuracy": 0.0,
    "Precision": 0.0,
    "Recall": 0.0,
    "F1_Score": 0.0,
    "IoU": 0.0
}
conteo = 0

# Procesar todas las imágenes del ground truth
for ruta_gt in glob(os.path.join(carpeta_gt, "tile_*.png")):
    nombre_archivo = os.path.basename(ruta_gt)
    ruta_pred = os.path.join(carpeta_pred, nombre_archivo)

    # Verificar que exista predicción correspondiente
    if not os.path.exists(ruta_pred):
        print(f"⚠ Predicción no encontrada para: {nombre_archivo}")
        continue

    # Cargar máscaras
    y_true = cargar_mascara(ruta_gt)
    y_pred = cargar_mascara(ruta_pred)

    # Inicializar métricas
    accuracy = BinaryAccuracy()
    precision = BinaryPrecision()
    recall = BinaryRecall()
    f1 = BinaryF1Score()
    iou = BinaryJaccardIndex()

    # Calcular métricas
    Resultados = {
        "Accuracy": float(accuracy(y_pred, y_true)),
        "Precision": float(precision(y_pred, y_true)),
        "Recall": float(recall(y_pred, y_true)),
        "F1_Score": float(f1(y_pred, y_true)),
        "IoU": float(iou(y_pred, y_true))
    }

    # Guardar métricas individuales
    nombre_json = f"metricas_{nombre_archivo.replace('.png', '.json')}"
    ruta_salida = os.path.join(carpeta_Resultados, nombre_json)
    with open(ruta_salida, "w") as f:
        json.dump(Resultados, f, indent=4)

    # Sumar métricas para el promedio final
    for key in suma_metricas:
        suma_metricas[key] += Resultados[key]
    conteo += 1

# Calcular y guardar promedio si hubo al menos una imagen
if conteo > 0:
    promedio = {key: suma_metricas[key] / conteo for key in suma_metricas}
    ruta_promedio = os.path.join(carpeta_Resultados, "promedio_metricas.json")
    with open(ruta_promedio, "w") as f:
        json.dump(promedio, f, indent=4)
    print(f"✔ Procesadas {conteo} imágenes. Promedio guardado en {ruta_promedio}")
else:
    print("❌ No se procesó ninguna imagen válida.")
