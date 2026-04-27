import matplotlib.pyplot as plt
import pandas as pd, numpy as np
import xarray as xr
import dask
import cartopy.crs as ccrs, cartopy.feature as cfeature
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import os
import sys
import matplotlib.gridspec as GridSpec
from matplotlib.gridspec import GridSpec

ds = xr.open_dataset('NetCDF Files/nam_whole_run2.nc')
ds_sub = ds.isel(y = slice(30, 1050), x = slice(90, 1760))
temp_f = ds_sub['t2m_F'].values
tcc = ds_sub['tcc'].values
dew_f = ds_sub['d2m_F'].values
wsp = ds_sub['wsp'].values
run = 2
hour = run*3

def PWO(dataset):
    temp_contribution = np.zeros_like(temp_f)

    mask = (temp_f >= 30) & (temp_f < 60)
    temp_contribution[mask] = (temp_f[mask] - 30) / 30

    mask = (temp_f >= 60) & (temp_f <= 75)
    temp_contribution[mask] = 1.0

    mask = (temp_f > 75) & (temp_f < 105)
    temp_contribution[mask] = 1.0 - (temp_f[mask] - 75) / 30

    mask = (temp_f >= 105)
    temp_contribution[mask] = 0

    tcc_contribution = np.zeros_like(tcc)

    mask2 = (tcc >= 0) & (tcc <= 100)
    tcc_contribution[mask2] = 1.0 - (tcc[mask2]) / 100

    dew_contribution = np.zeros_like(dew_f)

    mask = (dew_f >= -10) & (dew_f < 40)
    dew_contribution[mask] = (dew_f[mask] + 10) / 50

    mask = (dew_f >= 40) & (dew_f < 60)
    dew_contribution[mask] = 1

    mask = (dew_f > 60) & (dew_f < 80)
    dew_contribution[mask] = 1.0 - (dew_f[mask] - 60) / 20

    mask = (dew_f >= 80)
    dew_contribution[mask] = 0

    wsp_contribution = np.zeros_like(wsp)

    mask = (wsp >= 10) & (wsp <= 30)
    wsp_contribution[mask] = 1.0 - (wsp[mask] - 5) / 20

    mask = (wsp < 10)
    wsp_contribution[mask] = 1

    mask = (wsp > 30)
    wsp_contribution[mask] = 0

    PWO = (temp_contribution*0.40 + dew_contribution*0.25 + tcc_contribution*0.1 + wsp_contribution*0.25)*5
    PWO = np.round(PWO)
    mask = PWO == 0
    PWO[mask] = 1
    PWO = PWO+0.1
    
    return PWO
PWO_current = PWO(ds_sub)

init_time = ds['valid_time'].values[0]
init_time = pd.to_datetime(init_time)
init_time = init_time.strftime('%HZ %a %b %d %Y')

valid_time = ds['valid_time'].values[run]
valid_time = pd.to_datetime(valid_time)
valid_time = valid_time.strftime('%HZ %a %b %d %Y')
dataproj = ccrs.PlateCarree()
mapproj = ccrs.LambertConformal()
lat = ds_sub.latitude
lon = ds_sub.longitude

def GeoAxes():
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.LambertConformal())
    ax.add_feature(cfeature.COASTLINE, linewidth=2)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=1.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linestyle=':',linewidth=1)
    ax.set_extent([-120, -73, 23, 50])
    return fig,ax

hours = np.arange(0,61,3)
legend_items = [
        ("lightcoral", "1 - Unpleasant"),
        ("sandybrown", "2 - Bad"),
        ("#fcf477", "3 - Ok"),
        ("#88f788", "4 - Good"),
        ("mediumseagreen", "5 - Pleasant")
]
patches = [mpatches.Patch(color=color, label=label) for color, label in legend_items]

for value in hours:
    ts = int(value/3)
    fig,ax=GeoAxes()
    levels = np.arange(1, 6, 1)
    valid_time = ds_sub['valid_time'].values[ts]
    valid_time = pd.to_datetime(valid_time)
    valid_time = valid_time.strftime('%HZ %a %b %d %Y')
    plt.legend(handles=patches, loc="lower left")
    cs = ax.contourf(lon, lat, PWO_current[ts], colors=['lightcoral','sandybrown','#fcf477','#88f788','mediumseagreen'], vmin = 1,vmax = 5,levels=levels,extend="max",transform=dataproj, transform_first = True)
    plt.title(f"Pleasant Weather Outlook \u2022 Init: {init_time} \u2022 Valid: {valid_time}", fontweight = "bold")
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', zorder=3)
    ax.add_feature(cfeature.LAKES, facecolor='lightblue', zorder=3)
    plt.tight_layout()
    plt.savefig(os.path.join('run', f"pwo_f_{ts:02d}.png"))
    plt.show()

