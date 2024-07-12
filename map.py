from flask import Blueprint, render_template, render_template_string, jsonify, request
import json
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly

map_bp = Blueprint('map', __name__)

# Function to calculate distance between two coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    return np.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

# Read the CSV files
df_2021 = pd.read_csv('WQ2021.csv')
df_2022 = pd.read_csv('WQ2022.csv')
df_2023 = pd.read_csv('WQ2023.csv')

# Rename columns in df_2023 to match other datasets
df_2023 = df_2023.rename(columns={'latitude': 'Latitude', 'longitude': 'Longitude'})

# Store dataframes in a dictionary
data_frames = {
    '2021': df_2021,
    '2022': df_2022,
    '2023': df_2023
}

# Function to find matching or nearby coordinates
def find_matching_coordinates(row, df_other, threshold=0.0001):
    distances = df_other.apply(lambda x: calculate_distance(row['Latitude'], row['Longitude'], 
                                                            x['Latitude'], x['Longitude']), axis=1)
    min_distance_index = distances.idxmin()
    if distances[min_distance_index] <= threshold:
        return min_distance_index
    return None

# Find matches for 2021 data in 2022 and 2023 data
df_2021['Match_Index_2022'] = df_2021.apply(lambda row: find_matching_coordinates(row, df_2022), axis=1)
df_2021['Match_Index_2023'] = df_2021.apply(lambda row: find_matching_coordinates(row, df_2023), axis=1)

# Define limits for parameters
limits = {'pH': (6.5, 8.5), 'Hardness': (0, 300), 'Alkalinity': (0, 200)}

# Function to calculate Water Quality Index (WQI)
def calculate_wqi(row):
    wqi = 0
    for param, (lower, upper) in limits.items():
        if param in row and pd.notna(row[param]):
            if lower <= row[param] <= upper:
                wqi += 100
            else:
                wqi += max(0, 100 - abs(row[param] - (lower + upper)/2) / ((upper - lower)/2) * 100)
    return wqi / len(limits)

# Function to count parameters exceeding limits
def count_exceeding_params(row):
    return sum(1 for param, (lower, upper) in limits.items() if param in row and pd.notna(row[param]) and (row[param] < lower or row[param] > upper))

# Process data and calculate WQI and exceeding parameters
for year, df in data_frames.items():
    df[f'WQI_{year}'] = df.apply(calculate_wqi, axis=1)
    df[f'Exceeding_{year}'] = df.apply(count_exceeding_params, axis=1)

# Load GeoJSON data
with open('Nallampatti.geojson') as f:
    ward_boundaries = json.load(f)

# HTML template
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Water Quality Data Visualization</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        select { margin-right: 10px; }
        #map-plot { height: 70vh; }
        #stats-panel { margin-top: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="text-align: center; color: #2c3e50;">Water Quality Data Visualization</h1>
        <div>
            <label for="year-select">Select Year:</label>
            <select id="year-select">
                {% for year in years %}
                <option value="{{ year }}">{{ year }}</option>
                {% endfor %}
            </select>
            <label for="compare-select">Compare with:</label>
            <select id="compare-select">
                <option value="none">None</option>
                {% for year in years %}
                <option value="{{ year }}">{{ year }}</option>
                {% endfor %}
            </select>
        </div>
        <div id="map-plot"></div>
        <div id="stats-panel"></div>
    </div>
    <script>
        function updateGraph() {
            const selectedYear = $('#year-select').val();
            const compareYear = $('#compare-select').val();
            
            $.ajax({
                url: '/update_graph',
                method: 'POST',
                data: {
                    selected_year: selectedYear,
                    compare_year: compareYear
                },
                success: function(response) {
                    Plotly.newPlot('map-plot', response.graph.data, response.graph.layout);
                    updateStats(response.stats);
                }
            });
        }

        function updateStats(stats) {
            const statsHtml = `
                <h3>Water Quality Statistics for ${stats.year}</h3>
                <table>
                    <tr>
                        <th>Statistic</th>
                        <th>WQI</th>
                        <th>pH</th>
                        <th>Hardness</th>
                        <th>Alkalinity</th>
                    </tr>
                    <tr>
                        <td>Mean</td>
                        <td>${stats.mean.WQI}</td>
                        <td>${stats.mean.pH}</td>
                        <td>${stats.mean.Hardness}</td>
                        <td>${stats.mean.Alkalinity}</td>
                    </tr>
                    <tr>
                        <td>Median</td>
                        <td>${stats.median.WQI}</td>
                        <td>${stats.median.pH}</td>
                        <td>${stats.median.Hardness}</td>
                        <td>${stats.median.Alkalinity}</td>
                    </tr>
                    <tr>
                        <td>% Exceeding Limits</td>
                        <td>${stats.exceeding.WQI}</td>
                        <td>${stats.exceeding.pH}</td>
                        <td>${stats.exceeding.Hardness}</td>
                        <td>${stats.exceeding.Alkalinity}</td>
                    </tr>
                </table>
            `;
            $('#stats-panel').html(statsHtml);
        }

        $(document).ready(function() {
            updateGraph();
            $('#year-select, #compare-select').change(updateGraph);
        });
    </script>
</body>
</html>
'''

@map_bp.route('/')
def index():
    return render_template_string(html_template, years=list(data_frames.keys()))

@map_bp.route('/update_graph', methods=['POST'])
def update_graph():
    selected_year = request.form['selected_year']
    compare_year = request.form['compare_year']
    
    df = data_frames[selected_year]
    
    # Create a new Figure object
    fig = go.Figure()

    # Add ward boundaries
    for feature in ward_boundaries['features']:
        ward_name = feature['properties']['Name']
        geometry = feature['geometry']
        
        if geometry['type'] == 'Polygon':
            coordinates = geometry['coordinates'][0]
        elif geometry['type'] == 'LineString':
            coordinates = geometry['coordinates']
        else:
            continue  # Skip other geometry types
        
        lons, lats = zip(*coordinates)
        
        fig.add_trace(go.Scattermapbox(
            lon=lons,
            lat=lats,
            mode='lines',
            line=dict(width=2, color='rgba(0, 0, 0, 0.5)'),
            name=f"Ward {ward_name}",
            hoverinfo='name',
            showlegend=False
        ))

    # Add trace for the selected year
    fig.add_trace(go.Scattermapbox(
        lon=df['Longitude'],
        lat=df['Latitude'],
        mode='markers',
        marker=dict(
            size=df[f'Exceeding_{selected_year}'] * 5 + 5,
            color=df[f'WQI_{selected_year}'],
            colorscale='RdYlGn',
            colorbar=dict(title='WQI'),
            cmin=0,
            cmax=100
        ),
        text=df.apply(lambda row: f"Sample ID: {row['Sample ID']}<br>"
                                  f"WQI: {row[f'WQI_{selected_year}']:.2f}<br>"
                                  f"pH: {row['pH']}<br>"
                                  f"Hardness: {row['Hardness']}<br>"
                                  f"Alkalinity: {row['Alkalinity']}", axis=1),
        hoverinfo='text',
        name=f'WQI {selected_year}'
    ))
    
    # Add comparison data if selected
    if compare_year != 'none' and compare_year != selected_year:
        df_compare = data_frames[compare_year]
        fig.add_trace(go.Scattermapbox(
            lon=df_compare['Longitude'],
            lat=df_compare['Latitude'],
            mode='markers',
            marker=dict(
                size=df_compare[f'Exceeding_{compare_year}'] * 5 + 5,
                color=df_compare[f'WQI_{compare_year}'],
                colorscale='RdYlGn',
                colorbar=dict(title='WQI'),
                cmin=0,
                cmax=100,
                symbol='circle-open'
            ),
            text=df_compare.apply(lambda row: f"Sample ID: {row['Sample ID']}<br>"
                                              f"WQI: {row[f'WQI_{compare_year}']:.2f}<br>"
                                              f"pH: {row['pH']}<br>"
                                              f"Hardness: {row['Hardness']}<br>"
                                              f"Alkalinity: {row['Alkalinity']}", axis=1),
            hoverinfo='text',
            name=f'WQI {compare_year}'
        ))
    
    # Update layout
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lon=df['Longitude'].mean(), lat=df['Latitude'].mean()),
            zoom=11
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        showlegend=True
    )
    
    # Calculate statistics
    stats = {
        "year": selected_year,
        "mean": {
            "WQI": f"{df[f'WQI_{selected_year}'].mean():.2f}",
            "pH": f"{df['pH'].mean():.2f}",
            "Hardness": f"{df['Hardness'].mean():.2f}",
            "Alkalinity": f"{df['Alkalinity'].mean():.2f}"
        },
        "median": {
            "WQI": f"{df[f'WQI_{selected_year}'].median():.2f}",
            "pH": f"{df['pH'].median():.2f}",
            "Hardness": f"{df['Hardness'].median():.2f}",
            "Alkalinity": f"{df['Alkalinity'].median():.2f}"
        },
        "exceeding": {
            "WQI": f"{(df[f'Exceeding_{selected_year}'] > 0).mean()*100:.1f}%",
            "pH": f"{((df['pH'] < limits['pH'][0]) | (df['pH'] > limits['pH'][1])).mean()*100:.1f}%",
            "Hardness": f"{(df['Hardness'] > limits['Hardness'][1]).mean()*100:.1f}%",
            "Alkalinity": f"{(df['Alkalinity'] > limits['Alkalinity'][1]).mean()*100:.1f}%"
        }
    }
    
    return jsonify({
        'graph': json.loads(plotly.io.to_json(fig)),
        'stats': stats
    })

@map_bp.route('/map')
def map():
    return render_template('base.html', title="Map of Nallampatti", content=render_template_string(html_template, years=list(data_frames.keys())))