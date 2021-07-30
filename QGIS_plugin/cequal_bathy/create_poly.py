# -*- coding: utf-8 -*-
from qgis.core import QgsProject

def createPolygon_func(self, selectedLayer, seg_ct, transectWidth):
    import processing
    root = QgsProject.instance().layerTreeRoot()

    extendWidth = transectWidth / 2

    #get active layer
    iface = self.iface
    alyr=iface.activeLayer()

    #Get length of river centerline
    #params = { 'CALC_METHOD' : 0, 'INPUT' : QgsProcessingFeatureSourceDefinition('G:/2ERDC02/GIS/Demo_Files_31Mar2021/NapaRiver_CL.shp'), 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    params = { 'CALC_METHOD' : 0, 'INPUT' : selectedLayer, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_len = processing.run("qgis:exportaddgeometrycolumns", params)
    result_layer1 = result_len['OUTPUT']
    len=0
    for feature in result_layer1.getFeatures():
        len += feature["length"]

    #calc segment length
    seg_len = round(len/seg_ct,4)

    #Get points with angle
    #params = { 'DISTANCE' : seg_len, 'END_OFFSET' : 0, 'INPUT' : QgsProcessingFeatureSourceDefinition('G:/2ERDC02/GIS/Demo_Files_31Mar2021/NapaRiver_CL.shp'), 'OUTPUT' : 'TEMPORARY_OUTPUT', 'START_OFFSET' : 0 }
    params = { 'DISTANCE' : seg_len, 'END_OFFSET' : 0, 'INPUT' : selectedLayer, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'START_OFFSET' : 0 }
    result_pts = processing.run("native:pointsalonglines", params)
    result_layer_pts = result_pts['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_pts)

    #Extend and rotate lines
    params ={ 'EXPRESSION' : 'extend(\r\n make_line(\r\n $geometry,\r\n project (\r\n $geometry, \r\n '+str(extendWidth) +', \r\n radians(\"angle\"-90))\r\n ),\r\n '+str(extendWidth) +',\r\n 0\r\n)', 'INPUT' : result_layer_pts, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'OUTPUT_GEOMETRY' : 1, 'WITH_M' : False, 'WITH_Z' : False }
    result_rot = processing.run("native:geometrybyexpression", params)
    result_layer_rot = result_rot['OUTPUT']

    #populate order id
    params={ 'FIELD_LENGTH' : 10, 'FIELD_NAME' : 'order_id', 'FIELD_PRECISION' : 4, 'FIELD_TYPE' : 1, 'INPUT' : result_layer_rot, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_rot = processing.run("native:addfieldtoattributestable", params)
    result_layer_rot = result_rot['OUTPUT']
    params={ 'FIELD_LENGTH' : 0, 'FIELD_NAME' : 'order_id', 'FIELD_PRECISION' : 0, 'FIELD_TYPE' : 1, 'FORMULA' : '@row_number', 'INPUT' : result_layer_rot, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_rot = processing.run("native:fieldcalculator", params)
    result_layer_rot = result_rot['OUTPUT']
    #remove existing Transects Layer
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "Transects":
            QgsProject.instance().removeMapLayers([lyr.id()])
    result_layer_rot.setName("Transects")
    QgsProject.instance().addMapLayer(result_layer_rot)

    #Get starting points
    params = { 'INPUT' : result_layer_rot, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'VERTICES' : '0' }
    result_sp = processing.run("native:extractspecificvertices", params)
    result_layer_sp = result_sp['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_sp)

    #Get end points
    params = { 'INPUT' : result_layer_rot, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'VERTICES' : '-1' }
    result_ep = processing.run("native:extractspecificvertices", params)
    result_layer_ep = result_ep['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_ep)

    #connect paths
    params = { 'CLOSE_PATH' : False, 'GROUP_EXPRESSION' : '', 'INPUT' : result_layer_sp, 'NATURAL_SORT' : False, 'ORDER_EXPRESSION' : '', 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_p1 = processing.run("native:pointstopath", params)
    result_layer_p1 = result_p1['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_p1)

    params = { 'CLOSE_PATH' : False, 'GROUP_EXPRESSION' : '', 'INPUT' : result_layer_ep, 'NATURAL_SORT' : False, 'ORDER_EXPRESSION' : '', 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_p2 = processing.run("native:pointstopath", params)
    result_layer_p2 = result_p2['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_p2)

    #merge paths
    params={ 'CRS' : None, 'LAYERS' : [result_layer_rot,result_layer_p1,result_layer_p2], 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_lines = processing.run("native:mergevectorlayers", params)
    result_layer_lines = result_lines['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_lines)

    #polygonize
    params={ 'INPUT' : result_layer_lines, 'KEEP_FIELDS' : False, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_poly = processing.run("native:polygonize", params)
    result_layer_poly = result_poly['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_poly)

    #add number ID field
    params={ 'FIELD_LENGTH' : 10, 'FIELD_NAME' : 'order_id', 'FIELD_PRECISION' : 4, 'FIELD_TYPE' : 1, 'INPUT' : result_layer_poly, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_poly = processing.run("native:addfieldtoattributestable", params)
    result_layer_poly = result_poly['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_poly)

    #populate order id
    params={ 'FIELD_LENGTH' : 0, 'FIELD_NAME' : 'order_id', 'FIELD_PRECISION' : 0, 'FIELD_TYPE' : 1, 'FORMULA' : '@row_number', 'INPUT' : result_layer_poly, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_poly = processing.run("native:fieldcalculator", params)
    result_layer_poly = result_poly['OUTPUT']
    #remove existing Segments Layer
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "Segments":
            QgsProject.instance().removeMapLayers([lyr.id()])
    result_layer_poly.setName("Segments")
    QgsProject.instance().addMapLayer(result_layer_poly)

    #run convex check function
    segmentLayer = QgsProject.instance().mapLayersByName('Segments')[0]
    self.convexCheck(segmentLayer)

    #run centerline check function
    segmentLayer = QgsProject.instance().mapLayersByName('Segments')[0]
    transectLayer = QgsProject.instance().mapLayersByName('Transects')[0]
    centerlineLayer = selectedLayer
    self.centerlineCheck(segmentLayer, transectLayer, centerlineLayer)

    #run symbology check function
    segmentLayer = QgsProject.instance().mapLayersByName('Segments')[0]
    transectLayer = QgsProject.instance().mapLayersByName('Transects')[0]
    centerlineLayer = selectedLayer
    self.symbologyCheck(segmentLayer, transectLayer, centerlineLayer)
