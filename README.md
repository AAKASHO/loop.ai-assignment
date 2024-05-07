# Store Active Time Calculation API

## Overview
This Flask-based API efficiently calculates the active time of stores based on provided data from three tables: `data`, `BusinessHours`, and `store_timezone`. The calculation considers the store's operational hours and timezone information.

## Setup
1. **Clone the repository.**
2. **Create a virtual environment:**
   ```bash
   python3 -m venv myenv
   ```
3. **Activate the virtual environment:**
   ```bash
   .\myenv\Scripts\activate
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Set up the PostgreSQL database URL:**
   - Replace `[your-password]`, `[your-port-number]`, and `[database-name-in-postgres]` with appropriate values.
6. **Configure the database URI in `app.py`:**
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:[your-password]@localhost:[your-port-number]/[database-name-in-postgres]'
   ```
7. **Create tables:**
   ```bash
   python app.py
   ```

## Uploading Data
- To upload data for the `data` table, use the `/upload/data` endpoint with a CSV file containing timestamped store data.
- Similarly, use the `/upload/business_hours` and `/upload/store_timezone` endpoints to upload data for the `BusinessHours` and `store_timezone` tables, respectively.

## Triggering a Report
- Initiate a new report calculation by using the `/trigger_report` endpoint, which returns a unique report ID.
- The report runs asynchronously, and its progress can be tracked using the `/get_report` endpoint with the provided report ID.

## Endpoints
- `/data`: Retrieves data from the `data` table.
- `/business_hours`: Retrieves data from the `BusinessHours` table.
- `/store_timezone`: Retrieves data from the `store_timezone` table.

## Note
- Pytz is used for timezone handling, and SQLAlchemy manages the database.
- Ensure that the CSV files uploaded match the expected format for each table.

## logic for interpolation of the data
- to get the data for last hour of current_time here function will take the current time of your choice but it can be changed and assumming there is no data after the time of current-time we will get the observation which have closest time from the current-time assuming the data has taken the observation roughly every hour for a store we will take the data taken in betweeen 2 hours of the current time"

# for example
- current time is 04/05/2024 2:32 pm the the observation taken after 12:32 and 2:32 ae taken into account the get the closest minute of every minute , as some minutes can be closer to the observation taken before 1 hours this is assuming ecery store is observed roughly every hour..., and if the at the observation closest to the given minute given store was active then we will assume store is active at the minute

example
`lets say for a minute at 1:40 pm ` closest observation taken is `1:00 pm` and store is marked active at the time then we will add 1 to the uptime in last hour


for downtime we will take the minimum if min(60,current time - start time) as if store is open for more the 1 hour only take 1 hour else taking the `current time - start time` as total time 

<!-- Calculation of downtime is of timecomplexity O(n)  -->

`total down time hour = total time - total uptime`

similarily we have taken the total uptime for last day 

we have saparated the observation taken for the store in the last day and for every given hour from its start_time on that day to end_time on that day if at the closest observation of the given hour, store is active then we assume store is active at the given hour

to improve time complexity after saperating the data for the day we are doing the binary search to find the closest hour

## for example 

lets say store is active on a given day from `9:00 AM to 8:00 PM` for any hour lets us take `1:00 pm` at the closest observation taken lets us say `1:40 PM` value is `active` then store is marked active on that hour

for downtime last day we have taken total work time of the store on that day - total active time on that day

now for uptime last week

we will find the uptime of the given store every day on last week using above method of finding total uptime last day 

total downtime is taken accordingily

## Time Complexity
The overall time complexity of the API is O(n log n), where n is the size of the data:
- Storing data in a map for quick access: O(n log n).
- Calculating uptime in the last hour: O(60 log a + n), where a is the number of observations in the last 2 hours for a store.
- Calculating uptime in the last day: O(24 log a + n), where a is the number of observations in the last day.
- Calculating uptime in the last week: O(7 * (24 log a + n)).

## Contributors
- Akash Kumar
