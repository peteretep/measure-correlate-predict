from scipy.stats import linregress
from IPython import embed
import pandas as pd
import numpy as np


class memoize(dict):
    """Used to memoize function values"""
    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        return self[args]

    def __missing__(self, key):
        result = self[key] = self.func(*key)
        return result


def kts_to_ms(kts_spd):
    """Converts a wind speed in knots to m/s"""
    return kts_spd * 0.514


def extrapolate_to_60(ms_speed):
    """Extrapolates a wind speed to a height of 60m using
       a shear coefficient 0.2"""
    spd_60 = ms_speed * (60 / 10) ** 0.2
    return spd_60


@memoize
def raw_mast_data():
    """Reads the mast_data.csv file and returns a dataframe
       with mast wind speed at 60m.
       It takes the maximum value from the two anemometers"""
    df = pd.read_csv('mast_data.csv',
                     header=11,
                     parse_dates=['time'],
                     dayfirst=True,
                     usecols=[0, 1, 2, 8],
                     names=['time', 's60_one', 's60_two', 'mast_dir'],
                     index_col='time')
    df['mean_mast_speed'] = df[['s60_one', 's60_two']].max(axis=1)
    return df


@memoize
def cleaned_mast_data():
    """Removes any data containing all 0's - when the mast is broken"""
    # TODO: Remove any data when the temperature is below zero!?
    df = raw_mast_data()[(raw_mast_data()['s60_one'] != 0) & (raw_mast_data()['s60_two'] != 0) & (raw_mast_data()['mast_dir'] != 0)]
    df = df.drop('s60_one', 1)
    df = df.drop('s60_two', 1)
    return df


def hourly_mast_data():
    return cleaned_mast_data().groupby(pd.TimeGrouper(freq='H')).mean()


@memoize
def raw_reference_data():
    df = pd.read_csv('reference_site_wind_speed_dir_1980_2013.csv',
                     parse_dates={'time': [0, 1, 2, 3]},
                     header=0)
    df['time'] = pd.to_datetime(df['time'], format="%Y %m %d %H")
    df['ref_speed_ms'] = pd.Series(kts_to_ms(df['wsp_kts']))
    df = df.drop('wsp_kts', 1)
    df = df.set_index('time')
    return df


def extrapolated_reference_data():
    """Returns a dataframe with the hourly wind speeds:
        - measured at the reference site,
        - extrapolated to 60m
    """
    df = raw_reference_data()
    df['extr_speed_ms'] = pd.Series(extrapolate_to_60(df['ref_speed_ms']))
    return df


@memoize
def joined_2012_data():
    """Returns a dataframe with the data for 2012"""
    df = hourly_mast_data().join(extrapolated_reference_data(), how='inner').dropna()
    return df


def predicted_speeds():
    """Returns a dataframe with the hourly wind speeds:
        - measured at the reference site,
        - extrapolated to 60m
        - predicted at the mast site
       """
    slope, intercept, r_value, p_value, std_err = linregress(joined_2012_data().mean_mast_speed.tolist(), joined_2012_data().extr_speed_ms.tolist())
    df = extrapolated_reference_data()
    df['site_speed'] = pd.Series((df['extr_speed_ms'] - intercept) / slope)
    df = df.drop('wdir_deg', 1)
    return df


def mean_speeds_from_predicted():
    """Returns a dataframe with yearly mean windspeeds for:
        - measured at the reference site,
        - extrapolated to 60m
        - predicted at the mast site
    """
    return predicted_speeds().groupby(predicted_speeds().index.year).mean()


def mean_speed_from_mast():
    """Returns the mean wind speed measured at the mast site"""
    return np.mean(cleaned_mast_data().mean_mast_speed.as_matrix())


def rms_error():
    """Returns the Root Mean Square Error between
       predicted and measured speeds"""
    df = predicted_speeds().join(hourly_mast_data()).dropna()
    actual = df.mean_mast_speed.as_matrix()
    predicted = df.site_speed.as_matrix()
    rmse = np.sqrt(((actual - predicted) ** 2).mean())
    return rmse


def bias_error_degrees():
    """The problem is getting the average windspeed for the hour from the mast.
       This is where wrap around is an issue.
       The hourly data we have collected in joined_2012_data may contain
       incorrect means wind directions per hour"""
    df = joined_2012_data()
    mast_direction = df.mast_dir.as_matrix()
    site_direction = df.wdir_deg.as_matrix()
    bias = (mast_direction - site_direction).mean()
    return bias


slope, intercept, r_value, p_value, std_err = linregress(joined_2012_data().mean_mast_speed.tolist(), joined_2012_data().extr_speed_ms.tolist())

print "Pearson correlation coefficient:"
print r_value
print "Slope:"
print slope
print "Intercept:"
print intercept

print "Predicted mean wind speeds per year:"
print mean_speeds_from_predicted()

print "Measured mean wind speed from mast site:"
print mean_speed_from_mast()

print "The Root Mean Square Error between predicted and measured windspeed:"
print rms_error()

print "The Bias error in degrees:"
print bias_error_degrees()
# embed()

# TODO: Get average wind direction of mast measurements
