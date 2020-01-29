from mpl_toolkits.basemap import Basemap
import osr, gdal
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

font = {'family' : 'normal',
        'size'   : 20}

matplotlib.rc('font', **font)


def convertXY(xy_source, inproj, outproj):
    # function to convert coordinates
    shape = xy_source[0,:,:].shape
    size = xy_source[0,:,:].size

    # the ct object takes and returns pairs of x,y, not 2d grids
    # so the the grid needs to be reshaped (flattened) and back.
    ct = osr.CoordinateTransformation(inproj, outproj)
    xy_target = np.array(ct.TransformPoints(xy_source.reshape(2, size).T))

    xx = xy_target[:,0].reshape(shape)
    yy = xy_target[:,1].reshape(shape)

    return xx, yy

def save_fig_maximized(fig, path_fig, name_fig):
    manager = plt.get_current_fig_manager()
    manager.full_screen_toggle()
    manager.window.showMaximized()
    fig = plt.gcf()
    print(manager)
    plt.show()
    fig.savefig(path_fig.format(name_fig), format="png", dpi=300)


################
# Main program #
################

# Read the data and metadata
path_tif = r"D:/UTwente/PycharmProjects/04_Risk_Model/data/tifs/Exposure.tif"
# path_rail = r"/usr/people/garciama/data/geodata/vector/NATREG_SpoorWegen/railways"

ds = gdal.Open(path_tif, gdal.GA_ReadOnly)
data = ds.ReadAsArray()
data[np.isnan(data)] = -99
z = np.ma.masked_array(data, data < 0)

# get the edge coordinates and add half the resolution
# to go to center coordinates
gt = ds.GetGeoTransform()
proj = ds.GetProjection()
xres = gt[1]
yres = gt[5]
xmin = gt[0] + xres * 0.5
xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
ymax = gt[3] - yres * 0.5

ds = None

# create a grid of xy coordinates in the original projection
xy_source = np.mgrid[xmin:xmax+xres:xres, ymax+yres:ymin:yres]

# Create the figure and basemap object
fig = plt.figure()

plt.title("(a)", size = 24)

m = Basemap(projection='merc', lon_0=3.0, lat_0=52.0, resolution='h', llcrnrlon=3.0, llcrnrlat=50.0, urcrnrlon=8.0, urcrnrlat=54.0)
m.drawcountries(zorder=4)
m.drawcoastlines(zorder=5)
m.fillcontinents(color='tan',lake_color='lightblue', zorder=2)
m.drawmapboundary(fill_color='lightblue',zorder=1)

# Create the projection objects for the convertion
inproj = osr.SpatialReference()
inproj.ImportFromWkt(proj)
outproj = osr.SpatialReference()
outproj.ImportFromProj4(m.proj4string)

mycmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["darkblue","yellow","darkred"])

xx, yy = convertXY(xy_source, inproj, outproj)

# im1 = m.pcolormesh(xx, yy, z.T, cmap=plt.cm.get_cmap('RdYlBu_r', 3), vmin=1, vmax=3, zorder=3)

colors = ["darkblue","yellow","darkred"]

im1 = m.pcolormesh(xx, yy, z.T, cmap=matplotlib.colors.ListedColormap(colors), vmin=1, vmax=3, zorder=3)

arrnames = np.array(["Low", "Low", "Medium", "High"])
formatter = plt.FuncFormatter(lambda val, loc: arrnames[val])
cbar = m.colorbar(im1,location='bottom',pad="5%", size="5%", ticks=[0, 1, 2, 3], format=formatter)
cbar.set_label('Exposure', size="28", labelpad=20)

# # This function formatter will replace integers with target names
# arrnames = np.array(["Low", "Medium", "High"])
# formatter = plt.FuncFormatter(lambda val, loc: arrnames[val])
#
# # We must be sure to specify the ticks matching our target names
# plt.colorbar(ticks=[1, 2, 3], format=formatter);
#
# # Set the clim so that labels are centered on each block
# plt.clim(-0.5, 2.5)

# rails = m.readshapefile(path_rail, 'railways',drawbounds=True, zorder=6)
# col = rails[-1]
# col.set_linestyle('dotted')
# plt.title("Frost suitability for 13/01/2016")
# plt.show()

# path_fig_out = r"D:\UTwente\PhD\Papers\Journals\04_Exposure\submission\SREP\r3\images_review_280918\{0}"
# name_fig = r"03_ExposureMap.png"
# save_fig_maximized(m, path_fig_out, name_fig)

plt.show()
