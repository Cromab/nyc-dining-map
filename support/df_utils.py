import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt

@st.cache_data
def map_dataframe_to_serializable_list(df: pd.DataFrame, date_cols: list, sort_cols: list, fill_na_cols: dict) -> list:
    """
    Function that cleans data inputs for the map data fed to Leaflet as a serializable list.
    Returns a list to be converted to JSON or other serialization.
    """
    # Trim inspection date to relevant data dates
    if 'inspection date' in df.columns:
        df = df[df['inspection date'] > dt.date(1900, 1, 1)]
        
    # Sort by sort columns
    df = df.sort_values(by=sort_cols, ascending=False)
    
    # Convert date cols to string
    df[date_cols] = df[date_cols].astype(str)
    
    # Fill Columns with custom NA values
    for col, fill in fill_na_cols.items():
        df[col].fillna(fill, inplace=True)
    
    
    return df.values.tolist() 

@st.cache_data
def get_column_size(df, col):
    size = df.groupby(col)[col].transform('size')
    return size