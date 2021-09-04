from pydantic import BaseModel

class TripDuration(BaseModel):
    passenger_count: float         
    pickup_longitude: float 
    pickup_latitude: float 
    dropoff_longitude: float
    dropoff_latitude: float
    store_and_fwd_flag: float 
    distance: float
    pickup_day: float
    pickup_month: float
    pickup_weekday: float
    pickup_weekofyear: float
    pickup_time: float
    avg_speed_hr: float
    avg_speed_week: float
    avg_speed_weekofyear: float
    avg_speed_month: float
    avg_speed_day: float
    lat_diff: float
    long_diff: float
    North: float
    South: float
    West: float
    Easr: float
      
      
