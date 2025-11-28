from datetime import datetime
import pandas as pd
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

import streamlit as st

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")


# # 1- Download Data
# Downloading Historical Data for Net Demand and Fuel Sources.

# In[2]:


def download_caiso_data(start_date, end_date, target='netdemand'):
    #target options are: demand, netdemand, fuelsource
    
    dataframes = []

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y%m%d')
        url = f'https://www.caiso.com/outlook/history/{date_str}/{target}.csv'
        try:
            df = pd.read_csv(url)[:-1]
            df['Date'] = current_date
            dataframes.append(df)
        except Exception as e:
            print(f"Failed to load data for {date_str}: {e}")
        current_date += timedelta(days=1)

    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df
    else:
        print("No data was loaded.")
        return pd.DataFrame()


# In[4]:


#download net demand data
start_date = datetime(2019, 1, 1)
end_date = datetime(2025, 11, 1)


# # Download the netdemand data
# netdemand = download_caiso_data(start_date, end_date, target='netdemand')
# netdemand[['Time','Current demand','Net demand','Date']].to_csv('netdemand_2019_2025.csv', index = False)
# 

# # Download fuelsource data
# fuelsource = download_caiso_data(start_date, end_date, target='fuelsource')
# 
# # Combining Large Hydro and Natural Gas columns into one
# fuelsource.loc[fuelsource['Natural gas'].isna(),
#                'Natural gas']  = fuelsource.loc[fuelsource['Natural gas'].isna(),'Natural Gas']
# 
# 
# fuelsource.loc[fuelsource['Large hydro'].isna(),
#                'Large hydro']  = fuelsource.loc[fuelsource['Large hydro'].isna(),'Large Hydro']
# 
# fuelsource.drop(columns= ['Natural Gas', 'Large Hydro'], inplace= True)
# 
# fuelsource.to_csv('fuelsource_2019_2025.csv', index = False)
# 

# In[35]:


fuelsource = pd.read_csv('fuelsource_2019_2025.csv')
netdemand = pd.read_csv('netdemand_2019_2025.csv')


# # 2- Monthly and Daily Averages

# In[36]:


# Function to add ordinal suffix
def add_ordinal(n):
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

# Extract additional time features
def extract_time_features(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df['Datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'], format='%Y-%m-%d %H:%M')
    df['Year'] =df['Datetime'].dt.year
    df['Month'] = df['Datetime'].dt.month
    df['Hour'] = df['Datetime'].dt.hour
    df['Time'] = df['Datetime'].dt.time
    # Create new column with formatted date
    df['Day'] = df['Datetime'].apply(lambda x: f"{x.strftime('%B')} {add_ordinal(x.day)}")


# In[37]:


extract_time_features(fuelsource)


# In[38]:


extract_time_features(netdemand)


# In[39]:


#Monthly Averages
netdemand_yearly_monthly = netdemand.groupby(['Year','Month', 'Time'])['Net demand'].mean().reset_index()
fuelsource_yearly_monthly = fuelsource.groupby(['Year','Month', 'Time'])[['Solar','Wind','Natural gas']].mean().reset_index()
fuelsource_yearly_monthly['Solar_Wind'] = fuelsource_yearly_monthly['Solar'] + fuelsource_yearly_monthly['Wind']


# # 3- Plots

# In[40]:

st.markdown("# Net Load")
st.markdown("With the growing penetration of solar photovoltaic (PV) power in many utility grid systems, operating conditions increasingly depend on controllable generation rather than raw demand. Traditional power plants - such as gas and coal - can adjust their output relatively quickly, but solar and wind resources cannot be turned on or off at will. This introduces new challenges for grid operators.")

netdemand.tail(1)


# In[64]:


# Plot the April Changes
#--- Plot 1: Value vs Time for a chosen Month, colored by Year ---
# --- Controls ---
date_choice = st.date_input("Select a date",
                    min_value=start_date,
                    max_value= end_date)
fig1 = px.line(
    netdemand[netdemand["Date"] == pd.to_datetime(date_choice)].copy(),
    x="Time",
    y="Net demand",
    color="Date",
    markers=False,
    color_discrete_sequence=px.colors.sequential.algae,
    title=f"Net Demand vs Time — April 4th 2025",
)
fig1.update_layout(xaxis_title="Time of Day", yaxis_title="MW", legend_title="Year")
fig1.update_xaxes(type="category", tickangle=-70)

st.plotly_chart(fig1)
#fig1.show()


# In[63]:


# Plot Different sources compared to each other

cols = ['Solar', 'Wind','Batteries', 'Small hydro', 'Large hydro','Geothermal', 'Biomass', 'Biogas',
        'Coal', 'Nuclear', 'Natural gas' ,  'Imports', 'Other']

# Aggregate by Year
fuelsource_monthly = fuelsource[fuelsource.Date<datetime(2025, 11, 1)].groupby(['Year', 
                                        'Month'])[cols].sum().reset_index().sort_values(['Year', 'Month'])


# Build a proper Date column for the x-axis (first day of each month)
fuelsource_monthly['Date'] = pd.to_datetime(dict(year=fuelsource_monthly['Year'], month=fuelsource_monthly['Month'], day=1))

# Reshape for Plotly
long_df = fuelsource_monthly.melt(id_vars='Date', value_vars=cols,
                      var_name='Source', value_name='Generation')

# Create stacked area chart
fig2 = px.area(long_df, x='Date', y='Generation', color='Source', 
              color_discrete_sequence=px.colors.qualitative.Light24,
              title='Monthly Electricity Generation by Source',
              labels={'Generation': 'MW', 'Year': 'Year'})

st.plotly_chart(fig2)
#fig.show()


# In[45]:


# --- Controls ---
available_months = [m for m in netdemand_yearly_monthly["Month"].dropna().unique()]
available_months = sorted([int(m) for m in available_months])
month_names = {i: ["January","February","March","April",
                   "May","June","July","August","September",
                   "October","November","December"][i-1] for i in range(1,13)}


month_choice_num = st.selectbox(
    "Select Month",
    options=available_months,
    format_func=lambda x: f"{month_names[int(x)]} ({int(x)})"
)


#--- Plot 2: Net-demand vs Time for a chosen Month, colored by Year ---

fig3 = px.line(
    netdemand_yearly_monthly[netdemand_yearly_monthly["Month"] == month_choice_num].copy(),
    x="Time",
    y="Net demand",
    color="Year",
    markers=False,
    color_discrete_sequence=px.colors.sequential.algae,
    title=f"Net Demand vs Time — {month_names[int(month_choice_num)]}",
)
fig3.update_layout(xaxis_title="Time of Day", yaxis_title="MW", legend_title="Year")
fig3.update_xaxes(type="category", tickangle=-70)

st.plotly_chart(fig3)

#fig3.show()




