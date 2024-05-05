# Store Active Time Calculation API

## Overview
This Flask-based API calculates the active time of stores based on provided data from three tables: `data`, `BusinessHours`, and `store_timezone`. The calculation takes into account the store's operational hours and timezone information.

## Setup
1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Configure the PostgreSQL database URI in `app.config['SQLALCHEMY_DATABASE_URI']` in `app.py`.
4. Create the required tables by running the Flask application (`app.py`) once.

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

## Contributors
- [Your Name]

