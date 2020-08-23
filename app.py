#################################################
# import flask, SQL alchemy and other libraries
#################################################
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Create our session (link) from Python to the DB
#################################################
session = Session(engine)

#################################################
# Flask Routes
#################################################

# Home page
# List all routes that are available
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():

    print("Server received request for precipitation page...")

    max_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    latest_date = dt.datetime.strptime(max_date[0][0],'%Y-%m-%d')
    prev_yr_date = dt.date((latest_date.year - 1), latest_date.month, latest_date.day)

    prcp_data = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date <= latest_date).filter(Measurement.date >= prev_yr_date).all()
    
    prcp_dict = {}
    for data in prcp_data:
        prcp_dict[data[0]] = data[1]

    return jsonify(prcp_dict)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():

    print("Server received request for stations page...")

    stations_data = session.query(Station).all()
    
    stations_list = []
    for station in stations_data:
        stations_dict = {}
        stations_dict["id"] = station.id
        stations_dict["station"] = station.station
        stations_dict["name"] = station.name
        stations_list.append(stations_dict)
    
    return jsonify(stations_list)   


# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():

    print("Server received request for temperature page...")

    max_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    latest_date = dt.datetime.strptime(max_date[0][0],'%Y-%m-%d')
    prev_yr_date = dt.date((latest_date.year - 1), latest_date.month, latest_date.day)

    most_active_station_data = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    most_active_station = most_active_station_data[0]
    temp_data = session.query(Measurement.station,Measurement.date,Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date <= latest_date).filter(Measurement.date >= prev_yr_date).all()

    temp_list = []
    for temp in temp_data:
        temp_dict = {}
        temp_dict["date"] = temp.date
        temp_dict["tobs"] = temp.tobs
        temp_dict["station"] = temp.station
        temp_list.append(temp_dict)

    return jsonify(temp_list)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<startdt>")
def start(startdt):

    print("Server received request for start and end dates route...")
    print(startdt)

    start_date = dt.datetime.strptime(startdt,'%Y-%m-%d')

    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_data =  (session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).group_by(Measurement.date).all())

    start_data_list = []                       
    for data in start_data:
        start_data_dict = {}
        start_data_dict["Date"] = data[0]
        start_data_dict["Minimum Temp"] = data[1]
        start_data_dict["Average Temp"] = data[2]
        start_data_dict["Maximum Temp"] = data[3]
        start_data_list.append(start_data_dict)

    return jsonify(start_data_list)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<startdt>/<enddt>")
def startend(startdt,enddt):

    print("Server received request for start and end dates route...")
    print(startdt)
    print(enddt)

    start_date = dt.datetime.strptime(startdt,'%Y-%m-%d')
    end_date = dt.datetime.strptime(enddt,'%Y-%m-%d')

    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    startend_data =  (session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).filter(func.strftime("%Y-%m-%d", Measurement.date) <= end_date).group_by(Measurement.date).all())

    startend_data_list = []                       
    for data in startend_data:
        startend_data_dict = {}
        startend_data_dict["Date"] = data[0]
        startend_data_dict["Minimum Temp"] = data[1]
        startend_data_dict["Average Temp"] = data[2]
        startend_data_dict["Maximum Temp"] = data[3]
        startend_data_list.append(startend_data_dict)

    return jsonify(startend_data_list)



if __name__ == "__main__":
    app.run(debug=True)
