# Measure Correlate Predict

## Introduction
This python script takes two csv files containing weather data and compares the wind speeds and direction.
The `mast_data.csv` file contains one years wind speed and direction data from a weather mast placed at a potential wind farm site.
The `reference_site_Wind_speed_dir_1980_2013.csv` file contains weather data from a nearby met station from 1980 - 2013.

The aim of the exercise is to compare the data and make a long term (20 year) prediction for wind speed and direction at the proposed wind farm site.

## Tools
The python script uses a number of libraries.
  - scipy - for statistical functions
  - numpy - for mathematical functions
  - pandas - to help manage tables of data


## Methodology
The two csv files are loaded into pandas dataframes.

### Mast data
There a number of instruments on the mast including two anemometers at 60m. The maximum value at this height is used. The direction at 58m is used.
Other data is ignored. The timestamps are parsed correctly.

The mast data is cleaned to remove any invalid data. For a number of days, the instruments recorded 0's across all instruments. This indicates the instruments are not working. This data is ignored.

Hourly data is available from the reference site. The mast takes measurements every 10mins. The mast data is averaged out across the hour.

### Reference site data
The reference site data gives wind speed in knots. This is converted to m/s.
The reference data is taken at 10m. This is extrapolated to 60m using a shear coefficient of 0.2 to give the equivalent wind speed at 60m.


### Wind speed predictions
The hourly mast data and extrapolated reference data are joined on the timestamp.
The `linregress` function from `scipy` is used to get the slope, intercept and pearson correlation coefficient.

The slope and intercept are used to predict 20 years of data at the mast site.
The predicted wind speed annual averages are taken.
The RMSE between the predicted and measured wind speed is calculated.

### Wind direction bias
The wind direction bias can be calcuated by comparing the wind direction at the mast site with the wind direction at the reference site.
Unfortunately there is an issue calculating the average wind direction per hour at the mast site. The average of the 6 values per hour may not be valid due to wrap around issues.
This is

## Results
Based on these data files, the following values are calculated:

Pearson correlation coefficient:
0.77827227059
Slope:
0.721048002783
Intercept:
0.770927897863
Predicted mean wind speeds per year:
      ref_speed_ms  extr_speed_ms  site_speed
1980      5.188626       7.424764    9.228007
1981      5.405039       7.734443    9.657492
1982      5.594385       8.005393   10.033264
1983      6.104924       8.735957   11.046461
1984      6.296207       9.009678   11.426077
1985      6.571455       9.403549   11.972325
1986      6.848463       9.799939   12.522067
1987      6.094831       8.721515   11.026433
1988      6.135231       8.779326   11.106609
1989      6.311345       9.031340   11.456119
1990      6.638697       9.499771   12.105772
1991      5.166228       7.392713    9.183556
1992      5.074989       7.262153    9.002486
1993      5.022296       7.186751    8.897914
1994      5.184418       7.418741    9.219654
1995      4.998709       7.152998    8.851102
1996      5.161768       7.386330    9.174704
1997      5.090302       7.284064    9.032875
1998      5.235876       7.492377    9.321778
1999      5.213286       7.460051    9.276946
2000      5.042630       7.215848    8.938268
2001      4.773570       6.830831    8.404299
2002      5.135365       7.348548    9.122305
2003      4.965029       7.104803    8.784262
2004      4.915301       7.033643    8.685573
2005      4.984216       7.132259    8.822340
2006      4.915800       7.034357    8.686564
2007      4.734902       6.775499    8.327561
2008      4.950878       7.084553    8.756179
2009      4.902422       7.015214    8.660014
2010      4.614441       6.603122    8.088497
2011      5.035440       7.205559    8.923998
2012      4.850758       6.941285    8.557484
2013      5.154962       7.376592    9.161198
2014      5.140000       7.355181    9.131505
Measured mean wind speed from mast site:
8.47490142034
The Root Mean Square Error between predicted and measured windspeed:
2.9502990692
The Bias error in degrees:
-8.88163985661

## Further work
If temperature data was available, it would be good to remove mast data when the temperature is less than 0 as icing on instruments may be an issue.

