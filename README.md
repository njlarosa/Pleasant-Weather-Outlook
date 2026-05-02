# Meteo 473 Threat Index — Group 8

## Project Description
A Python script that generates where in the United States has ideal weather conditions considered to be "pleasant".
Pleasant Weather Outlook utilizes the North American Model every 3 hours for a total of 60 hours out from the valid time entered.

## Group Members
- Sam "Run" Testa
- Mark Riglin
- Christopher LaRosa

## How It Works
The project utilizes several Python libraries (primarily Herbie, Matplotlib, and Cartopy) to create a map of the United States. The outlook utilizes a high resolution North American Model (NAM) run for the date the user input. Pleasant Weather Outlook is weighted on the parameters with the following weights:
1. 2m Temperature (40%) 
2. 2m Dew Point (25%) 
3. Surface Wind Gusts (25%) 
4. Cloud Cover (10%)

Pleasant Weather Outlook runs on a 1-5 scale where 1 contains worst possible and 5 contains favorable conditions. The formula sums the four variables by contribution and multiples by a factor of 5, then rounded to the nearest whole number. (Any contribution > 0.5 is rounded up to the next nearest whole number, any contribution < 0.5 is rounded down to the next nearest whole number). Values of 0 and 1 are combined using a mask so that there is no blank space in the outlook. The addition of 0.1 of the formula is used to correct issues with the colorbar.

When the script 'pwo_gen.py' is ran, the script will instantly create two new folders, 'img_pwo' and 'netcdf' for organization purposes. 
- 'netcdf' is created for .nc files that contain the four variables from the NAM for the valid time entered by the user.
- 'img_pwo' is created for the 21 images that are created of the PWO and are sequentially numbered by the number of hours after the initial time (i.e. if the user enters 04-29-25-12z valid time, 'pwo_04-29-25-12_03.png' is three hours after the valid time (15z))

**This may take longer than desired as the NAM is a high resolution model. Allow a minute or two to run!**

## How to Run
1. Run "pwo_gen.py"
2. Enter a valid date to be your init time using YYYY-MM-DD-HH format (i.e. 2025-04-29-12)
3. Your Pleasant Weather Outlook images will deposit 21 images into a folder called 'img_pwo'

## License
MIT
