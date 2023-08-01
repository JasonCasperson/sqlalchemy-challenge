# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect


app = Flask(__name__)
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

Base = automap_base()
Base.prepare(autoload_with=engine)

hawaii_measurement = Base.classes.measurement
hawaii_stations = Base.classes.station

session = Session(engine)

recent_date =  session.query(hawaii_measurement.date)\
                                .order_by(hawaii_measurement.date.desc())\
                                .first().date
twelve_months = dt.datetime.strptime(recent_date,'%Y-%m-%d') - dt.timedelta(days=365)

@app.route("/")
def welcome ():
    return(
        f"<p>Welcome to the Hawaii weather API!</p>"
        f"<p>Available Routes Include:</p>"
        f"/api/v1.0/precipitation  - Returns a list of percipitation data for the last year of data in JSON format"
        f"/api/v1.0/stations  - Returns a list of the weather stations in JSON format"
        f"/api/v1.0/tobs  - Returns temperate data for the most active weather station for the past year in JSON format"
        f"/api/v1.0/date  - Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the given start date and 8/23/17<br/><br/>."
        f"/api/v1.0/start_date/end_date  - Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the given start date and end date<br/><br/>."

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    twelve_months_data = session.query(hawaii_measurement.date,func.avg(hawaii_measurement.prcp))\
        .filter(hawaii_measurement.date >= twelve_months)\
            .group_by(hawaii_measurement.date).all()
    twelve_months_data = [tuple(row) for row in twelve_months_data]
    return jsonify(twelve_months_data)

@app.route("/api/v1.0/stations")
def stations():
    
    station_data = session.query(hawaii_stations.id,hawaii_stations.name).all()
    station_data = [tuple(row) for row in station_data]
    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    station_name = session.query(hawaii_stations.name)\
                                .filter(hawaii_stations.station == hawaii_measurement.station)\
                                .group_by(hawaii_measurement.station)\
                                .order_by(func.count(hawaii_measurement.station)\
                                .desc()).first().name
    active_station_twelve_months = session.query(hawaii_stations.name,hawaii_stations.station,hawaii_measurement.prcp,hawaii_measurement.tobs).filter(hawaii_stations.station == hawaii_measurement.station,hawaii_stations.name==station_name,hawaii_measurement.date > twelve_months).all()
    active_station_twelve_months = [tuple(row) for row in active_station_twelve_months]
    return jsonify(active_station_twelve_months)

@app.route("/api/v1.0/<date>")
def date(date):
    formatteddate = dt.datetime.strptime(date,'%m%d%Y')
    date_filter = session.query(func.min(hawaii_measurement.tobs),\
                                 func.avg(hawaii_measurement.tobs),\
                                func.max(hawaii_measurement.tobs))\
                                .filter(hawaii_measurement.date >= formatteddate)
    date_filter = [tuple(row) for row in date_filter]
    return jsonify(date_filter)

@app.route("/api/v1.0/<start_date>/<end_date>")
def startenddate(start_date,end_date):
    formattedstartdate = dt.datetime.strptime(start_date,'%m%d%Y')
    formattedenddate = dt.datetime.strptime(end_date,'%m%d%Y')
    date_filter = session.query(func.min(hawaii_measurement.tobs),\
                                func.avg(hawaii_measurement.tobs),\
                                func.max(hawaii_measurement.tobs))\
                                .filter(hawaii_measurement.date>= formattedstartdate and hawaii_measurement.date<= formattedenddate)

    date_filter = [tuple(row) for row in date_filter]
    return jsonify(date_filter)
if __name__ == '__main__':
    app.run(debug=True)