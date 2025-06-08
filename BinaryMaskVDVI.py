import os
import numpy as np
from PIL import Image
from glob import glob

# Rutas
carpeta_rgb = "ground_truth_rgb"
carpeta_salida = "prediccionVDVI"
os.makedirs(carpeta_salida, exist_ok=True)

# Procesar todas las imágenes RGB
for ruta_img in glob(os.path.join(carpeta_rgb, "*.png")):
    nombre_archivo = os.path.basename(ruta_img)

    # Abrir imagen RGB y convertir a array NumPy
    img = Image.open(ruta_img).convert("RGB")
    img_np = np.array(img).astype(np.float32)

    # Extraer bandas
    red = img_np[:, :, 0]
    green = img_np[:, :, 1]
    blue = img_np[:, :, 2]

    # Calcular VDVI
    vdvi = (2 * green - red - blue) / (2 * green + red + blue)

    # Generar máscara binaria
    binary_mask = (vdvi > 0.2).astype(np.uint8) * 255  # Escalar a 0-255 para imagen

    # Guardar máscara como imagen PNG
    mask_img = Image.fromarray(binary_mask)
    mask_img.save(os.path.join(carpeta_salida, nombre_archivo))

    print(f"✔ Procesado: {nombre_archivo}")

print("✅ Todas las máscaras binarias fueron generadas con éxito.")
