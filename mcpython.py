import csv
from datetime import datetime
from itertools import islice
from scipy.stats import linregress
import matplotlib.pyplot as plt
from IPython import embed
import pandas as pd


class memoize(dict):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        return self[args]

    def __missing__(self, key):
        result = self[key] = self.func(*key)
        return result


def kts_to_ms(kts_spd):
    return kts_spd * 0.514


def extrapolate_to_60(ms_speed):
    spd_60 = ms_speed * (60 / 10) ** 0.143
    return spd_60


@memoize
def raw_mast_data():
    df = pd.read_csv('mast_data.csv',
                     header=11,
                     parse_dates=['time'],
                     usecols=[0, 1, 2, 8],
                     names=['time', 's60_one', 's60_two', 'mast_dir'],
                     index_col='time')
    df['mean_mast_speed'] = pd.Series(((df.s60_one + df.s60_two) / 2),
                                      index=df.index)
    return df


@memoize
def cleaned_mast_data():
    df = raw_mast_data()[(raw_mast_data()['s60_one'] != 0) & (raw_mast_data()['s60_two'] != 0) & (raw_mast_data()['mast_dir'] != 0)]
    df = drop_unused_cols(df)
    return df


def drop_unused_cols(df):
    df = df.drop('s60_one', 1)
    df = df.drop('s60_two', 1)
    return df


def hourly_mast_data():
    return cleaned_mast_data().groupby(pd.TimeGrouper(freq='H')).mean()


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
    df = raw_reference_data()
    df['extr_speed_ms'] = pd.Series(extrapolate_to_60(df['ref_speed_ms']))
    return df


@memoize
def joined_2012_data():
    df = hourly_mast_data().join(extrapolated_reference_data()).dropna()
    return df


# def plot_speeds_with_time():
#     plt.plot(mast_times(), mast_speeds(), 'ro')
#     plt.plot(reference_times(), reference_speeds(), 'bo')
#     plt.ylabel('Wind Speed')
#     plt.xlabel('Time')
#     plt.show()


# def plot_ref_mast():
#     plt.plot(reference_speeds(), mast_speeds(), 'ro')
#     plt.ylabel('Mast Speeds')
#     plt.xlabel('Reference Speeds')
#     plt.show()


# correlation_coeff = pearsonr(mast_speeds(), reference_speeds())
# print "The Pearson correlation coefficient is %f" % correlation_coeff[0]

slope, intercept, r_value, p_value, std_err = linregress(joined_2012_data().mean_mast_speed.tolist(), joined_2012_data().extr_speed_ms.tolist())

print "Pearson correlation coefficient: %f" % r_value
print "Slope: %f" % slope
print "Intercept: %f" % intercept


# def predict(ref_speed):
#     site_speed = (slope * ref_speed) + intercept
#     return site_speed


# def predicted_speeds():
#     predicted_data = []
#     for row in reference_data():
#         row_dict = {'time': row['time'],
#                     'reference_speed': row['speed'],
#                     'site_speed': predict(row['speed'])}
#         predicted_data.append(row_dict)
#     return predicted_data


embed()
# cProfile.run(pearsonr(mast_speeds(), reference_speeds()))
# embed()

# TODO: Get average of mast measurements
# TODO: Save big_dict to a new csv file
