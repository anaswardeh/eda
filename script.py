# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Load the data into a dataframe
filename = 'universal_db.csv'
df = pd.read_csv(filename)

# Pivot the dataframe, grouping by ['UniversityID', 'ClassCode'] and aggregating the average over some columns
# Pace • Self-Mastery • Support • Instructor Clarity • Instructor Engagement • Instructor Knowledge
values_columns = ['WeekPace', 'AcademicSupport', 'ConceptMastering', 'instructorEngagement',
                  'instructorClarity', 'instructorknowledgeable']

table = pd.pivot_table(df, index=['UniversityID', 'ClassCode'], values=values_columns, fill_value=0)

# Convert the dataframe into list of dictionary to feed into Dash-table
table_obj = table.reset_index().to_dict('records')

# Extract the column names for the Dash-table
col_names = table_obj[0].keys()

# List of unique values for available schools and classes
# To be used as the options in filter dropdown boxes
schools = ['All'] + table.index.get_level_values(0).unique().tolist()
classes = ['All'] + table.index.get_level_values(1).unique().tolist()

# The HTML layout
app.layout = html.Div([
    html.Div([
        html.Div([
            html.Label('Select School ID'),
            dcc.Dropdown(
                id='school-id',
                options=[{'label': i, 'value': i} for i in schools],
                value='All'
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Select Class Code'),
            dcc.Dropdown(
                id='class-code',
                options=[{'label': i, 'value': i} for i in classes],
                value='All'
            )
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
        
    html.Div([
        dash_table.DataTable(
            id = 'table',
            columns = [{"name": i, "id": i} for i in col_names],
            data = table_obj
        )
    ], style={'margin-top': '20px'})

])
        

# Callback that updates the table based on the dropdown filter values change
@app.callback(
    Output('table', 'data'),
    [Input('school-id', 'value'), 
     Input('class-code', 'value')]
)
def update_table(school_id, class_code):
    # Save a copy of the dataframe for filtering
    t = table.copy()
    
    # Create a multiindex slice indexer
    idx = pd.IndexSlice
    
    # Filter by school ID, if a value selected
    if school_id != 'All':
        t = t.loc[ idx[school_id, :], :]
        
    # Filter by class code, if a value selected
    if class_code != 'All':
        t = t.loc[ idx[:, class_code], :]
        
    
    # Convert the dataframe into list of dictionary to feed into Dash-table
    return t.reset_index().to_dict('records')


# Callbak to update the ClassCode filter options based on selected UniversityID
@app.callback(
    Output('class-code', 'options'),
    [Input('school-id', 'value')]
)
def update_class(school_id):
    # Save a copy of the dataframe for filtering
    t = table.copy()
    
    # Create a multiindex slice indexer
    idx = pd.IndexSlice
    
    # Filter by school ID, if a value selected
    if school_id != 'All':
        t = t.loc[ idx[school_id, :], :]
        
    # List the unique ClassCode values based on the current University filter
    classes = ['All'] + t.index.get_level_values(1).unique().tolist()
    
    # Return the ClassCode options to the dropdown
    return [{'label': i, 'value': i} for i in classes]
    
    


if __name__ == '__main__':
    app.run_server(debug=True)