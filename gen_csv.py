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
		choices=['daily', 'hourly', 'daily_climo', 'gdd', 'canopy_wetness', 'spray_conditions'])
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
		user_name = args.file.replace('.csv', '')
		user_dir = "./{}".format(user_name)

		if not os.path.exists(user_dir):
			os.makedirs(user_dir)

		output_name = './{}/{}_{}-{}.csv'.format(user_name, index, record['start'].replace('-', ''), record['end'].replace('-', ''))
		print "\tOutputting to: {}".format(output_name)
		with open(output_name, 'w') as output:
			csv_writer = csv.writer(output)
			header = ['location', 'latitude', 'longitude', 'date']

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

			# make header labels
			for date in sorted(r.keys()):
				for param in r[date].keys():
					if 'value' in r[date][param]:
						if r[date][param]['unit'] != 'n/a':
							header.append(str(param)+'('+str(r[date][param]['unit'])+')')
						else:
							header.append(str(param))
		 		break
			csv_writer.writerow(header)

		 	for date in sorted(r.keys()):
		 		row = [index, record['latitude'], record['longitude'], date]
		 		for param in r[date].keys():
		 			if 'value' in r[date][param]:
		 				row.append(str(r[date][param]['value']))
		 		csv_writer.writerow(row)


if __name__ == '__main__':
    main()
		 	