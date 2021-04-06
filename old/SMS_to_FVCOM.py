# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 16:13:34 2020

@author: jrutyna
"""

### NOTE: this files assumes the x/y data from SMS is in long/Lat referenced to WGS84 ###

import fromPyFVCOM

### Provide filename of SMS *.2dm file or path/filename if not in same directory ###

mesh_2dm = 'meshGen_4d_pt3_latlong.2dm'



### Read *.2dm file ###

functionReturn = fromPyFVCOM.read_sms_mesh(mesh_2dm)

triangles = functionReturn[0]
nodes = functionReturn[1]
x = functionReturn[2]
y = functionReturn[3]
z = functionReturn[4]
types = functionReturn[5]



### Write FVCOM grid and depth *.dat files; please provide filename or path/filename

FVCOM_mesh = 'FVCOM_grd.dat'
FVCOM_depth = 'FVCOM_dep.dat'
fromPyFVCOM.write_fvcom_mesh(triangles, nodes, x, y, z, FVCOM_mesh, extra_depth=FVCOM_depth)



### Create and Export Node & Element Shapefiles ###

import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

### Nodes Shapefile
df_nodes = pd.DataFrame({'NodeID': nodes, 'Latitude': y,'Longitude': x})
FVCOM_nodes = gpd.GeoDataFrame(df_nodes, geometry=gpd.points_from_xy(df_nodes.Longitude, df_nodes.Latitude))
FVCOM_nodes.crs = {'proj': 'latlong', 'ellps': 'WGS84', 'datum': 'WGS84', 'no_defs': True}
outfp_nodes = 'FVCOM_nodes.shp'
FVCOM_nodes.to_file(outfp_nodes)


### Elements Shapefile
element_count = len(triangles)
elements_no = list(range(1, element_count + 1))

df_elements = pd.DataFrame({'ElementID': elements_no, 'NodeID': triangles[:,0] + 1})
df_elements2 = pd.DataFrame({'ElementID': elements_no, 'NodeID': triangles[:,1] + 1})
df_elements3 = pd.DataFrame({'ElementID': elements_no, 'NodeID': triangles[:,2] + 1})

df_elements = df_elements.append(df_elements2,  ignore_index = True)
df_elements = df_elements.append(df_elements3,  ignore_index = True)

df_elements = pd.merge(df_elements, df_nodes)

FVCOM_elements = gpd.GeoDataFrame()
FVCOM_elements_itr = gpd.GeoDataFrame()
 
for name, group in df_elements.groupby('ElementID'): 
    # print the ID value
    current_ElementID = name
    print("ElementID: ",name)
    # print the rows
    #print(group)
    # print the Polygon
    if len(group)>= 3:
        poly = Polygon(zip(group.Longitude, group.Latitude)) #
        FVCOM_elements_itr.loc[0, 'geometry'] = poly
        FVCOM_elements_itr.loc[0, 'ElementID'] = current_ElementID
        FVCOM_elements = FVCOM_elements.append(FVCOM_elements_itr)
        #print(poly.wkt)

FVCOM_elements.crs = {'proj': 'latlong', 'ellps': 'WGS84', 'datum': 'WGS84', 'no_defs': True}
outfp_elements = 'FVCOM_elements.shp'
FVCOM_elements.to_file(outfp_elements)
