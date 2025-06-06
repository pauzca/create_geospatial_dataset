# Load the required library
library(terra)

setwd("/home/paula/Documentos/PROYECTOS/segmentacion_vegetacion")

input_raster <- "./Mapa_Florida_Combinado_Delimitado.tif"

r <- rast(input_raster)

nlyr(r)

red_original <- r[[1]]
green_original <- r[[2]]
blue_original <- r[[3]]


# --- Vegetation Indices ---


# 17. Visible-Band Difference Vegetation Index
vdvi <- (2 * green_original - red_original - blue_original) / (2 * green_original + red_original + blue_original)

r <- rast(input_raster)
nlyr(r)
raster_with_indices <- c(r,vdvi)


names(r)
# Assign band names
names(raster_with_indices) <- c("red", "green", "blue", "VDVI", )

path <- "mapa_florida_vegetation_indices.tiff"
f <- file.path(path,"")
f
path
# Save the new raster
writeRaster(raster_with_indices, path, overwrite=TRUE)
