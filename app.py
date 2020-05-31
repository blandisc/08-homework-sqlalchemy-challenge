import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import datetime as dt
from dateutil.relativedelta import *
import pandas as pd

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement

station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f""
        f"Available Routes:<br/>"
        f""
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/2017-01-23<br/>"
        f"/api/v1.0/start,end/2015-01-23,2017-01-23<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    dates=[]
    for i in session.query(measurement).all():
        dates.append((i.__dict__['date']))


    prcp =[]
    for i in session.query(measurement).all():
        prcp.append((i.__dict__['prcp']))

    session.close()

    precipitation = {k: v for k, v in zip(dates, prcp)}

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    query_stations= session.query(measurement.station).distinct().all()
    query_stations

    session.close()
    

    return jsonify(query_stations)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    dates=[]
    for i in session.query(measurement).all():
        dates.append((i.__dict__['date']))

    active_stations=session.query(measurement.station,
        func.count(measurement.id).label('qty')
        ).group_by(measurement.station
        ).order_by(desc('qty')).all()

    first_date = (session.query(measurement.date)
              .order_by(measurement.date.desc()).first())

    query_date =first_date[0].split("-")

    for i in range(0, len(query_date)): 
        query_date[i] = int(query_date[i])

    query_date=(dt.date(query_date[0],query_date[1],query_date[2]))

    query_date = query_date+relativedelta(months=-12)

    active_temp = session.query(measurement.tobs).\
        filter(measurement.date > query_date).\
        filter(measurement.station == active_stations[0][0]).all()

    flat_list = []
    for sublist in active_temp:
        for item in sublist:
            flat_list.append(item)
    active_temp = flat_list

    tobs_dict = {k: v for k, v in zip(dates, active_temp)}

    session.close()
    
    return jsonify(tobs_dict)

@app.route("/api/v1.0/start/<given_date>")
def start(given_date):

    session = Session(engine)
    
    given_date =given_date.split("-")

    for i in range(0, len(given_date)): 
        given_date[i] = int(given_date[i])
        
    given_date=(dt.date(given_date[0],given_date[1],given_date[2]))
        
    max_temp = session.query(func.max(measurement.tobs).\
    filter(measurement.date >= given_date)).all()
                             
    min_temp = session.query(func.min(measurement.tobs).\
    filter(measurement.date >= given_date)).all()
                            
    avg_temp= session.query(func.avg(measurement.tobs).\
    filter(measurement.date >= given_date)).all()
    
    session.close()

    return (f"The start date is {given_date}\n"
               f"the minimum temperature since then is {min_temp[0][0]} F \n"
               f"the average temperature {round(avg_temp[0][0],2)} F"
               f", and the max temperature {max_temp[0][0]} F")
    
@app.route("/api/v1.0/start,end/<start_date>,<end_date>")
def startend(start_date,end_date):

    start_date =start_date.split("-")

    for i in range(0, len(start_date)): 
        start_date[i] = int(start_date[i])
        
    start_date=(dt.date(start_date[0],start_date[1],start_date[2]))
    
    end_date =end_date.split("-")

    for i in range(0, len(end_date)): 
        end_date[i] = int(end_date[i])
        
    end_date=(dt.date(end_date[0],end_date[1],end_date[2]))

    session = Session(engine)
    
    max_temp = session.query(func.max(measurement.tobs).\
    filter(measurement.date >= start_date).\
    filter(measurement.date <= end_date)).\
    all()
                             
    min_temp = session.query(func.min(measurement.tobs).\
    filter(measurement.date >= start_date).\
    filter(measurement.date <= end_date)).\
    all()
                            
    avg_temp= session.query(func.avg(measurement.tobs).\
    filter(measurement.date >= start_date).\
    filter(measurement.date <= end_date)).\
    all()
    
    session.close()

    return (f"The start date is {start_date}\n"
            f" the end date is {end_date}\n"
            f"the minimum temperature during that period is {min_temp[0][0]} F \n"
            f"the average temperature {round(avg_temp[0][0],2)} F"
            f", and the max temperature {max_temp[0][0]} F")
    

    
    

if __name__ == "__main__":
    app.run(debug=True)