import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
#import plotly.express as px
#import pandas as pd
import utils.functions as fu
from utils.db_credentials import dwh_db_connection_params

engine=fu.initialize_engine(dwh_db_connection_params)
#df=fu.load_full_table(engine, 'aggregation_paper')
df_k=fu.prep_df_for_display(engine)

app=dash.Dash(__name__ , suppress_callback_exceptions=True)

app.layout=html.Div(children=[
    html.Div(children=[
        html.H3('Enter search term to search matching papers: '),
        html.Div(children=[
            html.Div("Search in specific column: "),
            dcc.Input(id='search_column', value='ontology', type='text'),
            html.Br(),
            "Select Column: ",
            dcc.Checklist(id='columns_to_search',
                options=[
                    {'label': 'Title', 'value': 'title'},
                    {'label': 'Keywords', 'value': 'keywords'},
                    {'label': 'Abstract', 'value': 'abstract'},
                ],
                value=['keywords']
            )],
            style={'width': '29%', 'display': 'inline-block'}
        ),
        html.Div(children=[
            html.Div("Search everything: "),
            dcc.Input(id='search_everything', value='', type='text'), 
            html.Br(),
            html.Br(),
            html.Button(id='submit_search_strings_button', n_clicks=0, children='Submit')
            ],
            style={'width': '69%', 'float': 'right', 'display': 'inline-block'}
    )]),    
    html.Br(),
    html.Div(id='searched_term'),
    html.Div(id='click_counter'),
    html.H4(children='Papers in the knowledge base'),
    dcc.Loading(id='loading1', type='cube', children=[
    html.Div(id='search_output', children=dash_table.DataTable(id='search_result_table'))]),
    html.Div(id='manual_selected_papers')
    ])

@app.callback(
    Output(component_id='searched_term', component_property='children'),
    Output(component_id='click_counter', component_property='children'),
    Output(component_id='search_output', component_property='children'),
    Input(component_id='submit_search_strings_button', component_property='n_clicks'),
    State(component_id='search_column', component_property='value'),
    State(component_id='columns_to_search', component_property='value'),
    State(component_id='search_everything', component_property='value')
)
#this is a callback function because it is defined after the callback
def update_output_div(n_clicks, search_column, columns_to_search, search_everything):
    if search_column!='':
        keyword=search_column
        result_df=fu.filter_df_columns_by_keyword(df_k, keyword, columns_to_search)
    else:
        keyword=search_everything
        result_df=fu.filter_entire_df_by_searchterm(df_k, keyword)
    table=fu.generate_result_table(result_df) 
    searchterm='Your searched term: {}'.format(keyword)
    clicks='Your clicked {} times.'.format(n_clicks)
    return searchterm, clicks, table

# @app.callback(
#     Output(component_id='manual_selected_papers', component_property='children'),
#     Input(component_id='search_result_table', component_property='derived_virtual_data'),
#     Input(component_id='search_result_table', component_property='derived_virtual_selected_rows'))

# def list_selected_titles(derived_virtual_data, derived_virtual_selected_rows):
#     sel_data=[derived_virtual_data[i] for i in derived_virtual_selected_rows]
#     sel_df=str(pd.DataFrame(sel_data)['paper_pk'].to_list())
#     # table=dash_table.DataTable(
#     #     id='man_sel_table',
#     #     columns=[{"name": i, "id": i} for i in sel_df.columns],
#     #     data=sel_df.to_dict('records'),
#     #     style_data={
#     #     'whiteSpace': 'normal',
#     # })
#     return sel_df

if __name__ == '__main__':
    app.run_server(debug=True)