library(wk)
library(geos)
library(vapour)
sf::sf_use_s2(FALSE)
region_df <- tibble::as_tibble(vapour::vapour_read_fields("data-bulk/ne_50m_admin_0_countries.shp"))
#region <- geos_read_wkb(vapour::vapour_read_geometry("data-bulk/ne_50m_admin_0_countries.shp"))
region <- sf::st_geometry(sf::read_sf("data-bulk/ne_50m_admin_0_countries.shp"))
grid <- geos_read_wkb(wk::as_wkb(spex::polygonize(raster::raster(raster::extent(-180, 180, -90, 90), res = 1))))

ins <- geos_intersects_matrix(grid, region)

grids_to_intersect <- lengths(ins) > 0
 x <- sf::st_intersection(sf::st_as_sfc(grid[grids_to_intersect]),
                          sf::st_cast(sf::st_as_sfc(region), "MULTIPOLYGON"))
 x <- sf::st_transform(sf::st_set_crs(x, "OGC:CRS84"), "ESRI:53034")
 region <- sf::st_transform(region, "ESRI:53034")
length(x)
# l <- vector("list", sum(grids_to_intersect))
# for (i in seq_along(l)) {
#   ii <- which(grids_to_intersect)[i]
#   l[[i]] <- geos_intersection(grid[ii], region[ins[[ii]]])
# }

x <- wk::as_wkb(x)
pt <- geos_centroid(x)
idx <- rep(NA_integer_, length(pt))
lookup <- geos_intersects_matrix(pt, region)
idx[lengths(lookup) > 0] <- unlist(lookup)
sovereignt <- region_df$SOVEREIGNT[idx]
plot(x[which(sovereignt == "Australia")])

