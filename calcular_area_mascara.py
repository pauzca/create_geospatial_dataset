import rasterio
from rasterio import features
from rasterstats import zonal_stats
import numpy as np
import geopandas as gpd
import json
from pathlib import Path

def calcular_porcentaje_y_area(mapa_tif, mascara_shape):
    # Abrir el mapa TIFF
    with rasterio.open(mapa_tif) as src:
        # Leer el raster (primera banda)
        raster = src.read(1)
        
        # Obtener la transformación affine para cálculos de área
        transform = src.transform
        pixel_area = abs(transform.a * transform.e)  # Área de un píxel en m² (para CRS proyectado)
        
        # Total de píxeles válidos (no nodata)
        total_pixels = np.sum(raster != src.nodata)
        area_total = total_pixels * pixel_area  # Área total en m²
        
        # Cargar la máscara shapefile
        gdf = gpd.read_file(mascara_shape)
        
        # Asegurar que estén en el mismo CRS
        if gdf.crs != src.crs:
            gdf = gdf.to_crs(src.crs)
        
        # Calcular estadísticas zonal
        stats = zonal_stats(gdf, mapa_tif, stats=['count'], nodata=src.nodata)
        pixels_mascara = stats[0]['count']
        area_mascara = pixels_mascara * pixel_area  # Área de la máscara en m²
        
        # Calcular porcentaje
        porcentaje = (pixels_mascara / total_pixels) * 100
        
        return {
            'area_total_m2': area_total,
            'area_mascara_m2': area_mascara,
            'porcentaje_mascara': porcentaje,
            'unidades': 'metros cuadrados (m²)',
            'archivos_utilizados': {
                'raster': mapa_tif,
                'shapefile': mascara_shape
            }
        }

def guardar_resultados_json(resultados, ruta_salida=None):
    if ruta_salida is None:
        ruta_salida = Path(mapa_tif).parent / 'resultados_mascara.json'
    
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)
    
    return ruta_salida

# Uso del script
if __name__ == "__main__":
    # Configura tus rutas aquí
    mapa_tif = 'C:/Users/Usuario/Downloads/Mascara_Vs_Tiff/Piedecuesta/Piedecuesta.tif'
    mascara_shape = 'C:/Users/Usuario/Downloads/Mascara_Vs_Tiff/Piedecuesta/mask_segmentation.shp'
    
    try:
        # Calcular resultados
        resultados = calcular_porcentaje_y_area(mapa_tif, mascara_shape)
        
        # Mostrar en consola
        print("\n=== RESULTADOS ===")
        print(f"Área total del mapa: {resultados['area_total_m2']:,.2f} m²")
        print(f"Área de la máscara: {resultados['area_mascara_m2']:,.2f} m²")
        print(f"Porcentaje ocupado: {resultados['porcentaje_mascara']:.2f}%")
        
        # Guardar en JSON
        ruta_json = guardar_resultados_json(resultados)
        print(f"\nResultados guardados en: {ruta_json}")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("\nPosibles causas:")
        print("- Archivos no encontrados en las rutas especificadas")
        print("- Falta alguno de los archivos del shapefile (.shp, .shx, .dbf)")
        print("- Los CRS no coinciden y no se puede reproyectar")
        print("- El raster no tiene valores nodata definidos correctamente")