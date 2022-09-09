import xarray as xr 
import geopandas as gp 
import pandas as pd 
import sparse

store = 'https://ncsa.osn.xsede.org/Pangeo/pangeo-forge/gpcp-feedstock/gpcp.zarr'

ds = xr.open_dataset(store, engine='zarr', chunks={})
encode = {"precip": {"zlib": True, "complevel": 9}}

ds.to_netcdf("file.nc")


regions_df = gp.read_file("ne_50m_admin_0_countries.shp")

# use an area preserving projections
crs = "ESRI:53034"
crs_orig = "OGC:CRS84"
regions_df = regions_df.to_crs(crs)
regions_df.geometry.plot()

# Now we extract just the horizontal grid information. The dataset has 
# information about the lat and lon bounds of each cell, which we need to create the polygons.

grid = ds.drop(['time', 'time_bounds',  'precip']).reset_coords().load()
grid


# Now we "stack" the data into a single 1D array. This is the first step towards transitioning to pandas.

points = grid.stack(point=("latitude", "longitude"))
points



from shapely.geometry import Polygon

def bounds_to_poly(lon_bounds, lat_bounds):
    if lon_bounds[0] >= 180:
        # geopandas needs this
        lon_bounds = lon_bounds - 360
    return Polygon([
        (lon_bounds[0], lat_bounds[0]),
        (lon_bounds[0], lat_bounds[1]),
        (lon_bounds[1], lat_bounds[1]),
        (lon_bounds[1], lat_bounds[0])
    ])
    
    


import numpy as np
boxes = xr.apply_ufunc(
    bounds_to_poly,
    points.lon_bounds,
    points.lat_bounds,
    input_core_dims=[("nv",),  ("nv",)],
    output_dtypes=[np.dtype('O')],
    vectorize=True
)
boxes


grid_df= gp.GeoDataFrame(
    data={"geometry": boxes.values, "latitude": boxes.latitude, "longitude": boxes.longitude},
    index=boxes.indexes["point"],
    crs=crs_orig
)
grid_df



grid_df = grid_df.to_crs(crs)
overlay = grid_df.overlay(regions_df)
overlay


