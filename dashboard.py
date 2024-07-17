from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import json
import plotly
import plotly.express as px
from functools import lru_cache

dashboard_bp = Blueprint('dashboard', __name__)

# Professional color scheme
professional_colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896']
blue_scale = ['#e6f2ff', '#bdd7e7', '#6baed6', '#3182bd', '#08519c']

# Data loading and preprocessing
@lru_cache(maxsize=None)
def load_data():
    death_df = pd.read_csv('Death person.csv')
    household_df = pd.read_csv('Household Lifestyle .csv')
    agriculture_df = pd.read_csv('Agricultural_practice.csv')

    death_df['Age_Group'] = pd.cut(death_df['Age'], bins=[0, 18, 30, 45, 60, 75, 100], 
                                   labels=['0-18', '19-30', '31-45', '46-60', '61-75', '75+'])

    return death_df, household_df, agriculture_df

@dashboard_bp.route('/dashboard')
def dashboard():
    death_df, household_df, _ = load_data()
    wards = sorted(household_df['Ward'].unique())
    age_range = [int(death_df['Age'].min()), int(death_df['Age'].max())]
    return render_template('dash.html', title="Community Dashboard", wards=wards, age_range=age_range)

@dashboard_bp.route('/mortality_charts')
def mortality_charts():
    death_df, _, _ = load_data()
    age_min = int(request.args.get('age_min', 0))
    age_max = int(request.args.get('age_max', 100))
    
    filtered_df = death_df[(death_df['Age'] >= age_min) & (death_df['Age'] <= age_max)]
    
    age_reason_fig = px.histogram(filtered_df, x='Age_Group', color='Reason',
                                  title='Distribution of Mortality Causes by Age Group',
                                  labels={'Age_Group': 'Age Group', 'count': 'Number of Cases'},
                                  height=500,
                                  color_discrete_sequence=professional_colors)
    
    ward_mortality = filtered_df['Ward'].value_counts().reset_index()
    ward_mortality.columns = ['Ward', 'Cases']
    ward_mortality_fig = px.bar(ward_mortality, x='Ward', y='Cases',
                                title='Mortality Cases by Ward',
                                labels={'Ward': 'Ward Number', 'Cases': 'Number of Cases'},
                                height=500,
                                color='Cases',
                                color_continuous_scale=blue_scale)
    
    top_causes = filtered_df['Reason'].value_counts().nlargest(3)
    analysis_text = f"""
    Key Observations:
    1. The top 3 causes of mortality in the selected age range are:
       {', '.join([f"{cause} ({count} cases)" for cause, count in top_causes.items()])}
    2. Ward {ward_mortality['Ward'].iloc[0]} has the highest number of cases with {ward_mortality['Cases'].iloc[0]} reported.
    3. The {filtered_df['Age_Group'].value_counts().index[0]} age group shows the highest incidence of cases.
    """
    
    return jsonify({
        'age_reason_chart': json.dumps(age_reason_fig, cls=plotly.utils.PlotlyJSONEncoder),
        'ward_mortality_chart': json.dumps(ward_mortality_fig, cls=plotly.utils.PlotlyJSONEncoder),
        'analysis_text': analysis_text
    })

@dashboard_bp.route('/infrastructure_charts')
def infrastructure_charts():
    _, household_df, _ = load_data()
    selected_ward = request.args.get('ward', 'All')
    
    filtered_df = household_df if selected_ward == 'All' else household_df[household_df['Ward'] == int(selected_ward)]
    
    water_source_counts = filtered_df['Source_of_drinking'].value_counts()
    water_source_percentages = (water_source_counts / water_source_counts.sum() * 100).round(1)
    water_source_fig = px.pie(
        values=water_source_percentages,
        names=water_source_percentages.index,
        title=f'Water Sources in Ward: {selected_ward}',
        labels={'label': 'Water Source', 'value': 'Percentage'},
        hole=0.3,
        color_discrete_sequence=professional_colors
    )
    water_source_fig.update_traces(textposition='inside', textinfo='percent+label')
    
    sanitation_counts = filtered_df['Presence of Toilet'].value_counts()
    sanitation_percentages = (sanitation_counts / sanitation_counts.sum() * 100).round(1)
    sanitation_fig = px.pie(
        values=sanitation_percentages,
        names=sanitation_percentages.index,
        title=f'Sanitation Facilities in Ward: {selected_ward}',
        labels={'label': 'Sanitation Presence', 'value': 'Percentage'},
        hole=0.3,
        color_discrete_map={'Yes': '#2ca02c', 'No': '#d62728'}
    )
    sanitation_fig.update_traces(textposition='inside', textinfo='percent+label')
    
    treatment_counts = filtered_df['Processed_for_Drinking'].value_counts()
    treatment_percentages = (treatment_counts / treatment_counts.sum() * 100).round(1)
    treatment_fig = px.bar(
        x=treatment_percentages.index,
        y=treatment_percentages.values,
        title=f'Water Treatment Methods in Ward: {selected_ward}',
        labels={'x': 'Treatment Method', 'y': 'Percentage of Households'},
        text=treatment_percentages.values,
        color=treatment_percentages.values,
        color_continuous_scale=blue_scale
    )
    treatment_fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    treatment_fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    
    total_households = len(filtered_df)
    toilets_percentage = sanitation_percentages.get('Yes', 0)
    top_water_source = water_source_percentages.index[0]
    top_water_source_percentage = water_source_percentages.iloc[0]
    top_treatment = treatment_percentages.index[0]
    top_treatment_percentage = treatment_percentages.iloc[0]
    
    analysis_text = f"""
    Infrastructure Analysis for Ward {selected_ward}:
    1. Total households analyzed: {total_households}
    2. Sanitation: {toilets_percentage:.1f}% of households have toilets.
    3. Water Source: The primary water source is {top_water_source} ({top_water_source_percentage:.1f}% of households).
    4. Water Treatment: {top_treatment_percentage:.1f}% of households use {top_treatment} as their primary water treatment method.
    5. Areas for Improvement:
       - {'Increase sanitation coverage' if toilets_percentage < 90 else 'Maintain high sanitation standards'}
       - {'Promote safer water sources' if top_water_source not in ['Bore well', 'Open well'] else 'Maintain good water sources'}
       - {'Encourage water treatment' if top_treatment == 'Nil' else 'Promote advanced water treatment methods'}
    """
    
    return jsonify({
        'water_source_chart': json.dumps(water_source_fig, cls=plotly.utils.PlotlyJSONEncoder),
        'sanitation_chart': json.dumps(sanitation_fig, cls=plotly.utils.PlotlyJSONEncoder),
        'water_treatment_chart': json.dumps(treatment_fig, cls=plotly.utils.PlotlyJSONEncoder),
        'analysis_text': analysis_text
    })

@dashboard_bp.route('/agriculture_chart')
def agriculture_chart():
    _, _, agriculture_df = load_data()
    farming_fig = px.scatter(agriculture_df, x='ACRES OF FARMING LAND', y='Crop-1',
                             size='ACRES OF FARMING LAND', color='ORGANIC FARMING',
                             hover_data=['NAME', 'Crop-2', 'FERTILIZER-1', 'PESTICIDES-1'],
                             title='Farming Practices Overview',
                             labels={'ACRES OF FARMING LAND': 'Farm Size (Acres)', 'Crop-1': 'Primary Crop'},
                             height=600,
                             color_discrete_map={'Yes': '#2ca02c', 'No': '#d62728', 'Partially': '#ff7f0e'})
    
    total_farms = len(agriculture_df)
    organic_percentage = (agriculture_df['ORGANIC FARMING'] == 'Yes').mean() * 100
    partial_organic = (agriculture_df['ORGANIC FARMING'] == 'Partially').mean() * 100
    avg_farm_size = agriculture_df['ACRES OF FARMING LAND'].mean()
    top_crop = agriculture_df['Crop-1'].value_counts().index[0]
    
    analysis_text = f"""
    Agricultural Practices Analysis:
    1. Total farms analyzed: {total_farms}
    2. {organic_percentage:.1f}% of farms use fully organic methods, while {partial_organic:.1f}% use partial organic techniques.
    3. The average farm size is {avg_farm_size:.1f} acres.
    4. The most common primary crop is {top_crop}.
    5. There appears to be a relationship between farm size and organic farming practices, which may impact resource use and overall agricultural health.
    """
    
    return jsonify({
        'farming_practices_chart': json.dumps(farming_fig, cls=plotly.utils.PlotlyJSONEncoder),
        'analysis_text': analysis_text
    })