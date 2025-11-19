#from pycaiso.oasis import Node
from datetime import datetime
import pandas as pd
from typing import List, Dict, TypeVar, Union, Optional, Any
#from pycaiso.oasis import Atlas, BadDateRangeError, Node, Oasis, SystemDemand, get_lmps
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
# select pnode

import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

import streamlit as st

import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

combined_df = pd.read_csv('demand_2019_2025.csv')




combined_df['Datetime'] = pd.to_datetime(combined_df['Date'].astype(str) + ' ' + combined_df['Time'], format='%Y-%m-%d %H:%M')

# Extract additional time features
combined_df['Year'] =combined_df['Datetime'].dt.year
combined_df['Month'] = combined_df['Datetime'].dt.month
combined_df['Day'] = combined_df['Datetime'].dt.day
combined_df['Hour'] = combined_df['Datetime'].dt.hour
combined_df['Time'] = combined_df['Datetime'].dt.time


# Define seasons
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

combined_df['Season'] = combined_df['Month'].apply(get_season)

# Group by Hour and compute average demand for each grouping
monthly_avg = combined_df.groupby(['Month', 'Time'])['Current demand'].mean().reset_index()
yearly_avg = combined_df.groupby(['Year', 'Time'])['Current demand'].mean().reset_index()
yearly_seasonal_avg = combined_df.groupby(['Year','Season', 'Time'])['Current demand'].mean().reset_index()
yearly_month_avg = combined_df.groupby(['Year','Month', 'Time'])['Current demand'].mean().reset_index()


# Group by Hour and compute average demand for each grouping
yearly_monthly_avg = combined_df.groupby(['Year','Month', 'Time'])['Current demand'].mean().reset_index()


yearly_monthly_avg['Month_name'] = (pd.to_datetime(yearly_monthly_avg['Month'].astype(str) + '-01-2000', format='%m-%d-%Y')).dt.strftime('%b')



# --- Controls ---
st.sidebar.header("Filters")
available_months = [m for m in yearly_monthly_avg["Month"].dropna().unique()]
available_months = sorted([int(m) for m in available_months])
month_names = {i: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][i-1] for i in range(1,13)}


month_choice_num = st.sidebar.selectbox(
    "Select Month (for Plot 1)",
    options=available_months,
    format_func=lambda x: f"{month_names[int(x)]} ({int(x)})"
)


years_available = sorted(yearly_monthly_avg["Year"].dropna().unique())

# For Plot 2
year_choice = st.sidebar.selectbox("Select Year (for Plot 2)", options=years_available)


#--- Plot 1: Value vs Time for a chosen Month, colored by Year ---
f1 = yearly_monthly_avg[yearly_monthly_avg["Month"] == month_choice_num].copy()
f1 = f1.sort_values(["Time", "Year"])

fig1 = px.line(
    f1,
    x="Time",
    y="Current demand",
    color="Year",
    markers=False,
    title=f"Value vs Time — {month_names[int(month_choice_num)]} (All Years)",
)
fig1.update_layout(xaxis_title="Time of Day", yaxis_title="Demand", legend_title="Year")
fig1.update_xaxes(type="category", tickangle=-45)



# --- Plot 2: For a selected Year, Value vs Time colored by Month ---
f2 = yearly_monthly_avg[yearly_monthly_avg["Year"] == year_choice].copy()
f2 = f2.sort_values(["Time", "Month"])

fig2 = px.line(
    f2,
    x="Time",
    y="Current demand",
    color="Month",
    title=f"Value vs Time — Year {int(year_choice)} (All Months)",
)
fig2.update_layout(xaxis_title="Time of Day", yaxis_title="Value", legend_title="Month")
fig2.update_xaxes(type="category", tickangle=-45)

# --- Layout ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("Plot 1")
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.subheader("Plot 2")
    st.plotly_chart(fig2, use_container_width=True)

# --- Optional data preview ---
with st.expander("Preview data (first 200 rows)"):
    st.dataframe(yearly_monthly_avg[["Year","Month","Time","Current demand"]].head(200))



