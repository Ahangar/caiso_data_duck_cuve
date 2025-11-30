from datetime import datetime
import pandas as pd
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st
import warnings
warnings.filterwarnings("ignore")

# # 1- Download Data from CAISO ----------------------------------

# Downloading Historical Data for Net Demand and Fuel Sources
#function to download CAISO data
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

start_date = datetime(2019, 1, 1) #start date for download
end_date = datetime(2025, 10, 31)  #end date for download

#-----Download the netdemand and fuelsource data for California from CAISO:start- comment out if already downloaded
#netdemand = download_caiso_data(start_date, end_date, target='netdemand') #download netdemand
#netdemand[['Time','Current demand','Net demand','Date']].to_csv('netdemand_2019_2025.csv', index = False) #save as csv
#fuelsource = download_caiso_data(start_date, end_date, target='fuelsource') #download fuelsource
# Combining Large Hydro and Natural Gas columns into one
#fuelsource.loc[fuelsource['Natural gas'].isna(),
 #              'Natural gas']  = fuelsource.loc[fuelsource['Natural gas'].isna(),'Natural Gas']
#fuelsource.loc[fuelsource['Large hydro'].isna(),
 #              'Large hydro']  = fuelsource.loc[fuelsource['Large hydro'].isna(),'Large Hydro']
#fuelsource.drop(columns= ['Natural Gas', 'Large Hydro'], inplace= True)
#fuelsource.to_csv('fuelsource_2019_2025.csv', index = False) #save as csv
#-----Download the netdemand and fuelsource data: end

#Read downloaded files if available
fuelsource = pd.read_csv('fuelsource_2019_2025.csv')
netdemand = pd.read_csv('netdemand_2019_2025.csv')

# # 2- Monthly and Daily Averages---------------------------

# Function to add ordinal date
# Extract additional time features
def extract_time_features(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df['Datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'], format='%Y-%m-%d %H:%M')
    df['Year'] =df['Datetime'].dt.year
    df['Month'] = df['Datetime'].dt.month
    df['Hour'] = df['Datetime'].dt.hour
    df['Time'] = df['Datetime'].dt.time

extract_time_features(fuelsource)
extract_time_features(netdemand)

#Monthly Averages
netdemand_yearly_monthly = netdemand.groupby(['Year','Month', 'Time'])['Net demand'].mean().reset_index()
fuelsource_yearly_monthly = fuelsource.groupby(['Year','Month', 'Time'])[['Solar','Wind','Natural gas']].mean().reset_index()
fuelsource['Solar_Wind'] = fuelsource['Solar'] + fuelsource['Wind']

# # 3- Dashboard and Plots-------------------------------------------------------------------

st.markdown("""
# What's with the&nbsp;Duck?!
## How Solar Generation Reshaped the Net Load&nbsp;Curve
""", unsafe_allow_html=True)

st.image('image_intro.png')

st.markdown("""

## Why the Duck Curve?

The "Duck Curve" is a graph that shows how solar power changes electricity demand throughout the day, creating a shape that looks like a duck.

As renewable energy sources, especially solar power, grow in many utility grid systems, operating conditions increasingly depend on controllable generation rather than raw demand. Traditional power plants - such as gas and coal - can adjust their output relatively quickly, but solar and wind resources cannot be turned on or off at will. This introduces new challenges for grid operators.

Electricity demand typically ramps up in the morning as people go to work and businesses open. During midday, when solar generation is high, the system requires significantly less power from conventional sources. What matters most is the total demand minus the output from variable renewable resources (solar and wind), which is called the "Net Load". In other words, net load equals the forecasted demand minus expected generation from solar and wind.

At night, while the demand and solar generation are both low, net load remains relatively stable. Starting the day, the demand increases and the net load increases too. In regions with high solar penetration - such as California - the net load dips sharply in the middle of the day due to abundant solar production. California Independent System Operator (CAISO) popularized the term "Duck Curve" because the midday dip makes the graph look like a duck [1].
""", unsafe_allow_html=True)

#--- Figure 1: Net Demand vs Time for a chosen day as well as solar+wind generation
date_choice = st.date_input("Select a date",
                    min_value=start_date,
                    max_value= end_date)

netdemand_date = netdemand[netdemand["Date"] == pd.to_datetime(date_choice)].copy()
#plot net demand (duck curve)
fig1 = px.line(
    netdemand_date,
    x="Time",
    y="Net demand",
    color=px.Constant("Net Demand"),
    markers=False,
    #color_discrete_sequence=px.colors.sequential.algae,
    title="The Duck Curve (Net Demand) and Solar and Wind Generation for Selected Date",
)

fig1.update_traces(line=dict(color="green"))
fig1.update_layout(xaxis_title="Time of Day", yaxis_title="MW", legend_title="Legend")
fig1.update_xaxes(type="category", tickangle=-70)

# Overlay from fuelsource (Solar_Wind vs Time)
fuelsource_date = fuelsource[fuelsource["Date"] == pd.to_datetime(date_choice)].copy()

fig1.add_scatter(
    x=fuelsource_date["Time"],
    y=fuelsource_date["Solar_Wind"],
    mode="lines",
    name="Solar + Wind",
    line=dict(color="red", width=2, dash="dot")  # Customize style
)

st.plotly_chart(fig1)
#fig1.show()

st.markdown("""

The effects of the duck curve are most pronounced during springtime in California, when sunny conditions coincide with mild temperatures. During these periods, electricity demand is low because heating and cooling systems are rarely used, yet solar generation remains high - creating steep ramps in net load later in the day.

---

## Challenges

High solar adoption - and the resulting larger belly in the net load curve - has introduced significant challenges for system operators. When the sun sets, solar generation rapidly declines, causing the net load to rise sharply. This creates a need for additional flexibility and fast ramp-up of conventional generation in the evening. Such steep ramps can lead to increased wear on generation units and reduced efficiency, particularly for coal-fired thermal plants [2].

Another challenge occurs during extreme duck curve conditions when renewable production exceeds demand in the afternoon. This surplus can lead to negative net load and sometimes even negative electricity prices, meaning California sometimes pays other states to absorb excess power [3].

These challenges can be mitigated through accurate solar generation forecasting, increased energy storage capacity, or enhanced system flexibility and demand response programs [4]

---

## Changes of the Duck Curve

In 2024, solar energy (utility and smaller scale) supplied about 32% of California's total electricity net generation [5]. The plot below illustrates how electricity generation has evolved in California between 2019 and 2025. As the solar generation has been increasing, the natural gas and import portion of electricity sources have been decreases.
""", unsafe_allow_html=True)

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
              title='Monthly Electricity Generation by Source in California (data from CAISO)',
              labels={'Generation': 'MW', 'Year': 'Year'})

st.plotly_chart(fig2)
#fig2.show()

st.markdown("""
With rising solar and wind generation, the duck curve has become increasingly pronounced. Here, I visualize these changes in California using data from CAISO. Notice how the net-load curve drops lower during midday each month as more solar capacity is added to the grid. During the spring months of 2025, the average net demand curve becomes negative in the afternoon.
""", unsafe_allow_html=True)

# plot historical monthly duck curve for different months 
# --- Controls ---
available_months = [m for m in netdemand_yearly_monthly["Month"].dropna().unique()]
available_months = sorted([int(m) for m in available_months])
month_names = {i: ["January","February","March","April",
                   "May","June","July","August","September",
                   "October","November","December"][i-1] for i in range(1,13)}

month_choice_num = st.selectbox(
    "Select Month",
    options=available_months,
    format_func=lambda x: f"{month_names[int(x)]}"
)


# Net-demand vs Time for a chosen Month, colored by Year ---
fig3 = px.line(
    netdemand_yearly_monthly[netdemand_yearly_monthly["Month"] == month_choice_num].copy(),
    x="Time",
    y="Net demand",
    color="Year",
    markers=False,
    color_discrete_sequence=px.colors.sequential.algae,
    title=f"Average Net Demand vs Time for {month_names[int(month_choice_num)]}",
)
fig3.update_layout(xaxis_title="Time of Day", yaxis_title="MW", legend_title="Year")
fig3.update_xaxes(type="category", tickangle=-70)

st.plotly_chart(fig3)

#fig3.show()

st.markdown("""
### Future of the Duck
In many places like California, solar and wind are the cheapest of power sources [6]. The growing solar penetration reshapes the grid and the net-load curve, with its impact increasing over time. The Duck Curve will keep deepening, with negative net loads becoming common. Ultimately, the deepening Duck Curve is a clear indicator of the energy transition ahead, where adaptability and innovation will define the success of a renewable-powered grid.

---

For better experience and full interactivity, check out this article as a Streamlit dashboard here: https://whats-with-the-duck.streamlit.app/

Github code is available here: https://github.com/Ahangar/caiso_data_duck_cuve

---

### Reference
[1] California Independent System Operator. (2016). Flexible resources help renewables: Fast facts. Retrieved from https://www.caiso.com/Documents/FlexibleResourcesHelpRenewables_FastFacts.pdf  
[2] Bird, L., Milligan, M., &amp; Lew, D. (2013). Integrating variable renewable energy: Challenges and solutions (Technical Report NREL/TP-6A20–60451). National Renewable Energy Laboratory. Retrieved from https://docs.nrel.gov/docs/fy13osti/60451.pdf  
[3] Bhandari, D. (2025, April 15). Negative prices in CAISO: What PPA buyers and renewable developers need to know. Renewable Energy World. Retrieved from https://www.renewableenergyworld.com/solar/negative-prices-in-caiso-what-ppa-buyers-and-renewable-developers-need-to-know/  
[4] U.S. Energy Information Administration. (2023, June 21). As solar capacity grows, duck curves are getting deeper in California. Today in Energy. Retrieved from https://www.eia.gov/todayinenergy/detail.php?id=56880  
[5] U.S. Energy Information Administration. (2025, June 20). California: State energy profile analysis. Retrieved from https://www.eia.gov/state/analysis.php?sid=CA  
[6] Plumer, B. (2025, March 17). A Trump overhaul of the Energy Dept. breaks up clean energy offices. The New York Times. Retrieved from https://www.nytimes.com/2025/03/17/climate/renewable-energy-trump-electricity.html  
""", unsafe_allow_html=True)






