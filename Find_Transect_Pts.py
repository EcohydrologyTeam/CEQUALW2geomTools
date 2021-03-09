# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 12:39:13 2021

@author: jrutyna
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, shape


#Number of CE-QUAL-W2 Segments (USER INPUT)
Seg_No = 100



#Import Shapefile Centerline (USER INPUT)
wrkDir = R"I:\2ERDC02 – WQ Model Enhancements FY2021\GIS\Data\LimnoTech"
pth_CL = wrkDir + R"\NapaRiver_CL.shp"
geo_df_CL = gpd.read_file(pth_CL)
CL_crs = geo_df_CL.crs



#Find Vertices from Centerline
geo_df_CL['points'] = geo_df_CL.apply(lambda x: [y for y in x['geometry'].coords], axis=1)
CL_list = geo_df_CL['points'].tolist()
CL_array = np.array(CL_list)
CL_array_x = CL_array[0,...,0]
CL_array_y = CL_array[0,...,1]



#Find total length of the input Centerline
n = 0
dist_total = 0

for row in CL_array_x:
    if n == 0:
        x_pre = CL_array_x[n]
        y_pre = CL_array_y[n]
        n = n + 1
    else:
        x_n = CL_array_x[n]
        y_n = CL_array_y[n]
        dist_seg = np.sqrt((x_n - x_pre)**2 + (y_n - y_pre)**2)
        dist_total = dist_total + dist_seg
        x_pre = x_n
        y_pre = y_n
        n = n + 1
        CL_total_vertices = n



#Find W2 transect mid-points and centerline segment bounding vertices along input centerline
Seg_Lngth = dist_total / Seg_No
n = 0
k = 0
Seg_total = 0
CLpts_W2seg_total = Seg_No + 1
CLpts_W2seg_shape = (CLpts_W2seg_total, 1)
CLpts_W2seg_Dist = np.zeros(CLpts_W2seg_shape)
CLpts_W2seg_X = np.zeros(CLpts_W2seg_shape)
CLpts_W2seg_Y = np.zeros(CLpts_W2seg_shape)
CLpts_W2seg_bnd_X1 = np.zeros(CLpts_W2seg_shape)
CLpts_W2seg_bnd_X2 = np.zeros(CLpts_W2seg_shape)
CLpts_W2seg_bnd_Y1 = np.zeros(CLpts_W2seg_shape)
CLpts_W2seg_bnd_Y2 = np.zeros(CLpts_W2seg_shape)

for row in CLpts_W2seg_Dist: 
    if k == 0:  #this if condition populates the data for the first point along the centerline
        x_pre = CL_array_x[n]
        y_pre = CL_array_y[n]
        x_n = CL_array_x[n + 1]
        y_n = CL_array_y[n + 1]
        np.put(CLpts_W2seg_Dist, [k], [0])
        np.put(CLpts_W2seg_X, [k], [x_pre])
        np.put(CLpts_W2seg_Y, [k], [y_pre])
        np.put(CLpts_W2seg_bnd_X1, [k], [x_pre])
        np.put(CLpts_W2seg_bnd_X2, [k], [x_n])
        np.put(CLpts_W2seg_bnd_Y1, [k], [y_pre])
        np.put(CLpts_W2seg_bnd_Y2, [k], [y_n])
        k = k + 1
    elif k == (CLpts_W2seg_total - 1):  #this if condition populates the data for the last point along the centerline
        x_pre = CL_array_x[CL_total_vertices - 2]
        y_pre = CL_array_y[CL_total_vertices - 2]
        x_n = CL_array_x[CL_total_vertices - 1]
        y_n = CL_array_y[CL_total_vertices - 1]        
        np.put(CLpts_W2seg_Dist, [k], [dist_total])
        np.put(CLpts_W2seg_X, [k], [x_n])
        np.put(CLpts_W2seg_Y, [k], [y_n])
        np.put(CLpts_W2seg_bnd_X1, [k], [x_pre])
        np.put(CLpts_W2seg_bnd_X2, [k], [x_n])
        np.put(CLpts_W2seg_bnd_Y1, [k], [y_pre])
        np.put(CLpts_W2seg_bnd_Y2, [k], [y_n])
    else:
        running_total = 0
        Seg_total = Seg_total + Seg_Lngth
        np.put(CLpts_W2seg_Dist, [k], [Seg_total])
        n = 0
        x_pre = CL_array_x[n]
        y_pre = CL_array_y[n]
        n = n + 1
        while  Seg_total >= running_total:  #this while statement determines if the centerline segment has a W2 transect mid-point along it
            x_n = CL_array_x[n]
            y_n = CL_array_y[n]
            dist_seg = np.sqrt((x_n - x_pre)**2 + (y_n - y_pre)**2)
            running_total = running_total + dist_seg
            np.put(CLpts_W2seg_bnd_X1, [k], [x_pre])
            np.put(CLpts_W2seg_bnd_X2, [k], [x_n])
            np.put(CLpts_W2seg_bnd_Y1, [k], [y_pre])
            np.put(CLpts_W2seg_bnd_Y2, [k], [y_n])    
            x_pre = x_n
            y_pre = y_n
            n = n + 1    
        running_total_pre = running_total - dist_seg
        D = Seg_total - running_total_pre
        x_pre = CL_array_x[n - 2]
        y_pre = CL_array_y[n - 2]
        dx_sign = np.sign(x_n - x_pre)
        if dx_sign == 0: #this if statement traps the undefined slope of the CL segment
            #dx = 0 #x-coor is the same as x_pre since the CL segment is vertical
            dy_sign = np.sign(y_n - y_pre)
            dy = dy_sign * D
            CL_PtX = x_pre
            CL_PtY = y_pre + dy
        else:
            m_seg = (y_n - y_pre)/(x_n - x_pre)
            b = y_pre - (m_seg * x_pre)
            dx = D/(np.sqrt(1 + m_seg**2))
            dx = dx_sign * dx
            CL_PtX = x_pre + dx
            CL_PtY = m_seg * CL_PtX + b
            
        np.put(CLpts_W2seg_X, [k], [CL_PtX])
        np.put(CLpts_W2seg_Y, [k], [CL_PtY])
        k = k + 1


    

######### The following was temporary code to read previously exported csv files from previously generated QGIS shapefiles ######### 

#Read Input Files
#filePath_CLpts_W2seg = R'I:/2ERDC02 – WQ Model Enhancements FY2021/GIS/Data/LimnoTech/2021_0303/TEMP_CL_pts_geom_2021_0303.csv'
#CLpts_W2seg = np.genfromtxt(filePath_CLpts_W2seg, delimiter=',',skip_header=1)

#filePath_CLpts_W2seg_bnd = R'I:/2ERDC02 – WQ Model Enhancements FY2021/GIS/Data/LimnoTech/2021_0303/TEMP_CL_sgmts_slctd_pts_geom_2021_0303.csv'
#CLpts_W2seg_bnd = np.genfromtxt(filePath_CLpts_W2seg_bnd, delimiter=',',skip_header=1)


#Retrieve Coordinate Information from Input Arrays
#CLpts_W2seg_Dist = CLpts_W2seg[..., 5]
#CLpts_W2seg_X = CLpts_W2seg[..., 7]
#CLpts_W2seg_Y = CLpts_W2seg[..., 8]

#CLpts_W2seg_bnd_X = CLpts_W2seg_bnd[..., 19]
#CLpts_W2seg_bnd_Y = CLpts_W2seg_bnd[..., 20]

#Reorganize X1 and X2 from Input Arrays
#n = 0
#odd_ct = 0
#even_ct = 0

#CLpts_W2seg_bnd_X1 = np.zeros((CLpts_W2seg_X.shape))
#CLpts_W2seg_bnd_X2 = np.zeros((CLpts_W2seg_X.shape))

#for row in CLpts_W2seg_bnd_X:
#    n = n + 1
#    if (n % 2) == 0:
#        np.put(CLpts_W2seg_bnd_X2, [even_ct], [row])
#        even_ct = even_ct + 1
#    else:
#        np.put(CLpts_W2seg_bnd_X1, [odd_ct], [row])
#        odd_ct = odd_ct + 1


#Reorganize Y1 and Y2 from Input Arrays
#n = 0
#odd_ct = 0
#even_ct = 0

#CLpts_W2seg_bnd_Y1 = np.zeros((CLpts_W2seg_Y.shape))
#CLpts_W2seg_bnd_Y2 = np.zeros((CLpts_W2seg_Y.shape))

#for row in CLpts_W2seg_bnd_Y:
#    n = n + 1
#    if (n % 2) == 0:
#        np.put(CLpts_W2seg_bnd_Y2, [even_ct], [row])
#        even_ct = even_ct + 1
#    else:
#        np.put(CLpts_W2seg_bnd_Y1, [odd_ct], [row])
#        odd_ct = odd_ct + 1

######### The previous was temporary code to read previously exported csv files from previously generated QGIS shapefiles  ######### 



#Find End Points in the Transect
n = 0
Width = 1000  #(USER INPUT)
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
    PtX1 = CLpts_W2seg_X[n] #This is the same value as row
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


#Create transect end point array
Transect_Pts_A = np.column_stack((CLpts_W2seg_Dist, CLpts_W2seg_PtX2_pos, CLpts_W2seg_PtY2_pos))
Transect_Pts_B = np.column_stack((CLpts_W2seg_Dist, CLpts_W2seg_PtX2_neg, CLpts_W2seg_PtY2_neg))
Transect_Pts = np.concatenate((Transect_Pts_A, Transect_Pts_B), axis=0)

#Create pandas data frame for transect end points
df_transects = pd.DataFrame(data=Transect_Pts, columns=["CL_Distance", "Transect_Xcoor", "Transect_Ycoor"])

#Zip the coordinates into a point object and convert to a geopanda data frame
geometry = [Point(xy) for xy in zip(df_transects.Transect_Xcoor, df_transects.Transect_Ycoor)]
geo_df_transect_pts = gpd.GeoDataFrame(df_transects, geometry=geometry)

#Create geopanda data frame for transect lines
geo_df_transect_lines = geo_df_transect_pts.groupby(['CL_Distance'])['geometry'].apply(lambda x: LineString(x.tolist()))
geo_df_transect_lines = gpd.GeoDataFrame(geo_df_transect_lines, geometry='geometry', crs = CL_crs)

#Export transect lines shape file
pth_transectLines = wrkDir + R"\TEMP_CL_Transect_Lines.shp"
geo_df_transect_lines.to_file(pth_transectLines)

    
    