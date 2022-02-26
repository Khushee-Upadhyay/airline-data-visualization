import plotly.graph_objects as go
from dash import Dash, html, dcc, ALL, MATCH
import plotly.express as px 
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import json
import os
#from preprocessing import generate_airport_data, generate_route_data, generate_total_flights_data, generate_country_level_data, generate_route_data_with_coordinates

#Starting Pre-Processing
#print("STARTING PRE-PROCESSING")
#generate_airport_data()
#generate_route_data()
#generate_total_flights_data()
#generate_country_level_data()
#generate_route_data_with_coordinates()
#print("FINISHED PRE-PROCESSING")

#Data
path = os.getcwd()
relpath = path+"/data/"
route_df = pd.read_csv(relpath+"routes_world_data_with_coordinates.csv")   #Function generated
total_flights_df = pd.read_csv(relpath+"total_flights_with_coordinates_with_scale.csv")    #Function generated
country_level_df = pd.read_csv(relpath+"Country level flight data.csv")    #Function generated
airport_df = pd.read_csv(relpath+"airports_with_country_names.csv")        #Function generated

countries = total_flights_df["country_name"].unique()
countries.sort()
countries = np.insert(countries, 0, "Select")


df = total_flights_df.groupby(["country_name", "country_code"])
country_code_dict = {key:value for key,value in df.first().index.to_list()}


#Default Graph variables

default_country_key = "Afghanistan"
clicked_labels = []
last_time_refreshed_btn_clicked=-1
details_trace_info = []

def generate_country_level_bar_map(array_selected_countries=[]):
    global country_level_df
    country_level_df.sort_values(by=['Total flights'],ascending=True, inplace=True)
    country_level_df_new = country_level_df[country_level_df['Country'].isin(array_selected_countries)]
    width = []
    height = 0
    
    if(country_level_df_new.shape[0]==0):
        width=width=[0.8]*country_level_df.shape[0]
        height=15*country_level_df.shape[0]
        country_level_df_new = country_level_df
    else:
        width=[0.6]*country_level_df_new.shape[0]
        height=60*country_level_df_new.shape[0]
        
        
    country_bar_map = go.Figure(data=[go.Bar(x=country_level_df_new['Total flights'],
                                                y=country_level_df_new["Country"], orientation='h',
                                                width=width)]
                        )
    country_bar_map.update_layout( margin={"r":20,"t":20,"l":20,"b":20},height=height,   paper_bgcolor='rgb(128,128,128)',
                                      uniformtext_minsize=12, uniformtext_mode='hide', font=dict( color="whitesmoke" ))
        
    return country_bar_map

def generate_airport_level_bar_map(array_selected_airports=[]):
    global total_flights_df
    total_flights_df.sort_values(by=['Total number of flights'], ascending=True, inplace=True)
    total_flights_df_new = total_flights_df[total_flights_df["Airport name"].isin(array_selected_airports)]
    width = []
    height = 0
    
    if(total_flights_df_new.shape[0]==0):
        width=[0.8]*total_flights_df.shape[0]
        height=15*total_flights_df.shape[0]
        total_flights_df_new = total_flights_df
       
    else:
        width=[0.6]*total_flights_df_new.shape[0]
        height=60*total_flights_df_new.shape[0]
      
    airport_bar_map = go.Figure(data=[go.Bar(x=total_flights_df_new['Total number of flights'],
                                                y=total_flights_df_new["Airport name"], orientation='h',
                                                width=width)]
                        )
    airport_bar_map.update_layout( margin={"r":20,"t":20,"l":20,"b":20}, height=height, paper_bgcolor='rgb(128,128,128)',
                                     uniformtext_minsize=12, uniformtext_mode='hide', font=dict( color="whitesmoke" ))
    return airport_bar_map

#Graph Generating functions

def pre_process_temp_route_data(temp_route_df):
    for i in range(temp_route_df.shape[0]):
        
        try:
            print("Iteration: "+str(i))
            airport_code = temp_route_df["Source"].iloc[i]
            print("Airport code: "+airport_code)
            temp_route_df["Source Airport Name"].iloc[i] = airport_df[airport_df["code"]==airport_code]['Airport name'].iloc[0]+" ("+airport_code+")"
            airport_code = temp_route_df["Destination"].iloc[i]
            print("Destination: "+airport_code)
            temp_route_df["Destination Airport Name"].iloc[i] = airport_df[airport_df["code"]==airport_code]['Airport name'].iloc[0]+" ("+airport_code+")"
        except:
            print("Iteration "+str(i))
            print("\n\nError Error Error Error Error Error\n\n")

    invalid_data = temp_route_df[(temp_route_df["Source Airport Name"]=="") | (temp_route_df["Destination Airport Name"]=="")]
    temp_route_df.drop(invalid_data.index, inplace=True)
    return temp_route_df

def generate_country_level_map():
    fig = px.scatter_mapbox(country_level_df, lat="Latitude", lon="Longitude", hover_name="Country",
                       hover_data=["Total flights"], color="Total flights", 
                        size=country_level_df["scale"], color_continuous_scale=px.colors.sequential.OrRd,
                        labels={"Total flights": "Total<br>Flights"},                        
                        size_max=50, height=500, zoom=1, width=1200)
    fig.update_layout(mapbox_style="carto-darkmatter", 
#                           mapbox_layers=[
#                               {
#                                   "below": 'traces',
#                                   "sourcetype": "raster",
#                                   "sourceattribution": "United States Geological Survey",
#                                   "source": [
#                 "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
#                                             ]
#                              }                          ]
                     )
    fig.update_layout(margin={"r":20,"t":20,"l":20,"b":20},  paper_bgcolor='rgb(38,70,109)', font=dict( color="whitesmoke" )
                     )
    
    return fig

    


def generate_airport_level_map():
    airport_map = px.scatter_mapbox(total_flights_df, lat="coordinates.lat", lon="coordinates.lon", 
                                    hover_name="Airport name",
                       hover_data=["Total number of flights"], color="Total number of flights", 
                        size=total_flights_df["scale"], color_continuous_scale=px.colors.sequential.OrRd,
                        labels={"Total number of flights": "Total<br>Flights"},                        
                        size_max=50, height=500, zoom=1, width=1200)
    airport_map.update_layout(mapbox_style="carto-darkmatter", 
#                           mapbox_layers=[
#                               {
#                                   "below": 'traces',
#                                   "sourcetype": "raster",
#                                   "sourceattribution": "United States Geological Survey",
#                                   "source": [
#                 "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
#                                             ]
#                              }                          ], 
                              margin={"r":20,"t":20,"l":20,"b":20},  
                               paper_bgcolor='rgb(38,70,109)', font=dict( color="whitesmoke" )
                             )
    return airport_map


    

def generate_flight_level_map(dropdown_index,country=default_country_key):
    print("Country: "+default_country_key)
    code_value = country_code_dict[country]
    print("Country Code: "+code_value)
    temp_df = total_flights_df[total_flights_df["country_code"]==code_value]
    
    list_of_airport_from_a_country = total_flights_df[total_flights_df["country_code"]==code_value]["code"]
    temp_route_df = route_df[(route_df["Source"].isin(list_of_airport_from_a_country.values)) | 
                             (route_df["Destination"].isin(list_of_airport_from_a_country.values)) ]
    temp_route_df['Source Airport Name'] = ''
    temp_route_df['Destination Airport Name'] = ''
    
    temp_route_df = pre_process_temp_route_data(temp_route_df)
    temp_route_df.to_csv(relpath+"routes_world_data_with_coordinates_with_airport_names.csv", index=False)
    all_latitude_coordinates = temp_route_df["source_lat"].append(temp_route_df["dest_lat"])
    all_longitude_coordinates = temp_route_df["source_lon"].append(temp_route_df["dest_lon"])
    all_airport_names = temp_route_df["Source Airport Name"].append(temp_route_df["Destination Airport Name"])
    
    list_of_trace_names = [ "From "+src+" to "+dest for src, dest in zip(temp_route_df.Source, temp_route_df.Destination)]
    temp_route_df["Trace_name"] = list_of_trace_names
    temp_route_df.to_csv(relpath+"routes_world_data_with_coordinates_with_airport_names_with_trace.csv", index=False)

    print(all_airport_names)
    
    flight_data = pd.DataFrame(list(zip(all_latitude_coordinates, all_longitude_coordinates, all_airport_names)),
                              columns=["LAT", "LON", "TEXT"])
    print(flight_data["TEXT"].iloc[0])
    
    flight_map =  go.Figure()
    flight_map.add_trace(go.Scattergeo(
                lat = flight_data['LAT'],
                lon = flight_data['LON'],
                text = flight_data['TEXT'],
                mode = 'markers+text',
                textfont={'color': 'rgb(199, 0, 57)'},
                marker = dict(
                    size = 5,
                    color = 'rgb(255, 0, 0)',
                )))
    

    print("Adding traces now")
    print("temp_route_df.shape[0]")
    print(temp_route_df.shape[0])

    for i in range(temp_route_df.shape[0]):
        print("Iteration")
        print(i)
        if(dropdown_index==None or i!=dropdown_index):
            flight_map.add_trace(
                    go.Scattergeo(
                        lon = [temp_route_df["source_lon"].iloc[i], temp_route_df["dest_lon"].iloc[i]],
                        lat = [temp_route_df["source_lat"].iloc[i], temp_route_df["dest_lat"].iloc[i]],
                        mode = 'lines+text',
                        line = dict(width = 0.5,color = 'blue'),
                        name=temp_route_df["Trace_name"].iloc[i]
                    )
                )
        else:
             flight_map.add_trace(
                    go.Scattergeo(
                        lon = [temp_route_df["source_lon"].iloc[i], temp_route_df["dest_lon"].iloc[i]],
                        lat = [temp_route_df["source_lat"].iloc[i], temp_route_df["dest_lat"].iloc[i]],
                        mode = 'lines+text',
                        line = dict(width = 0.5,color = 'green'),
                        name=temp_route_df["Trace_name"].iloc[i]
                    )
                )
    
    flight_map.update_traces(
        hoverlabel={"namelength": -1}
    )

    flight_map.update_layout(
        showlegend = False,
        margin=dict(l=20, r=20, t=20, b=20),
    
        geo = dict(
            projection_type = 'natural earth',
            showland = True,
            bgcolor='rgb(25, 25, 25)',          
            landcolor = 'rgb(0, 0, 0)',
            center=dict(lon=flight_data['LON'].iloc[0], lat=flight_data['LAT'].iloc[0]),
            showcountries=True, countrycolor="rgb(25, 25, 25)",
            
        ),
        height=500, width=1200,
          paper_bgcolor='rgb(38,70,109)' ##26466D
    )
    return flight_map, temp_route_df
    


#APP
app = Dash(__name__)


app.layout = html.Div(children=[
    
    #dcc.Store(id='clickDataInfo'),
       
    html.H1("Airlines Data Visualization", style={'text-align': 'center', 'color':'white'}),
    
    #html parent div component
    html.Div(children=[
            
        #Airport and Country level chart

        html.Div( children=[
                        
                        html.Div( children=[
                            
                                    dcc.Dropdown(
                                             id="level",
                                             options=[
                                                 {"label": "Country level", "value": "country"},
                                                 {"label": "Airport level", "value": "airport"}
                                                 ],
                                             multi=False,
                                             value="country",
                                             style={'width': "50%", "margin": "8px"} )

                                ]),
                        
                       html.Div(id='airport_output_container', children=[], style={"margin": "20px", "color": "white"}),
                       html.Br(),
                       dcc.Graph(id='airport_map', figure={})
                      
                       ],
                  
             style={'box-shadow': '10px 10px 16px','border-left': '1px solid black','border-top': '1px solid black','border-bottom': '1px solid black',#'border-color': 'black', 'border-style': 'solid', 
                    'grid-column-start': '1', 'grid-column-end': '2'}
            ),
        
        #Bar chart for number of flights per airline/country
        html.Div( children=[

                           html.Div(id='airport_output_bar_container', children=[], style={"margin": "5px", "color": "white"}),
                           html.Br(),
                           html.Button('Refresh', id='refresh_btn', n_clicks=0, 
                                       style={'width': "30%", "margin": "10px"}),
                           html.Br(),
                           dcc.Graph(id='airport_bar_map', figure={})],

                 style={"background-color":"#26466D", 'padding':"5px", #'border-color': 'black', 'border-style': 'solid', 
                       'overflow-inline':'scroll'}
                )],
             
             
        #Style of parent element
         style={'height':700, 'padding':'10px', #'border': '1px solid black' ,
                'display': 'grid', 'grid-template-columns': 'auto auto auto auto', 'grid-gap': '20px', 'grid-template-rows': '700px' }
             
             
             
             
    ),
    
 
    #Parent number 2 for Airline routes
   html.Div(
       children=[

                    html.Div(children=[ 

                                        html.Div( children=[


                                                     dcc.Dropdown(
                                                         id="select_country",
                                                         options=[{'label': x, 'value': x} for x in countries],
                                                         multi=False,
                                                         value="Select",
                                                         style={'width': "50%", "margin": "10px"}
                                                         )

                                                ]),

                                       html.Div(id='flight_output_container', children=[], style={"margin": "20px", 'color':"white"}),
                                       html.Br(),
                                       dcc.Graph(id='flight_map', figure={})



                                      ],

                           style={'box-shadow': '10px 10px 16px','border-left': '1px solid black','border-top': '1px solid black','border-bottom': '1px solid black',#'border-color': 'black', 'border-style': 'solid', 
                    'grid-column-start': '1', 'grid-column-end': '2'}
                             ),
                     
#                     html.Div(id="clickDataDiv", children=[],  style={'border-color': 'black', 'border-style': 'solid', 
#                     'grid-column-start': '1', 'grid-column-end': '2'}),

                    html.Div(id="collapsible_div", children=[
                        
#                             html.Details(id="collapsible",
#                                                     children=[
#                                                         html.Summary("Collapsible Title"),
#                                                         html.Div(id="collapsible_text",children=[])
#                                                     ],
#                                                     style={'border-color': 'black', 'border-style': 'solid',
#                                                           "margin": "20px", "padding":"20px"}
#                                                     )
                    ], style={"background-color" : "#26466D", #'border-color': 'black', 'border-style': 'solid', 
				'overflow-inline':'scroll', "margin": "20px", "padding":"20px"}
                    )

       ],
       
        #Style of parent element
         style={'height':700, 'padding':'10px', #'border': '1px solid black' ,
                'display': 'grid', 'grid-template-columns': 'auto auto auto auto', 'grid-gap': '5px' , 'grid-template-rows': '700px'}
   )  
    

], 
	#Style of main div
	style={'background-color': '#344152'}
)


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
#Graph 1
@app.callback(
    [Output(component_id='airport_output_container', component_property='children'),
     Output(component_id='airport_map', component_property='figure')],
    [Input(component_id='level', component_property='value')]
)
def update_graph(level_selected):
    print("Division 1 map for "+level_selected)
    
    container = "Level : {}".format(level_selected)
   
    if(level_selected=="airport"):
        fig = generate_airport_level_map()
        
    elif(level_selected=="country"):
        fig = generate_country_level_map()

    return container, fig
    
#Graph 2
@app.callback(
    [Output(component_id='airport_output_bar_container', component_property='children'),
     Output(component_id='airport_bar_map', component_property='figure')],
    [Input(component_id='level', component_property='value'),
     Input(component_id='airport_map', component_property='clickData'),
     Input(component_id='refresh_btn', component_property='n_clicks_timestamp')]
)
def update_graph(level_selected, clickData, n_clicks_timestamp):
    global clicked_labels
    global last_time_refreshed_btn_clicked
    print("Division 1 map for "+level_selected)
    container = "Level : {}".format(level_selected)
			#+" Button: {}".format(n_clicks_timestamp)
    
    if(clickData==None or (last_time_refreshed_btn_clicked!=-1 and n_clicks_timestamp!=last_time_refreshed_btn_clicked)):
        last_time_refreshed_btn_clicked = n_clicks_timestamp
        clicked_labels = []
        print("No clickdata is received yet")
        if(level_selected=="airport"):
            fig = generate_airport_level_bar_map()
        elif(level_selected=="country"):
            fig = generate_country_level_bar_map()

        
    else:
        print("Hovertext {}".format(clickData["points"][0]["hovertext"]))
        clicked_labels.append(clickData["points"][0]["hovertext"])
        if(level_selected=="airport"):
            fig = generate_airport_level_bar_map(clicked_labels)
        elif(level_selected=="country"):
            fig = generate_country_level_bar_map(clicked_labels)

      
   
   
    return container, fig



#Graph 3

@app.callback(
    [Output(component_id='flight_output_container', component_property='children'),
     Output(component_id='flight_map', component_property='figure'),
     Output(component_id='collapsible_div', component_property='children')],
    [Input(component_id='select_country', component_property='value')]
#      Input(component_id='clickDataInfo', component_property='data')]
)
def update_graph(country_selected):
    global details_trace_info
    details_trace_info = []
    print("Flight map for "+country_selected)
    
    container = "Country : {}".format(country_selected)
   
    if(country_selected=="Select"):
        container = "Country : {}".format(default_country_key)
        fig, route_dataframe = generate_flight_level_map(None)
    else:
        fig, route_dataframe = generate_flight_level_map(None, country_selected)
        
    details_list = []
    for i in range(len(route_dataframe)):
        summary = route_dataframe["Trace_name"].iloc[i]
        details_ele = html.Details(id={"type": "collapsible", "index": i},
                                                    children=[
                                                        html.Summary(summary),
                                                        html.Div(id={"type": "collapsible_text", "index": i},children=[])
                                                    ],
                                                    n_clicks=0,
                                                      style={#'border-color': 'black', 'border-style': 'solid',
                                                          "margin": "20px", "padding":"20px", "color": "white", "background-color":"grey"}
                    
        )
        details_list.append(details_ele)
        
        element = {"Source": route_dataframe["Source Airport Name"].iloc[i],
                   "Destination": route_dataframe["Destination Airport Name"].iloc[i],
                   "Airline": route_dataframe["Airline"].iloc[i],
                   "Planes": route_dataframe["planes"].iloc[i]}
        details_trace_info.append(element)
        
        
#     details_list = [  html.Details(id={"type": "collapsible", "index": 0},
#                                                     children=[
#                                                         html.Summary("Collapsible Title"),
#                                                         html.Div(id={"type": "collapsible_text", "index": 0},children=[])
#                                                     ],
#                                                     n_clicks=0,
#                                                       style={'border-color': 'black', 'border-style': 'solid',
#                                                           "margin": "20px", "padding":"20px"}
#                                                     ),
#                       html.Details(id={"type": "collapsible", "index": 1},
#                                                     children=[
#                                                         html.Summary("Collapsible Title"),
#                                                         html.Div(id={"type": "collapsible_text", "index": 1},children=[])
#                                                     ],
#                                                     n_clicks=0,

#                                                     style={'border-color': 'black', 'border-style': 'solid',
#                                                           "margin": "20px", "padding":"20px"}
#                                                     ),
#                       html.Details(id={"type": "collapsible", "index": 2},
#                                                     children=[
#                                                         html.Summary("Collapsible Title"),
#                                                         html.Div(id={"type": "collapsible_text", "index": 2},children=[])
#                                                     ],
#                                                     n_clicks=0,
#                                                     style={'border-color': 'black', 'border-style': 'solid',
#                                                           "margin": "20px", "padding":"20px"}
#                                                     )
#                     ]
                    

    return container, fig, details_list

#Details summary
@app.callback(
    [Output({'type': 'collapsible_text', 'index': MATCH}, component_property='children')],
    [Input({'type': 'collapsible', 'index': MATCH}, component_property='n_clicks'),
#      Input(component_id='flight_map', component_property='clickData'),
     State({'type': 'collapsible', 'index': MATCH}, 'id')]
)
def toggle_collapse(n_clicks, match_id):
    print(match_id)
#     container = "Click Data is:"+str(clickData)
#     clickDataInfo = clickData["points"][0]["curveNumber"]
    list_index = match_id['index']
#     print(type(details_trace_info[list_index]))
    src = details_trace_info[list_index]['Source']
    dest = details_trace_info[list_index]['Destination']
    airline = details_trace_info[list_index]['Airline']
    planes = details_trace_info[list_index]['Planes']
#     for val in n_clicks:
#         if(val%2==0):
#             container = ""
#         else:
#             container = "Collapsible text in side"
#         response_list.append(container)

#     if(n_clicks!=0 and n_clicks%2!=0):
#         container = "Collapsible text in side"
#     return [f"Source: {src}"+f"\nDestination: {dest}"]
    return [ [html.H3(f"Airline: {airline}"),
                        #html.Br(),
                        html.H3(f"Planes: {planes}"),
                        #html.Br(),
                        html.H4(f"Source: {src}"),
                        #html.Br(),
                        html.H4(f"Destination: {dest}")]]

#             +f"Destination: {details_trace_info[match_id['index']]["Destination"]}"]

# #Clicking on highlight button
# @app.callback(
#     [Output(component_id='clickDataInfo', component_property='data')],
#     [Input({'type': 'highlight_button', 'index': MATCH}, component_property='n_clicks'),
#      State({'type': 'highlight_button', 'index': MATCH}, 'id')],
#         prevent_initial_call=True
# )
# def store_clicked_data(n_clicks, match_id):
#     if n_clicks is None:
#         raise PreventUpdate
#     else:
# #         return "Elephants are the only animal that can't jump"
#         clicked_trace_dict = {"id": match_id['index']}
#         return clicked_trace_dict


# ------------------------------------------------------------------------------

if __name__ == '__main__':

    app.run_server(debug=True,host='127.0.0.1',port=8050)