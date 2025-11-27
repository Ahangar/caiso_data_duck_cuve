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

# Import downloaded files
netdemand = pd.read_csv('netdemand_2019_2025.csv')
fuelsource = pd.read_csv('fuelsource_2019_2025.csv')


netdemand['Datetime'] = pd.to_datetime(netdemand['Date'].astype(str) + ' ' + netdemand['Time'], format='%Y-%m-%d %H:%M')
fuelsource['Datetime'] = pd.to_datetime(fuelsource['Date'].astype(str) + ' ' + fuelsource['Time'], format='%m/%d/%Y %H:%M')

# Extract additional time features
def extract_time_features(df):
    
    df['Year'] =df['Datetime'].dt.year
    df['Month'] = df['Datetime'].dt.month
    df['Hour'] = df['Datetime'].dt.hour
    df['Time'] = df['Datetime'].dt.time


extract_time_features(netdemand)
extract_time_features(fuelsource)


#netdemand['Year'] =netdemand['Datetime'].dt.year
#netdemand['Month'] = netdemand['Datetime'].dt.month
#netdemand['Day of Year'] = netdemand['Datetime'].dt.dayofyear
#netdemand['Hour'] = netdemand['Datetime'].dt.hour
#netdemand['Time'] = netdemand['Datetime'].dt.time


# Function to add ordinal suffix
def add_ordinal(n):
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

# Extract month name and day with suffix

# Create new column with formatted date
netdemand['Day'] = netdemand['Datetime'].apply(lambda x: f"{x.strftime('%B')} {add_ordinal(x.day)}")


#yearly_avg = netdemand.groupby(['Year', 'Time'])['Net demand'].mean().reset_index()
netdemand_yearly_monthly = netdemand.groupby(['Year','Month', 'Time'])['Net demand'].mean().reset_index()
fuelsource_yearly_monthly = fuelsource.groupby(['Year','Month', 'Time'])[['Solar','Wind']].mean().reset_index()
fuelsource_yearly_monthly['Solar_Wind'] = fuelsource_yearly_monthly['Solar'] + fuelsource_yearly_monthly['Wind']



# --- Controls ---
available_months = [m for m in netdemand_yearly_monthly["Month"].dropna().unique()]
available_months = sorted([int(m) for m in available_months])
month_names = {i: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][i-1] for i in range(1,13)}


month_choice_num = st.selectbox(
    "Select Month (for Plot 1)",
    options=available_months,
    format_func=lambda x: f"{month_names[int(x)]} ({int(x)})"
)


#--- Plot 1: Value vs Time for a chosen Month, colored by Year ---
f1 = netdemand_yearly_monthly[netdemand_yearly_monthly["Month"] == month_choice_num].copy()
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
fig1.update_layout(xaxis_title="Time of Day", yaxis_title="MW", legend_title="Year")
fig1.update_xaxes(type="category", tickangle=-90)


#st.subheader("Plot 1")
st.plotly_chart(fig1, use_container_width=True)


#--- Plot 1: Value vs Time for a chosen Month, colored by Year ---
f2 = fuelsource_yearly_monthly[fuelsource_yearly_monthly["Month"] == month_choice_num].copy()
f2 = f2.sort_values(["Time", "Year"])

fig2 = px.line(
    f2,
    x="Time",
    y="Solar_Wind",
    color="Year",
    markers=False,
    color_discrete_sequence=px.colors.sequential.Burg,
    title=f"Solar-Wind vs Time — {month_names[int(month_choice_num)]}",
)
fig2.update_layout(xaxis_title="Time of Day", yaxis_title="MW", legend_title="Year")
fig2.update_xaxes(type="category", tickangle=-90)


#st.subheader("Plot 1")
st.plotly_chart(fig2, use_container_width=True)












