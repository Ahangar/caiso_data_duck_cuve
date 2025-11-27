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

combined_df = pd.read_csv('netdemand_2019_2025.csv')



combined_df['Datetime'] = pd.to_datetime(combined_df['Date'].astype(str) + ' ' + combined_df['Time'], format='%Y-%m-%d %H:%M')

# Extract additional time features
combined_df['Year'] =combined_df['Datetime'].dt.year
combined_df['Month'] = combined_df['Datetime'].dt.month
combined_df['Day of Year'] = combined_df['Datetime'].dt.dayofyear
combined_df['Hour'] = combined_df['Datetime'].dt.hour
combined_df['Time'] = combined_df['Datetime'].dt.time


# Function to add ordinal suffix
def add_ordinal(n):
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

# Extract month name and day with suffix

# Create new column with formatted date
combined_df['Day'] = combined_df['Datetime'].apply(lambda x: f"{x.strftime('%B')} {add_ordinal(x.day)}")


yearly_avg = combined_df.groupby(['Year', 'Time'])['Net demand'].mean().reset_index()
yearly_monthly_avg = combined_df.groupby(['Year','Month', 'Time'])['Net demand'].mean().reset_index()

# --- Controls ---
available_months = [m for m in yearly_monthly_avg["Month"].dropna().unique()]
available_months = sorted([int(m) for m in available_months])
month_names = {i: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][i-1] for i in range(1,13)}


month_choice_num = st.selectbox(
    "Select Month (for Plot 1)",
    options=available_months,
    format_func=lambda x: f"{month_names[int(x)]} ({int(x)})"
)


#--- Plot 1: Value vs Time for a chosen Month, colored by Year ---
f1 = yearly_monthly_avg[yearly_monthly_avg["Month"] == month_choice_num].copy()
f1 = f1.sort_values(["Time", "Year"])

fig1 = px.line(
    f1,
    x="Time",
    y="Net demand",
    color="Year",
    markers=False,
    color_discrete_sequence=px.colors.sequential.algae,
    title=f"Net Demand vs Time — {month_names[int(month_choice_num)]}",
)
fig1.update_layout(xaxis_title="Time of Day", yaxis_title="Net Demand", legend_title="Year")
fig1.update_xaxes(type="category", tickangle=-90)


#st.subheader("Plot 1")
st.plotly_chart(fig1, use_container_width=True)

#--- Plot 2: Value vs Time for a chosen day, colored by Year ---
# --- Controls ---
available_days = [m for m in combined_df["Day"].dropna().unique()]
#available_days = sorted([(m) for m in available_days])
#month_names = {i: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][i-1] for i in range(1,13)}


day_choice_num = st.selectbox(
    "Select Day (for Plot 2)",
    options=available_days#,
    #format_func=lambda x: f"({int(x)})"
)


f2 = combined_df[combined_df["Day"] == day_choice_num].copy()
f2 = f2.sort_values(["Time", "Year"])

fig2 = px.line(
    f2,
    x="Time",
    y="Net demand",
    color="Year",
    markers=False,
    color_discrete_sequence=px.colors.sequential.algae,
    title=f"Net Demand vs Time — " + day_choice_num,
)
fig2.update_layout(xaxis_title="Time of Day", yaxis_title="Net Demand", legend_title="Year")
fig2.update_xaxes(type="category", tickangle=-90)

# --- Layout ---


#st.subheader("Plot 2")
st.plotly_chart(fig2, use_container_width=True)




