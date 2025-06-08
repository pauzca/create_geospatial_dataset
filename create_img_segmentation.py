import json
import base64
from io import BytesIO
from PIL import Image, ImageDraw
import numpy as np


# Cargar el archivo JSON
with open("tile_4425_3540_segmentationFinal.json", "r") as f:
    data = json.load(f)

# Extraer tamaño de la imagen original
image_data = base64.b64decode(data["imageData"])
image = Image.open(BytesIO(image_data))
width, height = image.size

# Crear una imagen binaria inicializada en 0 (fondo no segmentado)
mask = Image.new("L", (width, height), 0)  # "L" = 8 bits (0-255)

# Dibujar los polígonos en blanco (valor 255)
draw = ImageDraw.Draw(mask)
for shape in data["shapes"]:
    polygon = [tuple(point) for point in shape["points"]]
    draw.polygon(polygon, outline=1, fill=255)  # Segmentado = 255

# Guardar la máscara binaria
mask.save("mascara_binaria_4425_3540.png")  # Puedes usar .tiff, .bmp, etc. si prefieres

# (Opcional) Convertirla en una matriz binaria (0 y 1)
binary_array = np.array(mask) // 255
np.save("mascara_binaria_4425_3540.npy", binary_array)  # Guarda como .npy si deseas usarlo en Python