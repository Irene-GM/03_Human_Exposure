from mpl_toolkits.basemap import Basemap
from osgeo import osr, gdal
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from mpl_toolkits.basemap import Basemap
from geopy.geocoders import Nominatim
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch




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
    fig.savefig(path_fig.format(name_fig), format="png", dpi=500)


################
# Main program #
################

# Read the data and metadata
path_tif = r"D:/UTwente/IJGIS_map/EPSG_4326/Risk_TickBites.tif"
# path_rail = r"/usr/people/garciama/data/geodata/vector/NATREG_SpoorWegen/railways"

ds = gdal.Open(path_tif, gdal.GA_ReadOnly)
data = ds.ReadAsArray()

print(np.unique(data, return_counts=True))

z2 = np.ma.masked_array(data, data == 0)
z = np.ma.masked_array(z2, z2 == 65536)


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
fig, axes = plt.subplots(nrows=1, ncols=2)

axes[0].set_title("(a)", size=24)

m = Basemap(projection='merc', lon_0=3.0, lat_0=52.0, resolution='h', llcrnrlon=3.0, llcrnrlat=50.0, urcrnrlon=8.0, urcrnrlat=54.0, ax=axes[0])
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
mynorm = matplotlib.colors.LogNorm(vmin=1, vmax=353)

xx, yy = convertXY(xy_source, inproj, outproj)
im1 = m.pcolormesh(xx, yy, z.T, cmap=mycmap, norm=mynorm, zorder=3)

cbar = m.colorbar(im1,location='bottom',pad="5%", size="5%")
cbar.set_label('Risk', size="28", labelpad=20)

toma = matplotlib.ticker.FuncFormatter(lambda y, pos: ('{:.0f}'.format(mynorm.inverse(y))))

cbar.ax.xaxis.set_major_formatter(toma)

hide = [1, 2, 3, 5, 6, 7, 8, 14, 15, 16, 17]
k = 0
for label in cbar.ax.get_xticklabels():
        # label.set_rotation(70)
        print(label)
        if k in hide:
            label.set_visible(False)
        k += 1



# NOW THE PART B OF THE FIGURE

axes[1].set_title("(b)", size=24)

geolocator = Nominatim()

loc_emm = geolocator.geocode("Emmen, NL")
loc_haa = geolocator.geocode("Haarlem, NL")
loc_mid = geolocator.geocode("Middelburg, NL")
loc_her = geolocator.geocode("Hertogenbosch, NL")
loc_ein = geolocator.geocode("Eindhoven, NL")

loc_ove = geolocator.geocode("Overijssel, NL")
loc_dre = geolocator.geocode("Drenthe, NL")
loc_gro = geolocator.geocode("Groningen, NL")

loc_heu = geolocator.geocode("Utrechtse Heuvelrug, NL")
loc_vel = geolocator.geocode("Hooge Veluwe, NL")

pack = [loc_emm, loc_haa, loc_mid, loc_her, loc_ein, loc_ove, loc_dre, loc_gro, loc_heu, loc_vel]

# fig, ax = plt.subplots()

m = Basemap(projection='merc', lon_0=3.0, lat_0=52.0, resolution='h', llcrnrlon=3.0, llcrnrlat=50.0, urcrnrlon=8.0, urcrnrlat=54.0, ax=axes[1])
# m.drawcountries(zorder=4)
m.drawcoastlines(zorder=5)
m.fillcontinents(color='tan',lake_color='lightblue', zorder=2)
m.drawmapboundary(fill_color='lightblue',zorder=1)

p1 = r"D:\GeoData\NLD_adm\NLD_adm1"
p2 = r"D:\GeoData\NatParks\TwoNatParks"

m.readshapefile(p1, 'NLD_adm1', drawbounds = True, zorder=6)
m.readshapefile(p2, 'TwoNatParks', drawbounds = True, zorder=7)

patches = []

for info, shape in zip(m.TwoNatParks_info, m.TwoNatParks):
    if "rug" in info['naam']:
        patches.append(Polygon(np.array(shape), True))
    if "uwe" in info['naam']:
        patches.append(Polygon(np.array(shape), True))

axes[1].add_collection(PatchCollection(patches, facecolor='#014023', edgecolor='#014023', linewidths=0.5, zorder=12))

lats = [item.latitude for item in pack]
lons = [item.longitude for item in pack]

fname = "Sans"

for item in pack:
    x, y = m(item.longitude, item.latitude)
    city = item.address.split(",")[0]
    print(city)
    # t = ax.text(x, y, city, fontdict={'variant': 'small-caps'})
    if "uwe" in city:
        city = "De Hoge Veluwe".upper()
        axes[1].annotate(city, (x, y), xytext=(5, -10), textcoords='offset pixels', size=24, variant='small-caps', fontname=fname)
        m.plot(x, y, marker='.', color='k', markersize=0)

    elif "rug" in city:
        # For windows
        axes[1].annotate(city.upper(), (x, y), xytext=(-2200, -80), textcoords='offset pixels', size=24, variant='small-caps', fontname=fname)
        # For linux
        # axes[1].annotate(city.upper(), (x, y), xytext=(-200, -40), textcoords='offset pixels', size=24, variant='small-caps', fontname=fname)
        m.plot(x, y, marker='.', color='k', markersize=0)

    elif city in ["Emmen", "Haarlem", "Middelburg", "'s-Hertogenbosch", "Eindhoven"]:
        if city == "Emmen":
            axes[1].annotate(city, (x, y), xytext=(5, -25), textcoords='offset points', size=24, variant='small-caps', fontname=fname)
            m.plot(x, y, marker='s', color='k')
        else:
            axes[1].annotate(city, (x, y), xytext=(5, 5), textcoords='offset points', size=24, variant='small-caps', fontname=fname)
            m.plot(x, y, marker='s', color='k')
    else:
        if city == "Groningen":
            axes[1].annotate(city.upper(), (x, y), xytext=(-50, 0), textcoords='offset points', size=24, variant='small-caps', fontname=fname)
            m.plot(x, y, marker='.', color='k', markersize=0)
        elif city == "Drenthe":
            axes[1].annotate(city.upper(), (x, y), xytext=(-50, -5), textcoords='offset points', size=24, variant='small-caps', fontname=fname)
            m.plot(x, y, marker='.', color='k', markersize=0)
        elif city == "Overijssel":
            axes[1].annotate(city.upper(), (x, y), xytext=(-50, -15), textcoords='offset points', size=24, variant='small-caps', fontname=fname)
            m.plot(x, y, marker='.', color='k', markersize=0)


# cbar.ax.set_xticklabels(toma, rotation=70)


# plt.text(0,0,'No data',bbox={'pad':10})

# cbar.ax.set_ticklabels(cbar.ax.get_ticklabels(), fontsize=28)
# print(cbar.ax.get_xticks())
# print(np.multiply(cbar.ax.get_xticks(), 353))
# print(np.interp(cbar.ax.get_xticks(), cbar.ax.get_xlim(), cbar.get_clim()))

# j=0
# for i in cbar.ax.get_xticklabels():
#     print(j, i.get_text())
#     j += 1
#
# sk = ["" for i in range(21)]
# sk[0] = "1"
# sk[9] = "10"
# sk[18] = "100"
#
# cbar.ax.set_xticklabels(sk)

# cbar.update_ticks()

# rails = m.readshapefile(path_rail, 'railways',drawbounds=True, zorder=6)
# col = rails[-1]
# col.set_linestyle('dotted')
# plt.title("Frost suitability for 13/01/2016")

path_fig_out = r"D:\UTwente\PhD\Papers\Journals\04_Exposure\submission\SREP\r3\images_review_280918\{0}"
name_fig = r"01_RiskMap_Tekenradar_Basemap.jpg"
save_fig_maximized(m, path_fig_out, name_fig)
