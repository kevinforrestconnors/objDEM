import sys
import os
import array
import urllib.request
from scipy.spatial import Delaunay
import numpy as np

elevation_data = []

m_per_deg_lat = 111619

def fetch_elevation_data(min_long=-113.36, min_lat=36.0, max_long=-113.13, max_lat=36.23, resolution=30):

    if (resolution < 30):
        resolution = 30

    resolution_in_deg = resolution / m_per_deg_lat

    long_range = max_long - min_long
    lat_range = max_lat - min_lat

    width = round(long_range / resolution_in_deg)
    height = round(lat_range / resolution_in_deg)

    res = urllib.request.urlopen('https://data.worldwind.arc.nasa.gov/elev?'
                                 'service=WMS'
                                 '&request=GetMap'
                                 '&layers=NED'
                                 '&crs=EPSG:4326'
                                 '&format=image/bil'
                                 '&transparent=FALSE'
                                 '&width=' + str(width) +
                                 '&height=' + str(height) +
                                 '&bgcolor=0xFFFFFF'
                                 '&bbox=' + str(min_long) + ',' + str(min_lat) + ',' + str(max_long) + ',' + str(max_lat) +
                                 '&styles='
                                 '&version=1.3.0')

    f = open('data.bil', 'wb')
    bytes_written = f.write(res.read())
    f.close()

    # Read from file
    b = array.array("h")
    with open("data.bil", "rb") as f:
        b.fromfile(f, width * height)
    if sys.byteorder == "big":
        b.byteswap()

    for x in range(0, width):
        row = []
        for y in range(0, height):
            start = height * x
            row.append(b[start + y])
        print(len(row))
        elevation_data.append(row)
# end function

def elevation_points_to_long_lat(min_long=-113.36, min_lat=36.0, max_long=-113.13, max_lat=36.23, resolution=30):

    resolution_in_deg = resolution / m_per_deg_lat

    data = []

    for i in range(0, len(elevation_data)):
        for j in range(0, len(elevation_data[0])):
            x = j#min_long + resolution_in_deg * j
            y = i#min_lat + resolution_in_deg * i
            z = elevation_data[i][j]
            element = [x, y, z]
            data.append(element)

    return data
# end function

def write_points_to_obj():

    os.remove("model.obj")
    f = open("model.obj", 'a')

    mlong=-80
    mlat=37.5
    maxlong=-79.5
    maxlat=38
    resolution=90

    fetch_elevation_data(min_long=mlong, min_lat=mlat, max_long=maxlong, max_lat=maxlat, resolution=resolution)
    long_lat_data = elevation_points_to_long_lat(min_long=mlong, min_lat=mlat, max_long=maxlong, max_lat=maxlat, resolution=resolution)

    for point in long_lat_data:
        f.write("v " + str(point[0]) + " " + str(point[1]) + " " + str(point[2]) + '\n')

    long_lat_minus_elevation = np.array(list(map(lambda x: [x[0], x[1]], long_lat_data)))

    delauny = Delaunay(long_lat_minus_elevation)

    for simplex in delauny.simplices:
        f.write("f " + str(simplex[0] + 1) + " " + str(simplex[1] + 1) + " " + str(simplex[2] + 1) + '\n')

    f.close()
# end function