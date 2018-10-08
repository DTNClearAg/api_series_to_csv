import clearag_apis
import csv
import json
from arrow import utcnow, Arrow, get as get_time
from argparse import ArgumentParser
import os


def main():
	''' 
		Main function.
	'''
	args = create_argparser()
	fields, labels = read_input(args.file)
	create_csv(args, labels, fields)


def create_argparser():
	''' 
		Create argument parser and return arguments object.
	'''
	parser = ArgumentParser(
		description='Generate CSV of specified contraints')
	parser.add_argument('-f', '--file',
		help='Specify input CSV file'),
	parser.add_argument('-e', '--endpoint',
		help='Specify which endpoints to compile data from.',
		choices=['daily', 'hourly', 'daily_climo', 'gdd', 'canopy_wetness', 'spray_conditions', 'weatherplot'])
	parser.add_argument('-u', '--units',
		help='Specify units for data.  Option: us-std or si-std',
		choices=['us-std', 'si-std', 'us-std-precise', 'si-std-precise'],
		default='us-std')
	parser.add_argument('-cp', '--climoperiod',
		help='Specify integer period for climotological data')
	parser.add_argument('-dt', '--datatype',
		help='Specify datatype for endpoint to be used',
		choices=['wx', 'airtemp', 'agweather', 'soil', 'hail', 'precip', 'frostrisk'])
	parser.add_argument('-bt', '--base_temp',
		help='Base temp for GDD')
	parser.add_argument('-ult', '--upper_limit_temp',
		help='Upper limit temp for GDD')

	return parser.parse_args()


def read_input(csv_name):
	'''
		Function reads through the input CSV to form a dictionary for querying data.  
		Requires header in this order: location, latitude, longitude, start, end
		Arguments:
			csv_name - input CSV name provided by create_argparser()
	'''
	fields = {}
	labels = []
	first_record = True
	with open(csv_name, 'rU') as csvfile:
		file_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for record in file_reader:
			# This assumes the header row will be a label row
			if first_record:
				for label in record:
					if '\xef\xbb\xbf' in label:
						label = label.replace('\xef\xbb\xbf', '')
					labels.append(label)
				first_record = False
			else:
				fields[record[0]] = {}
				for value in range(1, len(record)):
					fields[record[0]][labels[value]] = record[value]

	return fields, labels


def create_csv(args, labels, fields):
	''' 
		This function calls the APIs via clearag_apis.py.
		The returned dats is written to CSVs, one CSV per location specified by the input CSV.
		Output CSVs are collected in a folder with the same name as the input CSV.
		Args:
			args - Commandline arguments collected by create_argparser()
			labels - The Header provided by the input CSV
			fields - The actual field locations, their latitudes, longitudes, start times, and end times
	'''
	for index in sorted(fields.keys()):
		record = fields[index]
		user_name = 'yen_test_locations_v2' #args.file.replace('.csv', '')
		user_dir = "./{}".format(user_name)

		if not os.path.exists(user_dir):
			os.makedirs(user_dir)

		output_name = './{}/{}_{}-{}.csv'.format(user_name, index, record['start'].replace('-', ''), record['end'].replace('-', ''))
		print "\tOutputting to: {}".format(output_name)
		with open(output_name, 'w') as output:
			csv_writer = csv.writer(output)
			header = ['Location', 'Date [YYYY-MM-DD]', 'Latitude', 'Longitude', 'Units', 'Historical/Forecast [H/F]', 
				'Temperature Min [C]', 
				'Temperature Avg [C]', 
				'Temperature Max [C]', 
				'Temperature Climatological Min [C]', 
				'Temperature Climatological  Avg [C]', 
				'Temperature Climatological Max [C]', 
				'Relative Humidity Min [%]', 
				'Relative Humidity [%]', 
				'Relative Humidity Max [%]', 
				'Wind Min [kph]', 
				'Wind Avg [kph]', 
				'Wind Max [kph]', 'Climatological Avg Wind [kph]', 'Cloud Cover [%]', 'Solar Radiation [MJm^-2]', 'Solar Radiation Accumulated [MJm^-2]', 'Solar Radiation Climatology [MJm^-2]', 'Solar Radiation Climatology Accumulated [MJm^-2]', 'Precipitation [mm]', 'Precipitation Total [mm]', 'Precipitation Climatological [mm]', 'Precipitation Climatological Total [mm]', 'Soil Temperature Min 0 to 10cm [C]', 'Soil Temperature Avg 0 to 10cm [C]', 'Soil Temperature Max 0 to 10cm [C]', 'Soil Moisture 0 to 10cm [mm]', 'Soil Moisture 0 to 200cm [mm]', 'Scaled Soil Moisture 0 to 10cm [Historic Percentile]', 'Scaled Soil Moisture 0 to 200cm [Historic Percentile]', 'Evapotranspiration [mm]', 'AGDD', 'GDD']

			if args.endpoint == 'daily':
				r = clearag_apis.get_daily_history(record['latitude'], record['longitude'], record['start'], record['end'], units=args.units, datatype=args.datatype)
			elif args.endpoint == 'hourly':
				r = clearag_apis.get_hourly_history(record['latitude'], record['longitude'], record['start'], record['end'], units=args.units, datatype=args.datatype)
			elif args.endpoint == 'daily_climo':
				r = clearag_apis.get_daily_climo(record['latitude'], record['longitude'], record['start'], record['end'], units=args.units, climoperiod=args.climoperiod, datatype=args.datatype)
			elif args.endpoint == 'gdd':
				r = clearag_apis.get_gdd(record['latitude'], record['longitude'], record['start'], record['end'], units=args.units, base_temp=args.base_temp, upper_limit_temp=args.upper_limit_temp)
			elif args.endpoint == 'canopy_wetness':
				r = clearag_apis.get_leaf_canopy_wetness(record['latitude'], record['longitude'], record['start'], record['end'])
			elif args.endpoint == 'spray_conditions':
				r = clearag_aaapies.get_hourly_spray_conditions(record['latitude'], record['longitude'], record['start'], record['end'])
			elif args.endpoint == 'weatherplot':
				r_wx = clearag_apis.get_daily_history(record['latitude'], record['longitude'], record['start'], record['end'], units=args.units, datatype='wx')
				r_soil = clearag_apis.get_daily_history(record['latitude'], record['longitude'], record['start'], record['end'], units=args.units, datatype='soil')
				r_c = clearag_apis.get_daily_climo(record['latitude'], record['longitude'], record['start'], record['end'], units=args.units)
				r_gdd = clearag_apis.get_gdd(record['latitude'], record['longitude'], record['start'], record['end'], units=args.units)

			# make header labels
			# for date in sorted(r_wx.keys()):
			# 	for param in r[date].keys():
			# 		if 'value' in r_wx[date][param] and ('short_wave_radiation_avg' in param or param == 'precip_acc_period' or 'air_temp_' in param):
			# 			if param == 'short_wave_radiation_avg':
			# 				header.append(str(param)+'[MJ/m^2]')
			# 			else: 
			# 				if r_wx[date][param]['unit'] != 'n/a':
			# 					header.append(str(param)+'['+str(r_wx[date][param]['unit'])+']')
			# 				else:
			# 					header.append(str(param))
			# 		break
			csv_writer.writerow(header)

			precip_total = 0
			precip_climo_total = 0
			rad_total = 0
			rad_climo_total = 0
		 	for date in sorted(r_wx.keys()):
		 		rad = float(r_wx[str(date)]['short_wave_radiation_avg']['value']) * 0.0864
		 		rad_total += rad

		 		rad_climo = float(r_c[get_time(str(date)).format('MM-DD')]['short_wave_radiation_avg']['value']) * 0.0864
		 		rad_climo_total += rad_climo

		 		precip = r_wx[str(date)]['precip_acc_period']['value']
		 		precip_total += precip

		 		precip_climo = r_c[get_time(str(date)).format('MM-DD')]['precip_acc_avg']['value']
		 		precip_climo_total += precip_climo

		 		row = [index, date, record['latitude'], record['longitude'], args.units, 'H', 
		 			r_wx[date]['air_temp_min']['value'], 
		 			r_wx[date]['air_temp_avg']['value'], 
		 			r_wx[date]['air_temp_max']['value'], 
		 			r_c[get_time(str(date)).format('MM-DD')]['air_temp_min_avg']['value'], 
		 			r_c[get_time(str(date)).format('MM-DD')]['air_temp_avg']['value'], 
		 			r_c[get_time(str(date)).format('MM-DD')]['air_temp_max_avg']['value'], 
		 			r_wx[date]['relative_humidity_min']['value'], 
		 			r_wx[date]['relative_humidity_avg']['value'], 
		 			r_wx[date]['relative_humidity_max']['value'], 
		 			r_wx[date]['wind_speed_min']['value'], 
		 			r_wx[date]['wind_speed_avg']['value'], 
		 			r_wx[date]['wind_speed_max']['value'], 
		 			r_c[get_time(str(date)).format('MM-DD')]['wind_speed_avg']['value'], 
		 			r_wx[date]['cloud_cover_avg']['value'], 
		 			
		 			rad, #r[date]['Solar Radiation [MJm^-2]']['value'], 
		 			rad_total, #r[date]['Solar Radiation Accumulated [MJm^-2]']['value'], 
		 			
		 			rad_climo, #r[date]['Solar Radiation Climatology [MJm^-2]']['value'], 
		 			rad_climo_total, #r[date]['Solar Radiation Climatology Accumulated [MJm^-2]']['value'], 
		 			
		 			precip, #r_wx[date]['precip_acc_period']['value'], 
		 			precip_total, #r[date]['Precipitation Total [mm]']['value'], 

		 			precip_climo, #r_c[date]['precip_acc_avg']['value'], 
		 			precip_climo_total, #r[date]['Precipitation Climatological Total [mm]']['value'], 

		 			r_soil[date]['soil_temp_min_0to10cm']['value'], 
		 			r_soil[date]['soil_temp_0to10cm']['value'], 
		 			r_soil[date]['soil_temp_max_0to10cm']['value'], 
		 			r_soil[date]['soil_moisture_0to10cm']['value'], 
		 			r_soil[date]['soil_moisture_0to200cm']['value'], 
		 			r_soil[date]['scaled_soil_moisture_0to10cm']['value'], 
		 			r_soil[date]['normalized_soil_moisture_0to200cm']['value'], 
		 			r_wx[date]['pet_period']['value'],
		 			r_gdd[date]['agdd'], 
		 			r_gdd[date]['gdd']
		 		]
				# r_gdd = clearag_apis.get_gdd(record['latitude'], record['longitude'], date, date, units=args.units)
				# row.append([
			 	# 		r_gdd[date]['agdd'], 
			 	# 		r_gdd[date]['gdd']
			 	# 	])


		 		# for param in r_wx[date].keys():
		 		# 	if 'value' in r_wx[date][param] and ('short_wave_radiation_avg' in param or param == 'precip_acc_period' or 'air_temp_' in param):
		 		# 		if param == 'short_wave_radiation_avg' and r_wx[date][param]['value'] != 'n/a':
		 		# 			row.append(str(float(r_wx[date][param]['value']) * 0.0864))
		 		# 		else:
		 		# 			row.append(str(r_wx[date][param]['value']))
		 		csv_writer.writerow(row)


if __name__ == '__main__':
    main()
		 	