import dash
from dash import dcc, html
from dash.dependencies import Input, Output
#import plotly.express as px
#import pandas as pd
import utils.functions as fu
from utils.db_credentials import dwh_db_connection_params

engine=fu.initialize_engine(dwh_db_connection_params)
df=fu.load_full_table(engine, 'aggregation_paper')

def generate_table(dataframe, max_rows=10):
    return(html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ]))

app=dash.Dash(__name__)

app.layout=html.Div(children=[
    html.H6('Enter search term to search paper titles: '),
    html.Div([
        "Input: ",
        dcc.Input(id='search_term', value='literature review', type='text')
    ]),
    html.Br(),
    html.Div(id='searched_term'),
    html.H4(children='Papers in the knowledge base'),
    html.Div(id='search_output')
    ])

@app.callback(
    Output(component_id='searched_term', component_property='children'),
    Output(component_id='search_output', component_property='children'),
    Input(component_id='search_term', component_property='value')
)
#this is a callback function because it is defined after the callback
def update_output_div(input_value):
    table=generate_table(fu.filter_df_by_title(df, input_value), max_rows=3)
    searchterm='Your searched term: {}'.format(input_value)
    return searchterm, table

if __name__ == '__main__':
    app.run_server(debug=True)