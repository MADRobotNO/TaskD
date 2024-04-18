import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import dash
from dash import dcc, html, Input, Output
# from geopy.geocoders import Nominatim

df_with_geo = pd.read_csv("Sunshine_in_Asian_cities_with_lat_long.csv")
df_without_geo = df_with_geo.drop(columns=['Latitude', 'Longitude'])

dash_app = dash.Dash(__name__)
app = dash_app.server

# Code that was used to generate Sunshine_in_Asian_cities_with_lat_long.csv file in order to increase performance

# geolocator = Nominatim(user_agent="city_geocoder")

# def geocode_city(city):
#     location = geolocator.geocode(city)
#     if location:
#         return location.latitude, location.longitude
#     else:
#         return None, None
#
#
# df['Latitude'], df['Longitude'] = zip(*df['City'].apply(geocode_city))

scatter_map_default_center = {'lat': 30, 'lon': 80}
scatter_map_default_zoom = 2
scatter_height = 800

dash_app.layout = html.Div([
    html.H1("Sunshine Insights: Exploring Asian Cities", style={'text-align': 'center', 'margin-bottom': '20px'}),
    html.Div([
        html.Div([
            html.Div([
                        html.Label("Select City:"),
                        dcc.Dropdown(
                            id='city-dropdown',
                            options=[{'label': city, 'value': city} for city in df_without_geo['City']],
                            value=df_without_geo['City'].iloc[0],
                            clearable=False
                        ),
                    ], style={'width': '25%', 'display': 'inline-block', 'padding': '20px'}),
            dcc.Graph(id='bar-chart')
        ]),

        html.Div([
            html.Div([
                        html.Label("Select Month:"),
                        dcc.Dropdown(
                            id='month-dropdown',
                            options=[{'label': month, 'value': month} for month in df_without_geo.columns[1:]],
                            value='Jan',
                            clearable=False
                        ),
                    ], style={'width': '25%', 'display': 'inline-block', 'padding': '20px'}),

            html.Div([
                dcc.Graph(id='comparison-chart', style={'width': '50%', 'display': 'inline-block'}),
                dcc.Graph(id='map', style={'width': '50%', 'display': 'inline-block'})
            ]),
        ]),

        html.Div([
            dcc.Graph(id='line-chart')
        ]),

        html.Div([
            dcc.Graph(id='box-plot')
        ]),

        html.Div([
            dcc.Graph(id='heatmap')
        ]),

    ], style={'margin-bottom': '20px', 'border': '1px solid grey'}),
    html.Footer(
            html.Small("By Martin Agnar Dahl - 2024")
            , style={"text-align": "center"})
])


# Define callback to update graphs based on user input
@dash_app.callback(
    [Output('bar-chart', 'figure'),
     Output('box-plot', 'figure'),
     Output('line-chart', 'figure'),
     Output('map', 'figure'),
     Output('heatmap', 'figure'),
     Output('comparison-chart', 'figure')],
    [Input('city-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_graphs(selected_city, selected_month):

    bar_chart = go.Figure(data=[
        go.Bar(x=df_without_geo.columns[1:], y=df_without_geo.loc[df_without_geo['City'] == selected_city].values.flatten()[1:])
    ])
    bar_chart.update_layout(title=f"Average Sunshine Hours in {selected_city}")


    box_plot = go.Figure(data=[
        go.Box(y=df_without_geo[col], name=col) for col in df_without_geo.columns[1:]
    ])
    box_plot.update_layout(title="Distribution of Sunshine Hours Across Cities", height=scatter_height)

    line_chart = go.Figure()
    for city in df_without_geo['City']:
        line_chart.add_trace(go.Scatter(x=df_without_geo.columns[1:], y=df_without_geo.loc[df_without_geo['City'] == city].iloc[0, 1:],
                                        mode='lines+markers', name=city))
    line_chart.update_layout(
        title="Average Sunshine Hours for Each Month Across All Cities",
        yaxis_title="City",
        xaxis_title="Sunshine Hours",
        height=scatter_height
    )

    heatmap = go.Figure(data=go.Heatmap(
        z=df_without_geo.iloc[:, 1:].values,
        x=df_without_geo.columns[1:],
        y=df_without_geo['City'],
        colorscale='Viridis',
    ))
    heatmap.update_layout(title="Heatmap of Sunshine Hours Across Cities and Months", height=scatter_height)

    comparison_chart = px.bar(df_without_geo, y='City', x=selected_month,
                              title=f"Sunshine Hours in {selected_month} Across Cities",
                              labels={'City': 'City', selected_month: 'Sunshine Hours'}, height=scatter_height)

    map_fig = None
    if 'Latitude' in df_with_geo.columns and 'Longitude' in df_with_geo.columns:
        map_fig = px.scatter_geo(df_with_geo, lat='Latitude', lon='Longitude', hover_name='City',
                                 size=selected_month, color=selected_month,
                                 title=f"Sunshine Hours in {selected_month} Across Asian Cities",
                                 projection="mercator", height=scatter_height)
        map_fig.update_geos(center=scatter_map_default_center, projection_scale=scatter_map_default_zoom)

    return bar_chart, box_plot, line_chart, map_fig, heatmap, comparison_chart


if __name__ == '__main__':
    dash_app.run_server(debug=True)
