# Import the dependencies.
from flask import Flask
from flask import Flask, jsonify
from datetime import datetime, timedelta
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# reflect the tables
Base.classes.keys()

# Save references to each table
station=Base.classes.station
measurement=Base.classes.measurement

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
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_date=recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date_obj = datetime.strptime(recent_date[0], "%Y-%m-%d")

    # Calculate the date one year from the last date in data set.
    previous_year=last_date_obj-dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    data_pre=session.query(measurement.date,measurement.prcp).\
    filter(measurement.date >= previous_year).all()

    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    data_pre_df = pd.DataFrame(data_pre,columns=['date','precipitation'])
    all_names = list(np.ravel(data_pre))
    return jsonify(all_names)



@app.route("/api/v1.0/stations")
def stations():
    
    total_pre = session.query(measurement.station,func.count(measurement.tobs)).group_by(measurement.station).order_by(func.count(measurement.tobs).desc()).all()
    df_station= list(np.ravel(total_pre))
    return jsonify(df_station)


@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year from the last date in data set.

    recent_date=recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date_obj = datetime.strptime(recent_date[0], "%Y-%m-%d")

    # Calculate the date one year from the last date in data set.

    previous_year=last_date_obj-dt.timedelta(days=365)
    data_tobs=session.query(measurement.date,measurement.tobs).\
    filter(measurement.date >= previous_year).filter(measurement.station == 'USC00519281').all()
    df_tobs= list(np.ravel(data_tobs))
    return jsonify(df_tobs)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start, end=None):

        sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

        if not end:
                results = session.query(*sel).\
                        filter(measurement.date >= start).all()
                temps = list(np.ravel(results))
                return jsonify(temps)
        results = session.query(*sel).\
                        filter(measurement.date >= start).\
                        filter(measurement.date <= end).all()
        temps = list(np.ravel(results))
        return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)