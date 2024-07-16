import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import json

# Load the data
death_df = pd.read_csv('Death person.csv')
household_df = pd.read_csv('Household Lifestyle .csv')
agriculture_df = pd.read_csv('Agricultural_practice.csv')
water_quality_df = pd.read_csv('WQ2021.csv')

# Load GeoJSON data
with open('Nallampatti.geojson', 'r') as f:
    geojson_data = json.load(f)

# Convert LineString to Polygon
for feature in geojson_data['features']:
    if feature['geometry']['type'] == 'LineString':
        feature['geometry']['type'] = 'Polygon'
        feature['geometry']['coordinates'] = [feature['geometry']['coordinates']]

# Data preprocessing
death_df['Age_Group'] = pd.cut(death_df['Age'], bins=[0, 18, 30, 45, 60, 75, 100], 
                               labels=['0-18', '19-30', '31-45', '46-60', '61-75', '75+'])

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Community Health and Lifestyle Analysis Dashboard"),

    dcc.Tabs([
        dcc.Tab(label='Mortality Analysis', children=[
            html.Div([
                html.Div([
                    dcc.Graph(id='age-reason-chart'),
                    dcc.RangeSlider(
                        id='age-range-slider',
                        min=death_df['Age'].min(),
                        max=death_df['Age'].max(),
                        step=1,
                        marks={i: str(i) for i in range(0, 101, 10)},
                        value=[0, 100]
                    )
                ], style={'width': '48%', 'display': 'inline-block'}),
                html.Div([
                    dcc.Graph(id='ward-mortality-chart')
                ], style={'width': '48%', 'display': 'inline-block'})
            ]),
            html.Div(id='mortality-analysis')
        ]),
        dcc.Tab(label='Household Infrastructure', children=[
            html.Div([
                html.Div([
                    dcc.Graph(id='water-source-chart'),
                ], style={'width': '48%', 'display': 'inline-block'}),
                html.Div([
                    dcc.Graph(id='sanitation-chart'),
                ], style={'width': '48%', 'display': 'inline-block'}),
            ]),
            html.Div([
                dcc.Graph(id='water-treatment-chart'),
            ]),
            dcc.Dropdown(
                id='ward-dropdown',
                options=[{'label': i, 'value': i} for i in household_df['Ward'].unique()],
                value='All',
                multi=False
            ),
            html.Div(id='infrastructure-analysis')
        ]),
        dcc.Tab(label='Agricultural Practices', children=[
            dcc.Graph(id='farming-practices-chart'),
            html.Div(id='agriculture-analysis')
        ]),
        dcc.Tab(label='Water Quality Map', children=[
            dcc.Dropdown(
                id='water-quality-parameter',
                options=[{'label': col, 'value': col} for col in water_quality_df.columns if col not in ['Sample ID', 'Longitude', 'Latitude']],
                value='pH',
                multi=False
            ),
            dcc.Graph(id='water-quality-map')
        ])
    ])
])

@app.callback(
    [Output('age-reason-chart', 'figure'),
     Output('ward-mortality-chart', 'figure'),
     Output('mortality-analysis', 'children')],
    Input('age-range-slider', 'value')
)
def update_mortality_charts(age_range):
    filtered_df = death_df[(death_df['Age'] >= age_range[0]) & (death_df['Age'] <= age_range[1])]
    
    # Age-Reason Chart
    age_reason_fig = px.histogram(filtered_df, x='Age_Group', color='Reason',
                                  title='Distribution of Death Reasons by Age Group',
                                  labels={'Age_Group': 'Age Group', 'count': 'Number of Deaths'},
                                  height=500)
    
    # Ward Mortality Chart
    ward_mortality = filtered_df['Ward'].value_counts().reset_index()
    ward_mortality.columns = ['Ward', 'Deaths']
    ward_mortality_fig = px.bar(ward_mortality, x='Ward', y='Deaths',
                                title='Mortality by Ward',
                                labels={'Ward': 'Ward Number', 'Deaths': 'Number of Deaths'},
                                height=500)
    
    # Analysis text
    top_causes = filtered_df['Reason'].value_counts().nlargest(3)
    analysis_text = f"""
    Key Observations:
    1. The top 3 causes of death in the selected age range are:
       {', '.join([f"{cause} ({count})" for cause, count in top_causes.items()])}
    2. Ward {ward_mortality['Ward'].iloc[0]} has the highest mortality with {ward_mortality['Deaths'].iloc[0]} deaths.
    3. {filtered_df['Age_Group'].value_counts().index[0]} is the age group with the highest number of deaths.
    """
    
    return age_reason_fig, ward_mortality_fig, analysis_text

@app.callback(
    [Output('water-source-chart', 'figure'),
     Output('sanitation-chart', 'figure'),
     Output('water-treatment-chart', 'figure'),
     Output('infrastructure-analysis', 'children')],
    Input('ward-dropdown', 'value')
)
def update_infrastructure_charts(selected_ward):
    if selected_ward == 'All':
        filtered_df = household_df
    else:
        filtered_df = household_df[household_df['Ward'] == selected_ward]
    
    # Water Source Chart
    water_source_counts = filtered_df['Source_of_drinking'].value_counts()
    water_source_percentages = (water_source_counts / water_source_counts.sum() * 100).round(1)
    water_source_fig = px.pie(
        values=water_source_percentages,
        names=water_source_percentages.index,
        title=f'Drinking Water Sources (Ward: {selected_ward})',
        labels={'label': 'Water Source', 'value': 'Percentage'},
        hole=0.3
    )
    water_source_fig.update_traces(textposition='inside', textinfo='percent+label')

    # Sanitation Chart
    sanitation_counts = filtered_df['Presence of Toilet'].value_counts()
    sanitation_percentages = (sanitation_counts / sanitation_counts.sum() * 100).round(1)
    sanitation_fig = px.pie(
        values=sanitation_percentages,
        names=sanitation_percentages.index,
        title=f'Presence of Toilets (Ward: {selected_ward})',
        labels={'label': 'Toilet Presence', 'value': 'Percentage'},
        hole=0.3,
        color_discrete_map={'Yes': 'green', 'No': 'red'}
    )
    sanitation_fig.update_traces(textposition='inside', textinfo='percent+label')

    # Water Treatment Chart
    treatment_counts = filtered_df['Processed_for_Drinking'].value_counts()
    treatment_percentages = (treatment_counts / treatment_counts.sum() * 100).round(1)
    treatment_fig = px.bar(
        x=treatment_percentages.index,
        y=treatment_percentages.values,
        title=f'Water Treatment Methods (Ward: {selected_ward})',
        labels={'x': 'Treatment Method', 'y': 'Percentage of Households'},
        text=treatment_percentages.values
    )
    treatment_fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    treatment_fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    # Analysis text
    total_households = len(filtered_df)
    toilets_percentage = sanitation_percentages.get('Yes', 0)
    top_water_source = water_source_percentages.index[0]
    top_water_source_percentage = water_source_percentages.iloc[0]
    top_treatment = treatment_percentages.index[0]
    top_treatment_percentage = treatment_percentages.iloc[0]
    
    analysis_text = f"""
    Infrastructure Analysis for {selected_ward}:
    1. Total households analyzed: {total_households}
    2. Sanitation: {toilets_percentage:.1f}% of households have toilets.
    3. Water Source: The most common drinking water source is {top_water_source} ({top_water_source_percentage:.1f}% of households).
    4. Water Treatment: {top_treatment_percentage:.1f}% of households use {top_treatment} as their primary water treatment method.
    5. Areas for Improvement:
       - {'Increase toilet coverage' if toilets_percentage < 90 else 'Maintain high toilet coverage'}
       - {'Promote safer water sources' if top_water_source not in ['Bore well', 'Open well'] else 'Maintain good water sources'}
       - {'Encourage water treatment' if top_treatment == 'Nil' else 'Promote advanced water treatment methods'}
    """
    
    return water_source_fig, sanitation_fig, treatment_fig, analysis_text

@app.callback(
    [Output('farming-practices-chart', 'figure'),
     Output('agriculture-analysis', 'children')],
    Input('farming-practices-chart', 'id')  # Dummy input to trigger the callback
)
def update_agriculture_chart(_):
    # Farming Practices Chart
    farming_fig = px.scatter(agriculture_df, x='ACRES OF FARMING LAND', y='Crop-1',
                             size='ACRES OF FARMING LAND', color='ORGANIC FARMING',
                             hover_data=['NAME', 'Crop-2', 'FERTILIZER-1', 'PESTICIDES-1'],
                             title='Farming Practices Overview',
                             labels={'ACRES OF FARMING LAND': 'Farm Size (Acres)', 'Crop-1': 'Primary Crop'},
                             height=600)
    
    # Analysis text
    total_farms = len(agriculture_df)
    organic_percentage = (agriculture_df['ORGANIC FARMING'] == 'Yes').mean() * 100
    partial_organic = (agriculture_df['ORGANIC FARMING'] == 'Partially').mean() * 100
    avg_farm_size = agriculture_df['ACRES OF FARMING LAND'].mean()
    top_crop = agriculture_df['Crop-1'].value_counts().index[0]
    
    analysis_text = f"""
    Agricultural Practices Analysis:
    1. Total farms analyzed: {total_farms}
    2. {organic_percentage:.1f}% of farms practice fully organic farming, while {partial_organic:.1f}% practice partial organic farming.
    3. The average farm size is {avg_farm_size:.1f} acres.
    4. The most common primary crop is {top_crop}.
    5. There appears to be a relationship between farm size and organic farming practices, which may impact pesticide use and environmental health.
    """
    
    return farming_fig, analysis_text

@app.callback(
    Output('water-quality-map', 'figure'),
    Input('water-quality-parameter', 'value')
)
def update_water_quality_map(selected_parameter):
    fig = px.scatter_mapbox(water_quality_df,
                            lat="Latitude",
                            lon="Longitude",
                            color=selected_parameter,
                            size=selected_parameter,
                            hover_name="Sample ID",
                            hover_data=[selected_parameter],
                            zoom=12,
                            height=600)

    fig.update_layout(mapbox_style="open-street-map")

    # Add GeoJSON layer
    fig.add_choroplethmapbox(
        geojson=geojson_data,
        locations=[feature['properties']['Name'] for feature in geojson_data['features']],
        z=[1] * len(geojson_data['features']),  # Dummy values for coloring
        colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],  # Transparent fill
        marker_line_width=2,
        marker_line_color='red',
        showscale=False,
    )

    fig.update_layout(
        title=f'Water Quality Map - {selected_parameter}',
        mapbox=dict(
            center=dict(lat=water_quality_df['Latitude'].mean(), lon=water_quality_df['Longitude'].mean()),
            zoom=12
        )
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)