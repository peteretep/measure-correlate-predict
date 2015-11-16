import csv
from datetime import datetime
from itertools import islice
from scipy.stats.stats import pearsonr
from scipy.stats import linregress
import matplotlib.pyplot as plt
from IPython import embed


class memoize(dict):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        return self[args]

    def __missing__(self, key):
        result = self[key] = self.func(*key)
        return result


def average_mast_speed(s1, s2):
    return float(((float(s1) + float(s2)) / 2))


def mast_format_time(timestring):
    try:
        return datetime.strptime(timestring, '%d/%m/%Y %H:%M')
    except ValueError:
        return datetime.strptime(timestring, '%d/%m/%Y')


def ref_format_time(row):
    return datetime(int(row[0]), int(row[1]), int(row[2]), int(row[3]))


@memoize
def mast_data_start_time():
    return mast_data()[0]['time']


@memoize
def mast_data_end_time():
    return mast_data()[-1]['time']


@memoize
def mast_data():
    with open('mast_data.csv', 'rb') as mastfile:
        mastreader = csv.reader(mastfile)
        mast_data_arr = []
        for row in islice(mastreader, 12, None):
            time = mast_format_time(row[0])
            if time.minute != 0:
                continue
            if row[1] == '0' and row[2] == '0' and row[8] == '0':
                continue
            row_dict = {'time': time,
                        'speed': average_mast_speed(row[1], row[2]),
                        'direction': int(float(row[8]))}
            mast_data_arr.append(row_dict)
        return mast_data_arr


def ref_speed_in_ms(kts_spd):
    return kts_spd * 0.514


def extrapolated_ref_speed(ms_speed):
    spd_60 = ms_speed * (60 / 10) ** 0.143
    return spd_60


def reference_speed(kts_spd):
    ms_speed = ref_speed_in_ms(kts_spd)
    return extrapolated_ref_speed(ms_speed)


@memoize
def reference_data():
    with open('reference_site_wind_speed_dir_1980_2013.csv', 'rb') as reffile:
        referencereader = csv.reader(reffile)
        ref_data_arr = []
        for row in islice(referencereader, 1, None):
            row_dict = {'time': ref_format_time(row),
                        'speed': reference_speed(int(row[4])),
                        'direction': int(row[5])}
            ref_data_arr.append(row_dict)
        return ref_data_arr


@memoize
def big_dict():
    cleaned_array = []
    for row in mast_data():
        ref_row = next((r for r in reference_data() if r['time'] == row['time']), None)
        row_dict = {'time': row['time'],
                    'mast_speed': row['speed'],
                    'mast_direction': row['direction'],
                    'reference_speed': ref_row['speed'],
                    'reference_direction': ref_row['direction']}
        cleaned_array.append(row_dict)
    return cleaned_array


def reference_data_in_2012():
    data_2012 = []
    for row in reference_data():
        if mast_data_start_time() <= row['time'] <= mast_data_end_time():
            data_2012.append(row)
    return data_2012


def reference_speeds():
    return [d['reference_speed'] for d in big_dict()]


def mast_speeds():
    return [d['mast_speed'] for d in big_dict()]


def reference_times():
    times = []
    for row in reference_data_in_2012():
        times.append(row['time'])
    return times


def mast_times():
    times = []
    for row in mast_data():
        times.append(row['time'])
    return times


def plot_speeds_with_time():
    plt.plot(mast_times(), mast_speeds(), 'ro')
    plt.plot(reference_times(), reference_speeds(), 'bo')
    plt.ylabel('Wind Speed')
    plt.xlabel('Time')
    plt.show()


def plot_ref_mast():
    plt.plot(reference_speeds(), mast_speeds(), 'ro')
    plt.ylabel('Mast Speeds')
    plt.xlabel('Reference Speeds')
    plt.show()


correlation_coeff = pearsonr(mast_speeds(), reference_speeds())
print "The Pearson correlation coefficient is %f" % correlation_coeff[0]

slope, intercept, r_value, p_value, std_err = linregress(mast_speeds(), reference_speeds())

print "Pearson correlation coefficient: %f" % r_value
print "Slope: %f" % slope
print "Intercept: %f" % intercept


def predict(ref_speed):
    site_speed = (slope * ref_speed) + intercept
    return site_speed


def predicted_speeds():
    predicted_data = []
    for row in reference_data():
        row_dict = {'time': row['time'],
                    'reference_speed': row['speed'],
                    'site_speed': predict(row['speed'])}
        predicted_data.append(row_dict)
    return predicted_data


embed()
# cProfile.run(pearsonr(mast_speeds(), reference_speeds()))
# embed()

# TODO: Get average of mast measurements
# TODO: Save big_dict to a new csv file
