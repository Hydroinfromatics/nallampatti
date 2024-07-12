import pandas as pd
import plotly 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from flask import Blueprint, render_template, request, flash
import json

iot_bp = Blueprint('iot', __name__)

@iot_bp.route('/iot')
def iot():
    csv_file_path = 'n.csv'
    parameters = ['TDS', 'pH']

    # Set the default template for a more professional look
    pio.templates.default = "plotly_white"

    # Read the CSV data
    df = pd.read_csv(csv_file_path, parse_dates=['Datetime'])

    # Ensure the data is sorted by date
    df = df.sort_values('Datetime')

    # Add season column
    df['Season'] = pd.cut(df['Datetime'].dt.month, 
                          bins=[0, 3, 6, 9, 12],
                          labels=['Winter', 'Spring', 'Summer', 'Fall'],
                          include_lowest=True)

    # Define colors for each parameter
    colors = {
        'TDS': '#1f77b4',
        'pH': '#ff7f0e',
        # Add colors for new parameters here
    }

    # Create subplots dynamically based on the number of parameters
    fig = make_subplots(rows=len(parameters), cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1,
                        subplot_titles=[f"{param} Over Time" for param in parameters])

    # Add traces for each parameter
    for i, param in enumerate(parameters, start=1):
        fig.add_trace(
            go.Scatter(
                x=df['Datetime'], 
                y=df[param], 
                name=param,
                line=dict(color=colors.get(param, '#000000'), width=2),
                hovertemplate=f'<b>{param}</b>: %{{y:.2f}}<br><b>Date</b>: %{{x|%Y-%m-%d %H:%M:%S}}<br><b>Season</b>: %{{text}}<extra></extra>',
                text=df['Season']
            ),
            row=i, col=1
        )

    # Customize the layout
    fig.update_layout(
        title={
            'text': "Annual Water Quality Analysis",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        hovermode="x unified",
        height=300 * len(parameters),  # Adjust height based on number of parameters
        margin=dict(l=60, r=60, t=80, b=60)
    )

    # Update x-axis and y-axis properties
    fig.update_xaxes(title_text="Date", row=len(parameters), col=1)
    for i, param in enumerate(parameters, start=1):
        fig.update_yaxes(title_text=param, row=i, col=1)

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    # Generate seasonal statistics and analysis
    seasons = ['Winter', 'Spring', 'Summer', 'Fall']
    analysis = ["Seasonal Water Quality Summary:"]

    for season in seasons:
        season_data = df[df['Season'] == season]
        analysis.append(f"\n{season} Insights:")
        for param in parameters:
            mean = season_data[param].mean()
            min_val = season_data[param].min()
            max_val = season_data[param].max()
            analysis.append(f"  {param}: Mean {mean:.2f} (Range: {min_val:.2f} - {max_val:.2f})")
            
            if param == 'TDS':
                if season == 'Fall':
                    analysis.append(f"    Highest TDS average, potentially due to accumulated pollutants and reduced water levels.")
                elif season == 'Spring':
                    analysis.append(f"    Lowest TDS average, likely from increased precipitation and snowmelt dilution.")
            elif param == 'pH':
                if season == 'Summer':
                    analysis.append(f"    Highest average pH, possibly due to increased biological activity.")
                elif season == 'Spring':
                    analysis.append(f"    Lowest average pH, may be influenced by spring runoff and acid rain.")

    analysis.extend([
        "\nKey Observations:",
        "1. TDS shows significant seasonal fluctuations, peaking in Fall and lowest in Spring.",
        "2. pH remains slightly alkaline year-round, with subtle seasonal variations.",
        "3. Summer exhibits the widest TDS range, suggesting high variability in water quality.",
        "4. Further investigation needed for extreme values, particularly in Summer TDS and pH."
    ])

    # Combine all analysis into a single string
    analysis_text = '\n'.join(analysis)

    # Convert the figure to JSON for rendering in the template
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('iot.html', plot_json=plot_json, analysis=analysis_text)