# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List of all available api routes"""
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    """Return list of precipitation information"""
    date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).where(Measurement.date >= date).all()
    session.close()

    #create dictionary for results
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['pcrp'] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    """Return list of stations"""
    results = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    station_num = 'USC00519281'
    date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    """Return Dates and temperature observations of most active station"""

    results = temperature = session.query(Measurement.date, Measurement.tobs).where(Measurement.date >= date, Measurement.station == station_num).all()

    session.close()

    all_tobs = list(np.ravel(results))

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start_date(start):
    date = dt.datetime.strptime(start, "%m-%d-%Y")

    results = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).where(Measurement.date >= date).all()

    session.close()

    measure_temps = list(np.ravel(results))

    return jsonify(measure_temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    start_date = dt.datetime.strptime(start, "%m-%d-%Y")
    end_date = dt.datetime.strptime(end, "%m-%d-%Y")

    results = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).where(Measurement.date >= start_date, Measurement.date <=end_date).all()

    measure_temps = list(np.ravel(results))

    return jsonify(measure_temps)

if __name__ == '__main__':
    app.run(debug=True)