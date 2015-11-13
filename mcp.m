reference_data_file = 'reference_site_wind_speed_dir_1980_2013.csv';
reference_data = csvread(reference_data_file, 1,0);

mast_data_file = 'mast_data.csv';
mast_data = csvread(mast_data_file, 12,0);




# Mast data is taken every 10 mins. 
# Need to get the average
mast_data
