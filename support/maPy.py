import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk

# Color map for later functions
color_map = {
        'green':[0, 255, 0, 100],
        'yellow': [255, 255, 0, 130],
        'red':[255, 0, 0, 200]
    }

# Functions
def get_color_group(score):
    """
    Gives a color grouping based on health inspection scores
    """
    if score <= 13:
        return 'green'
    elif score <= 27:
        return 'yellow'
    else:
        return 'red'

@st.cache_data
def format_cluster_map(df, cluster_col='euclidean_cluster', size_col='euclidean_cluster_size'):
    """Formats the cluster data so it may be used in a pydeck visual.

    Args:
        df (_type_): dataframe
        cluster_col (str, optional): Name of column containing cluster assignments. Defaults to 'euclidean_cluster'.
        size_col (str, optional): Name of column containing cluster sizes. Defaults to 'euclidean_cluster_size'.
    """
    # Group by cluster column and eliminate blank column
    df = df[df[cluster_col] != -1].groupby(cluster_col).agg({
        'latitude':'median',
        'longitude':'median',
        'score':'mean',
        size_col:'first'
    }).reset_index()
    
    # Assign colorings
    df['color_group'] = df['score'].apply(get_color_group)
    df['color'] = df['color_group'].map(color_map)
    
    return df
    
    


