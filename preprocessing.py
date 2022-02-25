from urllib.request import urlopen
import json
import pandas as pd

def generate_airport_data():
    #Getting airport data
    url = "http://api.travelpayouts.com/data/en/airports.json"
    airport_response =  urlopen(url)

    # decode json data into a dict object
    airport_data = json.loads(airport_response.read())
    #Normalizing JSON data into a dataframe
    airport_df = pd.json_normalize(airport_data)
    airport_df = airport_df[airport_df["iata_type"]=='airport']
 
    #Getting countries data
    country_url = "http://api.travelpayouts.com/data/en/countries.json"
    country_response =  urlopen(country_url)

    # decode json data into a dict object
    country_data = json.loads(country_response.read())
    country_df = pd.DataFrame.from_records(country_data, columns=['code', 'name'])
    
    #Merging Airport and Country data
    df = pd.merge(country_df, airport_df, left_on=['code'], right_on=['country_code'])
    df.rename(columns={'name_x':'country_name','name_y':'Airport name', 'code_y':'code'}, inplace=True)
    df.drop(columns=['code_x','flightable','name_translations.en'],inplace=True)
    df.to_csv("airports_with_country_names.csv", index=False)

    return

def generate_route_data():
    #Getting route data
    route_url = "http://api.travelpayouts.com/data/routes.json"
    route_response = urlopen(route_url)
    route_data = json.loads(route_response.read())
    route_df = pd.DataFrame.from_records(route_data, columns=['airline_iata', 'departure_airport_iata', 
                                                          'arrival_airport_iata', 'codeshare', 'transfers',
                                                         'planes'])
    route_df.rename(columns={'departure_airport_iata': 'Source', 'arrival_airport_iata': 'Destination'}, inplace=True)
    route_df.rename(columns={'airline_iata': 'Airline'}, inplace=True)
    route_df.to_csv("routes_world_data.csv", index=False)
    return

def generate_total_flights_data():
    df = pd.read_csv("airports_with_country_names.csv")
    route_df = pd.read_csv("routes_world_data.csv")

    #Unique airports
    airport_list = df["Airport name"].unique().tolist()

    #Source and Destination Flights
    source_flights =route_df['Source'].value_counts()
    destination_flights = route_df["Destination"].value_counts()

    total_flights_for_airport = source_flights.add(destination_flights, fill_value=0)
    total_flights_df = total_flights_for_airport.to_frame().reset_index()
    total_flights_df.rename(columns={0:'Total number of flights'}, inplace=True)
    total_flights_df.to_csv("total_flights.csv",index=False)

    #Merging Airport and Route data
    new_df = df.merge(total_flights_df,left_on='code',right_on='index')
    new_df.to_csv("total_flights_with_coordinates.csv",index=False)

    total_flights_df = pd.read_csv("total_flights_with_coordinates.csv")
    
    #Defining scale in the total_flights_df
    #For bubble size
    total_flights_diffq = (total_flights_df["Total number of flights"].max() - total_flights_df["Total number of flights"].min()) / 16
    total_flights_df["scale"] = (total_flights_df["Total number of flights"] - total_flights_df["Total number of flights"].min()) / total_flights_diffq + 1
    total_flights_df.to_csv("total_flights_with_coordinates_with_scale.csv", index=False)
    return

def generate_country_level_data():
    total_flights_df = pd.read_csv("total_flights_with_coordinates_with_scale.csv")   
    #    flights_by_country = total_flights_df.groupby(by='country_name')
    dataframe_for_country_level = pd.DataFrame(data=total_flights_df['country_name'].unique(),columns=["Country"])
    dataframe_for_country_level["Latitude"] = ''
    dataframe_for_country_level["Longitude"] = ''
    dataframe_for_country_level["Total flights"] = -1
    for i in range(len(total_flights_df['country_name'].unique())):
        print("Starting i: "+str(i))
        country = dataframe_for_country_level["Country"].iloc[i]
        print("Country: "+country)
        country_l_df = total_flights_df[total_flights_df["country_name"]==country]
        maximum_flights = country_l_df["Total number of flights"].max()
    
        temp_df = country_l_df[country_l_df["Total number of flights"]==maximum_flights]
        temp_df.head()
        dataframe_for_country_level["Latitude"].iloc[i] = temp_df["coordinates.lat"].iloc[0]
        dataframe_for_country_level["Longitude"].iloc[i] = temp_df["coordinates.lon"].iloc[0]
        dataframe_for_country_level["Total flights"].iloc[i] = country_l_df["Total number of flights"].sum()
        print("Latitude: "+str(dataframe_for_country_level["Latitude"].iloc[i]))
        print("Longitude: "+str(dataframe_for_country_level["Longitude"].iloc[i]))
    
    #For bubble size
    country_level_diffq = (dataframe_for_country_level["Total flights"].max() - dataframe_for_country_level["Total flights"].min()) / 16
    dataframe_for_country_level["scale"] = (dataframe_for_country_level["Total flights"] - dataframe_for_country_level["Total flights"].min()) / country_level_diffq + 1
    dataframe_for_country_level.to_csv("Country level flight data.csv",index=False)
    return

def generate_route_data_with_coordinates():
    #route_df = pd.read_csv("routes_world_data.csv")
    #total_flights_df = pd.read_csv("total_flights_with_coordinates.csv")
    #route_df["source_lat"] = ''
    #route_df["dest_lat"] = ''
    #route_df["source_lon"] = ''
    #route_df["dest_lon"] = ''
    #for i in range(route_df.shape[0]):
    #    src_cntry = route_df["Source"].iloc[i]
    #    print("Source: "+src_cntry)
    #    route_df["source_lat"].iloc[i] = total_flights_df[total_flights_df["code"]==src_cntry]["coordinates.lat"].iloc[0]
    #    route_df["source_lon"].iloc[i] = total_flights_df[total_flights_df["code"]==src_cntry]["coordinates.lon"].iloc[0]
    #    dest_cntry = route_df["Destination"].iloc[i]
    #    print("Destination: "+dest_cntry)
    #    route_df["dest_lat"].iloc[i] = total_flights_df[total_flights_df["code"]==dest_cntry]["coordinates.lat"].iloc[0]
    #    route_df["dest_lon"].iloc[i]= total_flights_df[total_flights_df["code"]==dest_cntry]["coordinates.lon"].iloc[0]    
    #route_df.to_csv("routes_world_data_with_coordinates.csv", index=False)	

    route_df = pd.read_csv("routes_world_data.csv")
    #total_flights_df = pd.read_csv("total_flights_with_coordinates_with_scale.csv")

    df = pd.read_csv("airports_with_country_names.csv")
    route_df["source_lat"] = ""
    route_df["dest_lat"] = ""
    route_df["source_lon"] = ""
    route_df["dest_lon"] = ""

    for i in range(route_df.shape[0]):
        print("Iteration: "+str(i))
        src_airport = route_df["Source"].iloc[i]
        print(src_airport)
        if(len(df[df["code"]==src_airport])>0):
            src_lat = df[df["code"]==src_airport]['coordinates.lat'].iloc[0]
            src_lon = df[df["code"]==src_airport]['coordinates.lon'].iloc[0]
    
        dest_airport = route_df["Destination"].iloc[i]
        print(dest_airport)
        if(len(df[df["code"]==dest_airport])>0):
            dest_lat = df[df["code"]==dest_airport]['coordinates.lat'].iloc[0]
            dest_lon = df[df["code"]==dest_airport]['coordinates.lon'].iloc[0]
    
        route_df["source_lat"].iloc[i] = src_lat
        route_df["dest_lat"].iloc[i] = dest_lat
        route_df["source_lon"].iloc[i] = src_lon
        route_df["dest_lon"].iloc[i] = dest_lon
    
        src_lat, src_lon, dest_lat, dest_lon = -1, -1, -1, -1

    route_df.to_csv("routes_world_data_with_coordinates.csv")
    return
