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
    QgsDistanceArea,
    QgsApplication,
    #processing#
    )


#from qgis.core import *

# Supply path to qgis install location
#QgsApplication.setPrefixPath("C:/PROGRA~1/QGIS3~1.18/apps/qgis", True)
QgsApplication.setPrefixPath(r"C:/Program Files/QGIS 3.18/apps/qgis", True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)

# Load providers
qgs.initQgis()

# Write your code here to load some layers, use processing
# algorithms, etc.

#import sys
#sys.path.append("C:/Program Files/QGIS 3.18/apps/qgis/python/plugins/processing")

#import processing
#from processing.core.Processing import Processing

#Processing.initialize()
#Processing.updateAlgsList()

pth_CL = "I:/2ERDC02 – WQ Model Enhancements FY2021/GIS/Data/LimnoTech/NapaRiver_CL.shp"

lyr_CL = QgsVectorLayer(pth_CL, "Name", "Length")



from qgis import processing

lyr_CL_pts = processing.run("qgis:pointsalonglines", {lyr_CL, 2000, 0, 0})




# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
qgs.exitQgis()
