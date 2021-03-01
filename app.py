from flask import Flask
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
#################################################



app = Flask(__name__)



########################################## Routes ##########################################


# Home Page: List all routes that are available
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
    f"Welcome to my 'Home' page! <br/>"
    f"Available Routes: <br/>"
    f"/api/v1.0/precipitation <br/>"
    f"/api/v1.0/stations <br/>"
    f"/api/v1.0/tobs <br/>"
    f"/api/v1.0/<start><br/>"
    f"/api/v1.0/<start>/<end> <br/>"
    )





# Precipitation: Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    measurement = Base.classes.measurement
    session = Session(engine)

    """Return a list of all precipitation based on my previous query"""
    year_old = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_old_data = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= year_old).all()
    session.close()

    precipitation_by_date = []
    for date, prcp in year_old_data:
        date_dict = {}
        date_dict[date] = prcp
        precipitation_by_date.append(date_dict)
    
    # Return the JSON representation
    return jsonify(precipitation_by_date)





# Station: Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to the DB
    station = Base.classes.station
    session = Session(engine)
    
    # List all data from Station table
    station_results = session.query(station.id, station.station, station.name, station.latitude, station.longitude, station.elevation).all()
    session.close()

    # Create a dictionary
    station_list = []
    for id, station, name, latitude, longtitude, elevation in station_results:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longtitude"] = longtitude
        station_dict["elevation"] = elevation
        station_list.append(station_dict)
    
    # Return the JSON representation
    return jsonify(station_list)





# Tobs: Query the dates and temperature observations of the most active station for the last year of data
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    measurement = Base.classes.measurement
    session = Session(engine)

    # Query for USC00519523 - the most active station (last year data)
    year_old = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    USC00519523 = session.query(measurement.date, measurement.tobs).\
    filter(measurement.station == 'USC00519523').\
    filter(measurement.date >= year_old).all()
    session.close()

    # Create a dictionary
    USC00519523_data = []
    for date, tobs in USC00519523:
        USC00519523_dict = {}
        USC00519523_dict[date] = tobs
        USC00519523_data.append(USC00519523_dict)
    
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(USC00519523_data)





# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
def v1(start, end=None):

    # Create our session (link) from Python to the DB
    measurement = Base.classes.measurement
    session = Session(engine)

    tobs_results = [measurement.date,
        func.min(measurement.tobs),
        func.avg(measurement.tobs),
        func.max(measurement.tobs)]
    if end is None:
        tobs_query1 = session.query(*tobs_results).\
        group_by(measurement.date).\
        filter(measurement.date >= start).all()
        
    else:
        tobs_query1 = session.query(*tobs_results).\
        group_by(measurement.date).\
        filter(start < measurement.date).\
        filter(end > measurement.date).all()

    session.close()
    
    # Create a dictionary
    tobs_data1 = []
    for date, tobs_results[1], tobs_results[2], tobs_results[3] in tobs_query1:
        tobs_dict1 = {}
        tobs_dict1["date"] = date
        tobs_dict1["min"] = tobs_query1[0][1]
        tobs_dict1["average"] = tobs_query1[0][2]
        tobs_dict1["max"] = tobs_query1[0][3]
        tobs_data1.append(tobs_dict1)

    # Return a JSON list
    return jsonify(tobs_data1)


if __name__ == "__main__":
    app.run(debug=True)