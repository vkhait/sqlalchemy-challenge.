# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:////Users/verastyles/Desktop/DV_Homework/sqlalchemy-challenge./SurfsUp/Starter_code_10/Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(engine, reflect=True)

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    #Query for the dates and precipitation values
    prcp_values =  session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()

    #Convert to list of dictionaries 
    prcp_list = []

    for date, prcp in prcp_values:
        new_dict = {}
        new_dict[date] = prcp
        prcp_list.append(new_dict)


    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
   
#Query all stations
    result = session.query(Station.station).order_by(Station.station).all()
    
#Convert to list
    stations_list = list(np.ravel(result))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():

     #Get the most recent date and date one year prior
    last_data = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_before = (dt.datetime.strptime(last_data[0],'%Y-%m-%d') \
                    - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Get the dates and temperature
    result =   session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= year_before).order_by(Measurement.date).all()

    # Convert to list of dictionaries
    tobs_list = []

    for date, tobs in result:
        new_dict = {}
        new_dict[date] = tobs
        tobs_list.append(new_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    

    #Query all tobs
    query = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        result = session.query(*query).\
            filter(Measurement.date >= start).all()

        

        temps = list(np.ravel(result))

        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and end
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    result = session.query(*query).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(result))

    return jsonify(temps=temps)

session.close()

if __name__ == "__main__":
    app.run(debug=True)