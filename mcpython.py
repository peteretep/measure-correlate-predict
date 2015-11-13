import csv
from datetime import datetime
from itertools import islice
from scipy.stats.stats import pearsonr
from IPython import embed


class memoize(dict):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        return self[args]

    def __missing__(self, key):
        result = self[key] = self.func(*key)
        return result


def average_wind_speed(s1, s2):
    return int(((float(s1) + float(s2)) / 2))


def mast_format_time(timestring):
    try:
        return datetime.strptime(timestring, '%d/%m/%Y %H:%M')
    except ValueError:
        return datetime.strptime(timestring, '%d/%m/%Y')


def ref_format_time(row):
    return datetime(int(row[0]), int(row[1]), int(row[2]), int(row[3]))


@memoize
def mast_data():
    with open('mast_data.csv', 'rb') as mastfile:
        mastreader = csv.reader(mastfile)
        mast_data_arr = []
        for row in islice(mastreader, 12, None):
            time = mast_format_time(row[0])
            if time.minute != 0:
                continue
            row_dict = {'time': time,
                        'speed': average_wind_speed(row[1], row[2]),
                        'direction': int(float(row[8]))}
            mast_data_arr.append(row_dict)
        return mast_data_arr


@memoize
def mast_data_start_time():
    return mast_data()[0]['time']


@memoize
def mast_data_end_time():
    return mast_data()[-1]['time']


@memoize
def reference_data():
    with open('reference_site_wind_speed_dir_1980_2013.csv', 'rb') as reffile:
        referencereader = csv.reader(reffile)
        ref_data_arr = []
        for row in islice(referencereader, 1, None):
            row_dict = {'time': ref_format_time(row),
                        'speed': int(row[4]),
                        'direction': int(row[5])}
            ref_data_arr.append(row_dict)
        return ref_data_arr


def reference_data_in_2012():
    data_2012 = []
    for row in reference_data():
        if mast_data_start_time() <= row['time'] <= mast_data_end_time():
            data_2012.append(row)
    return data_2012


def reference_speeds():
    speeds = []
    for row in reference_data_in_2012():
        speeds.append(row['speed'])
    return speeds


def mast_speeds():
    speeds = []
    for row in mast_data():
        speeds.append(row['speed'])
    return speeds


embed()
