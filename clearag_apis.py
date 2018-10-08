# Built-in modules
import os

from time import tzset
from datetime import datetime
from string import Template
import urllib, json
import ssl


# Default items
url_base = 'https://ag.us.clearapis.com'
# ClearAg API Credentials:
app_id = ''
app_key = ''

os.environ['TZ'] = 'UTC'
tzset()
units_def = 'us-std'


def get_daily_history(lat,lon,start_date,end_date,units=units_def, datatype="wx"):
    ''' 
        Query any Daily endpoint excluding Climotology
        Arguments:
            lat - latitude
            lon - longitude
            start_date - start date, expected form YYYY-MM-DD
            end_date - end date, expected form YYYY-MM-DD
            units - measurement units, option us-std, si-std, us-std-precise, si-std-precise
            datatype - requested endpoint to query data from
    '''
    global units_def
    global url_base
    global app_id
    global app_key 
  
    max_range_sec = 365 * 86400 
    # Gets daily historical location for 1 lat/lon and time range
    data = None
    print units_def,url_base,app_id,app_key
    if datatype == "wx": 
        url_t = "{}/v1.2/historical/daily?app_id={}&app_key={}&location=$lat,$lon&start=$time_beg&end=$time_end&unitcode=$units".format(url_base, app_id, app_key)
    elif datatype == "airtemp":
        url_t = "{}/v1.2/historical/daily/air_temp?app_id={}&app_key={}&location=$lat,$lon&start=$time_beg&end=$time_end&unitcode=$units".format(url_base, app_id, app_key)
    elif datatype == "agweather":
        url_t = "{}/v1.0/historical/daily/ag_weather?app_id={}&app_key={}&location=$lat,$lon&start=$time_beg&end=$time_end&unitcode=$units".format(url_base, app_id, app_key)
    elif datatype == "soil":
        url_t = "{}/v1.1/daily/soil?app_id={}&app_key={}&location=$lat,$lon&start=$time_beg&end=$time_end&unitcode=$units".format(url_base, app_id, app_key)
    elif datatype == 'hail':
        url_t = "{}/v1.2/historical/daily/hail?app_id={}&app_key={}&location=$lat,$lon&start=$time_beg&end=$time_end&unitcode=$units".format(url_base, app_id, app_key)
    elif datatype == 'precip':
        url_t = "{}/v1.1/historical/daily/precip?app_id={}&app_key={}&location=$lat,$lon&start=$time_beg&end=$time_end&unitcode=$units".format(url_base, app_id, app_key)
    elif datatype == "frostrisk":
        url_t = "{}/v1.0/historical/daily/climatology/frost_risk?app_id={}&app_key={}&location=$lat,$lon&start_date=$time_beg&end_date=$time_end&unitcode=$units".format(url_base, app_id, app_key)
    else:
        print "Undefined data type requested: ", datatype
        return
        
    # Get start/stop epoch times from input date strings of YYYY-MM-DD format
    d_beg = datetime(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10]),0,0,0)
    d_end = datetime(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10]),0,0,0)

    # compute epochs
    time_beg = int(d_beg.strftime("%s"))
    time_end = int(d_end.strftime("%s"))

    time1 = time_beg
    # The 'end' value when selecting range for this endpoint isn't inclusive.
    time2 = min([time_end,time1+max_range_sec]) + 1
 
    while time1 < time_end:
        url = Template(url_t)
        if datatype == "frostrisk":
            url2get = url.substitute(lat=lat,lon=lon,time_beg=start_date,time_end=end_date,units=units)
        else:
            url2get = url.substitute(lat=lat,lon=lon,time_beg=time1,time_end=time2,units=units)
        print url2get
        response = urllib.urlopen(url2get)

        if response is not None:
            if data == None:

                # We are restricting to one location per call of this routine,
                # so let's strip off the outer element of the JSON ("lat,lon" key)
                # and let the calling application be responsible for knowing that.

                data = (json.loads(response.read())).values()[0]
            else:
                data.update( (json.loads(response.read())).values()[0])

        # Time2 had that extra second, so clip it off and re-add for next time
        time1 = time2 + 86400 - 1 
        time2 = min([time1+max_range_sec,time_end]) + 1

    return data


def get_hourly_history(lat,lon,start_date,end_date,units=units_def,datatype="wx"):
    ''' 
        Query any Daily endpoint excluding Climotology
        Arguments:
            lat - latitude
            lon - longitude
            start_date - start date, expected form YYYY-MM-DDTHH:MM
            end_date - end date, expected form YYYY-MM-DDTHH:MM
            units - measurement units, option us-std, si-std, us-std-precise, si-std-precise
            datatype - requested endpoint to query data from
    '''
    global units_def
    global url_base
    global app_id
    global app_key 


    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
  
    max_range_sec = 240 * 3600 
    # Gets daily historical location for 1 lat/lon and time range
    data = None
    print units_def,url_base,app_id,app_key 
    if datatype == "wx":
        url_t = "{}/v1.1/historical/hourly?app_id={}&app_key={}&location=$lat,$lon&start=$time_beg&end=$time_end&unitcode=$units".format(url_base, app_id, app_key)
    elif datatype == "hail":
        url_t =  "{}/v1.1/historical/hourly/hail?app_id={}&app_key={}&location=$lat,$lon&start=$time_beg&end=$time_end&unitcode=$units".format(url_base, app_id, app_key)
    elif datatype == "soil":
        url_t = "{}/v1.1/historical/hourly/soil?app_id={}&app_key={}&location=$lat,$lon&start=$time_beg&end=$time_end&unitcode=$units".format(url_base, app_id, app_key)
    elif datatype == "soilraw":
        url_t = "{}/v1.2/historical/hourly/soil/raw?location=$lat,$lon&start=$time_beg&end=$time_end&unitcode=$units" % (url_base)
    else:
        print "Undefined data type requested: ", datatype
        return
        
    # Get start/stop epoch times from input date strings of YYYY-MM-DDTHH:MM format
    d_beg = datetime.strptime(start_date,'%Y-%m-%dT%H:%M')
    d_end = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')

    # compute epochs
    time_beg = int(d_beg.strftime("%s"))
    time_end = int(d_end.strftime("%s"))

    time1 = time_beg
    time2 = min([time_end,time1+max_range_sec])
 
    while time1 < time_end:
        url = Template(url_t)
        url2get = url.substitute(lat=lat,lon=lon,time_beg=time1,time_end=time2,units=units)
        print url2get
        response = urllib.urlopen(url2get, context=ctx)

        if response is not None:
            if data == None:

                # We are restricting to one location per call of this routine,
                # so let's strip off the outer element of the JSON ("lat,lon" key)
                # and let the calling application be responsible for knowing that.

                data = (json.loads(response.read())).values()[0]
            else:
                data.update( (json.loads(response.read())).values()[0])

        time1 = time2 + 3600
        time2 = min([time1+max_range_sec,time_end])

    return data
    

def get_daily_climo(lat,lon,start_date,end_date,units=units_def, climoperiod=30):
    ''' 
        Query Daily Climotological endpoints
        Arguments:
            lat - latitude
            lon - longitude
            start_date - start date, expected form YYYY-MM-DD
            end_date - end date, expected form YYYY-MM-DD
            units - measurement units, option us-std, si-std, us-std-precise, si-std-precise
            climoperiod - define number of years to query climotological data
    '''
    global units_def
    global url_base
    global app_id
    global app_key 
  
    max_range_sec = 366 * 86400 
    # Gets daily historical location for 1 lat/lon and time range
    data = None
    print units_def,url_base,app_id,app_key
    if climoperiod > 10: 
        url_t = "{}/v1.3/historical/daily/climatology?app_id={}&app_key={}&location=$lat,$lon&start_date=$time_beg&end_date=$time_end&unitcode=$units".format(url_base, app_id, app_key)
    elif climoperiod > 5:
        url_t = "{}/v1.0/historical/daily/climatology/ten_year?app_id={}&app_key={}&location=$lat,$lon&start_date=$time_beg&end_date=$time_end&unitcode=$units".format(url_base, app_id, app_key)
    else:
        url_t = "{}/v1.0/historical/daily/climatology/five_year?app_id={}&app_key={}&location=$lat,$lon&start_date=$time_beg&end_date=$time_end&unitcode=$units".format(url_base, app_id, app_key)
        
    # Get start/stop epoch times from input date strings of YYYY-MM-DD format
    d_beg = datetime(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10]),0,0,0)
    # We add 1-second to end date because of the non-inclusive nature of our end date arguments in the apis
    d_end = datetime(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10]),0,0,1)

    # compute epochs
    time_beg = int(d_beg.strftime("%s"))
    time_end = int(d_end.strftime("%s"))
    if ((time_end-time_beg) > max_range_sec):
        time_end =time_beg + max_range_sec
        d_end = datetime.utcfromtimestamp(time_end)
        

    start_date = d_beg.strftime("%Y-%m-%d")
    end_date = d_end.strftime("%Y-%m-%d")
     
   
    url = Template(url_t)
    url2get = url.substitute(lat=lat,lon=lon,time_beg=start_date,time_end=end_date,units=units)
    print url2get
    response = urllib.urlopen(url2get)

    if response is not None:
        if data == None:

            # We are restricting to one location per call of this routine,
            # so let's strip off the outer element of the JSON ("lat,lon" key)
            # and let the calling application be responsible for knowing that.

            data = (json.loads(response.read())).values()[0]
        else:
            data.update( (json.loads(response.read())).values()[0])

    return data


def get_gdd(lat,lon,start_date,end_date,units=units_def,base_temp=50,upper_limit_temp=86):
    ''' 
        Query Growing Degree Days endpoint
        Arguments:
            lat - latitude
            lon - longitude
            start_date - start date, expected form YYYY-MM-DD
            end_date - end date, expected form YYYY-MM-DD
            units - measurement units, option us-std, si-std, us-std-precise, si-std-precise
            base_temp - initial temperature
            upper_limit_temp - upper-limit temperature
    '''
    global units_def
    global url_base
    global app_id
    global app_key

    max_range_sec = 365 * 86400
    # Gets daily historical location for 1 lat/lon and time range
    data = None
    url_t = "{}/v1.0/crop_health/general/single_sine_gdd?app_id={}&app_key={}&location=$lat,$lon&start_date=$time_beg&days=$days&base_temp=$base_temp&upper_limit_temp=$upper_limit_temp".format(url_base, app_id, app_key)

    # Get start/stop epoch times from input date strings of YYYY-MM-DD format
    d_beg = datetime(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10]),0,0,0)
    # We add 1-second to end date because of the non-inclusive nature of our end date arguments in the apis
    d_end = datetime(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10]),0,0,1)

    # compute epochs
    time_beg = int(d_beg.strftime("%s"))
    time_end = int(d_end.strftime("%s"))

    time1 = time_beg
    # days = int((time_end - time_beg) / 86400)+1
    # The 'end' value when selecting range for this endpoint isn't inclusive.
    time2 = min([time_end,time1+max_range_sec]) + 1

    while time1 < time_end:
        days = int((time2 - time1) / 86400+1)
        if days > 366:
            days = 366
        url = Template(url_t)
        url2get = url.substitute(lat=lat,lon=lon,time_beg=time1, days=days,upper_limit_temp=upper_limit_temp,base_temp=base_temp)
        print url2get
        response = urllib.urlopen(url2get)

        if response is not None:
            if data == None:

                # We are restricting to one location per call of this routine,
                # so let's strip off the outer element of the JSON ("lat,lon" key)
                # and let the calling application be responsible for knowing that.

                data = (json.loads(response.read())).values()[0].values()[0]
            else:
                data.update( (json.loads(response.read())).values()[0].values()[0])


        # Time2 had that extra second, so clip it off and re-add for next time
        time1 = time2 + 86400 - 1 
        time2 = min([time1+max_range_sec,time_end]) + 1

    # need to aggregate gdd for entire data set
    agdd_correct = 0
    for date in sorted(data.keys()):
        agdd_correct += data[date]['gdd']
        data[date]['agdd'] = agdd_correct

    return data


def get_leaf_canopy_wetness(lat,lon,start_date,end_date):
    ''' 
        Query Leaf Canopy Wetness endpoint
        Arguments:
            lat - latitude
            lon - longitude
            start_date - start date, expected form YYYY-MM-DDTHH:MM
            end_date - end date, expected form YYYY-MM-DDTHH:MM
    '''
    global units_def
    global url_base
    global app_id
    global app_key 

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
  
    max_range_sec = 240 * 3600 
    # Gets daily historical location for 1 lat/lon and time range
    data = None
    url_t = "{}/v1.1/canopywetness/hourly?app_id={}&app_key={}&location=$lat,$lon&start=$time_beg&end=$time_end".format(url_base, app_id, app_key)
        
    # Get start/stop epoch times from input date strings of YYYY-MM-DDTHH:MM format
    d_beg = datetime.strptime(start_date,'%Y-%m-%dT%H:%M')
    d_end = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')

    # compute epochs
    time_beg = int(d_beg.strftime("%s"))
    time_end = int(d_end.strftime("%s"))

    time1 = time_beg
    time2 = min([time_end,time1+max_range_sec])
 
    while time1 < time_end:
        url = Template(url_t)
        url2get = url.substitute(lat=lat,lon=lon,time_beg=time1,time_end=time2)
        print url2get
        response = urllib.urlopen(url2get, context=ctx)

        if response is not None:
            if data == None:

                # We are restricting to one location per call of this routine,
                # so let's strip off the outer element of the JSON ("lat,lon" key)
                # and let the calling application be responsible for knowing that.

                data = (json.loads(response.read())).values()[0]
            else:
                data.update( (json.loads(response.read())).values()[0])

        time1 = time2 + 3600
        time2 = min([time1+max_range_sec,time_end])

    return data    


def get_hourly_spray_conditions(lat,lon,start_date,end_date):
    ''' 
        Query Hourly Spray Conditions
        Arguments:
            lat - latitude
            lon - longitude
            start_date - start date, expected form YYYY-MM-DDTHH:MM
            end_date - end date, expected form YYYY-MM-DDTHH:MM
    '''
    global units_def
    global url_base
    global app_id
    global app_key 

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
  
    max_range_sec = 240 * 3600 
    # Gets daily historical location for 1 lat/lon and time range
    data = None
    url_t = "{}/v1.0/hourly/spray_conditions?app_id={}&app_key={}&location=$lat,$lon&start=$time_beg&end=$time_end".format(url_base, app_id, app_key)
        
    # Get start/stop epoch times from input date strings of YYYY-MM-DDTHH:MM format
    d_beg = datetime.strptime(start_date,'%Y-%m-%dT%H:%M')
    d_end = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')

    # compute epochs
    time_beg = int(d_beg.strftime("%s"))
    time_end = int(d_end.strftime("%s"))

    time1 = time_beg
    time2 = min([time_end,time1+max_range_sec])
 
    while time1 < time_end:
        url = Template(url_t)
        url2get = url.substitute(lat=lat,lon=lon,time_beg=time1,time_end=time2)
        print url2get
        response = urllib.urlopen(url2get, context=ctx)

        if response is not None:
            if data == None:

                # We are restricting to one location per call of this routine,
                # so let's strip off the outer element of the JSON ("lat,lon" key)
                # and let the calling application be responsible for knowing that.

                data = (json.loads(response.read())).values()[0]
            else:
                data.update( (json.loads(response.read())).values()[0])

        time1 = time2 + 3600
        time2 = min([time1+max_range_sec,time_end])

    return data    