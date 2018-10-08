----- Introduction -----
This repository is designed to allow ClearAg users a way to pull large amounts of historical data without having to write their own script.  gen_csv.py is the main script used to read in a csv of location and time ranges.  clearag_apis.py is the module that actually queries the APIs and returns the data.


----- clearag_apis.py -----
clearag_apis.py is a collection of methods to call historical ClearAg APIs in bulk.  The ClearAg API endpoint themselves are limited by the amount of data that can be pulled in a single query (366 days for daily endoints, 240 hours for hourly endpoints), these method can query in bulk.  Whatever start and end times are passed into the clearag_apis methods, whether from gen_csv or some other script, clearag_apis methods will return one master response object of all data.

Credentials:  You'll need to edit the 'app_id' and 'app_key' arguments to the credentials provided to you by ClearAg.

Date Format: Different endpoint methods require different date formats
	'%Y-%m-%d'
		get_daily_history()
		get_daily_climo()
		get_gdd()

	'%Y-%m-%dT%H:%M'
		get_hourly_history()
		get-leaf_canopy_wetness()
		get_hourly_spray_conditions()


----- gen_csv.py -----
Read an input file with locations and start/end times to pull ClearAg API data.

Command Line Arguments:

Name: file
Definition: input CSV file containing locations and times.  First row will be a label header.  Order doesn't matter as argument dictionary keys will be given names labels.  Requires 'latitude', 'longitude', 'start', 'end'.

Name: endpoint
Definition: ClearAg Endpoint family to use.  clearag_apis.py uses different methods based on the base endpoint being called, e.g. Daily Historical, Hourly Historical, etc.

Name: datatype
Definition: The specific endpoint in the --endpoint endpoint family. Options listed below.

	Endpoint Family: daily_wx
	Datatype Options: 
		1.	wx
			Endpoint: Daily Historical
			Link: https://docs.clearag.com/documentation/Field_Weather_API/latest#_daily_historical_v1_2
		2. 	airtemp
			Endpoint: Daily Historical Air Temperature
			Link: https://docs.clearag.com/documentation/Field_Weather_API/latest#_daily_historical_air_temperature_v1_2
		3. 	agweather
			Endpoint: Daily Historical Ag Weather
			Link: https://docs.clearag.com/documentation/Field_Weather_API/latest#_daily_historical_ag_weather_v1_0
		4.	soil
			Endpoint: Daily Soil
			Link: https://docs.clearag.com/documentation/Soil_Conditions_API/latest#_daily_soil_v1_1
		5.	hail
			Endpoint: Daily Historical Hail
			Link: https://docs.clearag.com/documentation/Field_Weather_API/latest#_daily_historical_hail_v1_2
		6. 	precip
			Endpoint: Precipitation Summary
			Link: https://docs.clearag.com/documentation/Field_Weather_API/latest#_precipitation_summary_v1_0
		7.	frostrisk
			Endpoint: Daily Frost Risk Climatology
			Link: https://docs.clearag.com/documentation/Field_Weather_API/latest#_daily_frost_risk_climatology_v1_0

	Endpoint Family: hourly_wx
	Datatype Options:
		1. 	wx
			Endpoint: Hourly Historical
			Link: https://docs.clearag.com/documentation/Field_Weather_API/latest#_hourly_historical_v1_1
		2.	hail
			Endpoint: Hourly Historical Hail
			Link: https://docs.clearag.com/documentation/Field_Weather_API/latest#_hourly_historical_hail_v1_1
		3. 	soil
			Endpoint: Hourly Soil
			Link: https://docs.clearag.com/documentation/Soil_Conditions_API/latest#_hourly_soil_v1_1

	Endpoint family: daily_climo
		Daily Climotology is the only method to use 'climoperiod'.  This is an integer that will determine if the method uses a five, ten, or thirty year climatological period.
	Datatype Options:
		2.	climoperiod > 10 or undefined
			Endpoint: Daily Historical Climotology
			Link: https://docs.clearag.com/documentation/Field_Weather_API/latest#_daily_historical_climatology_v1_3
		3.	climoperiod > 5
			Endpoint: Daily Historical 10-Year Climatology
			Link: https://docs.clearag.com/documentation/Field_Weather_API/latest#_daily_historical_10_year_climatology_v1_0
		4. 	climoperiod <= 5
			Endpoint: Daily Historical 5-Year Climotology
			Link: https://docs.clearag.com/documentation/Field_Weather_API/latest#_daily_historical_5_year_climatology_v1_0

	Endpoint family: gdd
	Note:  This is the only endpoint to use arguments 'base_temp' and 'upper_limit_temp'.  If these are not defined by user, defaults are base_temp=50 and upper_limit_temp=86.
		Endpoint: Single Sine GDD
		Link: https://docs.clearag.com/documentation/Crop_Health_API/latest#_single_sine_v1_0

	Endpoint family: canopy_wetness
		Endpoint: Leaf Canopy Wetness
		Link: https://docs.clearag.com/documentation/Crop_Health_API/latest#_leaf_canopy_wetness_v1_1

	Endpoint Family: spray_conditions
		Endpoint: Hourly Spray Conditions
		Link: https://docs.clearag.com/documentation/Field_Weather_API/latest#_hourly_spray_conditions_v1_0


# api_series_to_csv
