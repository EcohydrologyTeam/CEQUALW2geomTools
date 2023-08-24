# -*- coding: utf-8 -*-
from qgis.core import QgsProject, QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer, QgsLinePatternFillSymbolLayer, QgsSingleSymbolRenderer
from PyQt5.QtGui import QColor

def symbologyCheck_func(self, segmentLayer, transectLayer, centerlineLayer):
    import processing
    root = QgsProject.instance().layerTreeRoot()



    #Display Symbology for existing Centerline Layer
    centerlineLayer.selectAll()
    clone_centerlineLayer = processing.run("native:saveselectedfeatures", {'INPUT': centerlineLayer, 'OUTPUT': 'memory:'})['OUTPUT']
    centerlineLayer.removeSelection()
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "Centerline":
            QgsProject.instance().removeMapLayers([lyr.id()])
    clone_centerlineLayer.setName("Centerline")
    symbol_CL = QgsSymbol.defaultSymbol(clone_centerlineLayer.geometryType())
    symbol_CL.setWidth(1)
    symbol_CL.setColor(QColor.fromRgb(31,120,180))
    renderer = QgsSingleSymbolRenderer(symbol_CL)
    clone_centerlineLayer.setRenderer(renderer)
    QgsProject.instance().addMapLayer(clone_centerlineLayer)



    #Display Symbology for existing Transect Layer
    transectLayer.selectAll()
    clone_transectLayer = processing.run("native:saveselectedfeatures", {'INPUT': transectLayer, 'OUTPUT': 'memory:'})['OUTPUT']
    transectLayer.removeSelection()
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "Transects":
            QgsProject.instance().removeMapLayers([lyr.id()])
    clone_transectLayer.setName("Transects")
    symbol_T = QgsSymbol.defaultSymbol(clone_transectLayer.geometryType())
    symbol_T.setWidth(1)
    symbol_T.setColor(QColor("green"))
    renderer = QgsSingleSymbolRenderer(symbol_T)
    clone_transectLayer.setRenderer(renderer)
    QgsProject.instance().addMapLayer(clone_transectLayer)



    #Create field for centerline all inside W2 segment check
    params = {
        'FIELD_LENGTH': 10,
        'FIELD_NAME': 'Is_Cnx_CL_In',
        'FIELD_PRECISION': 10,
        'FIELD_TYPE': 1,
        'FORMULA': '\"IsConvex\" * 10 + \"Is_CL_In\"',
        'INPUT': segmentLayer,
        'OUTPUT': 'TEMPORARY_OUTPUT'}
    result_Segments = processing.run("native:fieldcalculator", params)
    result_layer_Segments = result_Segments['OUTPUT']
    
    #remove extra fields
    params={ 'FIELDS' : ['order_id', 'SEGMENT', 'Is_Cnx_CL_In'], 'INPUT' : result_layer_Segments, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_Segments = processing.run("native:retainfields", params)
    result_layer_Segments = result_Segments['OUTPUT']

    #Remove existing Segments Layer and
    #Add Updated Segment Layer with Centerline Check Attribute and
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "Segments":
            QgsProject.instance().removeMapLayers([lyr.id()])
    result_layer_Segments.setName("Segments")
    symbol_1 = QgsSymbol.defaultSymbol(result_layer_Segments.geometryType())
    symbol_2 = QgsSymbol.defaultSymbol(result_layer_Segments.geometryType())
    symbol_3 = QgsSymbol.defaultSymbol(result_layer_Segments.geometryType())
    symbol_4 = QgsSymbol.defaultSymbol(result_layer_Segments.geometryType())
    symbol_1.setColor(QColor('orange'))
    symbol_2.setColor(QColor('yellow'))
    symbol_3.setColor(QColor('red'))
    symbol_4.setColor(QColor('blue'))
    symbol_1.setOpacity(0.3)
    symbol_2.setOpacity(0.3)
    symbol_3.setOpacity(0.3)
    symbol_4.setOpacity(0.15)

    #Define a line pattern for symbol_1
    symbol_lyr_line = QgsLinePatternFillSymbolLayer()
    symbol_lyr_line.setLineAngle(45)
    symbol_lyr_line.setDistance(2)
    symbol_lyr_line.setLineWidth(0.35)
    symbol_lyr_line.setColor(QColor("black"))
    symbol_1.appendSymbolLayer(symbol_lyr_line)
    symbol_lyr_line = QgsLinePatternFillSymbolLayer()
    symbol_lyr_line.setLineAngle(135)
    symbol_lyr_line.setDistance(2)
    symbol_lyr_line.setLineWidth(0.35)
    symbol_lyr_line.setColor(QColor("black"))
    symbol_1.appendSymbolLayer(symbol_lyr_line)

    #Define a line pattern for symbol_2
    symbol_lyr_line = QgsLinePatternFillSymbolLayer()
    symbol_lyr_line.setLineAngle(45)
    symbol_lyr_line.setDistance(2)
    symbol_lyr_line.setLineWidth(0.35)
    symbol_lyr_line.setColor(QColor("black"))
    symbol_2.appendSymbolLayer(symbol_lyr_line)

    #Define a line pattern for symbol_3
    symbol_lyr_line = QgsLinePatternFillSymbolLayer()
    symbol_lyr_line.setLineAngle(135)
    symbol_lyr_line.setDistance(2)
    symbol_lyr_line.setLineWidth(0.35)
    symbol_lyr_line.setColor(QColor("black"))
    symbol_3.appendSymbolLayer(symbol_lyr_line)

    #Display symbology
    c1 = QgsRendererCategory(0,symbol_1,"Concave; Centerline Out",True)
    c2 = QgsRendererCategory(10,symbol_2,"Convex; Centerline Out",True)
    c3 = QgsRendererCategory(1,symbol_3,"Concave; Centerline In",True)
    c4 = QgsRendererCategory(11,symbol_4,"Convex; Centerline In",True)
    renderer = QgsCategorizedSymbolRenderer("Is_Cnx_CL_In", [c1,c2,c3,c4])
    result_layer_Segments.setRenderer(renderer)
    QgsProject.instance().addMapLayer(result_layer_Segments)
