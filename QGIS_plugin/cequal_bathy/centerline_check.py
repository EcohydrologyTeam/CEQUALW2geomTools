# -*- coding: utf-8 -*-
from qgis.core import QgsProject

def centerlineCheck_func(self, segmentLayer, transectLayer, centerlineLayer):
    import processing
    root = QgsProject.instance().layerTreeRoot()

    #Split Centerline at previously calculated W2 transects
    params = {
        'INPUT': centerlineLayer,
        'LINES': transectLayer,
        'OUTPUT': 'TEMPORARY_OUTPUT' }
    result_splitCenterline = processing.run("native:splitwithlines", params)
    result_layer_splitCenterline = result_splitCenterline['OUTPUT']

    #Match with W2 segment IDs
    params = {
        'DISCARD_NONMATCHING' : False,
        'INPUT' : result_layer_splitCenterline,
        'JOIN' : segmentLayer,
        'JOIN_FIELDS' : [],
        'METHOD' : 1,
        'OUTPUT' : 'TEMPORARY_OUTPUT',
        'PREDICATE' : [0],
        'PREFIX' : 'sgmt_' }
    result_splitCenterlineJoin = processing.run("native:joinattributesbylocation", params)
    result_layer_splitCenterlineJoin = result_splitCenterlineJoin['OUTPUT']

    #Intersection of split centerlines and W2 polygon segments
    params = {
        'INPUT' : result_layer_splitCenterlineJoin,
        'INPUT_FIELDS' : [],
        'OUTPUT' : 'TEMPORARY_OUTPUT',
        'OVERLAY' : segmentLayer,
        'OVERLAY_FIELDS' : [],
        'OVERLAY_FIELDS_PREFIX' : '' }
    result_splitCenterlineJoinIntrct = processing.run("native:intersection", params)
    result_layer_splitCenterlineJoinIntrct = result_splitCenterlineJoinIntrct['OUTPUT']

    #Assign Geometry Attributes to Split Centerlines
    params = {
        'CALC_METHOD': 0,
        'INPUT': result_layer_splitCenterlineJoin,
        'OUTPUT': 'TEMPORARY_OUTPUT'}
    result_splitCenterlineJoinAttr = processing.run("qgis:exportaddgeometrycolumns", params)
    result_layer_splitCenterlineJoinAttr = result_splitCenterlineJoinAttr['OUTPUT']

    #Assign Geometry Attributes to Split Centerlines that have been "intersected" with the W2 segments
    params = {
        'CALC_METHOD': 0,
        'INPUT': result_layer_splitCenterlineJoinIntrct,
        'OUTPUT': 'TEMPORARY_OUTPUT'}
    result_splitCenterlineJoinIntrctAttr = processing.run("qgis:exportaddgeometrycolumns", params)
    result_layer_splitCenterlineJoinIntrctAttr = result_splitCenterlineJoinIntrctAttr['OUTPUT']

    #Spatial Join with the W2 segments to Split Centerlines
    params = {
        'DISCARD_NONMATCHING' : False,
        'INPUT' : segmentLayer,
        'JOIN' : result_layer_splitCenterlineJoinAttr,
        'JOIN_FIELDS' : [],
        'METHOD' : 2,
        'OUTPUT' : 'TEMPORARY_OUTPUT',
        'PREDICATE' : [0],
        'PREFIX' : 'splt_' }
    result_Segments_Split = processing.run("native:joinattributesbylocation", params)
    result_layer_Segments_Split = result_Segments_Split['OUTPUT']

    #Spatial Join with the W2 segments to Split Centerlines that have been "intersected"
    params = {
        'DISCARD_NONMATCHING' : False,
        'INPUT' : segmentLayer,
        'JOIN' : result_layer_splitCenterlineJoinIntrctAttr,
        'JOIN_FIELDS' : [],
        'METHOD' : 2,
        'OUTPUT' : 'TEMPORARY_OUTPUT',
        'PREDICATE' : [0],
        'PREFIX' : 'spltInt_' }
    result_Segments_SplitIntrct = processing.run("native:joinattributesbylocation", params)
    result_layer_Segments_SplitIntrct = result_Segments_SplitIntrct['OUTPUT']

    #Perform Table Join between W2 segements Split and W2 segements Split that have been "intersected"
    params = {
        'DISCARD_NONMATCHING': False,
        'FIELD': 'order_id',
        'FIELDS_TO_COPY': [],
        'FIELD_2': 'order_id',
        'INPUT': result_layer_Segments_Split,
        'INPUT_2': result_layer_Segments_SplitIntrct,
        'METHOD': 1,
        'OUTPUT': 'TEMPORARY_OUTPUT',
        'PREFIX': ''}
    result_Segments_joined = processing.run("native:joinattributestable", params)
    result_layer_Segments_joined = result_Segments_joined['OUTPUT']

    #Create field for centerline all inside W2 segment check
    params = {
        'FIELD_LENGTH': 10,
        'FIELD_NAME': 'Is_CL_In',
        'FIELD_PRECISION': 10,
        'FIELD_TYPE': 1,
        'FORMULA': 'if( round( \"splt_length\", 4) - round( \"spltInt_length\", 4) = 0, 1, 0)',
        'INPUT': result_layer_Segments_joined,
        'OUTPUT': 'TEMPORARY_OUTPUT'}
    result_Segments_joined_chck = processing.run("native:fieldcalculator", params)
    result_layer_Segments_joined_chck = result_Segments_joined_chck['OUTPUT']

    #Remove unwanted fields
    # params = {
        # 'INPUT': result_layer_Segments_joined_chck,
        # 'COLUMN': ["splt_Name",
                   # "splt_sgmt_order_id",
                   # "splt_sgmt_IsConvex",
                   # "splt_length",
                   # "order_id_2",
                   # "IsConvex_2",
                   # "spltInt_Name",
                   # "spltInt_sgmt_order_id",
                   # "spltInt_sgmt_IsConvex",
                   # "spltInt_order_id",
                   # "spltInt_IsConvex",
                   # "spltInt_length"],
        # 'OUTPUT': 'TEMPORARY_OUTPUT'}
    # result_Segments_joined_chck_rmv = processing.run("qgis:deletecolumn", params)
    # result_layer_Segments_joined_chck_rmv = result_Segments_joined_chck_rmv['OUTPUT']

    #Remove existing Segments Layer and Add Updated Segment Layer with Centerline Check Attribute
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "Segments":
            QgsProject.instance().removeMapLayers([lyr.id()])
    #result_layer_Segments_joined_chck_rmv.setName("Segments")
    #QgsProject.instance().addMapLayer(result_layer_Segments_joined_chck_rmv)
    result_layer_Segments_joined_chck.setName("Segments")
    QgsProject.instance().addMapLayer(result_layer_Segments_joined_chck)


