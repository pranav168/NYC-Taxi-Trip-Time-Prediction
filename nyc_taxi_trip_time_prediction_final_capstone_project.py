# -*- coding: utf-8 -*-
"""NYC Taxi Trip Time Prediction Final - Capstone Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ekRcHRtARbxNOdHslf0ifMhDAWOiyBdu

# <b><u> Project Title : Taxi trip time Prediction : Predicting total ride duration of taxi trips in New York City</u></b>

## <b> Problem Description </b>

### Your task is to build a model that predicts the total ride duration of taxi trips in New York City. Your primary dataset is one released by the NYC Taxi and Limousine Commission, which includes pickup time, geo-coordinates, number of passengers, and several other variables.

## <b> Data Description </b>

### The dataset is based on the 2016 NYC Yellow Cab trip record data made available in Big Query on Google Cloud Platform. The data was originally published by the NYC Taxi and Limousine Commission (TLC). The data was sampled and cleaned for the purposes of this project. Based on individual trip attributes, you should predict the duration of each trip in the test set.

### <b>NYC Taxi Data.csv</b> - the training set (contains 1458644 trip records)


### Data fields
* #### id - a unique identifier for each trip
* #### vendor_id - a code indicating the provider associated with the trip record
* #### pickup_datetime - date and time when the meter was engaged
* #### dropoff_datetime - date and time when the meter was disengaged
* #### passenger_count - the number of passengers in the vehicle (driver entered value)
* #### pickup_longitude - the longitude where the meter was engaged
* #### pickup_latitude - the latitude where the meter was engaged
* #### dropoff_longitude - the longitude where the meter was disengaged
* #### dropoff_latitude - the latitude where the meter was disengaged
* #### store_and_fwd_flag - This flag indicates whether the trip record was held in vehicle memory before sending to the vendor because the vehicle did not have a connection to the server - Y=store and forward; N=not a store and forward trip
* #### trip_duration - duration of the trip in seconds
"""

from google.colab import drive
drive.mount('/content/drive')

#Importing all the required packages and libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime as dt
!pip install haversine
import haversine as hs
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_colwidth', -1)
plt.style.use('fivethirtyeight')
!pip install catboost
from catboost import CatBoostRegressor

from mpl_toolkits.mplot3d import axes3d
from sklearn.metrics import r2_score,accuracy_score  
from sklearn.model_selection import train_test_split  
from xgboost import XGBRegressor
from sklearn import metrics
import warnings                                                                 # Removing all those annoying Warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')

df=pd.read_csv('/content/drive/MyDrive/Copy of NYC Taxi Data.csv') 
df.head()

df.info()                                                                       #No nulls

column_list=['id', 'vendor_id', 'pickup_datetime', 'dropoff_datetime',
       'passenger_count', 'pickup_longitude', 'pickup_latitude',
       'dropoff_longitude', 'dropoff_latitude', 'store_and_fwd_flag',
       'trip_duration']
count_dataset=pd.DataFrame()
distinct_features=[]                                                                                          #Empty list to know the number of distict features,sum of all these values, and sum of values top 10 comprises
for i in column_list:                                                                                               
  count_dataset[i]= pd.Series(df[i].value_counts().sort_values(ascending=False).head(10).index)      
  count_dataset[f'{i}_count']=pd.Series(df[i].value_counts().sort_values(ascending=False).head(10).values).astype('int')   
  distinct_features.append((len(df[i].value_counts().index),df[i].value_counts().sum(),df[i].value_counts().sort_values(ascending=False).head(10).sum())) 
# final_tally=list(zip(column_list,distinct_features))                                                           #Zipping with column_list
col_ref={}  
for i in column_list:
  if i in ['trip_duration']:                                                                    #colur red shows the Dependent Variable('trip_duration')
    col_ref[i]='background-color: red'  
  else:
    col_ref[i]='background-color: blue'                                                                       #colur blue shows the features 
  temp=f'{i}_count'
  col_ref[temp]='background-color: green'                                                                     #colur green shows the count
def Nan_as_black(val):
  if str(val)=='nan':
    color = 'black'
    return 'color: %s' % color
count_dataset=count_dataset.style.apply(lambda x: pd.DataFrame(col_ref, index=count_dataset.index, columns=count_dataset.columns).fillna(''), axis=None).highlight_null('black').applymap(Nan_as_black)
count_dataset

corr = df.corr()                                                                #plotting co-relation chart
plt.figure(figsize=(25,15))
sns.heatmap(corr, annot=False)
plt.show()                                                                      #there is no correlation whatsoever between our dependent and independent variables, thus i will be making various features to improve this situation

df.describe()                                                                   #their are few cases with passanger count 0, lets explore it
                                                                                #also minimum drip duretion is 1 sec which show an anomaly, lets remove them first
                                                                                # Minimum pickup and dropoff longitude are really low than mean

df=df[df.passenger_count!=0]                                                    #Removing rows with 0 passenger count

df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], format='%Y-%m-%d %H:%M:%S')                 #Converting these dates to datetime format
df['dropoff_datetime']=pd.to_datetime(df['dropoff_datetime'],format='%Y-%m-%d %H:%M:%S')
df.columns

print(np.percentile(df.trip_duration,0.1),
np.percentile(df.trip_duration,0.5),
np.percentile(df.trip_duration,1.5),                                            #after this the value starts to get saturated thus anything below 107 sec is mostly a outlier, now lets look for maximum value as well
np.percentile(df.trip_duration,2),
np.percentile(df.trip_duration,2.5),
np.percentile(df.trip_duration,3),
np.percentile(df.trip_duration,3.5))

print(np.percentile(df.trip_duration,98.5),
np.percentile(df.trip_duration,99),
np.percentile(df.trip_duration,99.5),                                           #after this the value starts to get increase suddenly thus anything above 4139 sec is mostly a outlier, lets remove these values
np.percentile(df.trip_duration,99.9))

df=df[(df.trip_duration>=107) & (df.trip_duration<=4139)]

print(np.percentile(df.pickup_longitude,0.1),
      np.percentile(df.pickup_longitude,0.05),                                  #after this their is anomaly 
      np.percentile(df.pickup_longitude,0.01),                                                                  
      np.percentile(df.pickup_longitude,0.001),
      np.percentile(df.pickup_longitude,0.0001))
df=df[df.pickup_longitude>-74.017]
print(np.percentile(df.dropoff_longitude,0.1),
      np.percentile(df.dropoff_longitude,0.05),
      np.percentile(df.dropoff_longitude,0.01),                                 #after this their is anomaly                                 
      np.percentile(df.dropoff_longitude,0.001),
      np.percentile(df.dropoff_longitude,0.0001))
df=df[df.dropoff_longitude>=-74.467]

plt.figure(figsize=(30,5))
plt.title('Trip Duration Distribution')
plt.xlabel('Trip Duration, minutes')
plt.ylabel('Density of Trips made')
sns.distplot(df.trip_duration/60, bins=100)

#adding another column with distance metric calculted using lat and long 
df['haversine distance (km)'] = df.apply(lambda x: float(hs.haversine((x['pickup_latitude'],x['pickup_longitude']),(x['dropoff_latitude'], x['dropoff_longitude']))),axis=1)
df.shape

pd.set_option('display.float_format', lambda x: '%.3f' % x)
df.describe()                                                                   #Data looks Perfect now,still their can be some relative anomalies, which i will remove using isolation forest

minmax = MinMaxScaler(feature_range=(0, 1))                                     #Using Isolation Forest algorithm for anomaly detection, for contamination i will use various values and visualize the best scatter plot
X = minmax.fit_transform(df[['trip_duration','haversine distance (km)','pickup_longitude','pickup_latitude','dropoff_longitude','dropoff_latitude']])
contamination_list=[0.025,0.05,0.075,0.1]
for contamination in contamination_list:
  clf = IsolationForest(n_estimators=100, contamination=contamination, random_state=0)      
  try:
    clf.fit(X)
  except:
    pass
  temp=df
  temp['multivariate_outlier'] = clf.predict(X)                                   # prediction of a datapoint category outlier or inlier
  temp=temp[temp.multivariate_outlier==1]                                             #removing these outliers
  f, (ax1, ax2) = plt.subplots(1, 2, sharey=True,figsize=(15,5))

  temp.plot(kind='scatter', x='pickup_longitude', y='pickup_latitude',
                  color='yellow', 
                  s=.02, alpha=.6, subplots=True, ax=ax1)
  ax1.set_title(f"Pickups_contamination= {contamination}")
  ax1.set_facecolor('black')

  temp.plot(kind='scatter', x='dropoff_longitude', y='dropoff_latitude',
                  color='yellow', 
                  s=.02, alpha=.6, subplots=True, ax=ax2)
  ax2.set_title(f"Dropoffs_contamination= {contamination}")
  ax2.set_facecolor('black') 
  plt.show()

'''Thus contamination=0.075 works best as we want to retain maximum amount of data'''
minmax = MinMaxScaler(feature_range=(0, 1))                                     #Using Isolation Forest algorithm for anomaly detection, for contamination i will use various values and visualize the best scatter plot
X = minmax.fit_transform(df[['trip_duration','haversine distance (km)',
                             'pickup_longitude','pickup_latitude',
                             'dropoff_longitude','dropoff_latitude']])
clf = IsolationForest(n_estimators=100, contamination=0.075, random_state=0)      
clf.fit(X)
df['multivariate_outlier'] = clf.predict(X)                                     # prediction of a datapoint category outlier or inlier
df=df[df.multivariate_outlier==1]  
df.drop('multivariate_outlier',axis=1,inplace=True)

def plot_scatter(df):                                                           
  fig = plt.figure(figsize = (20, 10))
  ax = plt.axes(projection ="3d")
  # Creating color map
  z=range(1,len(df['pickup_longitude'])+1)
  Z=[]
  count=0
  my_cmap = plt.get_cmap('hot')
  plot=ax.scatter3D(df['pickup_longitude'],df['pickup_latitude'],
                    1,cmap = my_cmap,alpha = 0.8,
                    c =df['trip_duration'],s=0.02) 
  plt.title("3D scatter plot")
  ax.set_xlabel('pickup_longitude', fontweight ='bold')
  ax.set_ylabel('pickup_latitude', fontweight ='bold')
  fig.colorbar(plot, ax = ax, aspect = 5)
  ax.view_init(-140, -60)
  plt.show()       
                                                                              
plot_scatter(df)

import folium
from folium import plugins
from folium.plugins import HeatMap

map_NY = folium.Map(location=[40.767937,-73.982155 ],
                    zoom_start = 13) 
heat_df = df[:20000]
heat_df = heat_df[['pickup_latitude', 'pickup_longitude']]
heat_df = heat_df.dropna(axis=0, subset=['pickup_latitude', 'pickup_longitude'])
heat_data = [[row['pickup_latitude'],row['pickup_longitude']] for index, row in heat_df.iterrows()] # List comprehension to make out list of lists

HeatMap(heat_data).add_to(map_NY)                                                                    # Plot it on the map

map_NY

df.head()

try:
  df.drop('id',axis=1,inplace=True)                                             #this is of no use
except:
  pass
sns.countplot(df.passenger_count)

# one_hot_entity='Passenger_count'    
# column_one_hot=['passenger_count']                # one hot encoding 
# count=0
# for i in column_one_hot:
#   temp_df=pd.get_dummies(df[i], prefix=one_hot_entity)
#   count+=1
#   try:
#     df_one_hot=pd.concat([df_one_hot, temp_df], axis=1)
#   except:
#     df_one_hot=temp_df
# df=pd.concat([df,df_one_hot], axis=1)
# df.drop('passenger_count',axis=1,inplace=True)
# df.head()

list=['pickup_','dropoff_']
for i in list:  
  df[i+'date'] = df[i+'datetime'].dt.date
  df[i+'day'] = df[i+'datetime'].dt.day
  df[i+'month'] = df[i+'datetime'].dt.month
  df[i+'weekday'] = df[i+'datetime'].dt.weekday
  df[i+'weekofyear'] = df[i+'datetime'].dt.weekofyear
  df[i+'time'] = df[i+'datetime'].dt.hour

df['avg_speed_h2']=df['haversine distance (km)']*3600  / df['trip_duration']    #converting sec to hours
with sns.axes_style('white'):
    sns.jointplot('avg_speed_h2', "trip_duration", df[:200], kind='hex',height=10)    
avg_speed_vs_hr=df.groupby('pickup_time')['avg_speed_h2'].mean()
avg_speed_vs_week=df.groupby('pickup_weekday')['avg_speed_h2'].mean()
avg_speed_vs_weekofyear=df.groupby('pickup_weekofyear')['avg_speed_h2'].mean()
avg_speed_vs_month=df.groupby('pickup_month')['avg_speed_h2'].mean()
avg_speed_vs_day=df.groupby('pickup_day')['avg_speed_h2'].mean()
avg_speed_vs_date=df.groupby('pickup_date')['avg_speed_h2'].mean()
dict_hr=dict(zip(avg_speed_vs_hr.index,avg_speed_vs_hr.values))
dict_week=dict(zip(avg_speed_vs_week.index,avg_speed_vs_week.values))
dict_weekofyear=dict(zip(avg_speed_vs_weekofyear.index,avg_speed_vs_weekofyear.values))
dict_month=dict(zip(avg_speed_vs_month.index,avg_speed_vs_month.values))
dict_day=dict(zip(avg_speed_vs_day.index,avg_speed_vs_day.values))

df['avg_speed_hr']=df['pickup_time'].apply(lambda x:dict_hr[x])                            #now we can put this value in our model, and it will not create a baise.
df['avg_speed_hr']=np.log(df['avg_speed_hr'])
df['avg_speed_week']=df['pickup_weekday'].apply(lambda x:dict_week[x])                     #now we can put this value in our model, and it will not create a baise.
df['avg_speed_week']=np.log(df['avg_speed_week'])
df['avg_speed_weekofyear']=df['pickup_weekofyear'].apply(lambda x:dict_weekofyear[x])      #now we can put this value in our model, and it will not create a baise.
df['avg_speed_weekofyear']=np.log(df['avg_speed_weekofyear'])
df['avg_speed_month']=df['pickup_month'].apply(lambda x:dict_month[x])                     #now we can put this value in our model, and it will not create a baise.
df['avg_speed_month']=np.log(df['avg_speed_month'])
df['avg_speed_day']=df['pickup_day'].apply(lambda x:dict_day[x])                           #now we can put this value in our model, and it will not create a baise.
df['avg_speed_day']=np.log(df['avg_speed_day'])

df['log_trip_duration']= np.log(df.trip_duration)                               #Normalizing the value of trip_duration
df['haversine distance (km)']= np.log(df['haversine distance (km)']) 
df['store_and_fwd_flag']=df.store_and_fwd_flag.apply(lambda x: np.where(x=='N',0,1))
df.head()

list1=['day','month','weekday','weekofyear','date','time']
list2=['pickup_','dropoff_']
for i in list2:
  for j in list1:
    plt.figure(figsize=(30,5))
    temp=df.groupby(i+j)['trip_duration'].mean()
    sns.barplot(temp.index,temp.values)
    plt.xticks(rotation=90)
    plt.show()                                                                  # for all the time criteria trip durations are almost the same, except that of hours in a day, lets plot autocorelation chart to look for seasonality.

time_attribute=['day','month','weekday','weekofyear','time']
service_nature=['pickup_','dropoff_']
count=0
counter=0
fig,ax=plt.subplots(2,5,figsize=(30,12))
plt.rcParams['axes.facecolor'] = 'black'
for service in service_nature:
  if counter==5:
    count=1
    counter=0
  for attribute in time_attribute:
    sns.regplot(df[service+attribute][:100000],df.trip_duration[:100000],color='red',ax=ax[count,counter])
    
    counter+=1                                                                  # Reg plot shows the linear relationship between trip duration and all the time formats.

plot_list=['pickup_weekday','pickup_month','dropoff_weekday','pickup_weekofyear']
count=0
for i in plot_list:
  count+=1
  if count==4:
    plt.figure(figsize=(30,20))
  else:
    plt.figure(figsize=(30,2))
  sns.heatmap(data=pd.crosstab(df[i], 
                              df.pickup_time, 
                              values=df.vendor_id, 
                              aggfunc='count',
                              normalize='index'))
  if count==3:
    plt.title(f'Dropoff heatmap, {i} vs Day Hour')
    plt.ylabel(i) ; plt.xlabel('Day Hour, 0-23')
    
    plt.show()
  else:
    plt.title(f'Pickup heatmap, {i} vs Day Hour')
    plt.ylabel(i) ; plt.xlabel('Day Hour, 0-23')
    
    
    plt.show()                                                                    #Both heat maps tells the similar story, 6-7pm are the peak times, and nights hardly have any bookings.

df.drop(['avg_speed_h2'],axis=1,inplace=True)

df.drop(['pickup_datetime','dropoff_datetime','trip_duration','pickup_date','dropoff_date','dropoff_day','dropoff_month','dropoff_weekday','dropoff_weekofyear','dropoff_time'],axis=1,inplace=True)

df['lat_diff']=df.dropoff_latitude-df.pickup_latitude
df['long_diff']=df.dropoff_longitude-df.pickup_longitude                        # west yeild -ve on long_diff, vice versa & north yeild + lat_diff and vice versa, thus we can now give directions.
# df.drop(['pickup_longitude','pickup_latitude','dropoff_longitude','dropoff_latitude'],axis=1,inplace=True)

df['North']=df['lat_diff'].apply(lambda x: np.where(x>0,1,0))
df['South']=df['lat_diff'].apply(lambda x: np.where(x<0,1,0))
df['West']=df['long_diff'].apply(lambda x: np.where(x<0,1,0))
df['East']=df['long_diff'].apply(lambda x: np.where(x>0,1,0))

df.head()

# column_one_hot=['pickup_time','pickup_weekofyear','pickup_weekday','pickup_month','pickup_day','vendor_id']                # one hot encoding 
# for i in column_one_hot:
#   temp2_df=pd.get_dummies(df[i], prefix=i)
#   try:
#     df_one_hot2=pd.concat([df_one_hot2, temp2_df], axis=1)
#   except:
#     df_one_hot2=temp2_df

# df=pd.concat([df,df_one_hot2], axis=1)
# df.drop(['pickup_time','pickup_weekofyear','pickup_weekday','pickup_month','pickup_day','vendor_id','pickup_longitude','pickup_latitude','dropoff_longitude','dropoff_latitude'],axis=1,inplace=True)

df.head()

corr =df.corr()                                                                #plotting co-relation chart
plt.figure(figsize=(25,15))
sns.heatmap(corr, annot=False)
plt.show()

X=df.drop('log_trip_duration',axis=1)[:100000]                                  # using a smaller size for hyperparameter tuning, as dataset is quite large
y=df['log_trip_duration'][:100000]
X_train, X_test, y_train, y_test= train_test_split(X,y,test_size=0.05)
X_train, X_val, y_train, y_val= train_test_split(X_train,y_train,test_size=0.1)

"""#HyperParameter Tuning  for XGBoost and CatBoost Model"""

# Commented out IPython magic to ensure Python compatibility.
from sklearn.model_selection import GridSearchCV  
xgb_model = XGBRegressor()
learning_rate= [0.1,0.25,0.5]                                                   # various learning rates i will tryout
nax_depth = [10,12]      
n_estimators=[100,200,300]                                                      # various depths that i will try out
parameters = dict(learning_rate=learning_rate, nax_depth=nax_depth, n_estimators=n_estimators,objective=['reg:squarederror'])     
grid = GridSearchCV(xgb_model,parameters,scoring='r2', cv=None)                 # we can also use 'neg_mean_squared_error', here i am not using cv as dataset is quite large and well distributed.
grid_result=grid.fit(X_train, y_train)
print ("r2 / variance : ", grid.best_score_,'with parameter: ',grid_result.best_params_)
print("RMSE score: %.2f"
#               % np.sqrt(metrics.mean_squared_error(y_test,grid.predict(X_test))))

"""As, Dataset is quite huge, using Kfold Cross-Validation and gridsearch was impossible due to hardware constraints, thus i decided to change values on by own by running model and looking at result multiple times."""

# Commented out IPython magic to ensure Python compatibility.
from sklearn.model_selection import GridSearchCV  
cat_model = CatBoostRegressor()
learning_rate= [0.05,0.1,0.15]                                                  # various learning rates i will tryout
depth = [6,8,10]                                                                 # various depths that i will try out
parameters = dict(depth=depth,learning_rate=learning_rate,iterations=[1000],    # max iterations are set to 1000 
                  od_type=["Iter"],od_wait=[200],metric_period=[999],           # i have used overfitting detector & enables the use of best model
                  use_best_model = [True] )     
grid = GridSearchCV(cat_model,parameters,scoring='r2', cv=None)                 #we can also use 'neg_mean_squared_error', here i am not using cv as dataset is quite large and well distributed.
grid_result=grid.fit(X_train, y_train, eval_set=(X_val,y_val))
print ("r2 / variance : ", grid.best_score_,'with parameter: ',grid_result.best_params_)
print("RMSE score: %.2f"
#               % np.sqrt(metrics.mean_squared_error(y_test,grid.predict(X_test))))

X=df.drop('log_trip_duration',axis=1)
y=df['log_trip_duration']
X_train, X_test, y_train, y_test= train_test_split(X,y,test_size=0.05)
X_train, X_val, y_train, y_val= train_test_split(X_train,y_train,test_size=0.1) # Validation Set, which is used in Catboost Regressor to facilitate backpropogation.
print(f'Shape of X_train = {X_train.shape}')
print(f'Shape of X_test = {X_test.shape}')
print(f'Shape of X_val = {X_val.shape}')

model = XGBRegressor(max_depth=10,                                              # best set of hyperparameters {'learning_rate': 0.25, 'n_estimators': 300, 'nax_depth': 10, 'objective': 'reg:squarederror'}                  
                     learning_rate=0.25,
                     n_estimators=300,
                     verbosity=0,
                     objective='reg:squarederror')                                                         
model.fit(X_train,y_train)
y_pred_test=model.predict(X_test)
y_pred_train=model.predict(X_train)
print(r2_score(y_test,y_pred_test))
print('RMSE score for the CatRegressor is : {}'.format(np.sqrt(metrics.mean_squared_error(y_test,y_pred_test))))
print(r2_score(y_train,y_pred_train))
print('RMSE score for the CatRegressor is : {}'.format(np.sqrt(metrics.mean_squared_error(y_train,y_pred_train))))
#certainly there is overfitting, i will now decrease the max_depth

model = XGBRegressor(max_depth=8,                                                            
                     learning_rate=0.25,
                     n_estimators=300,
                     verbosity=0,
                     objective='reg:squarederror')                                                         
model.fit(X_train,y_train)
y_pred_test=model.predict(X_test)
y_pred_train=model.predict(X_train)
print(r2_score(y_test,y_pred_test))
print('RMSE score for the CatRegressor is : {}'.format(np.sqrt(metrics.mean_squared_error(y_test,y_pred_test))))
print(r2_score(y_train,y_pred_train))
print('RMSE score for the CatRegressor is : {}'.format(np.sqrt(metrics.mean_squared_error(y_train,y_pred_train))))

"""78% is the best r2 score i  was able to achieve using XGBoost model, after switching various Hyperparameters."""

def plot_feature_importance(importance,names,model_type):
    
    #Create arrays from feature importance and feature names
    feature_importance = np.array(importance)
    feature_names = np.array(names)
    
    #Create a DataFrame using a Dictionary
    data={'feature_names':feature_names,'feature_importance':feature_importance}
    fi_df = pd.DataFrame(data)
    fi_df.sort_values(by=['feature_importance'], ascending=False,inplace=True)  #Sort the DataFrame in order decreasing feature importance
    plt.figure(figsize=(30,8))
    sns.barplot(y=fi_df['feature_importance'], x=fi_df['feature_names'])
    plt.title(model_type + 'FEATURE IMPORTANCE')
    plt.xlabel('FEATURE IMPORTANCE')
    plt.xticks(rotation=90)
    plt.ylabel('FEATURE NAMES')

plot_feature_importance(model.feature_importances_,X_train.columns,'XG BOOST')  #Plotting Feature Importance for XGboost

cat_model = CatBoostRegressor(loss_function = "RMSE", eval_metric = "RMSE", metric_period = 1000, iterations=30000,
                        use_best_model = True,
                        random_strength = 0.005,
                        learning_rate=0.1,
                        depth=8,
                        random_seed = 93,                                       # using best set of hyperparameters {'depth': 8, 'iterations': 1000, 'learning_rate': 0.1, 'metric_period': 999, 'od_type': 'Iter', 'od_wait': 200, 'use_best_model': True}
                        l2_leaf_reg = 0.1,
                        verbose=True,
                        logging_level = None,od_type = "Iter",
                        od_wait = 200)
cat_model.fit( X_train, y_train, cat_features=None, eval_set=(X_val,y_val))
y_pred_test_cat=cat_model.predict(X_test)
y_pred_train_cat=cat_model.predict(X_train)
print(f'For learning rate = {0.1}, following are the scores of evaluation metrics:')
print(f'r2 score for test set using  CatRegressor is : {r2_score(y_test,y_pred_test_cat)}')
print('RMSE score for test set using CatRegressor is : {}'.format(np.sqrt(metrics.mean_squared_error(y_test,y_pred_test_cat))))
print(f'r2 score for train set using CatRegressor is : {r2_score(y_train,y_pred_train_cat)}')
print('RMSE score for train set using CatRegressor is : {}'.format(np.sqrt(metrics.mean_squared_error(y_train,y_pred_train_cat))))
# we are able to achieve 80 percent r2 score using this model

"""this model is not only fast but much more accurate as well."""

plot_feature_importance(cat_model.get_feature_importance(),X_train.columns,'CATBOOST ') #Plotting Feature Importance for CatBoost Model