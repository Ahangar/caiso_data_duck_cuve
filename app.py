from pycaiso.oasis import Node
from datetime import datetime
import pandas as pd
from typing import List, Dict, TypeVar, Union, Optional, Any
from pycaiso.oasis import Atlas, BadDateRangeError, Node, Oasis, SystemDemand, get_lmps
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
# select pnode

import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

import pycaiso.oasis as oasis


def node_lmps_default_df(scope="session"):
    """
    Basic API call to get LMPs in DAM for period 2020-01-1 to 2020-01-02 as df usng Node method
    """

    cj = Node("CAPTJACK_5_N003", )
    df = cj.get_lmps(datetime(2025, 1, 1), datetime(2025, 1, 2), market="RTM")

    time.sleep(5)  # TODO: add rate limiter

    return df

df = node_lmps_default_df()
df = df[df.GROUP ==4].copy()


# Create figure
fig = px.line(df, x='INTERVALSTARTTIME_GMT', y='MW', title='Hourly Trend Comparison')



#Dash app
app = dash.Dash(__name__)
server = app.server  # for deployment



app.layout = html.Div([
    html.H1("Hourly Trend Dashboard"),
    dcc.Graph(figure=fig),
    html.P("Compare today's hourly trend with previous days.")
])

if __name__ == '__main__':
    app.run(debug=True)
