import numpy as np
import gdal
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import jenkspy
from collections import defaultdict
import osr
import seaborn as sb
import pandas as pd

def clean(m):
    m[np.isinf(m)]=0
    m[np.isnan(m)]=0
    return m

def scale(l):
    X = np.array(l)
    X_std = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
    return X_std

def write_tif(m, path):
    spatialref = osr.SpatialReference()
    spatialref.ImportFromEPSG(28992)
    # Just point to a KNMI layer to get the reference metadata/size (350x300)
    tif_template = gdal.Open("E:/RSData/KNMI/yearly/tmax/2014_tmax.tif")
    rows = tif_template.RasterXSize
    cols = tif_template.RasterYSize

    # Get the origin coordinates for the tif file
    geotransform = tif_template.GetGeoTransform()
    outDs = tif_template.GetDriver().Create(path, rows, cols, 1, gdal.GDT_Float32)
    outBand = outDs.GetRasterBand(1)

    # write the data
    outDs.GetRasterBand(1).WriteArray(m)

    # flush data to disk, set the NoData value and calculate stats
    outBand.FlushCache()
    outBand.SetNoDataValue(-1)

    # georeference the image and set the projection
    outDs.SetGeoTransform(geotransform)
    outDs.SetProjection(spatialref.ExportToWkt())
    outDs = None
    outBand = None

def process_lyr(path, vble):
    # Load data and locate the zero and non-zero pixels
    tif = gdal.Open(path)
    band = tif.GetRasterBand(1).ReadAsArray().astype(np.float)
    band[np.isnan(band)]=-1
    pos_nz = np.where(band>0.0)
    pos_ze = np.where(band<=0.0)
    canvas = paint_zeros(pos_ze, 0)

    # Add to a list the >0 pixels
    lv = []
    rows = pos_nz[0]
    cols = pos_nz[1]
    for i in range(len(rows)):
        r = rows[i]
        c = cols[i]
        lv.append(band[r,c])

    # Scale and re-locate non-zero pixels in place
    X_std = scale(lv)
    values = np.empty((350, 300))
    for i in range(pos_nz[0].shape[0]):
        r = pos_nz[0][i]
        c = pos_nz[1][i]
        values[r,c] = X_std[i]

    # Create exposure layer
    lyr = canvas + values
    lyr_ori = canvas + band

    print("PROCESSING: {0}".format(vble))
    print("-" * 40)
    print("Exposure values (before scaling)")
    print("\tMin: {0}\tMax: {1}".format(np.amin(band[band>=0]), np.amax(band)))
    print("Exposure values (after scaling)")
    print("\tMin: {0}\tMax: {1}".format(np.amin(lyr), np.amax(lyr)))
    print("Checking for extreme values")
    print("\tNaNs: {0}, \tInf: {1}, \tNegInf: {2}".format(np.isnan(lyr).any(), np.isinf(lyr).any(), np.isneginf(lyr).any()))
    print()

    return [lyr, lyr_ori]


def process_layers(path_ris, path_exp, path_haz_irn):
    risk, risk_ori = process_lyr(path_ris, "RISK")
    exposure, exposure_ori = process_lyr(path_exp, "EXPOSURE")
    hazard, hazard_ori = process_lyr(path_haz_irn, "HAZARD")
    return [risk, exposure, hazard, risk_ori, exposure_ori, hazard_ori]


def goodness_of_variance_fit(array, classes):
    # classes = jenks(array, classes)
    the_breaks = np.round(jenkspy.jenks_breaks(array.tolist(), nb_class=classes), decimals=2).tolist()
    print("These are the breaks for the gvf fit: ", the_breaks)
    classifiedd = np.array([classify(np.round(i, decimals=2), the_breaks) for i in array])
    maxz = np.amax(classifiedd)
    zone_indices = [[idx for idx, val in enumerate(classifiedd) if zone + 1 == val] for zone in range(maxz)]
    sdam = np.sum((array - array.mean()) ** 2)
    array_sort = [np.array([array[index] for index in zone]) for zone in zone_indices]
    sdcm = np.sum([np.sum((cla - cla.mean()) ** 2) for cla in array_sort])
    gvf = (sdam - sdcm) / sdam
    return gvf

def classify(value, breaks):
    # print("Value and breaks: ", value, breaks)
    for i in range(1, len(breaks)):
        if value < breaks[i]:
            return i
    return len(breaks) - 1

def natural_breaks(m):
    gvf = 0.0
    nclasses = 2
    print("Calculating breaks", m.shape)
    while gvf < 0.85 and nclasses < 10:
        gvf = goodness_of_variance_fit(m, nclasses)
        print("\tGVF for {0} classes: {1}".format(nclasses, round(gvf,2)))
        nclasses += 1

    print("Running jenks with {0} classes".format(nclasses-1))
    # breaks = jenks(m, nclasses-1)
    breaks = np.round(jenkspy.jenks_breaks(m.tolist(), nb_class=nclasses-1), decimals=2)
    print("\t Breaks in: ", breaks)
    classified = np.array([classify(i, breaks) for i in m])
    return classified

def paint_zeros(pos_zer, v):
    canvas = np.empty((350, 300))
    rows = pos_zer[0]
    cols = pos_zer[1]

    for i in range(len(rows)):
        r = rows[i]
        c = cols[i]
        canvas[r, c] = v

    return canvas


def find_pos_nonzero_values(exposure):
    dic = defaultdict(list)
    for i in range(exposure.shape[0]):
        for j in range(exposure.shape[1]):
            if exposure[i, j] > 0.0:
                key = (i,j)
                dic[key] = [i, j, exposure[i, j]]
    return dic

def matcher(expnz, classified):
    l = []
    for i in range(len(lv)):
        item = expnz[i] + [classified[i]]
        l.append(item)
    return l

def place(l):
    r = np.empty((350, 300))
    c = np.empty((350, 300))

    for item in l:
        rowpos = item[0]
        colpos = item[1]
        valraw = item[2]
        valcls = item[3]
        r[rowpos, colpos] = valraw
        c[rowpos, colpos] = valcls
    return [r, c]

def do_boxplots(risk, hazard, exposure):
    sb.set_style("darkgrid", {"axes.facecolor": ".9"})
    df = pd.DataFrame()
    df['Risk'] = risk.ravel()
    df['Hazard'] = hazard.ravel()
    df['ExpRaw'] = exposure.ravel()
    df['Exposure'] = exposure.ravel()

    df2 = df.copy()

    df['Exposure'][df2["Exposure"]==1] = "Low"
    df['Exposure'][df2["Exposure"]==2] = "Medium"
    df['Exposure'][df2["Exposure"]==3] = "High"

    exp_nz = df["ExpRaw"].isin([1, 2, 3, 27])
    print(df["ExpRaw"].unique())

    pal = {"Low":"#0084CC", "Medium":"#F0DF6A", "High":"#D93223"}

    plt.subplot(1, 2, 1)
    ax1 = sb.boxplot("Exposure", "Risk", data=df[exp_nz], palette=pal)
    ax1.axes.set_title("Title", fontsize=36)
    ax1.set_xlabel("Exposure", fontsize=28)
    ax1.set_ylabel("Risk", fontsize=28)
    ax1.tick_params(labelsize=24)
    plt.title("(a) Exposure (Classified) vs. Risk", size=36)

    plt.subplot(1, 2, 2)
    ax2 = sb.boxplot("Exposure", "Hazard", data=df[exp_nz], palette=pal)
    ax2.axes.set_title("Title", fontsize=36)
    ax2.set_xlabel("Exposure", fontsize=28)
    ax2.set_ylabel("Hazard", fontsize=28)
    ax2.tick_params(labelsize=24)
    plt.title("(b) Exposure (Classified) vs. Hazard", size=36)

    print(df["Hazard"].unique())
    print(df["Risk"].unique())

def save_fig_maximized(path_fig, name_fig):
    manager = plt.get_current_fig_manager()
    manager.full_screen_toggle()
    manager.window.showMaximized()
    fig = plt.gcf()
    print(manager)
    plt.show()
    print("Saving in... ", path_fig.format(name_fig))
    fig.savefig(path_fig.format(name_fig), format="pdf", dpi=300)


################
# Main program #
################

# In this version I am getting rid of the MinMaxScaler, because it has some
# side effects with the existence of -99 values. I will also get rid of the -99
# to focus on making the cross plots without them.

# I am also using the hazard as the maximum for all years in the time-series

path_ris_tif = r"D:\PycharmProjects\IGM_PhD_Materials\data\P03\in\Risk_Tekenradar_2006-2016_1km_RD_New.tif"
path_haz_tif = r"D:\PycharmProjects\IGM_PhD_Materials\data\P03\in\NL_Hazard_Mean_2006-2016_Max.tif"
path_exp_tif = r"D:\PycharmProjects\IGM_PhD_Materials\data\P03\in\Exposure_RD_New.tif"
path_exp_out_tif = r"D:\PycharmProjects\IGM_PhD_Materials\data\P03\out\Exposure_RD_New_classified.tif"

risk, exposure, hazard, risk_ori, exposure_ori, hazard_ori = process_layers(path_ris_tif, path_exp_tif, path_haz_tif)

pos_zer = np.where(exposure==0.0)

canvas = paint_zeros(pos_zer, 27)

dicpos = find_pos_nonzero_values(exposure)

exposure_nonzero = []
for key in sorted(dicpos.keys()):
    exposure_nonzero.append(dicpos[key])

lv = [item[2] for item in exposure_nonzero]

classified = natural_breaks(np.array(lv))

matched = matcher(exposure_nonzero, classified)

rawexp, clsexp = place(matched)

tif = canvas + clsexp

# This is to avoid an outlier causing visual cluttering
hazard_ori[hazard_ori<2] = 34
do_boxplots(risk_ori, hazard_ori, clsexp)

plt.clf()
plt.imshow(clsexp, interpolation="None")
plt.colorbar()
print("Uniques: ", np.unique(clsexp, return_counts=True))
plt.show()

# write_tif(tif, path_exp_out_tif)

