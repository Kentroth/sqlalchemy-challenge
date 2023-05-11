# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement=Base.classes.measurement
station=Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Last 12 Months of Precipitation Data"""
    # Query precipitation data for the last 12 months
    recent_date = dt.date(2017, 8, 23)
    year_ago = recent_date - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= year_ago).all()

    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Station List"""
    # Query the list of stations
    stations = session.query(station.station).\
        all()

    session.close()

    # Extract the station names from the query results and convert them to a list
    station_names = [name[0] for name in stations]

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Temperature Observations"""
    # Query the most active station
    active_station_id = session.query(measurement.station, 
        func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).\
        first()[0]

    # Query the temperature observations for the most active station
    active_station_data = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == active_station_id).\
        filter(measurement.date >= '2016-08-23').\
        all()

    # Create a dictionary of date and temperature observations
    tobs_data = {date: tobs for date, tobs in active_station_data}

    session.close()

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Temperature Statistics from Start Date"""
    # Query temperature statistics for dates greater than or equal to the start date
    temperature_stats = session.query(func.min(measurement.tobs), 
        func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        all()

    session.close()

    # Create a dictionary to store the temperature statistics
    stats_dict = {
        "temp_min": temperature_stats[0][0],
        "temp_ave": temperature_stats[0][1],
        "temp_max": temperature_stats[0][2]
    }

    return jsonify(stats_dict)


@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Temperature Statistics for Date Range"""
    # Query temperature statistics for the date range
    temperature_stats = session.query(func.min(measurement.tobs), 
        func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).\
        all()

    session.close()

    # Create a dictionary to store the temperature statistics
    stats_dict = {
        "temp_min": temperature_stats[0][0],
        "temp_ave": temperature_stats[0][1],
        "temp_max": temperature_stats[0][2]
    }

    return jsonify(stats_dict)

if __name__ == '__main__':
    app.run(debug=True)
