import uvicorn
from fastapi import FastAPI
from TripDuration import TripDuration
import numpy as np
import pickle
import pandas as pd

app = FastAPI()
pickle_in = open("cat_model.pkl","rb")
cat_model=pickle.load(pickle_in)

@app.get('/')
def index():
    return {'message': 'Lets predict your Trip duration'}
@app.post('/predict')
def predict_banknote(data:TripDuration):
    data = data.dict()
    passenger_count= data['passenger_count']      
    pickup_longitude= data['pickup_longitude'] 
    pickup_latitude= data['pickup_latitude'] 
    dropoff_longitude= data['dropoff_longitude'] 
    dropoff_latitude= data['dropoff_latitude'] 
    store_and_fwd_flag= data['store_and_fwd_flag'] 
    distance= data['distance'] 
    pickup_day= data['pickup_day'] 
    pickup_month= data['pickup_month'] 
    pickup_weekday= data['pickup_weekday'] 
    pickup_weekofyear= data['pickup_weekofyear'] 
    pickup_time= data['pickup_time'] 
    avg_speed_hr= data['avg_speed_hr'] 
    avg_speed_week= data['avg_speed_week'] 
    avg_speed_weekofyear= data['avg_speed_weekofyear'] 
    avg_speed_month= data['avg_speed_month'] 
    avg_speed_day= data['avg_speed_day'] 
    lat_diff= data['lat_diff'] 
    long_diff= data['long_diff'] 
    North= data['North'] 
    South= data['South'] 
    West= data['West'] 
    East= data['East'] 
    prediction = cat_model.predict([[passenger_count,pickup_longitude,pickup_latitude,dropoff_longitude,dropoff_latitude,
                                    store_and_fwd_flag,distance,pickup_day,pickup_month,pickup_weekday,pickup_weekofyear,
                                    pickup_time,avg_speed_hr,avg_speed_week,avg_speed_weekofyear,avg_speed_month,avg_speed_day,
                                    lat_diff,long_diff,North,South,West,East]])
    return {
        'prediction':  2.71828**prediction
    }

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
    
#uvicorn app:app --reload
