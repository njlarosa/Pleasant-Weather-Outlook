# Pleasant-Weather-Outlook
Developed by Mark Riglin, Sam Testa, and Christopher La Rosa.

A python-coded script that generates a CONUS comfortability outlook index for a given NetCDF file.

Based on the North American Model (NAM), the outlook utilizes Matplotlib, Cartopy, numpy, and xarray.

Depicts 2m Temperature, 2m Dewpoint, 10m Wind Speed, and Total Cloud Cover over the continental United States.


Weight Scale is as follows:
1. 2m Temperature (45%)
2. 2m Dew Point (30%)
3. 10m Wind Speed (15%)
4. Total Cloud Cover (10%)

A legend is provided in the bottom left, starting at 1 with worst possible conditions, and incremently increases to 5 with the most favorable conditions.
