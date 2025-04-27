import plotly.express as px
from dash import dcc

def create_line_chart(df, x_col, y_col, title):
    """
    Creates a line chart using Plotly Express.

    :param df: DataFrame containing the data
    :param x_col: Column name for the X-axis
    :param y_col: Column name for the Y-axis
    :param title: Title of the graph
    :return: A Dash dcc.Graph component
    """
    fig = px.line(
        df, x=x_col, y=y_col,
        title=title,
        template="plotly_dark",
        markers=True,
        color_discrete_sequence=["#00BFFF"]  # Deep Sky Blue
    )
    fig.update_layout(xaxis_showgrid=True, yaxis_showgrid=True)
    return dcc.Graph(figure=fig, config={"displayModeBar": False})

def create_bar_chart(df, x_col, y_col, title):
    """
    Creates a bar chart using Plotly Express.

    :param df: DataFrame containing the data
    :param x_col: Column name for the X-axis
    :param y_col: Column name for the Y-axis
    :param title: Title of the graph
    :return: A Dash dcc.Graph component
    """
    fig = px.bar(
        df, x=x_col, y=y_col,
        title=title,
        template="plotly_dark",
        color_discrete_sequence=["#FF4500"]  # Orange Red
    )
    fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=True)
    return dcc.Graph(figure=fig, config={"displayModeBar": False})

def create_area_chart(df, x_col, y_col, title):
    """
    Creates an area chart using Plotly Express.

    :param df: DataFrame containing the data
    :param x_col: Column name for the X-axis
    :param y_col: Column name for the Y-axis
    :param title: Title of the graph
    :return: A Dash dcc.Graph component
    """
    fig = px.area(
        df, x=x_col, y=y_col,
        title=title,
        template="plotly_dark",
        color_discrete_sequence=["#00BFFF"],
    )
    fig.update_traces(line=dict(width=3))
    fig.update_layout(xaxis_showgrid=True, yaxis_showgrid=True)
    return dcc.Graph(figure=fig, config={"displayModeBar": False})
