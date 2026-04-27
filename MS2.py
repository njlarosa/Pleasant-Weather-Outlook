#!/usr/bin/env python
# coding: utf-8

# In[73]:


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

ds = xr.open_dataset('nam_whole_run2.nc')
ds_sub = ds.isel(y = slice(30, 1050), x = slice(90, 1760))
temp_f = ds_sub['t2m_F'].values
tcc = ds_sub['tcc'].values
dew_f = ds_sub['d2m_F'].values
wsp = ds_sub['wsp'].values
run = 2
hour = run*3


# In[74]:


def PWO(dataset):
    # TEMPERATURE CONTRIBUTION

    # Start with all contributions set to 0
    temp_contribution = np.zeros_like(temp_f)

    # 30 <= T < 60 : linear increase from 0 to 1
    mask = (temp_f >= 30) & (temp_f < 60)
    temp_contribution[mask] = (temp_f[mask] - 30) / 30

    # 60 <= T <= 75 : contribution = 1
    mask = (temp_f >= 60) & (temp_f <= 75)
    temp_contribution[mask] = 1.0

    # T > 75 : linear decrease from 1 to 0 ending at 105 degrees
    mask = (temp_f > 75) & (temp_f < 105)
    temp_contribution[mask] = 1.0 - (temp_f[mask] - 75) / 30

    # T > 105 : contribution = 0
    mask = (temp_f >= 105)
    temp_contribution[mask] = 0

    # TOTAL CLOUD COVER CONTRIBUTION

    # Start with all contributions set to 0
    tcc_contribution = np.zeros_like(tcc)

    # 0 <= tcc < 100 : linear decrease from 1 to 0
    mask2 = (tcc >= 0) & (tcc <= 100)
    tcc_contribution[mask2] = 1.0 - (tcc[mask2]) / 100

    # DEW POINT TEMPERATURE CONTRIBUTION

    # Start with all contributions set to 0
    dew_contribution = np.zeros_like(dew_f)

    # -10 <= D < 40 : linear increase from 0 to 1
    mask = (dew_f >= -10) & (dew_f < 40)
    dew_contribution[mask] = (dew_f[mask] + 10) / 50

    # 40 <= D < 60 : contribution = 1
    mask = (dew_f >= 40) & (dew_f < 60)
    dew_contribution[mask] = 1

    # D > 60 : linear decrease from 1 to 0 ending at 80
    mask = (dew_f > 60) & (dew_f < 80)
    dew_contribution[mask] = 1.0 - (dew_f[mask] - 60) / 30

    # D >= 80 : contribution = 0
    mask = (dew_f >= 80)
    dew_contribution[mask] = 0

    #WIND SPEED CONTRIBUTION

    # Start with all contributions set to 0
    wsp_contribution = np.zeros_like(wsp)

    # 5 <= W <= 25 : linear decrease from 1 to 0
    mask = (wsp >= 5) & (wsp <= 25)
    wsp_contribution[mask] = 1.0 - (wsp[mask] - 5) / 20

    # W < 5 mph : contribution = 1
    mask = (wsp < 5)
    wsp_contribution[mask] = 1

    # W > 25 mph : contribution = 0
    mask = (wsp > 25)
    wsp_contribution[mask] = 0

    #Creating the PWO index
    PWO = (temp_contribution*0.45 + dew_contribution*0.3 + tcc_contribution*0.1 + wsp_contribution*0.15)*5
    PWO = np.round(PWO)
    PWO = PWO+0.1
    return PWO
PWO_current = PWO(ds_sub)


# In[75]:


# Set initial time 
init_time = ds['valid_time'].values[0]
init_time = pd.to_datetime(init_time)
init_time = init_time.strftime('%HZ %a %b %d %Y')

# Set step and valid time 
valid_time = ds['valid_time'].values[run]
valid_time = pd.to_datetime(valid_time)
valid_time = valid_time.strftime('%HZ %a %b %d %Y')
dataproj = ccrs.PlateCarree()
mapproj = ccrs.LambertConformal()
lat = ds_sub.latitude
lon = ds_sub.longitude


# In[79]:


hours = np.arange(0,61,3)
legend_items = [
        ("lightcoral", "1 - Unpleasant"),
        ("sandybrown", "2 - Bad"),
        ("#fcf477", "3 - Ok"),
        ("#88f788", "4 - Good"),
        ("mediumseagreen", "5 - Pleasant")
]
patches = [mpatches.Patch(color=color, label=label) for color, label in legend_items]


# In[80]:


for value in hours:
    timestep = int(value/3)
    fig = plt.figure(figsize=(10,8))
    valid_time = ds_sub['valid_time'].values[timestep]
    valid_time = pd.to_datetime(valid_time)
    valid_time = valid_time.strftime('%HZ %a %b %d %Y')
    fig.suptitle(f"NAM \u2022 Init: {init_time} \u2022 Valid: {valid_time}", fontweight="bold", fontsize = 13)
    # 2 rows, 4 columns
    gs = GridSpec(2, 4, figure=fig, height_ratios=[1, 3])

    # top row (4 small maps)
    ax1 = fig.add_subplot(gs[0,0], projection=ccrs.LambertConformal())
    ax1.set_extent([-120, -73, 23, 50])
    ax1.add_feature(cfeature.COASTLINE.with_scale('50m'))
    ax1.add_feature(cfeature.STATES.with_scale('50m'), linestyle=':')
    ax1.add_feature(cfeature.BORDERS.with_scale('50m'))
    levels = np.arange(-10,106,5)
    cs1 = ax1.contourf(lon, lat, ds_sub['t2m_F'].values[timestep], cmap='turbo', vmin=-10,vmax = 105,levels=levels,transform=dataproj, transform_first = True)

    cbar1 = plt.colorbar(cs1,ax=ax1,orientation="horizontal",pad=0.04,fraction=0.05,aspect=40)


    ax2 = fig.add_subplot(gs[0,1], projection=ccrs.LambertConformal())
    ax2.set_extent([-120, -73, 23, 50])
    ax2.add_feature(cfeature.COASTLINE.with_scale('50m'))
    ax2.add_feature(cfeature.STATES.with_scale('50m'), linestyle=':')
    ax2.add_feature(cfeature.BORDERS.with_scale('50m'))                   
    levels2 = np.arange(-10,91,5)
    cs2 = ax2.contourf(lon, lat, ds_sub['d2m_F'].values[timestep], cmap='turbo', vmin=-10,vmax = 90,levels=levels2,transform=dataproj, transform_first = True)
    cbar2 = plt.colorbar(cs2,ax=ax2,orientation="horizontal",pad=0.04,fraction=0.05,aspect=40)


    ax3 = fig.add_subplot(gs[0,2], projection=ccrs.LambertConformal())
    ax3.set_extent([-120, -73, 23, 50])
    ax3.add_feature(cfeature.COASTLINE.with_scale('50m'))
    ax3.add_feature(cfeature.STATES.with_scale('50m'), linestyle=':')
    ax3.add_feature(cfeature.BORDERS.with_scale('50m'))  
    levels3 = np.arange(0,51,5)
    cs3 = ax3.contourf(lon, lat, ds_sub['wsp'].values[timestep], cmap='turbo', vmin=0,vmax = 50,levels=levels3,transform=dataproj,transform_first = True)
    cbar3 = plt.colorbar(cs3,ax=ax3,orientation="horizontal",pad=0.04,fraction=0.05,aspect=40)


    ax4 = fig.add_subplot(gs[0,3], projection=ccrs.LambertConformal())
    ax4.set_extent([-120, -73, 23, 50])
    ax4.add_feature(cfeature.COASTLINE.with_scale('50m'))
    ax4.add_feature(cfeature.STATES.with_scale('50m'), linestyle=':')
    ax4.add_feature(cfeature.BORDERS.with_scale('50m'))  
    levels4 = np.arange(0,101,10)
    cs4 = ax4.contourf(lon, lat, ds_sub['tcc'].values[timestep], cmap = 'binary', vmin=0, vmax = 100, levels=levels4, transform=dataproj, transform_first = True)
    cbar4 = plt.colorbar(cs4,ax=ax4,orientation="horizontal",pad=0.04,fraction=0.05,aspect=40)

    # bottom row (spans all columns)
    ax5 = fig.add_subplot(gs[1,:], projection=ccrs.LambertConformal())
    ax5.set_extent([-120, -73, 23, 50])
    ax5.add_feature(cfeature.COASTLINE.with_scale('50m'))
    ax5.add_feature(cfeature.STATES.with_scale('50m'), linestyle=':')
    ax5.add_feature(cfeature.BORDERS.with_scale('50m'))  
    levels5 = np.arange(1, 6, 1)
    ax5.add_feature(cfeature.OCEAN,facecolor='lightblue',zorder=3)
    ax5.add_feature(cfeature.LAKES,facecolor='lightblue',zorder=3)
    cs5 = ax5.contourf(lon, lat, PWO_current[timestep], colors=['lightcoral','sandybrown','#fcf477','#88f788','mediumseagreen'], vmin = 1,vmax = 5,levels=levels5,extend="max",transform=dataproj, transform_first = True)

    plt.legend(handles=patches, loc = "lower left")

    # Example content
    ax1.set_title("2m Temperature [°F]")
    ax2.set_title("2m Dewpoint [°F]")
    ax3.set_title("10m Wind Speed [mph]")
    ax4.set_title("Total Cloud Cover [%]")
    ax5.set_title("Pleasant Weather Outlook", fontweight = "bold")

    plt.tight_layout()

    plt.savefig(os.path.join('run', f"pwo_f_{timestep:02d}.png"))
    plt.close()

# In[ ]:





# In[ ]:




