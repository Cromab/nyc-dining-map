import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import pydeck as pdk
from support.cluster import filter_valid_inspection_data, geospatial_preprocessing, dbscan_clustering
from support.df_utils import get_column_size
from support.maPy import format_cluster_map

st.set_page_config(page_title="DBSCAN", page_icon='📦', layout='wide')

#Use local css
def local_css(file_name):
	with open(file_name) as f:
		st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style/style.css")

# ---- Introduction ---- #
with st.container():
    st.title("Health Clusters in NYC Dining")
    st.markdown(
        """
        Whether a restaurant is healthy or unhealthy goes much deeper than just inspection scores. New York City has the highest population density of any American city, with approximately 29,303 per square mile (11,319 per square km). This 50% more dense than San Francisco! 
        
        Given this, consumers should be aware of not just the restaurant they're dining at, but the surrounding area! Knowing whether a particular diner is in a high violation area or whether surrounding eateries are immaculate is important!
        
        To approach this problem, we have opted to use a geospatial algorithm, DBSCAN, to find clusters within NYC. The rationale here is as follows:
        
        1. **We don't have a specific target number of clusters.** DBSCAN will find our clusters based on density.
        2. **There's no assumption of cluster shape.** The shape of our clusters can be complex, non-linear shapes which is super common in spatial data where clusters may not be nice circular shapes.
        3. **Outliers are labeled automatically.** While NYC is very dense, there are still very lonely restaurants (often attached to facilities such as schools) that don't belong to any single cluster. We call this *noise*.
        4. **Our cluster sizes are unlikely to be uniform.** NYC has very dense areas, such as in the more populous boroughs like Manhattan, where we can expect much larger, concentrated clusters. As we go to outlying islands, we'd expect clusters to get smaller.
        """
    )

# ---- Data Pre-Processing ---- #
with st.container():
    st.write("---")
    st.header("Feature Selection")
    st.write("""
        With our clustering, we are most interested in two things: location of our restaurants and their health scores. Thus, we look at our geospatial characteristics, latitude and longitude, and our raw health inspection scores.
        However, this data goes back a fair ways, and in order to more fairly represent restaurants and to see **current** health trends, we also want to look at the most recent data available.
        In order to achieve this we'll look at ONLY the most recent inspection results for each restaurant. Let's see what this data looks like
    """)

    # Pull in display data
    data = filter_valid_inspection_data()
    st.dataframe(
        data=data,
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown(
        "<span style='color:red;'>Recall that better inspection results correlate to lower scores!</span>",
        unsafe_allow_html=True
    )
    
    st.write("---")
    st.header("Understanding Hyperparamters")
    st.markdown("""
        With DBSCAN, there are two extremely important hyperparameters to consider: ε and min_samples. 
        
        Let's consider ε first. This is the max distance between two samples allowed for the two samples to be considered as being neighbors. This IS NOT a bound on the distances of points within a cluster.
        This will be the most important parameter.
        
        The second hyperparameters are our min_samples. As the name implies, this is the minimum number of points required to form a dense region, or rather, a cluster.
        It is built on two primary concepts: Core Points and Directly Reachable Points. A point is a core point if and only if there are min_samples points within ε distance.
        A point that is directly reachable from a core point, i.e. in ε distance to a core point is a Directly Reachable Point. 
        
        From the above, it is clear that the most important hyperparameter is ε. Thus, how we define ε is imperative. We will consinder two distinct views on distance: Euclidean and Haversine.
        To calculate Haversine distance we will need to convert or latitude and longitude to radians, like so. Additionally, we will scale our score and apply a weight to it.
    """)
    
    # Get geospatial preprocessing
    data_radians, eps = geospatial_preprocessing(data)
    st.dataframe(
        data=pd.DataFrame(data_radians, columns=['latitude', 'longitude', 'score']),
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown(f"""
        Normally, using radians for Euclidean distance would be a problem, however when points are extremely close together, difference due to curvature are significantly diminished.
        Thus, we will use the above for both Haversine and Euclidean distance clustering.
    """)
    
# ---- DBSCAN ---- #
with st.container():
    st.write("---")
    st.header("Clustering with DBSCAN")
    st.write("Let's apply our clustering algorithm, defining our min_samples as 4 neighbors (5 including the point itself), and ε corresponding to 1 kilometer distance. What will be the results?")
    
    # Get Haversine Distance and clusters
    haversine_clusters, haversine_cluster_size = dbscan_clustering(data_radians, eps*0.03, min_samples=5, metric='haversine')
    # Get Euclidean Distance and clusters
    euclidean_clusters, euclidean_cluster_size = dbscan_clustering(data_radians, eps*.5, min_samples=5, metric='euclidean')
    
    # Append to dataframe
    df = data.copy()
    df['haversine_cluster'], df['euclidean_cluster'] = haversine_clusters, euclidean_clusters
    
    st.write("How many clusters did we find?")
    
    # Display difference between haversine and euclidean calculation
    col1, col2 = st.columns(2)
    cols = ['dba', 'score']
    with col1:
        st.subheader("Euclidean Clusters")
        st.write(f"Total Clusters: {len(df['euclidean_cluster'].unique())}")
        st.write(f"Average Cluster Size: {len(df)/len(df['euclidean_cluster'].unique())}")
        st.dataframe(
            data=df[cols+ ['euclidean_cluster']],
            hide_index=True,
            use_container_width=True
        )
    with col2:
        st.subheader("Haversine Clusters")
        st.write(f"Total Clusters: {len(df['haversine_cluster'].unique())}")
        st.write(f"Average Cluster Size: {len(df)/len(df['haversine_cluster'].unique())}")
        st.dataframe(
            data=df[cols+ ['haversine_cluster']],
            hide_index=True,
            use_container_width=True
        )
    
    # Display overall clustering results
    st.subheader("Clustering Results")
    st.write("If we include the sizes of clusters than our relevant data looks as follows after running DBSCAN")
    df['euclidean_cluster_size'] = get_column_size(df, 'euclidean_cluster')
    df['haversine_cluster_size'] = get_column_size(df, 'haversine_cluster')
    cols = ['dba', 'latitude', 'longitude', 'score', 'euclidean_cluster', 'euclidean_cluster_size', 'haversine_cluster', 'haversine_cluster_size']
    st.dataframe(
        data=df[cols],
        hide_index=True,
        use_container_width=True
    )
    
# ---- Map ---- #
with st.container():
    st.write("---")
    st.header("Mapping out Clusters of Euclidean vs. Haversine metric")
    
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
    
# ---- Conclusions ---- #
with st.container():
    st.write("""
        We can see from both the Haversine DBSCAN and the Euclidean DBSCAN distance metrics that our largest clusters tend to be in Manhattan. This coincides with our knowledge of how populous this borough is.
        Additionally, when viewing general cluster trends, we can see that our healthy clusters, represented by green, represent a larger proportion of our population.
        This would imply that NYC generally has many healthy restaurants! If you'd like to find some of these (or some that are less healthy), please view the 🗺 Map page!
        On this page exists an interactive map where you can see a hierarchical clustering as well as a heatmap concentrating on these health hotspots, with the added feature of being able to see the historical violations of any restauraunt in NYC!
    """)

st.session_state['DBSCAN_df'] = df

