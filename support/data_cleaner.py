import streamlit as st
import pandas as pd
import zipfile
import tempfile
import os
import requests

@st.cache_data
def read_map_data(file_path="data/data.zip", map_data="data.json", from_nyc_db=False):
    """
    Function that read and cleans data from the NYC Dining dataset.
    This function is cached to improve performance.
    Specify from_nyc_db = True to load directly from DOHMH DB
    """
    if from_nyc_db:
        base_url = r"https://data.cityofnewyork.us/resource/43nn-pn8j.json"
        limit = 1000
        offset = 0
        data = pd.DataFrame()
        
        # Set up a loop to paginate through data
        while True:
            response = requests.get(f"{base_url}?$limit={limit}&$offset={offset}")
            
            # Handle if no response is returned
            if response.status_code != 200:
                print(f"Failed to fetch data: {response.status_code}. Defaulting to stored data.")
                return read_map_data(file_path, from_nyc_db=False)
            
            new_data = response.json()
            
            if not new_data: # No more data to retrieve
                break
            
            # convert new data to dataframe
            new_df = pd.DataFrame(new_data)
            
            # append to existing dataframe
            data = pd.concat([data, new_df], ignore_index=True)
            
            offset += limit
        data.columns = data.columns.str.lower()
        print(f"Total rows fetched: {len(data)}")
    else:
        # Unpack Zip File and Read Data
        with tempfile.TemporaryDirectory() as temp_dir:
            # Open zip file in temporary directory in context manager
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extract(map_data, temp_dir)
            # Load data
            data = pd.read_json(os.path.join(temp_dir, 'data.json')) 
        
    # Format Data Types
    data_types = {'zipcode':pd.Int64Dtype(),
                'phone':pd.Int64Dtype(),
                'score':pd.Int64Dtype(),
                'community board':pd.Int64Dtype(),
                'council district':pd.Int64Dtype(),
                'census tract':pd.Int64Dtype(),
                'bin':pd.Int64Dtype(),
                'bbl':pd.Int64Dtype(),}
        
    for col, data_type in data_types.items():
        try:
            data[col] = data[col].astype(data_type)
        except Exception as e:
            print(f"Column {col} has the following error: {e}")
        
    for col in ['inspection date', 'grade date', 'record date']:
        data[col] = pd.to_datetime(data[col]).dt.date
        
    return data
        
        