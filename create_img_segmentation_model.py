import json
import numpy as np
from pycocotools import mask as maskUtils
from PIL import Image

# Cargar archivo JSON
with open("tile_13275_4425.json", "r") as f:
    data = json.load(f)

# Obtener tamaño de la imagen desde el primer objeto de segmentación
height, width = data["masks"][0]["segmentation"]["size"]
mask_total = np.zeros((height, width), dtype=np.uint8)

# Convertir segmentaciones RLE a máscaras binarias
for mask in data['masks']:
    rle = mask['segmentation']
    binary_mask = maskUtils.decode(rle)
    mask_total = np.maximum(mask_total, binary_mask.astype(np.uint8))  # combinar todas

# Guardar la imagen de máscara binaria
output_path = "mascara_binaria_model_tile_13275_4425.png"
Image.fromarray(mask_total * 255).save(output_path)

print(f"✅ Máscara binaria guardada como: {output_path}")
