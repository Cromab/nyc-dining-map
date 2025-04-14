import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
from support.data_cleaner import read_map_data

st.set_page_config(page_title="EDA", page_icon=':bar_chart:', layout='wide')

st.title("Exploratory Data Analysis (EDA)")

# Load dataset
data = read_map_data(r"data/data.zip", from_nyc_db=False)

# Convert inspection date to datetime
data["inspection date"] = pd.to_datetime(data["inspection date"], errors="coerce")

with st.container():
    st.markdown(
        """
        This page provides an exploratory data analysis of the New York City health inspection dataset from [NYC Open Data](https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j/about_data).
        The full dataset has a total of 27 columns and approximately 278,000 rows containing information about inspections for roughly 30,000 unique restaurants conducted by the NYC Department of Health and Mental Hygiene (DOHMH). It includes details such as:
        - **CAMIS**: Unique ID number for each restaurant.
        - **DBA**: The name of the restaurant (Doing Business As).
        - **Borough**: The borough where the restaurant is located (either Manhattan, Brooklyn, Queens, the Bronx, or Staten Island).
        - **Address**: The building number, street, and zip code of the restaurant.
        - **Cuisine Description**: The type of cuisine served (optional field).
        - **Inspection Date**: The date of the inspection.
        - **Score**: The score given during the inspection. A score of 0 to 13 is an A, 14 to 27 is a B, and greater than 28 is a C. 
        - **Grade**: The grade assigned based on the inspection score.
        - **Action**: The action taken during the inspection (e.g., violation, pass, etc.).
        - **Critical Flag**: Indicates whether the violation was critical or not. Violations flagged as critical are more likely to contribute to food-borne illness.
        - **Coordinates**: The latitude and longitude of the restaurant.
        """
    )


# Preview the dataset
st.subheader("Dataset Preview")
with st.container():
    st.markdown(
        """
Here is a brief preview of the dataset, which has been randomly sampled to show a variety of restaurants and their inspection results, but is otherwise unaltered.
        """
    )
sampled_data = data.sample(n=10, random_state=42)
st.write(sampled_data)


# Overall health score distribution
unique_df = data.sort_values(by=['camis', 'inspection date'], ascending=[True, False])
most_recent = unique_df.drop_duplicates(subset='camis', keep='first')
summary_df = most_recent[['score', 'boro']]
st.subheader("Overall Distribution of Health Scores")
with st.container():
    st.markdown(
        """
Below is a visualization of the distribution of health scores across all unique restaurants in the dataset. 
The distribution is shown with a histogram and a kernel density estimate (KDE) curve to visualize the underlying distribution of the data.
These results reflect only the *most recent* score for a given restaurant, which we think is the most relevant information for you, the user.
Keep in mind, a **lower** score corresponds to **fewer** health code violiations and an overall **healthier** restaurant.
        """
    )
# Plot the distribution of health scores
fig, ax = plt.subplots(figsize=(8, 4))
sns.histplot(pd.to_numeric(summary_df["score"].dropna(), errors='coerce'), bins=30, kde=False, ax=ax)
ax.set_xlabel("Inspection Score")
ax.set_ylabel("Count")
ax.set_title("Overall Distribution of Inspection Scores")
st.pyplot(fig)

average_score = summary_df["score"].mean()
failing = summary_df[summary_df["score"] > 28].shape[0]
high_score = summary_df[summary_df["score"] == 10].shape[0]
st.markdown(
    """
    We see that the distribution is right-skewed, with a long tail of restaurants that have high scores. 
    This suggests that most restaurants are performing well, but there are some outliers with very high scores (unfavorable health ratings).
    """
)
st.write(f"The average most-recent health inspection score for all of NYC is **{average_score:.2f}**, which is on the cusp between a low A and a high B. There are **{failing}** restaurants that currently have a failing score of greater than 28, and **{high_score}** restaurants that currently have a perfect score of 0.")


# Violation severity mapping
with st.container():
    st.markdown(
        """
    The following chart shows the distribution of health inspection scores by violation severity. 
    Violation codes and their classifications were obtained from DOHMH's [Food Service Establishment Inspection Scoring Parameters](https://www.nyc.gov/assets/doh/downloads/pdf/rii/blue-book.pdf).
    A violation code 'Critical' indicates a violation that is more likely to contribute to food-borne illness or injury (*e.g.*, live rats in the facility), and a 'General' violation poses a less direct health risk (*e.g.*, some containers not properly labeled). 
    A violation code of 'None' indicates that there were no violations recorded during the inspection and these instances were not included in this chart.
        """
    )
violation_severity_map = {
    '02A': 'Critical',
    '02B': 'Critical', '02C': 'Critical',
    '02D': 'Critical', '02E': 'Critical',
    '02F': 'Critical', '02G': 'Critical',
    '02H': 'Critical', '02I': 'Critical',
    '02J': 'Critical', '03A': 'Critical',
    '03B': 'Critical', '03C': 'Critical',
    '03D': 'Critical', '03E': 'Critical',
    '03F': 'Critical', '03G': 'Critical',
    '04A': 'Critical', '04B': 'Critical',
    '04C': 'Critical', '04D': 'Critical',
    '04E': 'Critical', '04F': 'Critical',
    '04G': 'Critical', '04H': 'Critical',
    '04I': 'Critical', '04J': 'Critical',
    '04K': 'Critical', '04L': 'Critical',
    '04M': 'Critical', '04N': 'Critical',
    '04O': 'Critical', '05A': 'Critical',
    '05B': 'Critical', '05C': 'Critical',
    '05D': 'Critical', '05E': 'Critical',
    '05F': 'Critical', '05G': 'Critical',
    '05H': 'Critical', '05I': 'Critical',
    '06A': 'Critical', '06B': 'Critical',
    '06C': 'Critical', '06D': 'Critical',
    '06E': 'Critical', '06F': 'Critical',
    '06G': 'Critical', '06H': 'Critical',
    '06I': 'Critical', '07A': 'Critical',
    '08A': 'General', '08B': 'General',
    '08C': 'General', '09A': 'General',
    '09B': 'General', '09C': 'General',
    '10A': 'General', '10B': 'General',
    '10C': 'General', '10D': 'General',
    '10E': 'General', '10G': 'General',
    '10H': 'General', '10I': 'General',
    '10J': 'General', '99B': 'General Other'
}

# Add a severity level column to most_recent
most_recent['violation_severity'] = most_recent['violation code'].map(violation_severity_map)
severity_score_df = most_recent.dropna(subset=['violation_severity', 'score'])

# Plot: Distribution of inspection scores by violation severity
fig, ax = plt.subplots(figsize=(8, 4))
sns.histplot(
    data=severity_score_df,
    x='score',
    hue='violation_severity',
    multiple='stack',
    bins=30,
    palette='Set1'
)
ax.set_title("Distribution of Inspection Scores by Violation Severity")
ax.set_xlabel("Inspection Score")
ax.set_ylabel("Number of Restaurants")
st.pyplot(fig)


# Summary statistics for score by borough
st.subheader("Summary Statistics by Borough")
with st.container():
    st.markdown(
        """
We have provided some basic summary statistics for health inspection scores grouped by borough. These results again reflect only the *most recent* score for a given restaurant.
        """
    )
grouped_stats = summary_df.groupby('boro').agg({"score": ["count", "mean", "median", "min", "max", "std"]})
grouped_stats = grouped_stats.rename(columns={'count': 'Count', 'mean': 'Mean', 'median': 'Median', 'min': 'Min', 'max': 'Max', 'std': 'Std'})
grouped_stats = grouped_stats.dropna()
grouped_stats.columns = grouped_stats.columns.droplevel(0)
grouped_stats = grouped_stats.rename_axis("Borough")
grouped_stats = grouped_stats.round(2)
st.write(grouped_stats)

# Average health score by borough
avg_score_df = (
    most_recent[['boro', 'score']]
    .dropna()
    .groupby('boro', as_index=False)
    .mean(numeric_only=True)
    .rename(columns={'score': 'average_score'})
)
# Plot
fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(data=avg_score_df, x='boro', y='average_score', palette='PuBu', ax=ax)
ax.set_xlabel("Borough")
ax.set_ylabel("Average Health Score")
ax.set_title("Average Most Recent Health Score by Borough")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)


# Correlation analysis 
st.subheader("Correlation Analysis")
with st.container():
    st.markdown(
        """
The correlation matrix below shows the monotonic relationships between different features in the dataset using the Spearman method. 
This helps highlight whether one variable consistently increases (or decreases) as the other does.
Categorical features have been numerically encoded for this analysis.
        """
    )

# Select relevant columns for correlation analysis
correlation_data = most_recent[['score', 'zipcode', 'cuisine description', 'boro']].dropna()
for col in ['cuisine description', 'boro']:
    correlation_data[col] = correlation_data[col].astype('category').cat.codes
correlation_matrix = correlation_data.corr(method='spearman')

# Plot the correlation matrix
fig, ax = plt.subplots(figsize=(5, 5))
sns.heatmap(
    correlation_matrix,
    annot=True,
    fmt=".2f",
    cmap="vlag",
    ax=ax,
    annot_kws={"size": 8},
    cbar_kws={"shrink": 0.8}
)
ax.set_title("Correlation Matrix", fontsize=10)
ax.tick_params(axis='x', labelrotation=45, labelsize=5)
ax.tick_params(axis='y', labelrotation=45, labelsize=5)
st.pyplot(fig)

st.markdown(
    """
    As we can see, most correlation coefficients are close to 0, indicating little to no correlation between variables. 
    This may be a surprising result for some who were expecting to see a relationship between the score and the cuisine description or the borough ("Do certain cuisines have higher scores?").
    This just means that relationships between variables are just more complex than simple linear relationships and that there are likely other (possibly socio-economic) factors at play, which is beyond the scope of this analysis.
    The most significant correlation is between borough and zip code, which are inherently correlated because they both indicate similar physical locations.
    """
)
