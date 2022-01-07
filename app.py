import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
#import plotly.express as px
import pandas as pd
import utils.functions as fu
from utils.db_credentials import dwh_db_connection_params

engine=fu.initialize_engine(dwh_db_connection_params)
#df=fu.load_full_table(engine, 'aggregation_paper')
df_k=fu.get_papers_with_keywords(engine)

def generate_result_table(result_df):
    return(dash_table.DataTable(
        id='search_result_table',
        columns=[{"name": i, "id": i, "deletable": True, "selectable": True} for i in result_df.columns],
        data=result_df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
        style_data={
        'whiteSpace': 'normal',
    },
        css=[{
        'selector': '.dash-spreadsheet td div',
        'rule': '''
            line-height: 15px;
            max-height: 30px; min-height: 30px; height: 30px;
            display: block;
            overflow-y: hidden;
        '''
    }],
        tooltip_data=[
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in result_df.to_dict('records')
    ],
    tooltip_duration=None,

        style_cell={'textAlign': 'left'}))

app=dash.Dash(__name__ , suppress_callback_exceptions=True)

app.layout=html.Div(children=[
    html.H3('Enter search term to search matching papers: '),
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
    html.Div(id='search_output', children=dash_table.DataTable(id='search_result_table')),
    html.Div(id='manual_selected_papers')
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
    result_df=fu.filter_df_by_keyword(df_k, keyword).drop(columns=['keywordgroup_pk', 'citekey', 'article_source_id']) #[['title', 'year', 'model_element', 'level',  'participants'..,'abstract']]
    table=generate_result_table(result_df) 
    searchterm='Your searched term: {}'.format(keyword)
    clicks='Your clicked {} times.'.format(n_clicks)
    return searchterm, clicks, table

@app.callback(
    Output(component_id='manual_selected_papers', component_property='children'),
    Input(component_id='search_result_table', component_property='derived_virtual_data'),
    Input(component_id='search_result_table', component_property='derived_virtual_selected_rows'))

def list_selected_titles(derived_virtual_data, derived_virtual_selected_rows):
    sel_data=[derived_virtual_data[i] for i in derived_virtual_selected_rows]
    sel_df=str(pd.DataFrame(sel_data)['paper_pk'].to_list())
    # table=dash_table.DataTable(
    #     id='man_sel_table',
    #     columns=[{"name": i, "id": i} for i in sel_df.columns],
    #     data=sel_df.to_dict('records'),
    #     style_data={
    #     'whiteSpace': 'normal',
    # })
    return sel_df

if __name__ == '__main__':
    app.run_server(debug=True)