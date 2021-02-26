# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 12:19:51 2021

@author: jrutyna
"""

from qgis.core import (
    QgsVectorLayer,
    QgsGeometry,
    QgsProject,
    QgsFeatureRequest,
    QgsDistanceArea
    )

#pth_CL = "I:/2ERDC02 – WQ Model Enhancements FY2021/GIS/Data/LimnoTech/NapaRiver_CL.shp"
pth_CL = "I:/2ERDC02 – WQ Model Enhancements FY2021/GIS/Data/LimnoTech/ProfileLines_Export_2021_0219"

lyr_CL = QgsVectorLayer(pth_CL, "Name", "Length")




