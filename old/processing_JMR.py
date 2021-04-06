import sys
sys.path.append(r'C:\Program Files\QGIS 3.18\apps\qgis\python\plugins')


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
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.18\apps\qgis", True)
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

wrkDir = R"I:\2ERDC02 – WQ Model Enhancements FY2021\GIS\Data\LimnoTech"

pth_CL = wrkDir + R"\NapaRiver_CL.shp"
pth_OUT = wrkDir + R"\TEMP_CL_pts.shp"
lyr_CL_pts = processing.run("native:pointsalonglines", {'INPUT':pth_CL, 'DISTANCE':2000, 'START_OFFSET':0, 'END_OFFSET':0, 'OUTPUT':pth_OUT})
print("Finished - Centerline Points")


pth_CL_pts = wrkDir + R"\TEMP_CL_pts.shp"
pth_OUT = wrkDir + R"\TEMP_CL_pts_Path.shp"
lyr_CL_pts = processing.run("qgis:pointstopath", {'INPUT':pth_CL_pts, 'ORDER_FIELD':"distance", 'OUTPUT':pth_OUT})
print("Finished - Centerline Points Path")


pth_CL_pts_Path = wrkDir + R"\TEMP_CL_pts_Path.shp"
pth_OUT = wrkDir + R"\TEMP_CL_trnsct.shp"
lyr_CL_pts = processing.run("native:transect", {'INPUT':pth_CL_pts_Path, 'LENGTH':500, 'ANGLE':90, 'SIDE':2, 'OUTPUT':pth_OUT})
print("Finished - Centerline Transect")


pth_CL_pts = wrkDir + R"\TEMP_CL_pts.shp"
pth_OUT = wrkDir + R"\TEMP_CL_pts_Buff.shp"
lyr_CL_pts = processing.run("native:buffer", {'INPUT':pth_CL_pts, 'DISTANCE':0.05, 'OUTPUT':pth_OUT})
print("Finished - Buffer Centerline Points")


pth_OUT = wrkDir + R"\TEMP_CL_sgmts.shp"
lyr_CL_sgmts = processing.run("native:explodelines", {'INPUT':pth_CL, 'OUTPUT':pth_OUT})
print("Finished - Centerline Segments")


pth_CL_sgmts = pth_OUT = wrkDir + R"\TEMP_CL_sgmts.shp"
pth_CL_pts_Buff = wrkDir + R"\TEMP_CL_pts_Buff.shp"
pth_OUT = wrkDir + R"\TEMP_CL_sgmts_slctd.shp"
lyr_CL_sgmts_slctd = processing.run("native:joinattributesbylocation", {'INPUT':pth_CL_sgmts, 'JOIN': pth_CL_pts_Buff, 'PREDICATE': 0, 'METHOD': 0, 'DISCARD_NONMATCHING': True, 'OUTPUT':pth_OUT})
print("Finished - Centerline Segments Selected")



qgs.exitQgis()
