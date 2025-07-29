"""
Persyst Dashboard for displaying spike activity and stage duration data.

To run the dashboard from the terminal with gunicorn, cd to the directory containing the project scripts 
and use the following command:
    gunicorn src.persyst_dashboard:server --bind 0.0.0.0:8050

To run the docker container, use:
    docker build --no-cache -t persyst-dashboards:v1 .
    docker run -it --rm -p 8050:8050 persyst-dashboards:v1

Delete all stopped containers, unused images, unused networks, and unused volumes:
    docker system prune -a --volumes

Kill Process Running on Port 8050:
    sudo lsof -i :8050
    sudo kill -9 <PID>
"""

from pathlib import Path
import os
import pandas as pd
import numpy as np
from .load_data import DataLoader

from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px


module_path = Path(__file__).parent
data_path = module_path.parent / "Stage_Spike_Occurrence_Rate"
#data_path = Path("/Stage_Spike_Occurrence_Rate")
data_loader = DataLoader(data_path=data_path, extension=".csv")
data_loader.get_files_in_folder()
data_df = data_loader.load_data()
# data_df = data_df[data_df["Stage"] != "Wake"]

# Utility function to convert hex color to rgb string
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgb({r},{g},{b})"

STAGES_COLORS_SELECT = {
    "N1": "#FAE163",    # Light gold
    "N2": "#29E8B2",    # Turquoise
    "N3": "#4CA9EE",    # Sky blue
    "REM": "#2F4571",   # Dark blue
    "Wake": "#B93D4E",  # Light red
    "Unknown": "#808080" # Gray
}

STAGES_COLORS = [hex_to_rgb(color) for color in STAGES_COLORS_SELECT.values()]

# Initialize the app - incorporate css
app = Dash()

# App layout
app.layout = [
    html.Div(
        children="Duration of Detected Awareness States",
        style={"border": "2px grey solid"},
    ),
    html.Hr(),
    dcc.RadioItems(
        options=["Spike-Activity", "Duration(min.)"],
        value="Spike-Activity",
        id="controls-and-radio-item",
        style={"margin-left": "0px", "margin-top": "20px"},
    ),
    html.Div(
        children=[
            dcc.Graph(
                figure={},
                id="figure_panel_adults",
                style={"margin-top": "0px", "display": "inline-block"},
            ),
            dcc.Graph(
                figure={},
                id="figure_panel_pediatric",
                style={"margin-top": "0px", "display": "inline-block"},
            ),
        ]
    ),
    dash_table.DataTable(data=data_df.to_dict("records"), page_size=6, id="data_table"),
    dcc.Checklist(
        ["Adult", "Pediatric"],
        ["Adult", "Pediatric"],
        inline=True,
        style={"margin-left": "100px", "margin-top": "0px"},
        id="patient-group-checklist",
    ),
]


@app.callback(
    [
        Output(component_id="data_table", component_property="data"),
        Output(component_id="figure_panel_adults", component_property="figure"),
        Output(component_id="figure_panel_pediatric", component_property="figure"),
    ],
    [
        Input(component_id="controls-and-radio-item", component_property="value"),
        Input(component_id="patient-group-checklist", component_property="value"),
    ],
)
def update_graph(col_chosen, group_chosen):

    plot_df = data_df[data_df["Group"].isin(group_chosen)]
    # print(plot_df["Group"].unique())
    if col_chosen == "Duration(min.)":
        data_colname = "StageDurM"
        figure_adult = px.pie(
            data_df[data_df["Group"] == "Adult"],
            values=data_colname,
            names="Stage",
            title="Adult",
            color="Stage",
        )
        figure_adult.update_traces(
            title=col_chosen,
            textposition="inside",
            textinfo="percent+label",
            textfont_size=10,
            hoverinfo="percent+label",
            marker=dict(colors=STAGES_COLORS, line=dict(color="#000000", width=1)),
        )
        figure_pediatric = px.pie(
            data_df[data_df["Group"] == "Pediatric"],
            values=data_colname,
            names="Stage",
            title="Pediatric",
            color="Stage",
        )
        figure_pediatric.update_traces(
            title=col_chosen,
            textposition="inside",
            textinfo="percent+label",
            textfont_size=10,
            hoverinfo="percent+label",
            marker=dict(colors=STAGES_COLORS, line=dict(color="#000000", width=1)),
        )

    elif col_chosen == "Spike-Activity":
        data_colname = "SpikeOccRate"
        figure_adult = px.box(
            data_df[data_df["Group"] == "Adult"],
            x="Stage",
            y=data_colname,
            color="Stage",
            notched=False,
            points="all",
        )
        figure_adult.update_layout(
            title="Adult", yaxis_title="Spike Activity<br>(avg.absolute amplitude)(μV)"
        )
        figure_pediatric = px.box(
            data_df[data_df["Group"] == "Pediatric"],
            x="Stage",
            y=data_colname,
            color="Stage",
            notched=False,
            points="all",
        )
        figure_pediatric.update_layout(
            title="Pediatric",
            yaxis_title="Spike Activity<br>(avg.absolute amplitude)(μV)",
        )

    data = plot_df.to_dict("records")
    return data, figure_adult, figure_pediatric

server = app.server

# Run the app
if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=8050)
