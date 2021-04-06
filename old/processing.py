import sys
sys.path.append(r'C:\Program Files\QGIS 3.4\apps\qgis\python\plugins')

from qgis.core import (
    QgsProcessing,
    QgsVectorLayer,
    QgsGeometry,
    QgsProject,
    QgsFeatureRequest,
    QgsDistanceArea,
    QgsApplication,
    )


#make sure to update pathway for you're QGIS installation
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.4\apps\qgis", True)
qgs = QgsApplication([], False)
qgs.initQgis()

from processing.core.Processing import Processing
Processing.initialize()

from qgis.analysis import QgsNativeAlgorithms
qgs.processingRegistry().addProvider(QgsNativeAlgorithms())

print('total algorithms found:', len(qgs.processingRegistry().algorithms()))
for alg in qgs.processingRegistry().algorithms():
    print(alg.id(), "->", alg.displayName())

from qgis import processing

processing.algorithmHelp('native:pointsalonglines')

pth_CL = R"X:\Federal\2ERDC02 – WQ Model Enhancements FY2021\GIS\Data\LimnoTech\NapaRiver_CL.shp"
pth_OUT = R"X:\Federal\2ERDC02 – WQ Model Enhancements FY2021\GIS\Data\LimnoTech\NapaRiver_CL_PAL.shp"
lyr_CL_pts = processing.run("native:pointsalonglines", {'INPUT':pth_CL, 'DISTANCE':2000, 'START_OFFSET':0, 'END_OFFSET':0, 'OUTPUT':pth_OUT

qgs.exitQgis()
