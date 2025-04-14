# %% Imports
import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
from support.data_cleaner import read_map_data


# %% Functions
@st.cache_data
def filter_valid_inspection_data():
    # Read Data
    data = read_map_data()
    
    # Remove uninspected restaurants
    df = data[data['inspection date'] != dt.date(1900, 1, 1)]
    
    # Get only most recent inspection data
    df.sort_values(by=['inspection date', 'camis'], ascending=[False, True], inplace=True)
    df = df.drop_duplicates(subset='camis', keep='first')
    
    # Append scores for restaurants with non-critical violations and remove unknown geospatial information
    df.loc[df['score'].isna(), 'score'] = 0
    df.dropna(subset=['latitude', 'longitude'], inplace=True)
    
    return df[['camis', 'dba', 'latitude', 'longitude', 'inspection date', 'score']]

@st.cache_data
def geospatial_preprocessing(df, score_weight = 0.1, km=1):
    # Convert latitude and longitude to radians
    coords_rad = np.radians(df[['latitude', 'longitude']])
    
    # Scale health inspection scores
    score_scaled = MinMaxScaler().fit_transform(df[['score']])
    
    # Combine for clustering + weight scores
    coords_with_score = np.hstack((coords_rad, score_scaled * score_weight))
    
    # Get eps in radians based on earth geography
    km_to_rad = lambda x: x/6371.0 # Earth's radius
    eps = km_to_rad(km) # km will now map to radian distance such that 1 km entry gives corresponding epsilon value
    
    return coords_with_score, eps

@st.cache_data
def dbscan_clustering(data, eps=.5, min_samples=5, metric='euclidean'):
    # Init DBSCAN
    db = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
    
    # Fit clusters to data
    if metric == 'haversine':
        clusters = db.fit_predict(data[:, :2])
    else:
        clusters = db.fit_predict(data)

    # Determine size of each cluster
    cluster_sizes = pd.Series(clusters).value_counts().sort_index() 
    
    return clusters, cluster_sizes

