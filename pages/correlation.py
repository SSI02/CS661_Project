# pages/correlation.py

import pandas as pd
import numpy as np
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash.dependencies import ALL, MATCH
import json
from dash import callback_context


# Load datasets
df_temp = pd.read_csv("data/GlobalLandTemperaturesByCountry.csv")
df_sea = pd.read_csv("data/Global_Sea_Level_Rise.csv")
df_emissions = pd.read_csv("data/Historical_Emissions.csv")

# Process temperature data
df_temp["dt"] = pd.to_datetime(df_temp["dt"])
df_temp["year"] = df_temp["dt"].dt.year
# Calculate global average temperature by year
global_temp = df_temp.groupby("year")["AverageTemperature"].mean().reset_index()
# Filter for years that we'll have across all datasets
global_temp = global_temp[global_temp["year"] >= 1990]
global_temp = global_temp[global_temp["year"] <= 2018]

# Process sea level data
df_sea["date"] = pd.to_datetime(df_sea["date"], format="%m/%d/%Y")
df_sea["year"] = df_sea["date"].dt.year
# Rename for clarity and calculate yearly average
df_sea.rename(columns={"mmfrom1993-2008average": "Sea Level (mm)"}, inplace=True)
sea_level_yearly = df_sea.groupby("year")["Sea Level (mm)"].mean().reset_index()
# Filter for common years
sea_level_yearly = sea_level_yearly[sea_level_yearly["year"] >= 1990]
sea_level_yearly = sea_level_yearly[sea_level_yearly["year"] <= 2018]

# Process emissions data
# Get yearly total global emissions
year_columns = [str(year) for year in range(1990, 2019)]
# Convert columns to numeric
df_emissions_yearly = df_emissions.copy()
df_emissions_yearly[year_columns] = df_emissions_yearly[year_columns].apply(pd.to_numeric, errors="coerce")
# Calculate total global emissions per year
global_emissions = pd.DataFrame({
    "year": range(1990, 2019),
    "Global Emissions": [df_emissions_yearly[str(year)].sum() for year in range(1990, 2019)]
})

# Create combined dataset for correlation analysis
# Merge on year
corr_data = global_temp.merge(sea_level_yearly, on="year", how="inner")
corr_data = corr_data.merge(global_emissions, on="year", how="inner")

# Layout with modern UI
layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H2("🔗 Climate Change Correlation Analysis", className="card-title text-primary"),
                    html.P(
                        "Explore the relationships between global temperature, sea level rise, and carbon emissions.",
                        className="card-text"
                    )
                ]),
                className="mb-4 shadow border-0"
            ),
            width=12
        )
    ]),
    
    # Visualization selector card
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Select Visualization", className="card-title mb-3"),
                    
                    # Visualization type selector
                    dbc.Row([
                        dbc.Col([
                            dbc.RadioItems(
                                id="correlation-viz-type",
                                options=[
                                    {"label": "Time Series Comparison", "value": "time"},
                                    {"label": "Correlation Matrix", "value": "matrix"},
                                    {"label": "Scatter Plot Analysis", "value": "scatter"},
                                    {"label": "Combined Dashboard", "value": "dashboard"}
                                ],
                                value="time",
                                inline=True,
                                className="mb-3"
                            )
                        ], width=12)
                    ]),
                    
                    # Year range selector
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Year Range:", className="fw-bold"),
                            dcc.RangeSlider(
                                id="correlation-year-range",
                                min=1990,
                                max=2018,
                                step=1,
                                marks={i: str(i) for i in range(1990, 2019, 4)},
                                value=[1990, 2018],
                                className="mb-3"
                            )
                        ], width=12)
                    ]),
                    
                    # Apply filters button
                    dbc.Row([
                        dbc.Col(
                            dbc.Button(
                                "Update Visualization",
                                id="update-correlation-btn",
                                color="primary",
                                className="w-100"
                            ),
                            width={"size": 4, "offset": 4}
                        )
                    ])
                ]),
                className="mb-4 shadow border-0"
            ),
            width=12
        )
    ]),
    
    # Main visualization card
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4(id="correlation-title", className="card-title text-center mb-4"),
                    dbc.Spinner(
                        dcc.Graph(
                            id="correlation-visualization",
                            config={
                                "responsive": True,
                                "scrollZoom": True,
                                "displayModeBar": True,
                                "modeBarButtonsToAdd": ["lasso2d", "select2d"]
                            },
                            style={"height": "600px"}
                        ),
                        color="primary",
                        type="border"   
                    )
                ]),
                className="mb-4 shadow border-0"
            ),
            width=12
        )
    ]),

    
    # Insights card
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Data Insights", className="card-title"),
                    dbc.Alert(
                        id="correlation-insights",
                        color="info",
                        className="mb-0"
                    )
                ]),
                className="shadow border-0"
            ),
            width=12
        )
    ])
], fluid=True, className="py-4 bg-light")


# Callbacks for interactive functionality
@callback(
    Output("correlation-viz-type", "value"),
    Output({"type": "viz-btn", "index": ALL}, "active"),
    Input({"type": "viz-btn", "index": ALL}, "n_clicks"),
    State({"type": "viz-btn", "index": ALL}, "id"),
    prevent_initial_call=True
)
def update_selected_viz(n_clicks, ids):
    # Find which button was clicked
    ctx = callback_context
    if not ctx.triggered:
        # Default to time series
        button_active = [True, False, False, False]
        return "time", button_active
    
    # Get the id of the clicked button
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    clicked_id = json.loads(button_id)["index"]
    
    # Set the active states
    button_indices = ["time", "matrix", "scatter", "dashboard"]
    button_active = [idx == clicked_id for idx in button_indices]
    
    return clicked_id, button_active

@callback(
    Output("correlation-visualization", "figure"),
    Output("correlation-title", "children"),
    Output("correlation-insights", "children"),
    Input("update-correlation-btn", "n_clicks"),
    State("correlation-viz-type", "value"),
    State("correlation-year-range", "value"),
    prevent_initial_call=False
)
def update_correlation_viz(n_clicks, viz_type, year_range):
    # Filter for selected years
    start_year, end_year = year_range
    filtered_data = corr_data[(corr_data["year"] >= start_year) & (corr_data["year"] <= end_year)]
    
    # Create title based on viz type
    title_prefix = {
        "time": "Time Series Comparison",
        "matrix": "Correlation Matrix",
        "scatter": "Scatter Plot Analysis",
        "dashboard": "Climate Indicators Dashboard"
    }
    
    # Create a completely new figure for each visualization type
    if viz_type == "time":
        # Create figure with secondary y-axes
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add temperature line
        fig.add_trace(
            go.Scatter(
                x=filtered_data["year"],
                y=filtered_data["AverageTemperature"],
                name="Global Temperature (°C)",
                line=dict(color="#FF9500", width=3),
                hovertemplate="Year: %{x}<br>Temp: %{y:.2f}°C<extra></extra>"
            ),
            secondary_y=False
        )
        
        # Add sea level line
        fig.add_trace(
            go.Scatter(
                x=filtered_data["year"],
                y=filtered_data["Sea Level (mm)"],
                name="Sea Level Rise (mm)",
                line=dict(color="#00A6FB", width=3),
                hovertemplate="Year: %{x}<br>Sea Level: %{y:.2f} mm<extra></extra>"
            ),
            secondary_y=True
        )
        
        # Add emissions line
        fig.add_trace(
            go.Scatter(
                x=filtered_data["year"],
                y=filtered_data["Global Emissions"],
                name="CO₂ Emissions",
                line=dict(color="#6A0572", width=3),
                hovertemplate="Year: %{x}<br>CO₂: %{y:.2f}<extra></extra>"
            ),
            secondary_y=False
        )
        
        # Update axes titles
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text="Temperature (°C) / Emissions", secondary_y=False)
        fig.update_yaxes(title_text="Sea Level (mm)", secondary_y=True)
        
        # Create insights
        insights = create_time_insights(filtered_data)
        
    elif viz_type == "matrix":
        # Calculate correlation matrix
        corr_matrix = filtered_data[["AverageTemperature", "Sea Level (mm)", "Global Emissions"]].corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            x=["Temperature", "Sea Level", "CO₂ Emissions"],
            y=["Temperature", "Sea Level", "CO₂ Emissions"],
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            text_auto=True
        )
        
        # Create insights
        insights = create_matrix_insights(corr_matrix)
        
    elif viz_type == "scatter":
        # Create scatter plot matrix
        fig = px.scatter_matrix(
            filtered_data,
            dimensions=["AverageTemperature", "Sea Level (mm)", "Global Emissions"],
            labels={
                "AverageTemperature": "Temperature (°C)",
                "Sea Level (mm)": "Sea Level Rise (mm)",
                "Global Emissions": "CO₂ Emissions"
            },
            color="year",
            color_continuous_scale="Viridis",
            hover_data={"year": True}
        )
        
        # Create insights
        insights = create_scatter_insights(filtered_data)
        
    else:  # dashboard view
        # Create a 2x2 subplot grid
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Temperature Trend", "Sea Level Rise",
                "CO₂ Emissions", "Temperature vs. Emissions"
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "scatter"}]
            ]
        )
        
        # Temperature trend
        fig.add_trace(
            go.Scatter(
                x=filtered_data["year"],
                y=filtered_data["AverageTemperature"],
                mode="lines+markers",
                name="Temperature",
                line=dict(color="#FF9500", width=2),
                hovertemplate="Year: %{x}<br>Temp: %{y:.2f}°C<extra></extra>"
            ),
            row=1, col=1
        )
        
        # Sea level trend
        fig.add_trace(
            go.Scatter(
                x=filtered_data["year"],
                y=filtered_data["Sea Level (mm)"],
                mode="lines+markers",
                name="Sea Level",
                line=dict(color="#00A6FB", width=2),
                hovertemplate="Year: %{x}<br>Sea Level: %{y:.2f} mm<extra></extra>"
            ),
            row=1, col=2
        )
        
        # Emissions trend
        fig.add_trace(
            go.Scatter(
                x=filtered_data["year"],
                y=filtered_data["Global Emissions"],
                mode="lines+markers",
                name="Emissions",
                line=dict(color="#6A0572", width=2),
                hovertemplate="Year: %{x}<br>CO₂: %{y:.2f}<extra></extra>"
            ),
            row=2, col=1
        )
        
        # Temperature vs. Emissions scatter
        fig.add_trace(
            go.Scatter(
                x=filtered_data["Global Emissions"],
                y=filtered_data["AverageTemperature"],
                mode="markers",
                marker=dict(
                    size=10,
                    color=filtered_data["year"],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Year")
                ),
                name="Temp vs. Emissions",
                hovertemplate="CO₂: %{x:.2f}<br>Temp: %{y:.2f}°C<br>Year: %{marker.color}<extra></extra>"
            ),
            row=2, col=2
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Year", row=1, col=1)
        fig.update_yaxes(title_text="Temp (°C)", row=1, col=1)
        
        fig.update_xaxes(title_text="Year", row=1, col=2)
        fig.update_yaxes(title_text="Sea Level (mm)", row=1, col=2)
        
        fig.update_xaxes(title_text="Year", row=2, col=1)
        fig.update_yaxes(title_text="CO₂ Emissions", row=2, col=1)
        
        fig.update_xaxes(title_text="CO₂ Emissions", row=2, col=2)
        fig.update_yaxes(title_text="Temp (°C)", row=2, col=2)
        
        # Create insights
        insights = create_dashboard_insights(filtered_data)
    
    # Common layout updates
    fig.update_layout(
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="white",
        plot_bgcolor="rgba(0,0,0,0.02)",
        title=dict(
            font=dict(size=20),
            x=0.5
        ),
        height=600,
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template="plotly_white"
    )
    
    return fig, f"{title_prefix[viz_type]} ({start_year}-{end_year})", insights


# Helper functions for insights generation
def create_time_insights(df):
    try:
        # Calculate trends
        temp_change = df["AverageTemperature"].iloc[-1] - df["AverageTemperature"].iloc[0]
        sea_change = df["Sea Level (mm)"].iloc[-1] - df["Sea Level (mm)"].iloc[0]
        emissions_change = df["Global Emissions"].iloc[-1] - df["Global Emissions"].iloc[0]
        
        temp_pct = (temp_change / abs(df["AverageTemperature"].iloc[0])) * 100
        sea_pct = (sea_change / abs(df["Sea Level (mm)"].iloc[0] + 0.001)) * 100  # Avoid division by zero
        emissions_pct = (emissions_change / abs(df["Global Emissions"].iloc[0])) * 100
        
        return html.Div([
            html.H5("Key Trends"),
            html.Ul([
                html.Li([
                    "Global temperature has changed by ",
                    html.Strong(f"{temp_change:.2f}°C ({temp_pct:.1f}%)"),
                    " over this period."
                ]),
                html.Li([
                    "Sea levels have risen by ",
                    html.Strong(f"{sea_change:.2f} mm ({sea_pct:.1f}%)"),
                    " during the same timeframe."
                ]),
                html.Li([
                    "Global carbon emissions have changed by ",
                    html.Strong(f"{emissions_change:.2f} units ({emissions_pct:.1f}%)"),
                    "."
                ])
            ]),
            html.P([
                "The parallel increases suggest a relationship between these climate indicators."
            ])
        ])
    except Exception as e:
        return html.P(f"Error generating insights: {e}")


def create_matrix_insights(corr_matrix):
    try:
        temp_sea_corr = corr_matrix.loc["AverageTemperature", "Sea Level (mm)"]
        temp_emis_corr = corr_matrix.loc["AverageTemperature", "Global Emissions"]
        sea_emis_corr = corr_matrix.loc["Sea Level (mm)", "Global Emissions"]
        
        # Interpret the correlation strengths
        def interpret_corr(corr):
            if abs(corr) > 0.8:
                return "very strong"
            elif abs(corr) > 0.6:
                return "strong"
            elif abs(corr) > 0.4:
                return "moderate"
            elif abs(corr) > 0.2:
                return "weak"
            else:
                return "very weak"
        
        return html.Div([
            html.H5("Correlation Analysis"),
            html.Ul([
                html.Li([
                    "Temperature and sea level show a ",
                    html.Strong(f"{interpret_corr(temp_sea_corr)} correlation ({temp_sea_corr:.2f})"),
                    "."
                ]),
                html.Li([
                    "Temperature and emissions show a ",
                    html.Strong(f"{interpret_corr(temp_emis_corr)} correlation ({temp_emis_corr:.2f})"),
                    "."
                ]),
                html.Li([
                    "Sea level and emissions show a ",
                    html.Strong(f"{interpret_corr(sea_emis_corr)} correlation ({sea_emis_corr:.2f})"),
                    "."
                ])
            ]),
            html.P([
                "Remember: correlation does not imply causation, but these relationships align with climate science models."
            ])
        ])
    except Exception as e:
        return html.P(f"Error generating insights: {e}")


def create_scatter_insights(df):
    try:
        from scipy import stats
        
        # Calculate linear regressions
        temp_emis_slope, temp_emis_intercept, temp_emis_r, _, _ = stats.linregress(
            df["Global Emissions"], df["AverageTemperature"]
        )
        
        sea_emis_slope, sea_emis_intercept, sea_emis_r, _, _ = stats.linregress(
            df["Global Emissions"], df["Sea Level (mm)"]
        )
        
        temp_sea_slope, temp_sea_intercept, temp_sea_r, _, _ = stats.linregress(
            df["AverageTemperature"], df["Sea Level (mm)"]
        )
        
        return html.Div([
            html.H5("Relationship Insights"),
            html.Ul([
                html.Li([
                    "For every unit increase in emissions, temperature changes by approximately ",
                    html.Strong(f"{temp_emis_slope:.4f}°C"),
                    f" (R² = {temp_emis_r**2:.2f})."
                ]),
                html.Li([
                    "For every unit increase in emissions, sea level changes by approximately ",
                    html.Strong(f"{sea_emis_slope:.4f} mm"),
                    f" (R² = {sea_emis_r**2:.2f})."
                ]),
                html.Li([
                    "For every 1°C increase in temperature, sea level changes by approximately ",
                    html.Strong(f"{temp_sea_slope:.2f} mm"),
                    f" (R² = {temp_sea_r**2:.2f})."
                ])
            ]),
            html.P([
                "The scatter plots reveal how these climate variables have changed together over time."
            ])
        ])
    except Exception as e:
        return html.P(f"Error generating insights: Detailed regression analysis requires additional libraries.")


def create_dashboard_insights(df):
    try:
        # Calculate rates of change
        years = df["year"].max() - df["year"].min()
        if years > 0:
            temp_rate = (df["AverageTemperature"].iloc[-1] - df["AverageTemperature"].iloc[0]) / years
            sea_rate = (df["Sea Level (mm)"].iloc[-1] - df["Sea Level (mm)"].iloc[0]) / years
            emissions_rate = (df["Global Emissions"].iloc[-1] - df["Global Emissions"].iloc[0]) / years
            
            # Get peak years
            max_temp_year = df.loc[df["AverageTemperature"].idxmax(), "year"]
            max_sea_year = df.loc[df["Sea Level (mm)"].idxmax(), "year"]
            max_emissions_year = df.loc[df["Global Emissions"].idxmax(), "year"]
            
            return html.Div([
                html.H5("Dashboard Insights"),
                html.Ul([
                    html.Li([
                        "Temperature has been changing at a rate of ",
                        html.Strong(f"{temp_rate:.4f}°C per year"),
                        f", with peak temperature observed in {max_temp_year}."
                    ]),
                    html.Li([
                        "Sea level has been rising at a rate of ",
                        html.Strong(f"{sea_rate:.2f} mm per year"),
                        f", with highest levels observed in {max_sea_year}."
                    ]),
                    html.Li([
                        "Emissions have been changing at a rate of ",
                        html.Strong(f"{emissions_rate:.2f} units per year"),
                        f", with peak emissions in {max_emissions_year}."
                    ])
                ]),
                html.P([
                    "The synchronized patterns across these climate indicators suggest interconnected climate system responses."
                ])
            ])
        else:
            return html.P("Select a wider year range to analyze trends.")
    except Exception as e:
        return html.P(f"Error generating insights: {e}")