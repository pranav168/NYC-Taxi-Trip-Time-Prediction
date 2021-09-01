# NYC-Taxi-Trip-Time-Prediction

## Problem Description
Your task is to build a model that predicts the total ride duration of taxi trips in New York City. Your primary dataset is one released by the NYC Taxi and Limousine Commission, which includes pickup time, geo-coordinates, number of passengers, and several other variables.
## Data Description
The dataset is based on the 2016 NYC Yellow Cab trip record data made available in Big Query on Google Cloud Platform. The data was originally published by the NYC Taxi and Limousine Commission (TLC). The data was sampled and cleaned for the purposes of this project. Based on individual trip attributes, you should predict the duration of each trip in the test set.
## NYC Taxi Data.csv - the training set (contains 1458644 trip records)
## Data fields
* id - a unique identifier for each trip
* vendor_id - a code indicating the provider associated with the trip record
* pickup_datetime - date and time when the meter was engaged
* dropoff_datetime - date and time when the meter was disengaged
* passenger_count - the number of passengers in the vehicle (driver entered value)
* pickup_longitude - the longitude where the meter was engaged
* pickup_latitude - the latitude where the meter was engaged
* dropoff_longitude - the longitude where the meter was disengaged
* dropoff_latitude - the latitude where the meter was disengaged
* store_and_fwd_flag - This flag indicates whether the trip record was held in vehicle memory before sending to the vendor because the vehicle did not have a connection to the server - Y=store and forward; N=not a store and forward trip
* trip_duration - duration of the trip in seconds


## Why NYC Taxi Trip Time Prediction?
Trip time prediction is an important problem. Taxi passengers often want to know when they will arrive at their destinations. We design a method of predicting taxi trip time by finding historical similar trips. Trips are clustered based on origin, destination, and start time. Then similar trips are mapped to road networks to find frequent sub-trajectories that are used to model travel time of the various parts of the routes. Experimental results show this method is effective.

![image](https://user-images.githubusercontent.com/86152517/131675088-a6632e18-d471-48ee-bf79-c610be6ec29e.png)



Machine learning has been of significant help as it has helped businesses in abundant ways. ML is a subset of AI and does not need to be directly trained like AI to perform tasks. ML is used for prediction analysis in businesses, which we will learn in this case study. ML Systems created a solution that can forecast time-based on initial partial trajectories. For someone in the logistics business, this is indispensable. It is important to predict how long a driver will have his taxi occupied. If a dispatcher got estimates about the taxi driver's current ride time, they could better recognize which driver to allocate for each pickup request.

![image](https://user-images.githubusercontent.com/86152517/131675122-d52239ad-bcbd-4892-9be6-fcaa1b68e173.png)



## Task Performed
* Data Wrangling
* Feature Engineering
* Exploratory Data Analysis
* Machine Leaning Model
* Model Evaluation


## Visualizations Used 



![image](https://user-images.githubusercontent.com/86152517/131451364-8a53ca83-7a5f-40fe-96c6-d8df645ec3c7.png)



![image](https://user-images.githubusercontent.com/86152517/131451415-24b3ba7a-9d2a-416e-866e-a2bfcc6aaa21.png)




![image](https://user-images.githubusercontent.com/86152517/131451437-1e0263de-801b-4ba1-a7d6-3de257fb0afe.png)



![image](https://user-images.githubusercontent.com/86152517/131451468-9c103db7-f87a-49b1-be49-90a090ec260f.png)




## Result 
* XGBoost : r2 score came out to be : 77% on Test set, while it was only 79% for the train set, increasing the max depth overfitted the model, where r2 score for test set remained almost the same, also root mean square error (rmse) score for both the model were 0.3 and 0.28 for test and train respectively.

* CatBoost : r2 score came out to be : 80.7% on Test set, while it was only 86.5% for the train set, one the best hyperparameter, if I would have trained more, It would have led to overfitting, also the RMSE score for test and train is 0.28 and 0.23 respectively, which means model is a better fit when compared to XGBoost.


