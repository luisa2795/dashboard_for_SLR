import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
#import plotly.express as px
#import pandas as pd
import utils.functions as fu
from utils.db_credentials import dwh_db_connection_params

engine=fu.initialize_engine(dwh_db_connection_params)
#df=fu.load_full_table(engine, 'aggregation_paper')
df_k=fu.get_papers_with_keywords(engine)


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
        "Search in Keywords: ",
        dcc.Input(id='search_keyword', value='ontology', type='text'),
        "Search in Title: ",
        dcc.Input(id='search_title', value='', type='text'),
        "Search in Abstract: ",
        dcc.Input(id='search_abstract', value='', type='text'),
        html.Button(id='submit_search_strings_button', n_clicks=0, children='Submit')
    ]),
    html.Br(),
    html.Div(id='searched_term'),
    html.Div(id='click_counter'),
    html.H4(children='Papers in the knowledge base'),
    html.Div(id='search_output')
    ])

@app.callback(
    Output(component_id='searched_term', component_property='children'),
    Output(component_id='click_counter', component_property='children'),
    Output(component_id='search_output', component_property='children'),
    Input(component_id='submit_search_strings_button',component_property='n_clicks'),
    State(component_id='search_keyword', component_property='value')
)
#this is a callback function because it is defined after the callback
def update_output_div(n_clicks, keyword):
    #table=generate_table(fu.filter_df_by_title(df_k, input_value)[['title', 'year', 'abstract']], max_rows=10)
    table=generate_table(fu.filter_df_by_keyword(df_k, keyword)[['title', 'year', 'abstract']], max_rows=20)
    searchterm='Your searched term: {}'.format(keyword)
    clicks='Your clicked {} times.'.format(n_clicks)
    return searchterm, clicks, table

if __name__ == '__main__':
    app.run_server(debug=True)