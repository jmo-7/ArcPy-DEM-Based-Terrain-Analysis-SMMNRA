# Initial Setup
import arcpy
from arcpy import env
from arcpy.sa import *
env.overwriteOutput = True

# Import DEM To Geodatabase (GDB):
arcpy.conversion.RasterToGeodatabase(r" # DEM's Path", r" # GDB's Path")

# Produce Slope Raster With Degree As Parameter:
outSlope = Slope(r" # DEM's Path", "DEGREE")
outSlope.save(r" # Path For Saving The Output Slop Raster")

# Produce Aspect Raster:
outAspect = Aspect(r" # DEM's Path")
outAspect.save(r" # Path For Saving The Output Aspect Raster")

# Reclassifying Aspect Raster To Output A New One with New Classification Scheme:
myRemapRange = RemapRange([[-1, -1, 1], [0, 22.5, 2], [22.5, 67.5, 3], [67.5, 112.5, 4], [112.5, 157.5, 5], [157.5, 202.5, 6], [202.5, 247.5, 7], [247.5, 292.5, 8], [292.5, 337.5, 9], [337.5, 360, 10]])
outReclass = Reclassify(r" # Input Aspect Raster's Path", "VALUE", myRemapRange, "DATA")
outReclass.save(r" # Path For Saving The New Output Aspect Raster")

# Produce Hillshade Raster:
outHillshade = Hillshade(r" # DEM's Path", 315, 45, "NO_SHADOWS", 1)
outHillshade.save(r" # Path For Saving The Hillshade Raster")

# Produce Hillshade Raster With 4 Pairs Of Azimuth And Altitude:
env.workspace = r" # GDB's Path For Storing The 4 New Hillshade Raster"
in_raster = r" # DEM's Path"
azimuth_list = [179.90, 186.64, 186.46, 182.36]
altitude_list = [56.13, 79.32, 55.77, 32.50]
for x, y in zip(azimuth_list, altitude_list):
    arcpy.HillShade_3d(in_raster, f"HS_{round(x)}_{round(y)}", x, y)
    print(f"\nHS_{round(x)}_{round(y)} is created")

# Map Algebra for Solar Radiation Calculation.i.e., Produce Solar Radiation Raster For Each Season:
env.workspace = r" # GDB's Path For Storing The 4 New Hillshade Raster"
HS_Ras_List = arcpy.ListRasters()
for HS_Ras in HS_Ras_List:
    print(f"\n{HS_Ras} is in this iteration")
    out_HS_raster = (Raster(HS_Ras) / 255.0) * 1000.0
    out_HS_raster.save(f"{HS_Ras}_Solar")
    print(f"\n{HS_Ras}_Solar is created")

# Annual Solar Radiation Calculation. i.e., Produce Annual Solar Radiation Raster:
Input_Solar_Ras1 = HS_Ras_List[0]
Input_Solar_Ras2 = HS_Ras_List[1]
Input_Solar_Ras3 = HS_Ras_List[2]
Input_Solar_Ras4 = HS_Ras_List[3]
Out_Annual_Solar_Ras = (Raster(Input_Solar_Ras1) + Raster(Input_Solar_Ras2) + Raster(Input_Solar_Ras3) + Raster(Input_Solar_Ras4)) / 4.0
Out_Annual_Solar_Ras.save("Annual_Solar_Ras")
print(f"\nAnnual_Solar_Ras is created!")

# Import DEM, Slope, Aspect, and the Summer Solar Radiation to Zonal_Stat GDB:
arcpy.conversion.RasterToGeodatabase(r" # Path For The DEM, Slope, Aspect, And Summer Solar Radiation Raster",
                                     r" # Path For THE GDB Used To Store The Zonal Statistics Output")

# Zonal Statistics:
inZoneData = r" # Vegetation Zone's Layer's Path"
zoneField = "# Field Name Used For Zonal Statistics"
env.workspace = r" # Path For THE GDB Used To Store The Zonal Statistics Output"
Ras_List_in_Zonal_GDB = arcpy.ListRasters()
print(f"\n{Ras_List_in_Zonal_GDB}")
for Raster in Ras_List_in_Zonal_GDB:
    print(f"\n{Raster} is in this iteration")
    outZSaT = ZonalStatisticsAsTable(inZoneData, zoneField, Raster,
                                     f"{Raster}_Stat", "DATA", "ALL")

print("\nProcess Completed!")