from mpl_toolkits.basemap import Basemap
import osr, gdal
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

import matplotlib.cm as cm
import matplotlib.colors as mcolors




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


def colorbar_index(ncolors, cmap):
    # cmap = cmap_discretize(cmap, ncolors)
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(-0.5, ncolors+0.5)
    colorbar = plt.colorbar(mappable)
    colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
    colorbar.set_ticklabels(range(ncolors))


################
# Main program #
################

# Read the data and metadata
# path_tif = r"F:/IJGIS_map/EPSG_4326/Exposure.tif"
path_tif = r"C:\Users\irene\Downloads\Exposure_RD_New_vIGM_classified_4CASESWITHRH_4326.tif"
# path_rail = r"/usr/people/garciama/data/geodata/vector/NATREG_SpoorWegen/railways"

path_mask = r"D:\Data\mask\mask_LGN.csv"

mask = np.loadtxt(path_mask, delimiter=";")

ds = gdal.Open(path_tif, gdal.GA_ReadOnly)
data = ds.ReadAsArray()

canvas = np.empty((352, 311))

for i in range(mask.shape[0]):
    for j in range(mask.shape[1]):
        canvas[i,j] = mask[i,j]

newmask = np.roll(canvas, 6, axis=1)

data_masked = np.ma.masked_array(data, newmask==0)

z = np.ma.masked_array(data, data == 6)

z = data_masked

# plt.imshow(z, interpolation="None", cmap=plt.cm.Set1)
# plt.colorbar()
# plt.show()

print(np.unique(z, return_counts=True))

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

# mycmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["darkblue","yellow","darkred"])

xx, yy = convertXY(xy_source, inproj, outproj)

# im1 = m.pcolormesh(xx, yy, z.T, cmap=plt.cm.get_cmap('RdYlBu_r', 3), vmin=1, vmax=3, zorder=3)

# colors = ["white", "#2A313B", "#F2E127", "grey"]

# colors = ["white", "#2D3C3F", "#F2E127", "#598763"]

colors = ["white", "#448C51", "#F2E127", "#3D3D3D"]


z[z==3] = 33 # Exposure
z[z==4] = 44 # No data
z[z==5] = 55 # Hazard
z[z==6] = 66 # Risk

z[z==33] = 1 # Exposure
z[z==66] = 2 # Risk
z[z==55] = 3 # Hazard
z[z==44] = 4 # No data


plt.title("(b)", size = 24)
im1 = m.pcolormesh(xx, yy, z.T, cmap=matplotlib.colors.ListedColormap(colors), vmin=1, vmax=9, zorder=3)
cbar = m.colorbar(im1, location='bottom', pad="5%", size="5%", ticks=matplotlib.ticker.FixedLocator([1, 2, 3, 4, 5, 6, 7, 8]))
cbar.set_ticklabels(["", "1", "", "2", "", "3", "", "4", ""])
print(cbar.ax.get_xticks())

im2 = m.pcolormesh(xx, yy, z.T, cmap=matplotlib.colors.ListedColormap(colors), vmin=1, vmax=4, zorder=4)

# cbar.ax.set_xlabel("Case")



#
#
# labels = np.arange(1, 5, 1)
# loc = labels + 0.25
# print(loc)
# cbar.set_ticks(ini)
# cbar.set_ticklabels(labels)



# cbar.set_label('Exposure', size="28", labelpad=20)
# # cbar.ax.xaxis.set_label_position('center')
# cbar.ax.xaxis.set_ticks_position('bottom')
# cbar.ax.set_xlabel("Case")
#
# # get the xtick labels
# tl = cbar.ax.get_xticklabels()
# tl[0].set_horizontalalignment('left')
# # tl[1].set_horizontalalignment('left')
# # tl[2].set_horizontalalignment('right')
# tl[-1].set_horizontalalignment('right')
#
# y_min, y_max = cbar.ax.get_xlim()
# ticks = [(tick - y_min)/(y_max - y_min) for tick in cbar.ax.get_xticks()]
#
# print(ticks)

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
# name_fig = r"07_FourCasesMap.png"
# save_fig_maximized(m, path_fig_out, name_fig)
plt.show()