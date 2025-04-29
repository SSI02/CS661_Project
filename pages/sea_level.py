# pages/sea_level.py

from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats

# Load dataset
df = pd.read_csv("data/Global_Sea_Level_Rise.csv")

# Convert 'year' to integer
df["year"] = df["year"].astype(int)

# Convert 'date' to datetime format
df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y")

# Rename the sea level column for clarity
df.rename(columns={"mmfrom1993-2008average": "Sea Level (mm)"}, inplace=True)

# Calculate additional metrics
df["year_decade"] = (df["year"] // 10) * 10  # Group by decade
df["month"] = df["date"].dt.month

# Calculate yearly and decadal averages
yearly_avg = df.groupby("year")["Sea Level (mm)"].mean().reset_index()
decadal_avg = df.groupby("year_decade")["Sea Level (mm)"].mean().reset_index()

# Calculate the rate of change (first derivative)
yearly_avg["rate_of_change"] = yearly_avg["Sea Level (mm)"].diff()

# Fit linear regression to predict future trend
x = yearly_avg["year"].values
y = yearly_avg["Sea Level (mm)"].values
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

# Create projection dataframe
projection_years = list(range(max(yearly_avg["year"]) + 1, max(yearly_avg["year"]) + 51))
projection_df = pd.DataFrame({
    "year": projection_years,
    "Sea Level (mm)_predicted": [intercept + slope * year for year in projection_years],
    "type": "Projection"
})

# Add type to original data for plotting
yearly_avg["type"] = "Historical"

# Combine historical and projection data
combined_df = pd.concat([
    yearly_avg[["year", "Sea Level (mm)", "type"]].rename(columns={"Sea Level (mm)": "Sea Level (mm)_predicted"}),
    projection_df
])

# Define seasonal pattern analysis function
# Fix seasonal pattern analysis
# In sea_level.py, replace the analyze_seasonal_patterns function with:

def analyze_seasonal_patterns():
    seasonal_data = df.copy()
    # Ensure we're working with datetime
    seasonal_data["date"] = pd.to_datetime(seasonal_data["date"])
    # Extract month name and number properly
    seasonal_data["month"] = seasonal_data["date"].dt.month
    
    # Group by month and calculate statistics
    monthly_avg = seasonal_data.groupby("month")["Sea Level (mm)"].mean().reset_index()
    monthly_std = seasonal_data.groupby("month")["Sea Level (mm)"].std().reset_index()
    
    # Merge averages and standard deviations
    monthly_stats = monthly_avg.merge(monthly_std, on="month", suffixes=("_mean", "_std"))
    
    # Add month names
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April", 
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    monthly_stats["month_name"] = monthly_stats["month"].map(month_names)
    
    return monthly_stats.sort_values("month")

seasonal_df = analyze_seasonal_patterns()


# Define layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H2("🌊 Global Sea Level Analysis", className="card-title text-info"),
                    html.P(
                        "Visualize sea level changes over time and explore future projections based on current trends.",
                        className="card-text"
                    )
                ]),
                className="mb-4 shadow border-0"
            ),
            width=12
        )
    ]),
    
    # Time Series Analysis Section
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Historical Sea Level Rise", className="card-title"),
                    html.P("Examine how global sea levels have changed over time with interactive visualizations."),
                    html.Hr(),
                    
                    # Time range selector
                    dbc.Label("Select Time Range:"),
                    dcc.RangeSlider(
                        id="sea-level-year-range",
                        min=df["year"].min(),
                        max=df["year"].max(),
                        step=1,
                        marks={i: str(i) for i in range(df["year"].min(), df["year"].max() + 1, 5)},
                        value=[df["year"].min(), df["year"].max()],
                        className="mb-4"
                    ),
                    
                    # Primary time series chart
                    dbc.Spinner(
                        dcc.Graph(id="sea-level-time-series", config={"responsive": True}),
                        color="info"
                    ),
                    
                    # Insights panel
                    dbc.Alert(
                        id="sea-level-insights",
                        color="info",
                        className="mt-3"
                    )
                ]),
                className="mb-4 shadow border-0"
            ),
            width=12
        )
    ]),
    
    # Additional Analysis Section
    dbc.Row([
        # Future Projections
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Future Projections", className="card-title"),
                    html.P("Based on historical trends, see potential sea level scenarios."),
                    dbc.Spinner(
                        dcc.Graph(
                            id="sea-level-projection",
                            figure=px.line(
                                combined_df,
                                x="year",
                                y="Sea Level (mm)_predicted",
                                color="type",
                                title="Sea Level Projection (50 Years)",
                                color_discrete_map={"Historical": "#1f77b4", "Projection": "#ff7f0e"},
                                template="plotly_white"
                            ).update_layout(
                                yaxis_title="Sea Level (mm)",
                                xaxis_title="Year",
                                legend_title="Data Type",
                                hovermode="x unified"
                            ),
                            config={"responsive": True}
                        ),
                        color="info"
                    ),
                    dbc.Alert([
                        html.H5("Projection Analysis"),
                        html.P([
                            "Based on historical data, sea levels are rising at a rate of ",
                            html.Strong(f"{slope:.2f} mm/year"),
                            ". At this rate, by ",
                            html.Strong(f"{projection_years[-1]}"),
                            ", sea levels could be ",
                            html.Strong(f"{projection_df.iloc[-1]['Sea Level (mm)_predicted']:.1f} mm"),
                            " above the 1993-2008 average."
                        ]),
                        html.P(
                            "Note: This is a simple linear projection and doesn't account for potential acceleration due to climate change feedback mechanisms."
                        )
                    ], color="warning", className="mt-3")
                ]),
                className="mb-4 shadow border-0"
            ),
            width=6
        )
        
        # Seasonal Analysis
    #     dbc.Col(
    #         dbc.Card(
    #             dbc.CardBody([
    #                 html.H4("Seasonal Patterns", className="card-title"),
    #                 html.P("Analyze how sea levels vary throughout the year."),
    #                 dbc.Spinner(
    #                     dcc.Graph(
    #                         id="sea-level-seasonal",
    #                         figure=px.bar(
    #                             seasonal_df,
    #                             x="month_name",
    #                             y="Sea Level (mm)_mean",
    #                             error_y="Sea Level (mm)_std",
    #                             title="Monthly Sea Level Variations",
    #                             labels={"Sea Level (mm)_mean": "Average Sea Level (mm)", "month_name": "Month"},
    #                             template="plotly_white",
    #                             color="Sea Level (mm)_mean",
    #                             color_continuous_scale="Blues"
    #                         ).update_layout(
    #                             xaxis=dict(
    #                                 categoryorder="array",
    #                                 categoryarray=[month for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
    #                                                                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
    #                             ),
    #                             yaxis=dict(title="Average Sea Level (mm)"),
    #                             coloraxis_showscale=False
    #                         ),
    #                         config={"responsive": True}
    #                     ),
    #                     color="info"
    #                 ),
    #                 dbc.Alert([
    #                     html.H5("Seasonal Insights"),
    #                     html.P([
    #                         "Sea levels typically peak in ",
    #                         html.Strong(f"{seasonal_df.loc[seasonal_df['Sea Level (mm)_mean'].idxmax(), 'month_name']}"),
    #                         " and are lowest in ",
    #                         html.Strong(f"{seasonal_df.loc[seasonal_df['Sea Level (mm)_mean'].idxmin(), 'month_name']}")
    #                     ]),
    #                     html.P(
    #                         "These seasonal variations are influenced by thermal expansion, ocean currents, and weather patterns."
    #                     )
    #                 ], color="info", className="mt-3")

    #             ]),
    #             className="mb-4 shadow border-0"
    #         ),
    #         width=6
    #     )
    ]),
    
    # Rate of Change Analysis
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Rate of Change Analysis", className="card-title"),
                    html.P("See how the rate of sea level rise has changed over time."),
                    dbc.Spinner(
                        dcc.Graph(
                            id="sea-level-rate",
                            figure=px.bar(
                                yearly_avg.dropna(subset=["rate_of_change"]),
                                x="year",
                                y="rate_of_change",
                                title="Annual Rate of Sea Level Change",
                                color="rate_of_change",
                                color_continuous_scale="RdBu_r",
                                template="plotly_white"
                            ).update_layout(
                                yaxis_title="Change Rate (mm/year)",
                                xaxis_title="Year",
                                coloraxis_showscale=False
                            ),
                            config={"responsive": True}
                        ),
                        color="info"
                    ),
                    dbc.Alert([
                        html.H5("Acceleration Analysis"),
                        html.P([
                            "The data shows that the rate of sea level rise ",
                            html.Strong("has been accelerating"), 
                            " in recent decades. This acceleration is consistent with climate model projections and is a concerning trend."
                        ])
                    ], color="danger", className="mt-3")
                ]),
                className="shadow border-0"
            ),
            width=12
        )
    ])
], fluid=True, className="py-4 bg-light")


# Callbacks
# Fix plot sizing issue in sea_level.py
@callback(
    Output("sea-level-time-series", "figure"),
    Output("sea-level-insights", "children"),
    Input("sea-level-year-range", "value")
)
def update_time_series(year_range):
    # Filter data by selected year range
    filtered_df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
    
    # Calculate statistics for the filtered range
    start_level = filtered_df.iloc[0]["Sea Level (mm)"]
    end_level = filtered_df.iloc[-1]["Sea Level (mm)"]
    total_change = end_level - start_level
    avg_annual_change = total_change / (year_range[1] - year_range[0]) if year_range[1] > year_range[0] else 0
    
    # Create time series figure with fixed height
    fig = go.Figure()
    
    # Add raw data points (lighter color)
    fig.add_trace(go.Scatter(
        x=filtered_df["date"],
        y=filtered_df["Sea Level (mm)"],
        mode="markers",
        name="Monthly Measurements",
        marker=dict(size=4, color="rgba(0, 123, 255, 0.3)"),
        hovertemplate="Date: %{x|%b %Y}<br>Sea Level: %{y:.1f} mm<extra></extra>"
    ))
    
    # Add rolling average for trend line
    filtered_df["Rolling Avg"] = filtered_df["Sea Level (mm)"].rolling(window=12, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=filtered_df["date"],
        y=filtered_df["Rolling Avg"],
        mode="lines",
        name="12-Month Moving Average",
        line=dict(width=3, color="rgba(220, 53, 69, 0.8)"),
        hovertemplate="Date: %{x|%b %Y}<br>12-Month Avg: %{y:.1f} mm<extra></extra>"
    ))
    
    # Add trend line (linear regression)
    x_numeric = np.array((filtered_df["date"] - filtered_df["date"].min()).dt.days)
    y = filtered_df["Sea Level (mm)"].values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, y)
    
    trend_y = intercept + slope * x_numeric
    fig.add_trace(go.Scatter(
        x=filtered_df["date"],
        y=trend_y,
        mode="lines",
        name="Linear Trend",
        line=dict(width=2, color="black", dash="dash"),
        hovertemplate="Date: %{x|%b %Y}<br>Trend Value: %{y:.1f} mm<extra></extra>"
    ))
    
    # Update layout with fixed height to prevent resizing issues
    fig.update_layout(
        title=f"Sea Level Change ({year_range[0]} to {year_range[1]})",
        xaxis_title="Date",
        yaxis_title="Sea Level (mm relative to 1993-2008 average)",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="x unified",
        height=600  # Fixed height to prevent resizing
    )
    
    # Create insights content
    insights = html.Div([
        html.H5("Sea Level Insights"),
        html.Ul([
            html.Li([
                html.Strong("Total Change: "),
                f"{total_change:.2f} mm over {year_range[1] - year_range[0]} years"
            ]),
            html.Li([
                html.Strong("Average Annual Rate: "),
                f"{avg_annual_change:.2f} mm/year"
            ]),
            html.Li([
                html.Strong("Correlation (R²): "),
                f"{r_value**2:.4f} - {'Strong' if r_value**2 > 0.7 else 'Moderate' if r_value**2 > 0.4 else 'Weak'} correlation"
            ])
        ]),
        html.P([
            "The data shows a ",
            html.Strong("statistically significant" if p_value < 0.05 else "non-significant"),
            f" trend with p-value of {p_value:.4f}."
        ])
    ])
    
    return fig, insights
