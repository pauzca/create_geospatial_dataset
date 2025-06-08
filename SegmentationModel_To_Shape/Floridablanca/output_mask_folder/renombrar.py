import os
import re
import argparse

def renombrar_archivos(directorio):
    """
    Elimina '_mascara_binaria' de los nombres de archivos PNG en el directorio especificado.
    """
    for archivo in os.listdir(directorio):
        if archivo.endswith(".png") and "_mascara_binaria" in archivo:
            nuevo_nombre = archivo.replace("_mascara_binaria", "")
            vieja_ruta = os.path.join(directorio, archivo)
            nueva_ruta = os.path.join(directorio, nuevo_nombre)
            
            if not os.path.exists(nueva_ruta):
                os.rename(vieja_ruta, nueva_ruta)
                print(f"Renombrado: {archivo} -> {nuevo_nombre}")
            else:
                print(f"¡Advertencia! {nuevo_nombre} ya existe. No se renombró {archivo}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Elimina "_mascara_binaria" de nombres de archivos PNG.')
    parser.add_argument('--directorio', default='.', help='Directorio a procesar (por defecto: directorio actual)')
    args = parser.parse_args()
    
    renombrar_archivos(args.directorio)