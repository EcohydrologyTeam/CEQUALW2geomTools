# -*- coding: utf-8 -*-
from qgis.core import QgsProject

def convexCheck_func(self, segmentLayer):
    import processing
    root = QgsProject.instance().layerTreeRoot()

    #Create Convex Hull Polygon
    params = {
        'INPUT': segmentLayer,
        'OUTPUT': 'TEMPORARY_OUTPUT'}
    result_Segments_CnxHull = processing.run("native:convexhull", params)
    result_layer_Segments_CnxHull = result_Segments_CnxHull['OUTPUT']

    #Assign Geometry Attributes to W2 segments
    params = {
        'CALC_METHOD': 0,
        'INPUT': segmentLayer,
        'OUTPUT': 'TEMPORARY_OUTPUT'}
    result_Segments = processing.run("qgis:exportaddgeometrycolumns", params)
    result_layer_Segments = result_Segments['OUTPUT']

    #Perform Table Join between W2 segements and Convex Hull W2 segments
    params = {
        'DISCARD_NONMATCHING': False,
        'FIELD': 'order_id',
        'FIELDS_TO_COPY': [],
        'FIELD_2': 'order_id',
        'INPUT': result_layer_Segments,
        'INPUT_2': result_layer_Segments_CnxHull,
        'METHOD': 1,
        'OUTPUT': 'TEMPORARY_OUTPUT',
        'PREFIX': 'cnx_'}
    result_Segments_joined = processing.run("native:joinattributestable", params)
    result_layer_Segments_joined = result_Segments_joined['OUTPUT']

    #Create field for convex polygon check
    params = {
        'FIELD_LENGTH': 10,
        'FIELD_NAME': 'IsConvex',
        'FIELD_PRECISION': 10,
        'FIELD_TYPE': 1,
        'FORMULA': 'if( round( \"perimeter\", 4) - round( \"cnx_perimeter\", 4) = 0, 1, 0)',
        'INPUT': result_layer_Segments_joined,
        'OUTPUT': 'TEMPORARY_OUTPUT'}
    result_Segments_joined_chck = processing.run("native:fieldcalculator", params)
    result_layer_Segments_joined_chck = result_Segments_joined_chck['OUTPUT']

    #Remove unwanted fields
    params = {
        'INPUT': result_layer_Segments_joined_chck,
        'COLUMN': ["area", "perimeter", "cnx_order_id", "cnx_area", "cnx_perimeter"],
        'OUTPUT': 'TEMPORARY_OUTPUT'}
    result_Segments_joined_chck_rmv = processing.run("qgis:deletecolumn", params)
    result_layer_Segments_joined_chck_rmv = result_Segments_joined_chck_rmv['OUTPUT']

    #Remove existing Segments Layer and Add Updated Segment Layer with Convex Check Attribute
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "Segments":
            QgsProject.instance().removeMapLayers([lyr.id()])
    result_layer_Segments_joined_chck_rmv.setName("Segments")
    QgsProject.instance().addMapLayer(result_layer_Segments_joined_chck_rmv)
    #QgsProject.instance().addMapLayer(output_4)



