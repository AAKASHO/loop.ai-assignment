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

## Data Interpolation Logic
The API employs a sophisticated interpolation logic to accurately calculate store activity:
- For the last hour, the algorithm considers the observation closest to the current time within the past two hours. If the store was active at that time, one hour is added to the uptime.
- To calculate downtime, the minimum of either 60 minutes or the difference between the current time and the store's opening time is taken.
- For the last day, the data is segmented into hourly intervals. The closest observation within each hour is considered, and if the store was active, it's marked as such for that hour.
- To optimize performance, binary search is used to find the closest observation within each hour.
- Similar processes are applied to calculate uptime for the last week.

## Time Complexity
The overall time complexity of the API is O(n log n), where n is the size of the data:
- Storing data in a map for quick access: O(n log n).
- Calculating uptime in the last hour: O(60 log a + n), where a is the number of observations in the last 2 hours for a store.
- Calculating uptime in the last day: O(24 log a + n), where a is the number of observations in the last day.
- Calculating uptime in the last week: O(7 * (24 log a + n)).

## Contributors
- Akash Kumar
