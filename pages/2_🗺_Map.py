import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import pydeck as pdk
import json
import streamlit.components.v1 as components
from support.data_cleaner import read_map_data
from support.df_utils import map_dataframe_to_serializable_list
from support.cluster import filter_valid_inspection_data, geospatial_preprocessing, dbscan_clustering
from support.df_utils import get_column_size
from support.maPy import format_cluster_map

# ---- Define Config ---- #
st.set_page_config(page_title="Mapping Out New York City Restaurants", page_icon=':world_map:', layout='wide')

#Use local css
def local_css(file_name):
	with open(file_name) as f:
		st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style/style.css")


# ---- Introduction ---- #
with st.container():
    st.title("Health Clusters in NYC Dining")
    st.write("""
        By leveraging two powerful clustering algorithms, Hierarchical Clustering and Density-Based Spatial Clustering of Applications with Noise (DBSCAN), we aim to uncover patterns in restaurant health based on their health scores, inspections records, and location.
        
        In the first of these interactive maps, we give a searchable index of the restauraunts to inspect historical violations, the concentration of healthy or unhealthy pockets and more. 
        
        In the second, we look at clusters informed by DBSCAN using both a Haversine and Euclidean metric that views average health inspection scores across clusters compounded with cluster sizes. We're gating this for now until you go check out the 📦 Cluster page! Afterwards a second map will appear here!
    """)
    

# ---- Data ---- #
data = read_map_data(r"data/data.zip", from_nyc_db=False) # Change to True in production to avoid need for stored data
      
# Sort by restaurant and inspection date descending
data = data.sort_values(by=['camis', 'inspection date'], ascending=[True, False])

# Keep only the most recent inspection per restaurant
# COMMENT OUT TO RETURN TO ALL VALUES
#data = data.drop_duplicates(subset='camis', keep='first')

# ---- Leaflet Map ---- #
with st.container():
    st.write("---")
    st.subheader("Heatmaps and Hierarchical Clustering")
    st.markdown("""The map displays restaurant locations in NYC, with **hiearchical clustering** markers based on proximity to other restaurants.
                The markers are color-coded based on either the average health inspection score or the most recent (toggleable view), with green indicating better scores and red indicating worse scores.
                The size of each cluster (large circles) represents the number of restaurants within the cluster, and the color represents the average score of its constituent restaurants. 
                You can click on each marker to view detailed information about the restaurant, including its name, inspection date, and any recorded violations.""")
    st.markdown("""The heatmap displays areas with higher and lower average health scores, providing a quick visual representation of regions with better or worse overall hygiene. The gradient on this heatmap ranges from green to red, coinciding with health inspection scores. NYC uses golf rules for these inspection scores, so the lower the better! From this we can see hot spots that update and render as increase zoom levels on our map.""")
    
    map_data = data[(data['latitude'] != 0) & (data['longitude'] != 0)].dropna(subset=['latitude', 'longitude'])
    # Read html file
    with open("templates/test.html", 'r', encoding='utf-8') as file:
        source = file.read()
    # Pass markers data to HTML Template and render
    markers_data = map_dataframe_to_serializable_list(df=map_data[['latitude', 'longitude', 'dba', 'inspection date', 'violation description', 'score']], 
                                                    date_cols=['inspection date'], sort_cols=['inspection date'], 
                                                    fill_na_cols={'violation description':'No violations recorded.', 'score': 0})
    source = source.replace("{{ markers_data|tojson }}", json.dumps(markers_data))
    components.html(source, height=700)
   
# ---- Pydeck Map --- #
with st.container():
    st.write("---")
    st.subheader("DBSCAN in NYC")
    
    # If dataframe exists
    if 'DBSCAN_df' in st.session_state:
        df = st.session_state['DBSCAN_df']
        
        # Radio button
        data_option = st.radio(
            "Choose a Method:",
            ('Euclidean', 'Haversine'),
            index=0 # Default selection
        )
        if data_option == 'Euclidean':
            cluster_df = format_cluster_map(df)
            radius = 'euclidean_cluster_size'
        else:
            cluster_df = format_cluster_map(df, cluster_col='haversine_cluster', size_col='haversine_cluster_size')
            radius = 'haversine_cluster_size'
        
        # Get Dataframes
        euclidean_df_clusters = format_cluster_map(df)
        haversine_df_clusters = format_cluster_map(df, cluster_col='haversine_cluster', size_col='haversine_cluster_size')
        
        # Select color mappings
        selected_colors = st.multiselect(
            "Select score levels to display",
            options=['green', 'yellow', 'red'],
            default=['green', 'yellow', 'red']
        )
        
        # Allow filtering to selected color
        filtered_df = cluster_df[cluster_df['color_group'].isin(selected_colors)]
        
        # Allow checkbox for changing cluster member sizes
        increase_size = st.checkbox("Increase cluster size", value=False)
        size_multiplier = 50 if increase_size else 1
        
        # pyDeck Chart
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position='[longitude, latitude]',
            get_radius=f'{radius} * {size_multiplier}', # Adjust for visual
            get_fill_color='color',
            get_line_color=[0,0,0],
            line_width_min_pixels=1,
            pickable=True,
            auto_highlight=True,
        )
        # view of NYC
        view_state = pdk.ViewState(
            latitude=40.7128,
            longitude=-74.0060,
            zoom=10,
            pitch=0
        )
        # Render map
        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text":"Cluster: {euclidean_cluster}\nScore: {score}\nSize: {euclidean_cluster_size}"} if data_option == 'Euclidean' else {"text":"Cluster: {haversine_cluster}\nScore: {score}\nSize: {haversine_cluster_size}"}
        ))
    else:
        st.markdown("""
                    <div style='text-align: center;'>
                        <span style='color: red; font-size: 24px;'>Check out the 📦 Cluster Page and then return here!</span>
                    </div>
                    """, 
                    unsafe_allow_html=True)
    