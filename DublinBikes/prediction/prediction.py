#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# import all required package
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree     import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt
import numpy as np
get_ipython().run_line_magic('matplotlib', 'inline')
from sklearn.linear_model import LinearRegression
from sklearn.metrics import classification_report, confusion_matrix


# In[ ]:


# stations data preparation
weatherdf = pd.read_csv('static/weatherdata.csv',  keep_default_na=True, sep=',\s+', delimiter=',')
weatherdf["new_dateframe"] = pd.to_datetime(weatherdf["dt"], unit="s")
weatherdf["hour"]= weatherdf["new_dateframe"].dt.hour
weatherdf["date"]= weatherdf["new_dateframe"].dt.date
weatherdf = weatherdf.drop(['humidity','pressure','temp_max','temp_min','description', 'icon', 'id', 'wind_deg', 'new_dateframe' ], axis = 1)


# In[ ]:


# weather data preparation
bikedf = pd.read_csv('static/bikesdata.csv',  keep_default_na=True, sep=',\s+', delimiter=',')
bikedf["new_dateframe"] = pd.to_datetime(bikedf["last_update"], unit="ms")
bikedf["hour"]= bikedf["new_dateframe"].dt.hour
bikedf["date"]= bikedf["new_dateframe"].dt.date
bikedf = bikedf.drop(['last_update','banking','bike_stands','status', 'new_dateframe','contract_name', 'address', 'position_lat', 'position_lng', 'bonus', 'name'], axis = 1)


# In[ ]:


# data processing for random forest
mergedf=pd.merge(bikedf,weatherdf,on=['hour','date'], how = "left")
mergedf = mergedf.dropna()
mergedf=mergedf.drop(['date'], axis = 1)
categorical_columns = mergedf[['main']].columns
for column in categorical_columns:
    mergedf[column] = mergedf[column].astype('category')
mergedf= pd.get_dummies(mergedf, columns=['main'], prefix = ['main'])
mergedf.duplicated()
mergedf=mergedf.drop_duplicates()
mergedf = mergedf.drop(['main_Clouds','main_Clear','available_bike_stands','dt'], axis = 1)


# # Random Forest

# In[ ]:


# select numeric features
numeric_columns = mergedf.select_dtypes(['int64','float64','uint8']).columns
numeric_columns = numeric_columns.drop(['available_bikes'])


# In[ ]:


numeric_columns = mergedf.select_dtypes(['int64','float64','uint8']).columns
X = mergedf[numeric_columns]
y = mergedf.available_bikes
print("\nDescriptive features in X:\n", X)
print("\nTarget feature in y:\n", y)
linreg_70train = LinearRegression().fit(X, y)
print("Features: \n", X.columns)
print("Coeficients: \n", linreg_70train.coef_)
print("\nIntercept: \n", linreg_70train.intercept_)


# In[ ]:


# set up prediction variables
X_train,X_test, y_train, y_test = train_test_split(X,y)
y_predicted = linreg_70train.predict(X_test)


# In[ ]:


# def print out format
def printMetrics(testActualVal, predictions):
    print('\n==============================================================================')
    print("MAE: ", metrics.mean_absolute_error(testActualVal, predictions))
    print("RMSE: ", metrics.mean_squared_error(testActualVal, predictions)**0.5)
    print("R2: ", metrics.r2_score(testActualVal, predictions))


# In[ ]:


# start training 
for i in mergedf.number.unique():
    mergedf_id = mergedf.loc[mergedf["number"] == i]
    numeric_columns = mergedf_id.select_dtypes(['int64','float64','uint8']).columns
    numeric_columns = numeric_columns.drop(['available_bikes'])
    X = mergedf_id[numeric_columns]
    y = mergedf_id.available_bikes
    # set up random forest arguement
    random_forest = RandomForestRegressor(max_depth=10, random_state=0, n_estimators=500)
    # 2/3 data training 1/3 data testing
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.33, random_state=42)
    random_forest.fit(X_train,y_train)
    y_predicted = random_forest.predict(X_test)
    # generate pickle files
    pkl_filename = str(i) + ".pkl"  
    with open('static/pickle/' + pkl_filename, 'wb') as file:
        pickle.dump(random_forest, file)
    actual_vs_predicted_multiplelinreg1 = pd.concat([y_test,pd.DataFrame(y_predicted, columns=['Predicted'],index=y_test.index)],axis=1)
    print(printMetrics(y_test,y_predicted))


# In[ ]:


# prediction function
def bikes_prediction(station_id,time_hour):
    r = requests.get('http://api.openweathermap.org/data/2.5/forecast?appid=9511c6f09bf671d3bd65bf650197234f&q=Dublin')
    weathers = r.json()               
    weather_detalis = weathers["list"]                                                                                           
    temp = weather_detalis[0]['main']['temp']                                                                                    
    wind = weather_detalis[0]['wind']['speed']                                                                                   
    main = weather_detalis[0]['weather'][0]['main']                                                                                  
    weather_Drizzle = 0
    weather_Rain = 0
    if main == 'Drizzle':
        weather_Drizzle = 1
    elif main == 'Rain':
        weather_Rain = 1
    f2 = pd.DataFrame(np.array([station_id,time_hour, temp, wind, weather_Drizzle, weather_Rain])).T
    models = {}
    with open(str(station_id) + ".pkl", "rb") as handle:
        models[station_id] = pickle.load(handle)
    return models[station_id].predict(f2).round()[0]


# In[ ]:


# test
bikes_prediction(12,13)

