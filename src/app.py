#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import plotly.express as px

# ### DASH ###

import dash
# (version 1.9.1) pip install dash==1.9.1
from dash import dcc
from dash import html
from dash.dependencies import Input, Output


terror_peru = pd.read_csv("terrorperu.csv", encoding='ISO-8859-1', low_memory=False)

app = dash.Dash(__name__, meta_tags=[{'name': 'viewport', 'content': 'width=device-width, '
                                                                     'initial-scale=1.0, '
                                                                     'maximum-scale=1.2, '
                                                                     'minimum-scale=0.5,'}] ) # external_stylesheets=external_stylesheets)

server = app.server

pd.set_option('display.max_rows', 150)

# seleccionamos las variables que vamos a usar y las renombramos

terror_peru = terror_peru.rename(columns={
    'iyear': 'Year',
    'imonth': 'Month',
    'iday': 'Day',
    'provstate': 'Department',
    'latitude': 'Latitude',
    'longitude': 'Longitude',
    'attacktype1_txt': 'AttackType',
    'nkill': 'Killed',
    'nwound': 'Wounded',
    'targtype1_txt': 'TargetType',
    'weaptype1_txt': 'WeaponType',
    'success': 'Success',
    'suicide': 'Suicide',
    'gname': 'TerroristGroup'
})

terror_peru = terror_peru[
    ['Year', 'Month', 'Day', 'Department', 'Latitude', 'Longitude', 'AttackType', 'Killed', 'Wounded',
     'TargetType', 'WeaponType', 'Success', 'Suicide', 'TerroristGroup']]

# Acá llenamos los nan en fallecidos con 0

terror_peru['Killed'] = terror_peru['Killed'].fillna(0).astype(int)

# Acá llenamos los nan en heridos con 0
terror_peru['Wounded'] = terror_peru['Wounded'].fillna(0).astype(int)

# cambio el día 0 a 1

###terror_peru['Day'][terror_peru.Day == 0] = 1

###terror_peru.isnull().sum()

###terror_peru['Date'] = pd.to_datetime(terror_peru[['Day', 'Month', 'Year']])


########################

# ***FINAL APP***


# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

dframe = terror_peru.copy()

# SE VA A HACER UN DF PARA EL GRÁFICO DE ATENTADOS POR AÑO

dfperyear = dframe.groupby(["Year", "Department"], as_index=False)["Success"].count()

dfperyear = pd.DataFrame(dfperyear)

dfperyear = dfperyear.rename(columns={'Year': 'Year',
                                      'Department': 'Department',
                                      'Success': 'Number of Terrorist Attacks'})


fig = px.line(dfperyear, x="Year", y="Number of Terrorist Attacks", color='Department',
              # title='Terror Attacks per Department',
              template='plotly_dark', color_discrete_sequence=px.colors.sequential.deep)
# fig.update_layout(title_text='Terror Attacks per Department', title_x=0.5)
# fig.show()

##############


# **CREAR EL DATAFRAME PARA LOS MAPAS TOTALES**

with open('peru_departamental_simple.geojson') as f:
    geo_json_data = json.load(f)

geoperu = geo_json_data

geo_id = {}
for xx in geoperu['features']:
    xx['id'] = xx['properties']['NOMBDEP']
    geo_id[xx["properties"]["NOMBDEP"]] = xx["id"]

# se quitan los unknown en departamentos

mapav = terror_peru[terror_peru.Department != "Unknown"]

# MAPAxHERIDOS

mapaxheridos = mapav.groupby('Department')['Wounded'].sum()
mapaxheridos = pd.DataFrame(mapaxheridos).reset_index()
mapaxheridos['Department'] = mapaxheridos['Department'].apply(lambda x: x.upper())

# MAPAxFALLECIDOS

mapaxfallecidos = mapav.groupby('Department')['Killed'].sum()
mapaxfallecidos = pd.DataFrame(mapaxfallecidos).reset_index()
mapaxfallecidos['Department'] = mapaxfallecidos['Department'].apply(lambda x: x.upper())

# MAPA NÚMERO TOTAL DE ATENTADOS POR DEPARTAMENTO

mapadeatentados = pd.DataFrame(mapav['Department'].value_counts())
mapadeatentados = mapadeatentados.reset_index()
mapadeatentados = mapadeatentados.rename(columns={'index': 'Department', 'Department': 'Terrorist Attacks'})
mapadeatentados['Department'] = mapadeatentados['Department'].apply(lambda x: x.upper())

# UNIR LOS DATAFRAMES

uniruno = pd.merge(mapadeatentados, mapaxfallecidos)

tablatotal = pd.merge(uniruno, mapaxheridos)

#############
# **TABLA PARA GRÁFICO PIE**

dframepie = dframe.copy()

dframepie = dframepie[["Department", "AttackType", "TargetType", "WeaponType"]]

dframepie = dframepie.rename(columns={"AttackType": "Attack Type",
                                      "TargetType": "Target Type",
                                      "WeaponType": "Weapon Type"})

# **TABLA PARA GRÁFICO HISTOGRAMA**

dframehist = dframe.copy()

dframehist = dframehist[["Department", "AttackType", "TargetType", "WeaponType", "TerroristGroup"]]

dframehist = dframehist.rename(columns={"AttackType": "Attack Type",
                                        "TargetType": "Target Type",
                                        "WeaponType": "Weapon Type",
                                        "TerroristGroup": "Terrorist Group"})


# GRÁFICO PARA SEGUNDO HISTOGRAMA (GRANDE)

fig2 = px.histogram(dframehist, y="Department", color="Terrorist Group",
                    template='plotly_dark', orientation="h",
                    # color_discrete_sequence =px.colors.qualitative.Plotly[::-1],
                    color_discrete_sequence=px.colors.sequential.deep
                    # color_discrete_sequence =px.colors.diverging.RdBu[::-1]
                    )
#fig2.show()

#########################################################
# **LA APP**
# ----------------------
#
app.title = 'Terrorism in Peru'

app.layout = html.Div([

    # Header
    html.Div([

        # Title
        html.Div([
            html.H2("Terrorism in Peru", style={'text-align': 'center', 'background': '#111111', 'color': 'white',
                                                'padding': '12px 12px 6px 12px', 'margin': '0px'}),
            html.P("by Sebastián D. Rosado", style={'text-align': 'center', 'background': '#111111', 'color': 'white',
                                                    'padding': '6px 12px 12px 12px', 'margin': '0px'}),
        ], className='four columns',
        ),

        # Text
        html.Div([
            html.P([
                       "Terrorism in Peru (1970-2017) dashboard made with data from The Global Terrorism Database (GTD) from the"
                       " National Consortium for the Study of Terrorism and Responses to Terrorism (START), headquartered at the"
                       " University of Maryland."
                       " For more information about the data go to ",
                       html.A("START website.", href='https://www.start.umd.edu/gtd/', target="_blank",
                              style={'color': '#6A5ACD',
                                     'text-decoration': 'none'}),
                       ], style={'text-align': 'justify', 'background': '#111111', 'color': 'white',
                                 'padding': '12px 10px 20px 10px', 'margin': '0px'}),
        ], className='eight columns',
        ),

    ], className='twelve columns', style={'background': "#171717"},
    ),

    # First row
    html.Div([

        # Line Graph
        html.Div([
            html.H6("Terrorist attacks per department",
                    style={'text-align': 'center', 'background': '#111111', 'color': 'white',
                           'padding': '11px 11px 11px 11px'}),
            html.Br(),
            dcc.Graph(figure=fig)

        ], className='six columns',
        ),

        # Map Graph
        html.Div([
            html.H6("Total number (1970-2017)",
                    style={'text-align': 'center', 'background': '#111111', 'color': 'white',
                           'padding': '11px 11px 11px 11px'}),
            dcc.Dropdown(id="slct_value",
                         options=[
                             {"label": "Killed", "value": "Killed"},
                             {"label": "Wounded", "value": "Wounded"},
                             {"label": "Terrorist Attacks", "value": "Terrorist Attacks"},
                         ],
                         multi=False,
                         value="Terrorist Attacks",
                         placeholder='Please select...',
                         style={'width': "80%"},
                         persistence=True,
                         persistence_type='local',
                         ),

            html.Div(id='output_container', children=[], style={'color': 'white', 'padding': '12px 11px 12px 11px'}),
            # html.Br(),
            dcc.Graph(id='terror_map', figure={}, )

        ], className='six columns',
        ),

    ], className='twelve columns', style={'background': "#171717"},
    ),

    # Second row
    html.Div([

        # Pie Graph
        html.Div([
            html.H6("Distribution of terrorist attacks",
                    style={'text-align': 'center', 'background': '#111111', 'color': 'white',
                           'padding': '11px 11px 11px 11px'}),
            dcc.Dropdown(id='my_dropdown',
                         options=[
                             {'label': 'Department', 'value': 'Department'},
                             {'label': 'Attack Type', 'value': 'Attack Type'},
                             {'label': 'Target Type', 'value': 'Target Type'},
                             {'label': 'Weapon Type', 'value': 'Weapon Type'}
                         ],
                         value='Department',  # dropdown value selected automatically when page loads
                         disabled=False,  # disable dropdown value selection
                         multi=False,  # allow multiple dropdown values to be selected
                         searchable=True,  # allow user-searching of dropdown values
                         search_value='',  # remembers the value searched in dropdown
                         placeholder='Please select...',  # gray, default text shown when no option is selected
                         clearable=True,  # allow user to removes the selected value
                         style={'width': "80%"},  # use dictionary to define CSS styles of your dropdown
                         persistence=True,
                         persistence_type='local',
                         ),
            html.Div(id='output_data', children=[], style={'color': 'white', 'padding': '12px 11px 12px 11px'}),
            dcc.Graph(id='our_graph')
        ], className='six columns', ),

        # Histogram
        html.Div([
            html.H6("Distribution of attacks per department",
                    style={'text-align': 'center', 'background': '#111111', 'color': 'white',
                           'padding': '11px 11px 11px 11px'}),
            dcc.Dropdown(id='my_dropdown2',
                         options=[
                             {'label': 'Attack Type', 'value': 'Attack Type'},
                             {'label': 'Target Type', 'value': 'Target Type'},
                             {'label': 'Weapon Type', 'value': 'Weapon Type'},
                             # {'label': 'Terrorist Group', 'value': 'Terrorist Group'},
                         ],
                         value='Attack Type',  # dropdown value selected automatically when page loads
                         disabled=False,  # disable dropdown value selection
                         multi=False,  # allow multiple dropdown values to be selected
                         searchable=True,  # allow user-searching of dropdown values
                         search_value='',  # remembers the value searched in dropdown
                         placeholder='Please select...',  # gray, default text shown when no option is selected
                         clearable=True,  # allow user to removes the selected value
                         style={'width': "80%"},  # use dictionary to define CSS styles of your dropdown
                         persistence=True,
                         persistence_type='local',
                         ),
            html.Div(id='output_data2', children=[], style={'color': 'white', 'padding': '12px 11px 12px 11px'}),
            dcc.Graph(id='our_graph2')
        ], className='six columns', ),
    ]
    ),

    # Third row
    html.Div([
        html.Div([
            html.H6("Terrorist attacks by terrorist group per department",
                    style={'text-align': 'center', 'background': '#111111', 'color': 'white',
                           'padding': '11px 11px 11px 11px'}),
            html.Br(),
            dcc.Graph(figure=fig2)

        ], className='twelve columns', ),

    ], className='twelve columns', style={'background': "#171717"},
    ),

    # spacing
    html.Div([
        html.Br(),
    ], className='twelve columns', style={'background': '#171717'},
    ),

    # Footer
    html.Div([
        # Name
        html.Div([
            html.P("Sebastián D. Rosado,  2023",
                   style={'text-align': 'right', 'background': '#111111', 'color': 'white',
                          'padding': '10px 10px 10px 10px'}),
        ], className='twelve columns'
        ),
    ],
    ),
], style={'backgroundColor': "#171717"}
)

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components

# Map Graph

# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='terror_map', component_property='figure')],
    [Input(component_id='slct_value', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "Total number of {} from 1970 to 2017".format(option_slctd)

    # Plotly Express
    fig = px.choropleth(
        data_frame=tablatotal,
        locations="Department",
        geojson=geo_json_data,
        color=option_slctd,
        hover_name="Department",
        # hover_data=["Fallecidos"],
        # title="Fallecidos en Perú",
        # color_continuous_scale=px.colors.sequential.YlOrRd,
        # color_continuous_scale=px.colors.sequential.deep,
        color_continuous_scale=px.colors.sequential.YlGnBu,
        # color_continuous_scale=px.colors.diverging.RdYlBu,
        template='plotly_dark',
        # width=800,
        height=390,
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=60, r=60, t=50, b=50), autosize=True, hovermode='closest', )

    return container, fig


#############################################################################################################
# Pie Graph

# ---------------------------------------------------------------
# Connecting the Dropdown values to the graph
@app.callback(
    Output(component_id='our_graph', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')]
)
def build_graph(column_chosen):
    dff = dframepie
    fig = px.pie(dff, names=column_chosen, template='plotly_dark',
                 color_discrete_sequence=px.colors.sequential.deep)
    # hover_data =  )

    fig.update_traces(textinfo='percent+label', textposition='inside', insidetextfont=dict(color='black'),
                      hoverinfo="label+percent")
    return fig


# ---------------------------------------------------------------
# For tutorial purposes to show the user the search_value

@app.callback(
    Output(component_id='output_data', component_property='children'),
    [Input(component_id='my_dropdown', component_property='value')]
)
def build_graph(data_chosen):
    container = 'Distribution of {} from 1970 to 2017'.format(data_chosen)
    return container


# ---------------------------------------------------------------


#############################################################################################################
# Histogram

# ---------------------------------------------------------------
# Connecting the Dropdown values to the graph
@app.callback(
    Output(component_id='our_graph2', component_property='figure'),
    [Input(component_id='my_dropdown2', component_property='value')]
)
def build_graph(column_chosen2):
    dff2 = dframehist
    fig = px.histogram(dff2, y="Department", color=column_chosen2,
                       template='plotly_dark', orientation="h",
                       # color_discrete_sequence =px.colors.qualitative.Pastel
                       color_discrete_sequence=px.colors.sequential.deep)
    fig.update_layout(legend=dict(
    ))
    return fig


# ---------------------------------------------------------------
# For tutorial purposes to show the user the search_value

@app.callback(
    Output(component_id='output_data2', component_property='children'),
    [Input(component_id='my_dropdown2', component_property='value')]
)
def build_graph(data_chosen2):
    container = 'Attacks by {}'.format(data_chosen2)
    return container


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)
