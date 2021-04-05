#!/usr/bin/env python
# coding: utf-8

# # Create Transects and Polygons from Centerline

# Note: The user input centerline shape file must have a Coordinate Reference System (CRS) that is projected as opposed to geographic. A CRS is also known as a Spatial Reference System (SRS). Examples of a projected CRS are a state plane or Universal Transverse Mercator (UTM).
# 

# ## Initialize

#get_ipython().system('jupyter nbextension enable --py --sys-prefix ipyleaflet')
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
#import ipywidgets as widgets
#from IPython.display import display, display_html
#from ipyfilechooser import FileChooser


# ## User Input Widgets


#Number of CE-QUAL-W2 Segments (USER INPUT)
Seg_No = 200

#Cross Section Width
width = 300  #(USER INPUT) [Units are the same as the projected CRS provided in the centerline shape file]

#Import shape file centerline (USER INPUT)
wrkDir = R"I:\2ERDC02 – WQ Model Enhancements FY2021\GIS\Data\LimnoTech"
pth_cl = wrkDir + R"\NapaRiver_CL_WGS84webMrctr_E.shp"
geo_df_cl = gpd.read_file(pth_cl)
geo_df_cl_cntrd = gpd.read_file(pth_cl)
geo_df_cl_bndry = gpd.read_file(pth_cl)
cl_crs = geo_df_cl.crs


# ## Find Vertices from Centerline


geo_df_cl['points'] = geo_df_cl.apply(lambda x: [y for y in x['geometry'].coords], axis=1)
cl_list = geo_df_cl['points'].tolist()
cl_array = np.array(cl_list)
cl_array_x = cl_array[0,...,0]
cl_array_y = cl_array[0,...,1]


# ## Find total length of the input Centerline

n = 0
dist_total = 0

for row in cl_array_x:
    if n == 0:
        x_pre = cl_array_x[n]
        y_pre = cl_array_y[n]
        n = n + 1
    else:
        x_n = cl_array_x[n]
        y_n = cl_array_y[n]
        dist_seg = np.sqrt((x_n - x_pre)**2 + (y_n - y_pre)**2)
        dist_total = dist_total + dist_seg
        x_pre = x_n
        y_pre = y_n
        n = n + 1
        cl_total_vertices = n


# ## Find W2 transect mid-points and centerline segment bounding vertices along input centerline

Seg_Lngth = dist_total / Seg_No
n = 0
k = 0
Seg_total = 0
clpts_w2Seg_total = Seg_No + 1
clpts_w2Seg_shape = (clpts_w2Seg_total, 1)
clpts_w2Seg_Dist = np.zeros(clpts_w2Seg_shape)
clpts_w2Seg_X = np.zeros(clpts_w2Seg_shape)
clpts_w2Seg_Y = np.zeros(clpts_w2Seg_shape)
clpts_w2Seg_bnd_X1 = np.zeros(clpts_w2Seg_shape)
clpts_w2Seg_bnd_X2 = np.zeros(clpts_w2Seg_shape)
clpts_w2Seg_bnd_Y1 = np.zeros(clpts_w2Seg_shape)
clpts_w2Seg_bnd_Y2 = np.zeros(clpts_w2Seg_shape)

for row in clpts_w2Seg_Dist: 
    if k == 0:  #this if condition populates the data for the first point along the centerline
        x_pre = cl_array_x[n]
        y_pre = cl_array_y[n]
        x_n = cl_array_x[n + 1]
        y_n = cl_array_y[n + 1]
        np.put(clpts_w2Seg_Dist, [k], [0])
        np.put(clpts_w2Seg_X, [k], [x_pre])
        np.put(clpts_w2Seg_Y, [k], [y_pre])
        np.put(clpts_w2Seg_bnd_X1, [k], [x_pre])
        np.put(clpts_w2Seg_bnd_X2, [k], [x_n])
        np.put(clpts_w2Seg_bnd_Y1, [k], [y_pre])
        np.put(clpts_w2Seg_bnd_Y2, [k], [y_n])
        k = k + 1
    elif k == (clpts_w2Seg_total - 1):  #this if condition populates the data for the last point along the centerline
        x_pre = cl_array_x[cl_total_vertices - 2]
        y_pre = cl_array_y[cl_total_vertices - 2]
        x_n = cl_array_x[cl_total_vertices - 1]
        y_n = cl_array_y[cl_total_vertices - 1]        
        np.put(clpts_w2Seg_Dist, [k], [dist_total])
        np.put(clpts_w2Seg_X, [k], [x_n])
        np.put(clpts_w2Seg_Y, [k], [y_n])
        np.put(clpts_w2Seg_bnd_X1, [k], [x_pre])
        np.put(clpts_w2Seg_bnd_X2, [k], [x_n])
        np.put(clpts_w2Seg_bnd_Y1, [k], [y_pre])
        np.put(clpts_w2Seg_bnd_Y2, [k], [y_n])
    else:
        running_total = 0
        Seg_total = Seg_total + Seg_Lngth
        np.put(clpts_w2Seg_Dist, [k], [Seg_total])
        n = 0
        x_pre = cl_array_x[n]
        y_pre = cl_array_y[n]
        n = n + 1
        while  Seg_total >= running_total:  #this while statement determines if the centerline segment has a W2 transect mid-point along it
            x_n = cl_array_x[n]
            y_n = cl_array_y[n]
            dist_seg = np.sqrt((x_n - x_pre)**2 + (y_n - y_pre)**2)
            running_total = running_total + dist_seg
            np.put(clpts_w2Seg_bnd_X1, [k], [x_pre])
            np.put(clpts_w2Seg_bnd_X2, [k], [x_n])
            np.put(clpts_w2Seg_bnd_Y1, [k], [y_pre])
            np.put(clpts_w2Seg_bnd_Y2, [k], [y_n])    
            x_pre = x_n
            y_pre = y_n
            n = n + 1    
        running_total_pre = running_total - dist_seg
        D = Seg_total - running_total_pre
        x_pre = cl_array_x[n - 2]
        y_pre = cl_array_y[n - 2]
        dx_sign = np.sign(x_n - x_pre)
        if dx_sign == 0: #this if statement traps the undefined slope of the cl segment
            #dx = 0 #x-coor is the same as x_pre since the cl segment is vertical
            dy_sign = np.sign(y_n - y_pre)
            dy = dy_sign * D
            cl_ptX = x_pre
            cl_ptY = y_pre + dy
        else:
            m_seg = (y_n - y_pre)/(x_n - x_pre)
            b = y_pre - (m_seg * x_pre)
            dx = D/(np.sqrt(1 + m_seg**2))
            dx = dx_sign * dx
            cl_ptX = x_pre + dx
            cl_ptY = m_seg * cl_ptX + b
            
        np.put(clpts_w2Seg_X, [k], [cl_ptX])
        np.put(clpts_w2Seg_Y, [k], [cl_ptY])
        k = k + 1


# ## Find End Points in the Transect

n = 0
d = width/2

clpts_w2Seg_m_seg = np.zeros((clpts_w2Seg_Y.shape))
clpts_w2Seg_m = np.zeros((clpts_w2Seg_Y.shape))
clpts_w2Seg_ptX2_pos = np.zeros((clpts_w2Seg_Y.shape))
clpts_w2Seg_ptY2_pos = np.zeros((clpts_w2Seg_Y.shape))
clpts_w2Seg_ptX2_neg = np.zeros((clpts_w2Seg_Y.shape))
clpts_w2Seg_ptY2_neg = np.zeros((clpts_w2Seg_Y.shape))
width_Check_array = np.zeros((clpts_w2Seg_Y.shape))


for row in clpts_w2Seg_X:
    segX1 = clpts_w2Seg_bnd_X1[n]
    segX2 = clpts_w2Seg_bnd_X2[n]
    segY1 = clpts_w2Seg_bnd_Y1[n]
    segY2 = clpts_w2Seg_bnd_Y2[n]
    ptX1 = clpts_w2Seg_X[n] #This is the same value as row
    ptY1 = clpts_w2Seg_Y[n]
    dx_seg = segX2 - segX1
    dy_seg = segY2 - segY1
    if dx_seg == 0:
        ptX2_pos = ptX1 + d
        ptX2_neg = ptX1 - d
        ptY2_pos = ptY1
        ptY2_neg = ptY1
    elif dy_seg == 0:
        ptX2_pos = ptX1
        ptX2_neg = ptX1
        ptY2_pos = ptY1 + d
        ptY2_neg = ptY1 - d
    else:
        m_seg = (dy_seg)/(dx_seg)
        m = -1 / m_seg    #This is the slope perpendicular to the CenterLine segment
        b = ptY1 - (m * ptX1)
        dX = d/(np.sqrt(1 + m**2))
        ptX2_pos = ptX1 + dX
        ptX2_neg = ptX1 - dX
        ptY2_pos = m * ptX2_pos + b
        ptY2_neg = m * ptX2_neg + b
    width_Check = np.sqrt((ptX2_pos - ptX2_neg)**2 + (ptY2_pos - ptY2_neg)**2)
    if ((segX2 - segX1) * m) > (segY2 - segY1):
        ptX2_pos_crss = ptX2_pos
        ptY2_pos_crss = ptY2_pos
        ptX2_neg_crss = ptX2_neg
        ptY2_neg_crss = ptY2_neg    
    else:
        ptX2_neg_crss = ptX2_pos
        ptY2_neg_crss = ptY2_pos
        ptX2_pos_crss = ptX2_neg
        ptY2_pos_crss = ptY2_neg
    np.put(clpts_w2Seg_m_seg, [n], [m_seg])
    np.put(clpts_w2Seg_m, [n], [m])
    np.put(clpts_w2Seg_ptX2_pos, [n], [ptX2_pos_crss])
    np.put(clpts_w2Seg_ptY2_pos, [n], [ptY2_pos_crss])
    np.put(clpts_w2Seg_ptX2_neg, [n], [ptX2_neg_crss])
    np.put(clpts_w2Seg_ptY2_neg, [n], [ptY2_neg_crss])
    np.put(width_Check_array, [n], [width_Check])
    n = n + 1


# ## Create Geopanda Data Frame for Transect Lines

#Create transect end point array
transect_pts_A = np.column_stack((clpts_w2Seg_Dist, clpts_w2Seg_ptX2_pos, clpts_w2Seg_ptY2_pos))
transect_pts_B = np.column_stack((clpts_w2Seg_Dist, clpts_w2Seg_ptX2_neg, clpts_w2Seg_ptY2_neg))
transect_pts = np.concatenate((transect_pts_A, transect_pts_B), axis=0)

#Create pandas data frame for transect end points
df_transects = pd.DataFrame(data=transect_pts, columns=["cl_Distance", "Transect_Xcoor", "Transect_Ycoor"])

#Zip the coordinates into a point object and convert to a geopanda data frame
geometry = [Point(xy) for xy in zip(df_transects.Transect_Xcoor, df_transects.Transect_Ycoor)]
geo_df_transect_pts = gpd.GeoDataFrame(df_transects, geometry=geometry)

#Create geopanda data frame for transect lines
geo_df_transect_lines = geo_df_transect_pts.groupby(['cl_Distance'])['geometry'].apply(lambda x: LineString(x.tolist()))
geo_df_transect_lines = gpd.GeoDataFrame(geo_df_transect_lines, geometry='geometry', crs = cl_crs)





# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/

# A Python3 program to find if 2 given line segments intersect or not 
  
class Point: 
    def __init__(self, x, y): 
        self.x = x 
        self.y = y 
  
# Given three colinear points p, q, r, the function checks if  
# point q lies on line segment 'pr'  
def onSegment(p, q, r): 
    if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and 
           (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))): 
        return True
    return False
  
def orientation(p, q, r): 
    # to find the orientation of an ordered triplet (p,q,r) 
    # function returns the following values: 
    # 0 : Colinear points 
    # 1 : Clockwise points 
    # 2 : Counterclockwise 
      
    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/  
    # for details of below formula.  
      
    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y)) 
    if (val > 0): 
          
        # Clockwise orientation 
        return 1
    elif (val < 0): 
          
        # Counterclockwise orientation 
        return 2
    else: 
          
        # Colinear orientation 
        return 0
  
# The main function that returns true if  
# the line segment 'p1q1' and 'p2q2' intersect. 
def doIntersect(p1,q1,p2,q2): 
      
    # Find the 4 orientations required for  
    # the general and special cases 
    o1 = orientation(p1, q1, p2) 
    o2 = orientation(p1, q1, q2) 
    o3 = orientation(p2, q2, p1) 
    o4 = orientation(p2, q2, q1) 
  
    # General case 
    if ((o1 != o2) and (o3 != o4)): 
        return True
  
    # Special Cases 
  
    # p1 , q1 and p2 are colinear and p2 lies on segment p1q1 
    if ((o1 == 0) and onSegment(p1, p2, q1)): 
        return True
  
    # p1 , q1 and q2 are colinear and q2 lies on segment p1q1 
    if ((o2 == 0) and onSegment(p1, q2, q1)): 
        return True
  
    # p2 , q2 and p1 are colinear and p1 lies on segment p2q2 
    if ((o3 == 0) and onSegment(p2, p1, q2)): 
        return True
  
    # p2 , q2 and q1 are colinear and q1 lies on segment p2q2 
    if ((o4 == 0) and onSegment(p2, q1, q2)): 
        return True
  
    # If none of the cases 
    return False


# ## Create and populate CE-QUAL-W2 polygons point arrays

chck_plygn_arry = np.array([0,1,2,3])
n = 1 #starting "for loop" at second record of the "clpts_w2Seg_pts#2_***" arrays to facilitate calling previous transect points
clpts_w2Segplygn_shape = (Seg_No, 1)
w2Seg_plygn_pt1_X = np.zeros((clpts_w2Segplygn_shape))
w2Seg_plygn_pt2_X = np.zeros((clpts_w2Segplygn_shape))
w2Seg_plygn_pt3_X = np.zeros((clpts_w2Segplygn_shape))
w2Seg_plygn_pt4_X = np.zeros((clpts_w2Segplygn_shape))
w2Seg_plygn_pt1_Y = np.zeros((clpts_w2Segplygn_shape))
w2Seg_plygn_pt2_Y = np.zeros((clpts_w2Segplygn_shape))
w2Seg_plygn_pt3_Y = np.zeros((clpts_w2Segplygn_shape))
w2Seg_plygn_pt4_Y = np.zeros((clpts_w2Segplygn_shape))
w2Seg_plygn_cldist = np.zeros((clpts_w2Segplygn_shape))
w2Seg_plygn_ID = np.zeros((clpts_w2Segplygn_shape))
w2Seg_plygn_convex = np.zeros((clpts_w2Segplygn_shape))
w2Seg_plygn_intersect = np.zeros((clpts_w2Segplygn_shape))
for row in w2Seg_plygn_pt1_X:
    pt1_X = clpts_w2Seg_ptX2_neg[n]
    pt1_Y = clpts_w2Seg_ptY2_neg[n]
    pt2_X = clpts_w2Seg_ptX2_pos[n]
    pt2_Y = clpts_w2Seg_ptY2_pos[n]
    pt3_X = clpts_w2Seg_ptX2_pos[n - 1]
    pt3_Y = clpts_w2Seg_ptY2_pos[n - 1]
    pt4_X = clpts_w2Seg_ptX2_neg[n - 1]
    pt4_Y = clpts_w2Seg_ptY2_neg[n - 1]
    cldist = clpts_w2Seg_Dist[n]
    plygn_ID = n
    #The following "for" statement checks for Concave CE-QUAL-W2 polygons
    for row in chck_plygn_arry:
        plygn_chck =         np.sign((pt2_X - pt1_X) * (pt3_Y - pt2_Y) - (pt3_X - pt2_X) * (pt2_Y - pt1_Y)) +         np.sign((pt3_X - pt2_X) * (pt4_Y - pt3_Y) - (pt4_X - pt3_X) * (pt3_Y - pt2_Y)) +         np.sign((pt4_X - pt3_X) * (pt1_Y - pt4_Y) - (pt1_X - pt4_X) * (pt4_Y - pt3_Y)) +         np.sign((pt1_X - pt4_X) * (pt2_Y - pt1_Y) - (pt2_X - pt1_X) * (pt1_Y - pt4_Y)) 
        if plygn_chck == 4:
            convex_plygn = 1
        else:
            convex_plygn = 0
    
    
    #The following "for" statement checks if polygon line segment pt2 to pt3 crosses any centerline segment
    k = 0
    intersect_cnt_pt2pt3 = 0
    for row in cl_array_x:
        if k == 0:
            k = k + 1
        else:
            p1 = Point(pt2_X, pt2_Y) 
            q1 = Point(pt3_X, pt3_Y) 
            p2 = Point(cl_array_x[k], cl_array_y[k]) 
            q2 = Point(cl_array_x[k - 1], cl_array_y[k - 1]) 

            if doIntersect(p1, q1, p2, q2): 
                intersect_cnt_pt2pt3 =  intersect_cnt_pt2pt3 + 1
            k = k + 1
 
    #The following "for" statement checks if polygon line segment pt4 to pt1 crosses any centerline segment
    k = 0
    intersect_cnt_pt4pt1 = 0
    for row in cl_array_x:
        if k == 0:
            k = k + 1
        else:
            p1 = Point(pt4_X, pt4_Y) 
            q1 = Point(pt1_X, pt1_Y) 
            p2 = Point(cl_array_x[k], cl_array_y[k]) 
            q2 = Point(cl_array_x[k - 1], cl_array_y[k - 1]) 

            if doIntersect(p1, q1, p2, q2): 
                intersect_cnt_pt4pt1 =  intersect_cnt_pt4pt1 + 1
            k = k + 1
        
    intersect_cnt = intersect_cnt_pt2pt3 + intersect_cnt_pt4pt1
    if intersect_cnt > 0:
        cl_intersect = 1
    else:
        cl_intersect = 0
    
    np.put(w2Seg_plygn_pt1_X, [n - 1], [pt1_X])
    np.put(w2Seg_plygn_pt2_X, [n - 1], [pt2_X])
    np.put(w2Seg_plygn_pt3_X, [n - 1], [pt3_X])
    np.put(w2Seg_plygn_pt4_X, [n - 1], [pt4_X])
    np.put(w2Seg_plygn_pt1_Y, [n - 1], [pt1_Y])
    np.put(w2Seg_plygn_pt2_Y, [n - 1], [pt2_Y])
    np.put(w2Seg_plygn_pt3_Y, [n - 1], [pt3_Y])
    np.put(w2Seg_plygn_pt4_Y, [n - 1], [pt4_Y])
    np.put(w2Seg_plygn_cldist, [n - 1], [cldist])
    np.put(w2Seg_plygn_ID, [n - 1], [plygn_ID])
    np.put(w2Seg_plygn_convex, [n - 1], [convex_plygn])
    np.put(w2Seg_plygn_intersect, [n - 1], [cl_intersect])
    n = n + 1


# ## Create Geopanda Data Frame for W2 Polygon Segments

#Assemble polygon points for use in pandas
polygon_pts_A = np.column_stack((w2Seg_plygn_ID, w2Seg_plygn_cldist, w2Seg_plygn_pt1_X, w2Seg_plygn_pt1_Y))
polygon_pts_B = np.column_stack((w2Seg_plygn_ID, w2Seg_plygn_cldist, w2Seg_plygn_pt2_X, w2Seg_plygn_pt2_Y))
polygon_pts_C = np.column_stack((w2Seg_plygn_ID, w2Seg_plygn_cldist, w2Seg_plygn_pt3_X, w2Seg_plygn_pt3_Y))
polygon_pts_D = np.column_stack((w2Seg_plygn_ID, w2Seg_plygn_cldist, w2Seg_plygn_pt4_X, w2Seg_plygn_pt4_Y))
polygon_pts = np.concatenate((polygon_pts_A, polygon_pts_B, polygon_pts_C, polygon_pts_D), axis=0)

#Create pandas data frame for W2 polygon segments
df_polygon = pd.DataFrame(data=polygon_pts, columns=["w2SegID", "cl_Distance", "plygn_Xcoor", "plygn_Ycoor"])
df_polygon.to_excel("df_polygoncheck_coordinates.xlsx")

#Zip the coordinates into a point object and convert to a geopanda data frame
#geometry = [Point(xy) for xy in zip(df_polygon.plygn_Xcoor, df_polygon.plygn_Ycoor)]
#geo_df_polygon_pts = gpd.GeoDataFrame(df_polygon, geometry=geometry)

#Create geopanda data frame for W2 polygon segments
#geo_df_polygon = geo_df_polygon_pts.groupby(['w2SegID'])['geometry'].apply(lambda x: Polygon(x.tolist()))
#geo_df_polygon = gpd.GeoDataFrame(geo_df_polygon, geometry='geometry', crs = cl_crs)

geo_df_polygon = gpd.GeoDataFrame()
geo_df_polygon_itr = gpd.GeoDataFrame()
 
for name, group in df_polygon.groupby('w2SegID'): 
    current_w2SegID = name
    #print("w2SegID: ",name)
    if len(group)>= 4:
        poly = Polygon(zip(group.plygn_Xcoor, group.plygn_Ycoor)) #
        geo_df_polygon_itr.loc[0, 'geometry'] = poly
        geo_df_polygon_itr.loc[0, 'w2SegID'] = current_w2SegID
        geo_df_polygon = geo_df_polygon.append(geo_df_polygon_itr)

geo_df_polygon = geo_df_polygon.set_crs(cl_crs, allow_override=True)

#Add attributes to W2 polygon segments
geo_df_polygon['w2SegID_B'] = w2Seg_plygn_ID
geo_df_polygon['cl_Distance'] = w2Seg_plygn_cldist
geo_df_polygon['convex'] = w2Seg_plygn_convex
geo_df_polygon['cl_intersect'] = w2Seg_plygn_intersect

#Create geopanda data frame for W2 polygon segment concave check
geo_df_polygon_check = geo_df_polygon[geo_df_polygon['convex']==0]

#Create geopanda data frame for W2 polygon segment that the centerline intersects
geo_df_polygon_intersect = geo_df_polygon[geo_df_polygon['cl_intersect']==1]

