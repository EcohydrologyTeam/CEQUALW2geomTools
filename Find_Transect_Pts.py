# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 12:39:13 2021

@author: jrutyna
"""
import numpy as np


#Read Input Files
filePath_CLpts_W2seg = R'I:/2ERDC02 – WQ Model Enhancements FY2021/GIS/Data/LimnoTech/2021_0303/TEMP_CL_pts_geom_2021_0303.csv'
CLpts_W2seg = np.genfromtxt(filePath_CLpts_W2seg, delimiter=',',skip_header=1)

filePath_CLpts_W2seg_bnd = R'I:/2ERDC02 – WQ Model Enhancements FY2021/GIS/Data/LimnoTech/2021_0303/TEMP_CL_sgmts_slctd_pts_geom_2021_0303.csv'
CLpts_W2seg_bnd = np.genfromtxt(filePath_CLpts_W2seg_bnd, delimiter=',',skip_header=1)


#Retrieve Coordinate Information from Input Arrays
CLpts_W2seg_Dist = CLpts_W2seg[..., 5]
CLpts_W2seg_X = CLpts_W2seg[..., 7]
CLpts_W2seg_Y = CLpts_W2seg[..., 8]

CLpts_W2seg_bnd_X = CLpts_W2seg_bnd[..., 19]
CLpts_W2seg_bnd_Y = CLpts_W2seg_bnd[..., 20]

#Reorganize X1 and X2 from Input Arrays
n = 0
odd_ct = 0
even_ct = 0

CLpts_W2seg_bnd_X1 = np.zeros((CLpts_W2seg_X.shape))
CLpts_W2seg_bnd_X2 = np.zeros((CLpts_W2seg_X.shape))

for row in CLpts_W2seg_bnd_X:
    n = n + 1
    if (n % 2) == 0:
        np.put(CLpts_W2seg_bnd_X2, [even_ct], [row])
        even_ct = even_ct + 1
    else:
        np.put(CLpts_W2seg_bnd_X1, [odd_ct], [row])
        odd_ct = odd_ct + 1


#Reorganize Y1 and Y2 from Input Arrays
n = 0
odd_ct = 0
even_ct = 0

CLpts_W2seg_bnd_Y1 = np.zeros((CLpts_W2seg_Y.shape))
CLpts_W2seg_bnd_Y2 = np.zeros((CLpts_W2seg_Y.shape))

for row in CLpts_W2seg_bnd_Y:
    n = n + 1
    if (n % 2) == 0:
        np.put(CLpts_W2seg_bnd_Y2, [even_ct], [row])
        even_ct = even_ct + 1
    else:
        np.put(CLpts_W2seg_bnd_Y1, [odd_ct], [row])
        odd_ct = odd_ct + 1


#Find End Points in the Transect
n = 0
Width = 1000
D = Width/2

CLpts_W2seg_m_seg = np.zeros((CLpts_W2seg_Y.shape))
CLpts_W2seg_m = np.zeros((CLpts_W2seg_Y.shape))
CLpts_W2seg_PtX2_pos = np.zeros((CLpts_W2seg_Y.shape))
CLpts_W2seg_PtY2_pos = np.zeros((CLpts_W2seg_Y.shape))
CLpts_W2seg_PtX2_neg = np.zeros((CLpts_W2seg_Y.shape))
CLpts_W2seg_PtY2_neg = np.zeros((CLpts_W2seg_Y.shape))
Width_Check_array = np.zeros((CLpts_W2seg_Y.shape))


for row in CLpts_W2seg_X:
    SegX1 = CLpts_W2seg_bnd_X1[n]
    SegX2 = CLpts_W2seg_bnd_X2[n]
    SegY1 = CLpts_W2seg_bnd_Y1[n]
    SegY2 = CLpts_W2seg_bnd_Y2[n]
    PtX1 = CLpts_W2seg_X[n]
    PtY1 = CLpts_W2seg_Y[n]
    m_seg = (SegY2 - SegY1)/(SegX2 - SegX1) #Need an if statement here to trap errors with zero & undefined slopes
    m = -1 / m_seg    #This is the slope perpendicular to the CenterLine Segment
    b = PtY1 - (m * PtX1)
    dX = D/(np.sqrt(1 + m**2))
    PtX2_pos = PtX1 + dX
    PtX2_neg = PtX1 - dX
    PtY2_pos = m * PtX2_pos + b
    PtY2_neg = m * PtX2_neg + b
    Width_Check = np.sqrt((PtX2_pos - PtX2_neg)**2 + (PtY2_pos - PtY2_neg)**2)
    np.put(CLpts_W2seg_m_seg, [n], [m_seg])
    np.put(CLpts_W2seg_m, [n], [m])
    np.put(CLpts_W2seg_PtX2_pos, [n], [PtX2_pos])
    np.put(CLpts_W2seg_PtY2_pos, [n], [PtY2_pos])
    np.put(CLpts_W2seg_PtX2_neg, [n], [PtX2_neg])
    np.put(CLpts_W2seg_PtY2_neg, [n], [PtY2_neg])
    np.put(Width_Check_array, [n], [Width_Check])
    n = n + 1


Transect_Pts_A = np.column_stack((CLpts_W2seg_Dist, CLpts_W2seg_PtX2_pos, CLpts_W2seg_PtY2_pos))
Transect_Pts_B = np.column_stack((CLpts_W2seg_Dist, CLpts_W2seg_PtX2_neg, CLpts_W2seg_PtY2_neg))
Transect_Pts = np.concatenate((Transect_Pts_A, Transect_Pts_B), axis=0)


import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, shape

wrkDir = R"I:\2ERDC02 – WQ Model Enhancements FY2021\GIS\Data\LimnoTech"
pth_CL = wrkDir + R"\NapaRiver_CL.shp"
geo_df_CL = gpd.read_file(pth_CL)

df_transects = pd.DataFrame(data=Transect_Pts, columns=["CL_Distance", "Transect_Xcoor", "Transect_Ycoor"])

#zip the coordinates into a point object and convert to a GeoData Frame
geometry = [Point(xy) for xy in zip(df_transects.Transect_Xcoor, df_transects.Transect_Ycoor)]
geo_df_transect_pts = gpd.GeoDataFrame(df_transects, geometry=geometry)

geo_df_transect_lines = geo_df_transect_pts.groupby(['CL_Distance'])['geometry'].apply(lambda x: LineString(x.tolist()))
geo_df_transect_lines = gpd.GeoDataFrame(geo_df_transect_lines, geometry='geometry')

CL_crs = geo_df_CL.crs
#geo_df_transect_lines.to_crs(CL_crs) #still need to assign a crs to this layer...JMR thinks it is a geopandas version issue because this worked previously before qgis downgraded geopanda version

pth_transectLines = wrkDir + R"\TEMP_CL_Transect_Lines.shp"
geo_df_transect_lines.to_file(pth_transectLines)

    
    