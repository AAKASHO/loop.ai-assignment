# Store Active Time Calculation API

## Overview
This Flask-based API calculates the active time of stores based on provided data from three tables: `data`, `BusinessHours`, and `store_timezone`. The calculation takes into account the store's operational hours and timezone information.

## Setup
1. Clone the repository.
2. create a virtual environment to run youy flask project by running `python3 -m venv myenv` in loop.ai-assignment folder location in the terminal
3. Run the environment by running `.\myenv\Scripts\activate`
4. Install the required dependencies using `pip install -r requirements.txt`.
5. add the postgres url in following format `postgresql://postgres:[your-password]@localhost:[your-port-number]/[database-name-in-postgres]`
6. Configure the PostgreSQL database URI in `app.config['SQLALCHEMY_DATABASE_URI']` in `app.py`.
7. Create the required tables by running the Flask application (`python app.py`) once.

## Uploading Data
- To upload data for the `data` table, use the `/upload/data` endpoint with a CSV file containing timestamped store data.
- Similarly, use the `/upload/business_hours` and `/upload/store_timezone` endpoints to upload data for the `BusinessHours` and `store_timezone` tables, respectively.

## Triggering a Report
- Use the `/trigger_report` endpoint to start a new report calculation. This endpoint returns a unique report ID.
- The report runs asynchronously, and its progress can be checked using the `/get_report` endpoint with the provided report ID.

## Endpoints
- `/data`: Retrieves data from the `data` table.
- `/business_hours`: Retrieves data from the `BusinessHours` table.
- `/store_timezone`: Retrieves data from the `store_timezone` table.

## Note
- The API uses Pytz for timezone handling and SQLAlchemy for database management.
- Ensure that the CSV files uploaded match the expected format for each table.

## logic for interpolation of the data
- to get the data for last hour of current_time here function will take the current time of your choice but it can be changed and assumming there is no data after the time of current-time we will get the observation which have closest time from the current-time assuming the data has taken the observation roughly every hour for a store "

# for example
- current time is 04/05/2024 2:32 pm with the pattern of observation taken there are atmost 2 observation in the span of last 2 hour 
lets say closest time a observation is take is 2:10 observation before that closest to it can be lets say 1:30 pm


## Contributors
- akash kumar

