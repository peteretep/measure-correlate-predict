require 'pry'
require 'csv'
require 'time'
require 'awesome_print'
require 'statsample'

def average_speed_at_60(speed1, speed2)
  (speed1.to_f + speed2.to_f) / 2
end

def extrapolate_mast_wind_speed(speed1, speed2)
  average_speed_at_60(speed1, speed2).to_i
end

def extrapolate_ref_wind_speed(measured_speed)
  # TODO: extrapolate
  measured_speed
end

# Converts the csv file to a nice ruby hash
# TODO: do the times take care of daylight savings or are they in GMT??
def convert_reference_data
  reference_data = CSV.read('reference_site_wind_speed_dir_1980_2013.csv')
  reference_array = []
  reference_data.drop(1).each do |row|
    time = Time.new(row[0], row[1], row[2], row[3])
    row_hash = { time: time,
     speed: extrapolate_ref_wind_speed(row[4].to_i),
     direction: row[5].to_i }
     reference_array << row_hash
   end
   reference_array
 end

 def convert_mast_data
  mast_data = CSV.read('mast_data.csv', 'r')
  mast_array = []
  mast_data.drop(12).each do |row|
    time = Time.parse(row[0])
    # TODO: Change this to average of windspeeds over the hour
    next unless time.min == 0
    row_hash = { time: Time.parse(row[0]),
     speed: extrapolate_mast_wind_speed(row[1], row[2]),
     direction: row[8].to_i }
     mast_array << row_hash
   end
   mast_array
 end

 def mast_data
  @mast_data ||= convert_mast_data
end

def reference_data
  @reference_data ||= convert_reference_data
end

def mast_data_start_time
  mast_data.first[:time]
end

def mast_data_end_time
  mast_data.last[:time]
end

def same_hour(time1, time2)
  return false unless time1.year == time2.year
  return false unless time1.month == time2.month
  return false unless time1.day == time2.day
  return false unless time1.hour == time2.hour
  return true
end

def mast_hourlys

  d = convert_mast_data
  d.each do |row|
    puts row[:time]
  end
  binding.pry
end

def reference_data_between

  data_between = []

  reference_data.each do |row|
    # binding.pry
    next unless row[:time].between?(mast_data_start_time, mast_data_end_time)
    data_between << row
  end
  return false unless data_between.map{|x| x[:time]} == mast_data.map{|x| x[:time]}

  data_between
end


def pearson
  @pearson ||= covariance(reference_data_between, mast_data) / (standard_deviation(reference_data_between).to_f * standard_deviation(mast_data).to_f)
end

# puts convert_mast_data
# binding.pry
puts reference_data_between
binding.pry

