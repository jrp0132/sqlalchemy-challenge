# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Homepage route
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Most recent date in the dataset
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    
    # Date one year ago from the most recent date
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query precipitation data for the last 12 months
    precipitation_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()
    
    # Query results to dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    # Return JSON representation of the dictionary
    return jsonify(precipitation_dict)

# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    stations_data = session.query(station.station).all()
    
    # Convert to list
    stations_list = list(np.ravel(stations_data))
    
    # Return the JSON of stations
    return jsonify(stations_list)

# Temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    # Most recent date in the dataset
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Most active station
    most_active_station = session.query(measurement.station, func.count(measurement.station)) \
        .group_by(measurement.station) \
        .order_by(func.count(measurement.station).desc()) \
        .first()[0]

    # Query temperature observations of most active station for last 12 months
    tobs_data = session.query(measurement.tobs).filter(
        measurement.station == most_active_station,
        measurement.date >= one_year_ago).all()

    # Convert the list of tuples into a list
    tobs_list = list(np.ravel(tobs_data))

    # Return the JSON list of temperature observations
    return jsonify(tobs_list)

# Define the start date route
@app.route("/api/v1.0/<start>")
def start(start):
    # Query temperature stats 
    temperature_stats = session.query(
        func.min(measurement.tobs),
        func.avg(measurement.tobs),
        func.max(measurement.tobs)
    ).filter(measurement.date >= start).all()

    # Convert results to a dictionary
    temp_dict = {
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]}

    # Return the JSON representation
    return jsonify(temp_dict)

# Define the start-end date route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Query temperature stats 
    temperature_stats = session.query(
        func.min(measurement.tobs),
        func.avg(measurement.tobs),
        func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()

    # Convert results to a dictionary
    temp_dict = {
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]}

    # Return JSON representation
    return jsonify(temp_dict)

# Run 
if __name__ == '__main__':
    app.run(debug=True)