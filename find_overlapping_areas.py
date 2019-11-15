from shapely.geometry import Polygon
from shapely.ops import transform
import pyproj
from functools import partial
import pandas as pd


def convert_coordinates_to_geographic_area(long_min, long_max, lat_min, lat_max):
    # So we are going to create a geometric object from the coords (a Polygon - in our case a rectangle)
    # This will allow us to utilize the 'area' and 'intersects' functions required for this task
    # Naming co-ords like so:
    #  . ----> .
    #  ^       |
    #  |       v
    #  . <---- .
    poly = Polygon(([long_max, lat_min], [long_max, lat_max], [long_min, lat_max], [long_min, lat_min]))

    # Then we will use pyproj to create a mapping of this polygon onto the Earth (Mercator projection)
    mercator = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        # Found from https://epsg.io/
        pyproj.Proj('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 '
                    '+k=1.0 +units=m +nadgrids=@null +no_defs')
    )

    # Apply mercator projection
    poly_transformed = transform(mercator, poly)

    return poly_transformed


def find_areas_from_file_that_overlap(input_area_coords, file_path):

    input_area = convert_coordinates_to_geographic_area(*input_area_coords)

    input_area_in_kilometres = input_area.area / 1000000.0
    print(f'Total area of input: {input_area_in_kilometres} km^2')

    areas_that_overlap = []

    data = pd.read_csv(file_path, delimiter=',')
    for row in data.itertuples():
        area = convert_coordinates_to_geographic_area(row.MIN_longitude,
                                                      row.MAX_longitude,
                                                      row.MIN_latitude,
                                                      row.MAX_latitude)
        if input_area.intersects(area):
            areas_that_overlap.append(row.analysis_area)

    return areas_that_overlap


if __name__ == '__main__':
    input_coordinates = [142.5, 143, -11.5, -11]
    overlapping_areas = find_areas_from_file_that_overlap(input_coordinates, 'AU_proj_coords.csv')
    print(overlapping_areas)
