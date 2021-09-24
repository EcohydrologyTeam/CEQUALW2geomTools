# -*- coding: utf-8 -*-
from qgis.core import QgsProject
from qgis.core import QgsProcessingFeatureSourceDefinition
from qgis.core import QgsProperty

def splitPolygon_func(self, transectWidth):

    seg_w = transectWidth / 2

    #TODO:  UI to specify transect, segment layers

    import processing
    import numpy
    root = QgsProject.instance().layerTreeRoot()

    cl_lyr=QgsProject.instance().mapLayersByName("Centerline")[0]
    #cl_lyr=selectedLayer
    transect_lyr=QgsProject.instance().mapLayersByName("Transects")[0]
    seg_lyr=QgsProject.instance().mapLayersByName("Segments")[0]

    #dissolve centerline
    params={ 'FIELD' : [], 'INPUT' : cl_lyr, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_cl = processing.run("native:dissolve", params)
    cl_lyr = result_cl['OUTPUT']
    params={ 'FIELDS' : ['Name'], 'INPUT' : cl_lyr, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_cl = processing.run("native:retainfields", params)
    cl_lyr = result_cl['OUTPUT']
   
    #split centerline by transects
    params={ 'INPUT' : cl_lyr, 'LINES' : transect_lyr, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_cl_seg = processing.run("native:splitwithlines", params)
    result_layer_cl_seg = result_cl_seg['OUTPUT']
    
    #add length field
    params={ 'CALC_METHOD' : 0, 'INPUT' : result_layer_cl_seg, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_cl_seg = processing.run("qgis:exportaddgeometrycolumns", params)
    result_layer_cl_seg = result_cl_seg['OUTPUT']
    
    #remove artifact segments
    params={ 'EXPRESSION' : ' \"length\" >0.1', 'INPUT' : result_layer_cl_seg, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_cl_seg = processing.run("native:extractbyexpression", params)
    result_layer_cl_seg = result_cl_seg['OUTPUT']
    
    #clip segments to ensure proper join
    params={ 'END_DISTANCE' : QgsProperty.fromExpression('"length"*0.999999'), 'INPUT' : result_layer_cl_seg, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'START_DISTANCE' : QgsProperty.fromExpression('"length"*0.000001') }
    result_cl_seg = processing.run("native:linesubstring", params)
    result_layer_cl_seg = result_cl_seg['OUTPUT']

    #match segments
    params={ 'DISCARD_NONMATCHING' : True, 'INPUT' : result_layer_cl_seg, 'JOIN' : QgsProcessingFeatureSourceDefinition(seg_lyr.id(), True), 'JOIN_FIELDS' : [], 'METHOD' : 2, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'PREDICATE' : [0], 'PREFIX' : '' }
    result_cl_seg3 = processing.run("native:joinattributesbylocation", params)
    result_layer_cl_seg = result_cl_seg3['OUTPUT']
    QgsProject.instance().addMapLayer(result_layer_cl_seg)
    
    #Get intersection of transects and centerline
    params={ 'INPUT' : cl_lyr, 'INPUT_FIELDS' : [], 'INTERSECT' : transect_lyr, 'INTERSECT_FIELDS' : [], 'INTERSECT_FIELDS_PREFIX' : '', 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_tpt = processing.run("native:lineintersections", params)
    result_layer_tpt = result_tpt['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_tpt)

    #add mid points for selected cl segments
    for feature in result_layer_cl_seg.getFeatures():
        len = feature["length"]
        id = feature["order_id"]
        mid=len/2
        
        #select segment
        params={ 'FIELD' : 'order_id', 'INPUT' : result_layer_cl_seg, 'METHOD' : 0, 'OPERATOR' : 0, 'VALUE' : str(id) }
        result_sel = processing.run("qgis:selectbyattribute", params)
        result_layer_sel = result_sel['OUTPUT']
        
        #add points    
        params={ 'DISTANCE' : mid, 'END_OFFSET' : 0, 'INPUT' : QgsProcessingFeatureSourceDefinition(result_layer_sel.id(), True), 'OUTPUT' : 'TEMPORARY_OUTPUT', 'START_OFFSET' : 0 }
        result_pts = processing.run("native:pointsalonglines", params)
        result_layer_pts = result_pts['OUTPUT']
        #QgsProject.instance().addMapLayer(result_layer_pts)
        
        #select only midpoint
        params = { 'INPUT' : result_layer_pts, 'INTERSECT' : QgsProcessingFeatureSourceDefinition(result_layer_sel.id(), True), 'OUTPUT' : 'TEMPORARY_OUTPUT', 'PREDICATE' : [2] }
        result_pts = processing.run("native:extractbylocation", params)
        result_layer_pts = result_pts['OUTPUT']
        #QgsProject.instance().addMapLayer(result_layer_pts)
        
        #increment order_id
        params={ 'FIELD_LENGTH' : 0, 'FIELD_NAME' : 'order_id', 'FIELD_PRECISION' : 0, 'FIELD_TYPE' : 0, 'FORMULA' : '\"order_id\" + 0.001', 'INPUT' : result_layer_pts, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
        result_pts = processing.run("native:fieldcalculator", params)
        result_layer_pts = result_pts['OUTPUT']
        #QgsProject.instance().addMapLayer(result_layer_pts)
        
        #add new point to existing points
        params={ 'CRS' : None, 'LAYERS' : [result_layer_tpt,result_layer_pts], 'OUTPUT' : 'TEMPORARY_OUTPUT' }
        result_mpts = processing.run("native:mergevectorlayers", params)
        result_layer_tpt = result_mpts['OUTPUT']

    #sort
    #params ={ 'ASCENDING' : True, 'EXPRESSION' : '\"order_id\"', 'INPUT' : result_layer_tpt, 'NULLS_FIRST' : False, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    #result_tpt = processing.run("native:orderbyexpression", params)
    #result_layer_tpt = result_tpt['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_tpt)
    QgsProject.instance().removeMapLayers( [result_layer_cl_seg.id()] )

    #Extend and rotate lines
    params ={ 'EXPRESSION' : 'extend(\r\n make_line(\r\n $geometry,\r\n project (\r\n $geometry, \r\n '+str(seg_w) +', \r\n radians(\"angle\"-90))\r\n ),\r\n '+str(seg_w) +',\r\n 0\r\n)', 'INPUT' : result_layer_tpt, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'OUTPUT_GEOMETRY' : 1, 'WITH_M' : False, 'WITH_Z' : False }
    result_rot = processing.run("native:geometrybyexpression", params)
    result_layer_rot = result_rot['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_rot)

    #sort
    params ={ 'ASCENDING' : True, 'EXPRESSION' : '\"order_id\"', 'INPUT' : result_layer_rot, 'NULLS_FIRST' : False, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_rot = processing.run("native:orderbyexpression", params)
    result_layer_rot = result_rot['OUTPUT']

    #populate order id
    params={ 'FIELD_LENGTH' : 0, 'FIELD_NAME' : 'order_id', 'FIELD_PRECISION' : 0, 'FIELD_TYPE' : 1, 'FORMULA' : '@row_number', 'INPUT' : result_layer_rot, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_rot = processing.run("native:fieldcalculator", params)
    result_layer_rot = result_rot['OUTPUT']

    #remove fields
    params={ 'FIELDS' : ['distance','angle','order_id'], 'INPUT' : result_layer_rot, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_rot = processing.run("native:retainfields", params)
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
    params = { 'CLOSE_PATH' : False, 'GROUP_EXPRESSION' : '', 'INPUT' : result_layer_sp, 'NATURAL_SORT' : False, 'ORDER_EXPRESSION' : '\"order_id\"', 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_p1 = processing.run("native:pointstopath", params)
    result_layer_p1 = result_p1['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_p1)

    params = { 'CLOSE_PATH' : False, 'GROUP_EXPRESSION' : '', 'INPUT' : result_layer_ep, 'NATURAL_SORT' : False, 'ORDER_EXPRESSION' : '\"order_id\"', 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_p2 = processing.run("native:pointstopath", params)
    result_layer_p2 = result_p2['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_p2)

    #merge paths
    params={ 'CRS' : None, 'LAYERS' : [result_layer_rot,result_layer_p1,result_layer_p2], 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_lines = processing.run("native:mergevectorlayers", params)
    result_layer_lines = result_lines['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_lines)

    #polygonize
    { 'INPUT' : result_layer_lines, 'KEEP_FIELDS' : True, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    params={ 'INPUT' : result_layer_lines, 'KEEP_FIELDS' : True, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_poly = processing.run("native:polygonize", params)
    result_layer_poly = result_poly['OUTPUT']
    #QgsProject.instance().addMapLayer(result_layer_poly)

    #populate order id
    params={ 'FIELD_LENGTH' : 0, 'FIELD_NAME' : 'order_id', 'FIELD_PRECISION' : 0, 'FIELD_TYPE' : 1, 'FORMULA' : '@row_number', 'INPUT' : result_layer_poly, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_poly = processing.run("native:fieldcalculator", params)
    result_layer_poly = result_poly['OUTPUT']

    #remove fields
    params={ 'FIELDS' : ['order_id'], 'INPUT' : result_layer_poly, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_poly = processing.run("native:retainfields", params)
    result_layer_poly = result_poly['OUTPUT']

    #add SEGMENT fields
    params={ 'FIELD_LENGTH' : 10, 'FIELD_NAME' : 'SEGMENT', 'FIELD_PRECISION' : 4, 'FIELD_TYPE' : 1, 'INPUT' : result_layer_poly, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_poly = processing.run("native:addfieldtoattributestable", params)
    params={ 'FIELD_LENGTH' : 0, 'FIELD_NAME' : 'SEGMENT', 'FIELD_PRECISION' : 0, 'FIELD_TYPE' : 1, 'FORMULA' : '@row_number', 'INPUT' : result_layer_poly, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_poly = processing.run("native:fieldcalculator", params)
    result_layer_poly = result_poly['OUTPUT']

    #remove existing Segments Layer
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "Segments":
            QgsProject.instance().removeMapLayers([lyr.id()])
    result_layer_poly.setName("Segments")
    QgsProject.instance().addMapLayer(result_layer_poly)

    #Create centerline layer
    #split centerline by transects
    params={ 'INPUT' : cl_lyr, 'LINES' : result_layer_rot, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_cl_seg = processing.run("native:splitwithlines", params)
    result_layer_cl_seg = result_cl_seg['OUTPUT']
    
    #add length field
    params={ 'CALC_METHOD' : 0, 'INPUT' : result_layer_cl_seg, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_cl_seg = processing.run("qgis:exportaddgeometrycolumns", params)
    result_layer_cl_seg = result_cl_seg['OUTPUT']
    
    #remove artifact segments
    params={ 'EXPRESSION' : ' \"length\" >0.1', 'INPUT' : result_layer_cl_seg, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_cl_seg = processing.run("native:extractbyexpression", params)
    result_layer_cl_seg = result_cl_seg['OUTPUT']

    #match segments
    params={ 'DISCARD_NONMATCHING' : True, 'INPUT' : result_layer_cl_seg, 'JOIN' : result_layer_poly, 'JOIN_FIELDS' : [], 'METHOD' : 2, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'PREDICATE' : [0], 'PREFIX' : '' }
    result_cl_seg3 = processing.run("native:joinattributesbylocation", params)
    result_layer_cl_seg3 = result_cl_seg3['OUTPUT']
    
    #fix geometry
    params={ 'INPUT' : result_layer_cl_seg3, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_cl_seg = processing.run("native:fixgeometries", params)
    result_layer_cl = result_cl_seg['OUTPUT']

    #add required fields to CL
    params={ 'FIELD_LENGTH' : 10, 'FIELD_NAME' : 'ELWS', 'FIELD_PRECISION' : 4, 'FIELD_TYPE' : 1, 'INPUT' : result_layer_cl, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_cl = processing.run("native:addfieldtoattributestable", params)
    result_layer_cl = result_cl['OUTPUT']
    params={ 'FIELD_LENGTH' : 10, 'FIELD_NAME' : 'FRIC', 'FIELD_PRECISION' : 4, 'FIELD_TYPE' : 1, 'INPUT' : result_layer_cl, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_cl = processing.run("native:addfieldtoattributestable", params)
    result_layer_cl = result_cl['OUTPUT']
    
    #remove extra fields
    params={ 'FIELDS' : ['order_id', 'SEGMENT', 'ELWS', 'FRIC'], 'INPUT' : result_layer_cl, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
    result_cl = processing.run("native:retainfields", params)
    result_layer_cl = result_cl['OUTPUT']

    #remove existing Centerline Layer
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "Centerline":
            QgsProject.instance().removeMapLayers([lyr.id()])
    result_layer_cl.setName("Centerline")
    QgsProject.instance().addMapLayer(result_layer_cl)
    
    #run convex check function
    segmentLayer = QgsProject.instance().mapLayersByName('Segments')[0]
    self.convexCheck(segmentLayer)

    #run centerline check function
    segmentLayer = QgsProject.instance().mapLayersByName('Segments')[0]
    transectLayer = QgsProject.instance().mapLayersByName('Transects')[0]
    #centerlineLayer = selectedLayer
    centerlineLayer = QgsProject.instance().mapLayersByName('Centerline')[0]
    self.centerlineCheck(segmentLayer, transectLayer, centerlineLayer)

    #run symbology check function
    segmentLayer = QgsProject.instance().mapLayersByName('Segments')[0]
    transectLayer = QgsProject.instance().mapLayersByName('Transects')[0]
    #centerlineLayer = selectedLayer
    centerlineLayer = QgsProject.instance().mapLayersByName('Centerline')[0]
    self.symbologyCheck(segmentLayer, transectLayer, centerlineLayer)