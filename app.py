# for this assignment i have choosen flaskto make apis and postgres to database management
#  we basically have 3 tables lets saye data, BusinessHours, storetimezone and we have to  get the
# store active time based on these table 

# now handle the timezone what we have done is at the time of calculation of active hours we will add the timesone
# of the given store to the db table BusinessHours so that it is easier to get in future calculations

# now we will use pytz to get the timezone and convert the given time to utc 

# we will convert start_time and end_time for calculation of total active hours using above method

    



from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, Integer, String, DateTime, Float,update
from sqlalchemy.ext.declarative import declarative_base

from flask import current_app


import threading

from io import StringIO
from uuid import uuid4 

import pytz

from collections import defaultdict

from datetime import datetime, timedelta,timezone,time
import csv

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/flasktest2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define models for data sources
class Data(db.Model):
    __tablename__ = 'data'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(String)
    timestamp_utc = db.Column(DateTime)
    status = db.Column(String)

class BusinessHours(db.Model):
    __tablename__ = 'business_hours'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(String)
    day = db.Column(Integer)
    start_time_local = db.Column(DateTime)
    end_time_local = db.Column(DateTime)
    timezone_str = db.Column(String,default="America/chicago")

class StoreTimezone(db.Model):
    __tablename__ = 'store_timezone'

    store_id = db.Column(String,primary_key=True)
    timezone_str = db.Column(String)



class Solution(db.Model):
    __tablename__ = 'solution'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    report_id=db.Column(String,primary_key=True)
    store_id = db.Column(String)
    uptime_last_hour=db.Column(Float,default=0.0)
    uptime_last_day=db.Column(Float,default=0.0)
    uptime_last_week=db.Column(Float,default=0.0)
    downtime_last_hour=db.Column(Float,default=0.0)
    downtime_last_day=db.Column(Float,default=0.0)
    downtime_last_week=db.Column(Float,default=0.0)
    timezone_str = db.Column(String)


# Create tables for all models
def create_tables():
    with app.app_context():
        db.create_all()

create_tables()

# Function to insert data into database
def insert_data(data, model):
    try:
        db.session.add(model(**data))
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # Handle integrity error, e.g., duplicate entry
        pass

# let me skip the video for when process is complete

# from datetime import datetime, timedelta, timezone

def find_closest_hour(observation_times, target):
    if not observation_times:
        return None
    
    # Initialize pointers
    left, right = 0, len(observation_times) - 1
    
    while left < right:
        mid = (left + right) // 2
        
        if observation_times[mid]['timestamp_utc'] < target:
            left = mid + 1
        else:
            right = mid
    
    # At this point, left and right will converge to the closest element
    closest = observation_times[left]

    # print(closest)
    
    # Check the adjacent elements if they exist and are closer
    if left > 0 and abs(observation_times[left - 1]['timestamp_utc'] - target) < abs(closest['timestamp_utc'] - target):
        closest = observation_times[left - 1]
    
    return closest


def calculate_uptime_hour(data):
    current_time = datetime(2023, 1, 24, 9, 30, 0, tzinfo=timezone.utc)  # Get current time in UTC timezone
    uptime_last_hour = 0
    
    observation_times=[]
    for row in data:
        timestamp_utc, status = row['timestamp_utc'], row['status']
        if timestamp_utc is not None: 

            if timestamp_utc.tzinfo is None or timestamp_utc.tzinfo.utcoffset(timestamp_utc) is None:
                timestamp_utc = timestamp_utc.replace(tzinfo=timezone.utc)
            # Calculate time difference
            time_difference = current_time - timestamp_utc
            # print((time_difference))

            # print("current_time-",(current_time))
            # print("timestamp-",(timestamp_utc))
            if time_difference <= timedelta(hours=2) and time_difference>=timedelta(hours=0):
                # print(abs(time_difference))

                observation_times.append({
                    'timestamp_utc': timestamp_utc,
                    'status': row['status']
                })
                # if last_hour1_val:
                #     last_hour2_val = timestamp_utc
                #     last_hour2 = 1 if status == "active" else 0
                # else:
                #     last_hour1_val = timestamp_utc
                #     last_hour1 = 1 if status == "active" else 0

        
    # return current_time

    observation_times.sort(key=lambda x: x['timestamp_utc'])
    temp = current_time - timedelta(hours=1)
    # print(last_hour1_val)
    while temp<current_time:
        # Determine which timestamp the current minute is closer to
        # print(current_time)
        closest_time = find_closest_hour(observation_times, current_time)
        if closest_time is not None and closest_time['status'] == 'active':
            uptime_last_hour+=1

        temp += timedelta(minutes=1)
        # return uptime_last_hour
    return uptime_last_hour
        # Add uptime based on the status
        
        # Move to the next minute



def get_timezone(timezone_str):
    try:
        return pytz.timezone(timezone_str)
    except pytz.UnknownTimeZoneError:
        return None





def calculate_uptime_day(data, start_time, end_time, date):
    observation_times = []

    # Convert start and end times to UTC timezone if they are naive
    if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None or end_time.tzinfo.utcoffset(end_time) is None:
        end_time = end_time.replace(tzinfo=timezone.utc)
    if not isinstance(start_time, datetime):
        start_time = datetime.combine(date, start_time)
    if not isinstance(end_time, datetime):
        end_time = datetime.combine(date, end_time)

    # Filter data based on the provided date
    for entry in data:
        timestamp_utc = entry['timestamp_utc']
        if timestamp_utc.tzinfo is None or timestamp_utc.tzinfo.utcoffset(timestamp_utc) is None:
            timestamp_utc = timestamp_utc.replace(tzinfo=timezone.utc)
        
        if timestamp_utc.date() == date:
            observation_times.append({
                'timestamp_utc': timestamp_utc,
                'status': entry['status']
            })

    # Sort observation times by timestamp
    observation_times.sort(key=lambda x: x['timestamp_utc'])


    current_time = start_time
    uptime_day_hours = 0

    # Iterate through each hour in the specified time range
    while current_time <= end_time:
        closest_time = find_closest_hour(observation_times, current_time)
        if closest_time is not None and closest_time['status'] == 'active':
            uptime_day_hours += 1
        current_time += timedelta(hours=1)

    return uptime_day_hours


report_id_status={}



# let me skipp the video for when process for when process is complete






# Route to upload CSV file for data source 1
@app.route('/upload/data', methods=['POST'])
def upload_data_csv():
    csv_file = request.files.get('file')
    if not csv_file:
        return jsonify({'error': 'No file provided'}), 400

    # Save the CSV file temporarily
    csv_file.save('data.csv')

    data_to_insert = []

    with open('data.csv', 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Adjust timestamp format string to match the format in the CSV file
            try:
                row['timestamp_utc'] = datetime.strptime(row['timestamp_utc'], '%Y-%m-%d %H:%M:%S %Z')
            except ValueError:
                try:
                    row['timestamp_utc'] = datetime.strptime(row['timestamp_utc'], '%Y-%m-%d %H:%M:%S.%f %Z')
                except ValueError:
                    pass

            # Add 'status' field based on your condition

            data_to_insert.append(row)

    # Perform bulk insert
    with app.app_context():
        db.session.bulk_insert_mappings(Data, data_to_insert)
        db.session.commit()

    return jsonify({'message': 'Data CSV uploaded successfully'}), 200
# Route to upload CSV file for data source 2
@app.route('/upload/business_hours', methods=['POST'])
def upload_business_hours_csv():
    csv_file = request.files.get('file')
    if not csv_file:
        return jsonify({'error': 'No file provided'}), 400

    csv_file.save('business_hours.csv')

    data_to_insert = []

    with open('business_hours.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Adjust timestamp format string to match the format in the CSV file
            row['start_time_local'] = datetime.strptime(row['start_time_local'], '%H:%M:%S')
            row['end_time_local'] = datetime.strptime(row['end_time_local'], '%H:%M:%S')
            data_to_insert.append(row)
            # insert_data(row, BusinessHours)
    with app.app_context():
        db.session.bulk_insert_mappings(BusinessHours, data_to_insert)
        db.session.commit()

    return jsonify({'message': 'Business Hours CSV uploaded successfully'}), 200

# Route to upload CSV file for data source 3
@app.route('/upload/store_timezone', methods=['POST'])
def upload_store_timezone_csv():
    csv_file = request.files.get('file')
    if not csv_file:
        return jsonify({'error': 'No file provided'}), 400

    csv_file.save('store_timezone.csv')

    with open('store_timezone.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            insert_data(row, StoreTimezone)

    return jsonify({'message': 'Store Timezone CSV uploaded successfully'}), 200




final_answer=[]

# @app.route('/calculate', methods=['GET'])
def calculate(report_id):
    # data = Data.query.all()

    current_time=datetime(2023, 1, 24, 7, 30, 0, tzinfo=timezone.utc)

    data = Data.query.filter(Data.timestamp_utc >= current_time - timedelta(weeks=1)).all()
    grouped_data = defaultdict(list)
    for row in data:
        grouped_data[row.store_id].append({
            'timestamp_utc': row.timestamp_utc,
            'status': row.status
        })


    update_stmt = (
        update(BusinessHours)
        .where(BusinessHours.store_id == StoreTimezone.store_id)
        .values(timezone_str=StoreTimezone.timezone_str)
    )

    # Execute the update statement
    db.session.execute(update_stmt)
    db.session.commit()

    day_of_week=current_time.weekday()


    
    for store_id, store_data in grouped_data.items():
        # print(store_id)
        len(store_data)
        uptime_hour = calculate_uptime_hour(store_data)
        
        # Default values for start_time_local and end_time_local
        start_time_local = datetime.combine(datetime.now().date(), time(0, 0))  # Start time assumed to be midnight
        end_time_local = datetime.combine(datetime.now().date(), time(23, 59, 59))  # End time assumed to be 11:59:59 PM
        
        # Query BusinessHours for the specific store and day of the week
        business_hours = BusinessHours.query.filter_by(store_id=store_id, day=current_time.weekday()).all()
        
        if business_hours:
            # Extract start and end times from the first record
            start_time_local = business_hours[0].start_time_local.time()
            end_time_local = business_hours[0].end_time_local.time()
            if not isinstance(start_time_local, datetime):
                start_time_local = datetime.combine(datetime.now().date(), start_time_local)
            if not isinstance(end_time_local, datetime):
                end_time_local = datetime.combine(datetime.now().date(), end_time_local)
            timezone_local = get_timezone(business_hours[0].timezone_str)
            if(timezone_local):
                start_time_local=timezone_local.localize(start_time_local).astimezone(pytz.utc)
                end_time_local=timezone_local.localize(end_time_local).astimezone(pytz.utc)

        uptime_day = calculate_uptime_day(store_data, start_time_local, end_time_local, current_time.date())
        
        uptime_week = 0
        total_uptime_week=0
        start_time = current_time - timedelta(days=7)
        while start_time <= current_time:
            day_of_week_date = start_time.weekday()
            business_hours_week = BusinessHours.query.filter_by(store_id=store_id, day=day_of_week_date).all()
            
            # Default values for start_time_local_week and end_time_local_week
            start_time_local_week = datetime.combine(datetime.now().date(), time(0, 0))  # Start time assumed to be midnight
            end_time_local_week = datetime.combine(datetime.now().date(), time(23, 59, 59))  # End time assumed to be 11:59:59 PM


            if business_hours_week:
                # Extract start and end times from the first record
                start_time_local_week = business_hours_week[0].start_time_local.time()
                end_time_local_week = business_hours_week[0].end_time_local.time()
                if not isinstance(start_time_local_week, datetime):

                    start_time_local_week = datetime.combine(datetime.now().date(), start_time_local_week)
                if not isinstance(end_time_local_week, datetime):
                    end_time_local_week = datetime.combine(datetime.now().date(), end_time_local_week)
                timezone_week = get_timezone(business_hours_week[0].timezone_str)
                if(timezone_week):
                    start_time_local_week=timezone_week.localize(start_time_local_week).astimezone(pytz.utc)
                    end_time_local_week=timezone_week.localize(end_time_local_week).astimezone(pytz.utc)
            total_uptime_week+=(end_time_local_week-start_time_local_week).total_seconds()/3600
            
            uptime_week += calculate_uptime_day(store_data, start_time_local_week, end_time_local_week, start_time.date())
            start_time += timedelta(days=1)
        start_time_local = start_time_local.replace(tzinfo=timezone.utc)
        end_time_local = end_time_local.replace(tzinfo=timezone.utc)
        
        row = {
            "report_id":report_id,
            'store_id': store_id,
            'uptime_last_hour': float(uptime_hour * 60 / 60),
            # 'uptime_last_hour': float(10000 * 60 / 60),
            'uptime_last_day': float(uptime_day * 60 / 60),
            # 'uptime_last_day': float(10000 * 60 / 60),
            'uptime_last_week': float(uptime_week * 60 / 60),
            # 'update_last_week': float(10000 * 60 / 60),
            'downtime_last_hour': min(60,(current_time-start_time_local).total_seconds()/60)-float(uptime_hour * 60 / 60),
            'downtime_last_day': (end_time_local-start_time_local).total_seconds()/3600-float(uptime_day * 60 / 60),
            'downtime_last_week': total_uptime_week-float(uptime_week * 60 / 60),
            'timezone_str': 'UTC'
        }
        final_answer.append(row)

        print(len(final_answer))
    #     insert_data(row, Solution)
    with app.app_context():
        db.session.bulk_insert_mappings(Solution, final_answer)
        db.session.commit()


    print("completed")
    report_id_status[report_id]={"status":"Completed"}

    return jsonify({'message': 'Calculated successfully'}), 200



def calculate_with_context(report_id):
    with app.app_context():
        calculate(report_id)

@app.route('/trigger_report', methods=['GET'])
def trigger_report():
    report_id = str(uuid4())
    report_id_status[report_id] = {"status": "Running"}

    # Start a new thread to execute calculate function within the application context
    threading.Thread(target=calculate_with_context, args=(report_id,)).start()

    return jsonify({"report_id": report_id})


# let me skip the video for when process completes






@app.route("/get_report", methods=["GET"])
def get_report():
    report_id = request.args.get("report_id")
    if report_id not in report_id_status:
        return jsonify({"error": "Invalid report ID"}), 400

    report_status = report_id_status[report_id]["status"]
    print(report_status)
    if report_status == "Running":
        return jsonify({"status": "Running"})
    elif report_status == "Completed":
        try:
            solution_list = Solution.query.filter_by(report_id=report_id).all()

            # Check if there are any solutions
            if not solution_list:
                return jsonify({"error": "No solutions found for the report"}), 404

            # Get field names from the first solution
            fieldnames = ["store_id", "uptime_last_hour", "uptime_last_day", "uptime_last_week",
                          "downtime_last_hour", "downtime_last_day", "downtime_last_week", "timezone_str"]

            csv_output = StringIO()
            writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
            writer.writeheader()
            for solution in solution_list:
                writer.writerow({fieldname: getattr(solution, fieldname) for fieldname in fieldnames})

            # Set content type and return CSV data
            response = csv_output.getvalue()

            return response, 200, {'Content-Type': 'text/csv'}
        except Exception as e:
            # Handle potential errors
            return jsonify({"error": str(e)}), 500
        
    else:
        # Handle unexpected report states
        return jsonify({"error": "Unknown report status"}), 500







# Route to get data from data source 1
@app.route('/data', methods=['GET'])
def get_data():
    data = Data.query.all()
    
    data_list = [{'id': d.id, 'timestamp_utc': d.timestamp_utc, 'status': d.status} for d in data]

    # Check for CSV preference based on Accept header
    if request.headers.get("Accept") == "text/csv":
        # Generate CSV data in memory
        print("yes")
        csv_output = StringIO()
        writer = csv.DictWriter(csv_output, fieldnames=data_list[0].keys())
        writer.writeheader()
        writer.writerows(data_list)

        # Set content type and return CSV data
        response = csv_output.getvalue()
        csv_output.close()  # Close the in-memory stream
        return response, 200, {'Content-Type': 'text/csv'}

    return jsonify(data_list), 200

# Route to get data from data source 2
@app.route('/business_hours', methods=['GET'])
def get_business_hours():
    business_hours = BusinessHours.query.all()
    business_hours_list = [{'id': bh.id, 'day': bh.day, 'start_time_local': bh.start_time_local, 'end_time_local': bh.end_time_local} for bh in business_hours]
    return jsonify(business_hours_list), 200

# Route to get data from data source 3
@app.route('/store_timezone', methods=['GET'])
def get_store_timezone():
    store_timezone = StoreTimezone.query.all()
    store_timezone_list = [{'id': stz.id, 'timezone_str': stz.timezone_str} for stz in store_timezone]
    return jsonify(store_timezone_list), 200


if __name__ == '__main__':
    app.run(debug=True)
