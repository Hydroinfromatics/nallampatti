from flask import Flask, Blueprint, render_template_string, jsonify, request
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json

app = Flask(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Read the CSV data
household_data = pd.read_csv(r'Household_lifestyle.csv')
general_data = pd.read_csv('1500Data.csv')

exclude_columns = ['Ward', 'Age','Cancer','Disease','Substance Abuse','Exposure_to_pesticide']
custom_colors = px.colors.qualitative.Set2

# HTML template
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Data Visualization Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
         body {
            font-family: Arial, sans-serif;
            background-color: #ecf0f1;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            font-size: 36px;
            margin-bottom: 30px;
        }
        .container {
            display: flex;
            justify-content: space-between;
        }
        .chart-container {
            width: 49%;
            display: inline-block;
            vertical-align: top;
        }
        h3 {
            text-align: center;
            color: #34495e;
        }
        select {
            width: 100%;
            margin: 10px auto;
            padding: 15px;
            font-size: 18px;
            border-radius: 5px;
            border: 1px solid #bdc3c7;
            background-color: #ffffff;
            cursor: pointer;
            appearance: none;
            -webkit-appearance: none;
            -moz-appearance: none;
            background-image: url('data:image/svg+xml;utf8,<svg fill="black" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="M7 10l5 5 5-5z"/><path d="M0 0h24v24H0z" fill="none"/></svg>');
            background-repeat: no-repeat;
            background-position-x: 98%;
            background-position-y: 50%;
        }
        select:focus {
            outline: none;
            box-shadow: 0 0 5px rgba(52, 152, 219, 0.7);
        }
        .summary {
            margin: 20px;
            font-size: 16px;
            color: #34495e;
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 5px;
            line-height: 1.6;
            }
    </style>
</head>
<body>
    <h1>Comprehensive Data Visualization Dashboard</h1>
    <div class="container">
        <div class="chart-container">
            <h3>Household Lifestyle Data</h3>
            <select id="household-dropdown">
                {% for option in household_options %}
                <option value="{{ option.value }}">{{ option.label }}</option>
                {% endfor %}
            </select>
            <div id="household-pie-chart"></div>
            <div id="household-summary" class="summary"></div>
        </div>
        <div class="chart-container">
            <h3>General Data</h3>
            <select id="general-dropdown">
                {% for option in general_options %}
                <option value="{{ option.value }}">{{ option.label }}</option>
                {% endfor %}
            </select>
            <div id="general-pie-chart"></div>
            <div id="general-summary" class="summary"></div>
        </div>
    </div>

    <script>
        function updateHouseholdChart() {
            $.ajax({
                url: '{{ url_for("dashboard.update_household_chart") }}',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({selected_category: $('#household-dropdown').val()}),
                success: function(response) {
                    Plotly.newPlot('household-pie-chart', response.chart.data, response.chart.layout);
                    $('#household-summary').html(response.summary.join('<br><br>'));
                }
            });
        }

        function updateGeneralChart() {
            $.ajax({
                url: '{{ url_for("dashboard.update_general_chart") }}',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({selected_column: $('#general-dropdown').val()}),
                success: function(response) {
                    Plotly.newPlot('general-pie-chart', response.chart.data, response.chart.layout);
                    $('#general-summary').html(response.summary.join('<br><br>'));
                }
            });
        }

        $(document).ready(function() {
            updateHouseholdChart();
            updateGeneralChart();

            $('#household-dropdown').change(updateHouseholdChart);
            $('#general-dropdown').change(updateGeneralChart);
        });
    </script>
</body>
</html>
'''

@dashboard_bp.route('/')
def dashboard():
    household_options = [
        {'label': 'Source of Drinking Water', 'value': 'Source_of_drinking'},
        {'label': 'Water Processing Method', 'value': 'Processed_for_Drinking'},
        {'label': 'Presence of Toilet', 'value': 'Presence of Toilet'},
        {'label': 'Grey Water Discharge Method', 'value': 'Grey Water Discharge'}
    ]
    general_options = [{'label': col, 'value': col} for col in general_data.columns if col not in exclude_columns]
    return render_template_string(html_template, household_options=household_options, general_options=general_options)

@dashboard_bp.route('/update_household_chart', methods=['POST'])
def update_household_chart():
    selected_category = request.json['selected_category']
    counts = household_data[selected_category].value_counts()
    labels = counts.index.tolist()
    values = counts.values.tolist()

    fig = px.pie(
        names=labels,
        values=values,
        title=f'{selected_category.replace("_", " ").title()}',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=80, b=100, l=20, r=20),
        title_x=0.5,
        title_font=dict(size=20),
        uniformtext_minsize=12,
        uniformtext_mode='hide'
    )

    summary = generate_household_summary(selected_category, counts)

    return jsonify({
        'chart': json.loads(fig.to_json()),
        'summary': summary
    })

@dashboard_bp.route('/update_general_chart', methods=['POST'])
def update_general_chart():
    selected_column = request.json['selected_column']
    value_counts = general_data[selected_column].value_counts()
    
    if len(value_counts) > 10:
        top_10 = value_counts.nlargest(10)
        others = pd.Series({'Others': value_counts.sum() - top_10.sum()})
        value_counts = pd.concat([top_10, others])
    
    fig = go.Figure(data=[go.Pie(
        labels=value_counts.index.tolist(),
        values=value_counts.values.tolist(),
        hole=.4,
        textposition='outside',
        textinfo='label+percent',
        insidetextorientation='radial',
        textfont=dict(size=12, color='#333333'),
        marker=dict(colors=custom_colors, line=dict(color='#FFFFFF', width=2)),
        pull=[0.05] * len(value_counts)
    )])
    
    fig.update_layout(
        title={
            'text': f'{selected_column} Distribution',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20, color='#2c3e50')
        },
        font=dict(family="Arial, sans-serif"),
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=80, b=100),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True
    )
    
    summary = generate_general_summary(selected_column, value_counts)

    return jsonify({
        'chart': json.loads(fig.to_json()),
        'summary': summary
    })

def generate_household_summary(selected_category, counts):
    total = counts.sum()
    most_common = counts.index[0]
    least_common = counts.index[-1]
    most_common_percentage = (counts[most_common] / total) * 100
    least_common_percentage = (counts[least_common] / total) * 100

    summary = []
    if selected_category == 'Source_of_drinking':
        summary = [
            f"The primary source of drinking water is {most_common}, used by {most_common_percentage:.1f}% of households. "
            f"This suggests a {('centralized' if 'Panchyat' in most_common else 'decentralized')} water supply system is prevalent in the area.",
            f"On the other hand, only {least_common_percentage:.1f}% rely on {least_common} as their water source, "
            f"indicating potential areas for infrastructure development.",
            f"The diversity in water sources ({len(counts)} different types) highlights the complexity of water management in this region. "
            f"This variety may pose challenges for ensuring consistent water quality across all households.",
            "Recommendation: Consider initiatives to standardize water sources or improve treatment methods for less common sources to ensure equitable access to safe drinking water."
        ]
    elif selected_category == 'Processed_for_Drinking':
        no_processing = counts.get('Nil', 0) / total * 100
        summary = [
            f"The most common water processing method is {most_common.lower()}, used by {most_common_percentage:.1f}% of households. "
            f"This indicates a {'high' if most_common != 'Nil' else 'low'} awareness of water treatment importance.",
            f"{no_processing:.1f}% of households do not process their drinking water, which could pose health risks.",
            f"The variety of processing methods ({len(counts)} types) suggests differing levels of access to or preference for water treatment technologies.",
            "Recommendation: Implement educational programs on the importance of water treatment and consider subsidizing effective treatment methods to improve adoption rates."
        ]
    elif selected_category == 'Presence of Toilet':
        toilet_percentage = counts.get('Yes', 0) / total * 100
        summary = [
            f"{toilet_percentage:.1f}% of households have a toilet, indicating {'good' if toilet_percentage > 80 else 'concerning'} sanitation coverage.",
            f"The {100 - toilet_percentage:.1f}% of households without toilets represent a significant sanitation challenge and potential public health risk.",
            "The presence or absence of toilets can have far-reaching impacts on public health, gender equality, and environmental cleanliness.",
            "Recommendation: For areas with low toilet coverage, prioritize toilet construction programs and educate about the importance of proper sanitation facilities."
        ]
    elif selected_category == 'Grey Water Discharge':
        summary = [
            f"The primary method of grey water discharge is {most_common.lower()}, practiced by {most_common_percentage:.1f}% of households. "
            f"This {'may have environmental implications' if 'ground' in most_common.lower() else 'suggests some level of water management'}.",
            f"Only {least_common_percentage:.1f}% use {least_common.lower()} for grey water discharge, "
            f"{'which could be an opportunity for promoting more sustainable practices' if 'Farming' not in least_common else 'indicating potential for increased water reuse'}.",
            f"The diversity in discharge methods ({len(counts)} types) reflects varying levels of water management infrastructure and awareness.",
            "Recommendation: Promote environmentally friendly grey water discharge methods and explore opportunities for grey water recycling in agriculture or landscaping."
        ]

    return summary

def generate_general_summary(selected_column, value_counts):
    total_count = value_counts.sum()
    top_category = value_counts.index[0]
    top_percentage = (value_counts.iloc[0] / total_count) * 100
    bottom_category = value_counts.index[-1]
    bottom_percentage = (value_counts.iloc[-1] / total_count) * 100
    
    summary = [
        f"The distribution of {selected_column} shows {len(value_counts)} {'categories' if len(value_counts) <= 10 else 'major categories (top 10 shown)'}. "
        f"'{top_category}' is most common ({top_percentage:.1f}%), while '{bottom_category}' is least common ({bottom_percentage:.1f}%).",
        f"This suggests {'a balanced' if (top_percentage - bottom_percentage) < 20 else 'an uneven'} distribution across categories.",
        f"The range of percentages from {bottom_percentage:.1f}% to {top_percentage:.1f}% indicates "
        f"{'significant variability' if (top_percentage - bottom_percentage) > 30 else 'moderate variability'} in the {selected_column} attribute.",
        "Interpretation: " +
        (f"The data shows a diverse range of {selected_column.lower()}s, with no single category dominating significantly. "
         f"This diversity might reflect a heterogeneous population or varied conditions across the study area."
         if (top_percentage - bottom_percentage) < 20 else
         f"There is a notable concentration in the '{top_category}' category, which may warrant further investigation into the factors contributing to its prevalence."),
        f"Recommendation: Focus on understanding factors influencing the prevalence of '{top_category}' "
        f"and address potential disparities related to '{bottom_category}'. Consider targeted interventions or policies based on this distribution."
    ]
    
    return summary