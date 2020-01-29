import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from mpl_toolkits.basemap import Basemap
from geopy.geocoders import Nominatim
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch



def save_fig_maximized(fig, path_fig, name_fig):
    manager = plt.get_current_fig_manager()
    manager.full_screen_toggle()
    manager.window.showMaximized()
    fig = plt.gcf()
    print(manager)
    plt.show()
    fig.savefig(path_fig.format(name_fig), format="png", dpi=300)



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

fig, ax = plt.subplots()

m = Basemap(projection='merc', lon_0=3.0, lat_0=52.0, resolution='h', llcrnrlon=3.0, llcrnrlat=50.0, urcrnrlon=8.0, urcrnrlat=54.0)
# m.drawcountries(zorder=4)
m.drawcoastlines(zorder=5)
m.fillcontinents(color='tan',lake_color='lightblue', zorder=2)
m.drawmapboundary(fill_color='lightblue',zorder=1)

parallels = np.arange(50, 54, 1)
# labels = [left,right,top,bottom]
m.drawparallels(parallels,labels=[False,True,True,False], dashes=[5,5], color="gray", size=20)
meridians = np.arange(3, 8, 1)
m.drawmeridians(meridians,labels=[True,False,False,True], dashes=[5,5], color="gray", size=20)


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

ax.add_collection(PatchCollection(patches, facecolor='#014023', edgecolor='#014023', linewidths=0.5, zorder=12))

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
        ax.annotate(city, (x, y), xytext=(5, -20), textcoords='offset pixels', size=24, variant='small-caps', fontname=fname)
        m.plot(x, y, marker='.', color='k', markersize=0)

    elif "rug" in city:
        ax.annotate(city.upper(), (x, y), xytext=(-620, -120), textcoords='offset pixels', size=24, variant='small-caps', fontname=fname)
        m.plot(x, y, marker='.', color='k', markersize=0)

    elif city in ["Emmen", "Haarlem", "Middelburg", "'s-Hertogenbosch", "Eindhoven"]:
        if city == "Emmen":
            ax.annotate(city, (x, y), xytext=(5, -25), textcoords='offset points', size=24, variant='small-caps', fontname=fname)
            m.plot(x, y, marker='s', color='k')
        else:
            ax.annotate(city, (x, y), xytext=(5, 5), textcoords='offset points', size=24, variant='small-caps', fontname=fname)
            m.plot(x, y, marker='s', color='k')
    else:
        if city == "Groningen":
            ax.annotate(city.upper(), (x, y), xytext=(-50, 0), textcoords='offset points', size=24, variant='small-caps', fontname=fname)
            m.plot(x, y, marker='.', color='k', markersize=0)
        elif city == "Drenthe":
            ax.annotate(city.upper(), (x, y), xytext=(-50, -5), textcoords='offset points', size=24, variant='small-caps', fontname=fname)
            m.plot(x, y, marker='.', color='k', markersize=0)
        elif city == "Overijssel":
            ax.annotate(city.upper(), (x, y), xytext=(-50, -15), textcoords='offset points', size=24, variant='small-caps', fontname=fname)
            m.plot(x, y, marker='.', color='k', markersize=0)


# plt.show()

# path_fig_out = r"D:\UTwente\PhD\Papers\Journals\04_Exposure\submission\SREP\r3\images\{0}"

path_fig_out = r"C:/Users/irene/Pictures/paper4_fin/newbatch/{0}"
name_fig = r"01b_Landmarks.png"
save_fig_maximized(m, path_fig_out, name_fig)



# Cartopy
#
# ax = plt.axes(projection=ccrs.Mollweide())
# ax.stock_img()
#
#
# ax = plt.axes(projection=cartopy.crs.PlateCarree())
# ax.add_feature(cartopy.feature.LAND)
# ax.add_feature(cartopy.feature.OCEAN)
# ax.add_feature(cartopy.feature.COASTLINE)
# ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5)
# ax.add_feature(cartopy.feature.LAKES, alpha=0.95)
#
# plt.show()
#
# ax.set_extent([-150, -20, -90, 90])
#
# plt.plot([ny_lon, delhi_lon], [ny_lat, delhi_lat],
#          color='gray', linestyle='--',
#          transform=ccrs.PlateCarree(),
#          )
#
# plt.text(ny_lon - 3, ny_lat - 12, 'New York',
#          horizontalalignment='right',
#          transform=ccrs.Geodetic())