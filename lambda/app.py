import os
from datetime import datetime
from datetime import timedelta

import boto3
import pytz
import requests
from timezonefinder import TimezoneFinder


def convert_utc_to_local(utc_time_str, timezone_name):
    try:
        # Get the current date
        current_date = datetime.now().date()

        # Combine the current date with the provided UTC time
        combined_utc_str = f"{current_date} {utc_time_str}"

        # Define the UTC timezone
        utc_timezone = pytz.utc

        # Convert the combined string to a datetime object and localize to UTC
        utc_datetime = utc_timezone.localize(datetime.strptime(combined_utc_str, "%Y-%m-%d %H:%M"))

        # Get the local timezone object
        local_timezone = pytz.timezone(timezone_name)

        # Convert the UTC time to local time in the specified timezone
        local_time = utc_datetime.astimezone(local_timezone)

        # Format the local time to 'HH:MM'
        local_time_str = local_time.strftime('%H:%M')

        return local_time_str
    except pytz.UnknownTimeZoneError:
        return f"Unknown timezone: {timezone_name}"
    except ValueError:
        return "Incorrect time format. Please use 'HH:MM'."


def get_local_time(timezone_name):
    try:
        # Get the timezone object
        timezone = pytz.timezone(timezone_name)

        # Get the current time in the specified timezone
        local_time = datetime.now(timezone).strftime('%H:%M')

        return local_time
    except pytz.UnknownTimeZoneError:
        return f"Unknown timezone: {timezone_name}"


def get_utc_offset(timezone_name):
    try:
        # Create a timezone object
        tz = pytz.timezone(timezone_name)

        # Get the current time in the given timezone
        current_time = datetime.now(tz)

        # Get the offset for standard time
        standard_offset = tz.utcoffset(current_time.replace(tzinfo=None)).total_seconds() / 3600

        # Get the offset during daylight saving time
        dst_offset = tz.dst(current_time.replace(tzinfo=None)).total_seconds() / 3600 if tz.dst(
            current_time.replace(tzinfo=None)) else 0

        # Calculate the total offset during DST
        total_offset_during_dst = standard_offset + dst_offset

        return standard_offset, total_offset_during_dst

    except Exception as e:
        return str(e)


def is_dst(date, timezone):
    tz = pytz.timezone(timezone)
    aware_date = tz.localize(date, is_dst=None)
    return aware_date.dst() != timedelta(0)


def get_local_timezone_offset(date, timezone):
    standard_offset, dst_offset = get_utc_offset(timezone)

    if is_dst(date, timezone):
        return dst_offset  # CDT (Central Daylight Time)
    else:
        return standard_offset  # CST (Central Standard Time)


def get_timezone(latitude, longitude):
    # Create an instance of TimezoneFinder
    tf = TimezoneFinder()
    # Get the timezone name
    return tf.timezone_at(lat=float(latitude), lng=float(longitude))


def get_local_twilight_times(latitude, longitude):
    sunrise_utc = None
    sunset_utc = None
    date = datetime.now()  # Today's date
    timezone = get_timezone(latitude, longitude)
    url = (f"https://aa.usno.navy.mil/api/rstt/oneday?date={date.strftime('%Y-%m-%d')}&coords={latitude},{longitude}")
    print(url)
    response = requests.get(url)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    data = response.json()
    print(data)
    sundata = data['properties']['data']['sundata']
    for entry in sundata:
        if entry['phen'] == 'Rise':
            sunrise_utc = entry['time']
        elif entry['phen'] == 'Set':
            sunset_utc = entry['time']

    if not sunrise_utc or not sunset_utc:
        raise ValueError("Sunrise or sunset time not found in the response")

    print(f"Sunrise UTC: {sunrise_utc}, Sunset UTC: {sunset_utc}")

    local_timezone = pytz.timezone(timezone)

    today_local = datetime.now(local_timezone).date().isoformat()
    sunrise_local = convert_utc_to_local(sunrise_utc, timezone)
    sunset_local = convert_utc_to_local(sunset_utc, timezone)

    print(f"Today local: {today_local} Sunrise local: {sunrise_local}, Sunset local: {sunset_local}")

    return today_local, sunrise_local, sunset_local


def lambda_handler(event, context):
    """
    Main handler function for the AWS Lambda. Fetches sun times and stores them in a DynamoDB table.

    Parameters:
    - event (dict): The event data passed to the Lambda function.
    - context (object): The context in which the Lambda function is running.

    Returns:
    - dict: A dictionary containing the status code and body message.
    """
    latitude = os.environ['LATITUDE']
    longitude = os.environ['LONGITUDE']
    ddb_table_name = os.environ['DDB_TABLE_NAME']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(ddb_table_name)

    try:
        today, sunrise, sunset = get_local_twilight_times(latitude, longitude)

        # Put item in the DynamoDB table, replacing the existing item with the same 'primary_key'
        table.put_item(
            Item={
                'primary_key': 'twilight',  # Fixed primary key to ensure single entry
                'date': today,
                'sunrise': sunrise,
                'sunset': sunset
            }
        )

        return {
            'statusCode': 200,
            'body': 'Twilight times updated successfully.'
        }

    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Error fetching data from USNO API: {e}")
        return {
            'statusCode': 500,
            'body': 'Failed to update twilight times.'
        }


if __name__ == '__main__':
    lambda_handler(None, None)
