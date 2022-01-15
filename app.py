import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
#import plotly.express as px
import pandas as pd
import utils.functions as fu
from utils.db_credentials import dwh_db_connection_params
from dash.exceptions import PreventUpdate
import dash_daq as daq
#import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # dbc.themes.QUARTZ is the most beautiful one but less serious, FLATLY

engine=fu.initialize_engine(dwh_db_connection_params)
dim_ent=fu.load_full_table(engine, 'dim_entity')
ent_hierarchy=fu.load_full_table(engine, 'map_entity_hierarchy')
#df=fu.load_full_table(engine, 'aggregation_paper')
df_k=fu.prep_df_for_display(engine)

app=dash.Dash(__name__ , external_stylesheets=external_stylesheets, suppress_callback_exceptions=True) #prevent_initial_callbacks=True



app.layout=html.Div(
    children=[
        html.H2('Welcome to the Systematic Review Dashboard'),
        html.P('This Dashboard was designed on top of a Data-Warehouse of Scientific Literature and can help you understand the current state of research or to find suitable papers to quote for a specific methodology. Try it out!'), 
        html.Div(children=[
            html.H4('Understand the current body of knowledge for your topic', style={'width': '29%', 'display': 'inline-block', 'padding': '10px'}),
            daq.ToggleSwitch(
                id='toggle_function',
                value=True,
                size=100,
                style={'width': '29%', 'display': 'inline-block', 'padding': '10px'}
            ),
            html.H4('Which paper and who have been referenced often for your topic?', style={'width': '29%', 'display': 'inline-block', 'padding': '10px'})
        ]),
        html.Div(id='search papers', children=[
            html.H5('Paper Search'),
            html.Div(children=[
                html.Div("Search keyword in column: "),
                dcc.Input(id='search_term', type='text'),#, value='ontology'
                html.Br(),
                "Select Column: ",
                dcc.Checklist(id='columns_to_search',
                    options=[
                        {'label': 'Title', 'value': 'title'},
                        {'label': 'Keywords', 'value': 'keywords'},
                        {'label': 'Abstract', 'value': 'abstract'},
                        {'label': 'search all fields', 'value': 'entire_df'},
                    ],
                    value=['keywords']
                ),
                html.Br(),
                html.Button(id='submit_search_strings_button', n_clicks=0, children='Submit keyword search'),
                html.Br(),
                html.Br()
                ],
                style={'width': '22%', 'display': 'inline-block', 'padding': '10px', 'border-style': 'solid', 'border-width': '1px', 'border-color': '#b1dcfa'}
            ),
            html.Div(children=[
                html.Div("Search entities: "),
                html.Div([
                    html.Div([
                        'Entity Label: ',
                        dcc.Dropdown(id='dropdown_labels', options=fu.get_label_options(dim_ent),
                            )#value='TOPIC'
                    ],
                    style={'width': '29%','padding': '10px', 'vertical-align': 'top', 'display': 'inline-block'}),
                    html.Div([
                        'available entities: ',
                        dcc.Dropdown(id='entity_name', 
                        )#value='open source'
                    ],
                    style={'width': '29%', 'padding': '10px', 'vertical-align': 'top', 'display': 'inline-block'}),
                    html.Div([
                        'include child entities?',
                        dcc.RadioItems(id='include_child_ents',
                        options=[
                            {'label': 'Yes', 'value': 1},
                            {'label': 'No', 'value': 0}
                        ],
                        value=0
                        ),
                        html.Div(id='implied_child_entities')
                    ],
                    style={'width': '22%', 'padding': '10px', 'vertical-align': 'top', 'display': 'inline-block'})
                ]),
            html.Button(id='submit_entity_search', n_clicks=0, children='Submit Entity Search')
            ], 
            style={'width': '60%', 'float': 'right', 'display': 'inline-block', 'padding': '10px', 'border-style': 'solid', 'border-width': '1px', 'border-color': '#b1dcfa'}
            ),    
            html.Br(),
            html.Div(id='searched_term'),
            html.Div(id='click_counter'),
            html.Br(),
            dcc.Loading(id='loading1', type='cube', children=[
                html.Div(id='for_select_all_btn'),
                html.Div(id='search_output', children=dash_table.DataTable(id='search_result_table'))
                ])
        ]),
        html.Div(id='analyse_papers', children=[
            html.Div(id='manual_selected_papers'),
            html.Div(id='for_analysis_button'),
            html.Div(id='for_paper_checkboxes'),
            html.Div(id='for_content_comparison_button'),
            html.Div(id='parallel_categories_overview'),
            html.Div(id='for_metadata_button'),
            html.Div(id='metadata_figures')
        ])     
])

@app.callback(
    Output(component_id='searched_term', component_property='children'),
    Output(component_id='click_counter', component_property='children'),
    Output(component_id='for_select_all_btn', component_property='children'),
    Output(component_id='search_output', component_property='children'),
    Input(component_id='submit_search_strings_button', component_property='n_clicks'),
    Input(component_id='submit_entity_search', component_property='n_clicks'),
    State(component_id='search_term', component_property='value'),
    State(component_id='columns_to_search', component_property='value'),
    State(component_id='dropdown_labels', component_property='value'),
    State(component_id='implied_child_entities', component_property='children'),
    State(component_id='entity_name', component_property='value'),
    State(component_id='include_child_ents', component_property='value')
)
def update_result_table(submit_search_strings_button_clicks, submit_entity_search, search_term, columns_to_search, dropdown_labels, implied_child_entities, entity_name, include_child_ents):
    ctx=dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        if ctx.triggered[0]['prop_id']=='submit_search_strings_button.n_clicks':
            if 'entire_df' in columns_to_search:
                result_df=fu.filter_entire_df_by_searchterm(df_k, search_term)
            else:
                result_df=fu.filter_df_columns_by_keyword(df_k, search_term, columns_to_search)
            searchterm='Your searched term: {}'.format(search_term)
            table=fu.generate_result_table(result_df) 
        else:
            result_df=fu.filter_df_by_entity(df_k, dropdown_labels, implied_child_entities, entity_name, include_child_ents)
            searchterm='Your searched entity: {}'.format(entity_name)
            table=fu.generate_result_table(result_df)
    clicks='Your clicked {} times.'.format(submit_search_strings_button_clicks + submit_entity_search)
    return searchterm, clicks, html.Button(id='select_all_button', n_clicks=0, children='Select all'), table
    

@app.callback(
    Output(component_id='entity_name', component_property='options'),
    Input(component_id='dropdown_labels', component_property='value')
)
def update_entity_options(dropdown_label):
    options=[]
    for ent_name in dim_ent[dim_ent['entity_label']==dropdown_label]['entity_name'].to_list():
        options.append({'label': ent_name, 'value': ent_name})
    return options

@app.callback(
    Output(component_id='implied_child_entities', component_property='children'),
    Input(component_id='entity_name', component_property='value'),
    Input(component_id='include_child_ents', component_property='value')
)
def display_included_entitiy_children(chosen_entity, include_child_ents):
    if include_child_ents==1:
        child_ents=fu.find_child_entities(dim_ent, ent_hierarchy, chosen_entity)
    else:
        child_ents=[]
    return (', '.join(child_ents))

@app.callback(
    Output('search_result_table', 'selected_rows'),
    Input('select_all_button', 'n_clicks'),
    State('search_result_table', 'derived_virtual_data')
)
def select_all(selbtn_clicks, search_results):
    if selbtn_clicks==0:
        raise PreventUpdate
    else:
        return [i for i in range(len(search_results))]


@app.callback(
    Output(component_id='manual_selected_papers', component_property='children'),
    Input(component_id='manual_selected_papers', component_property='children'),
    Input(component_id='search_result_table', component_property='derived_virtual_data'),
    Input(component_id='search_result_table', component_property='derived_virtual_selected_rows'))

def update_selected_titles(previously_selected_papers, derived_virtual_data, derived_virtual_selected_rows):
    if derived_virtual_selected_rows:
        sel_data=[derived_virtual_data[i] for i in derived_virtual_selected_rows]
        sel_keys=[str(pk) for pk in pd.DataFrame(sel_data)['paper_pk'].to_list()]
        if previously_selected_papers:
            previous_list=previously_selected_papers.split(', ')
            delta_keys=[k for k in sel_keys if (k not in previous_list)]
        else:
            previous_list=[]
            delta_keys=sel_keys
        return_keys=', '.join(previous_list+delta_keys)
        return return_keys
    else:
        raise PreventUpdate

@app.callback(
    Output(component_id='for_analysis_button', component_property='children'),
    Input(component_id='manual_selected_papers', component_property='children')
)
def show_analysis_button_upon_selection(manual_selected_papers):
    if manual_selected_papers:
        return html.Button(id='move_to_analysis_button', n_clicks=0, children='Search finished, move to analysis')
    else: 
        raise PreventUpdate

@app.callback(
    [
        Output(component_id='for_paper_checkboxes', component_property='children'),
        Output(component_id='for_content_comparison_button', component_property='children'),
        Output(component_id='for_metadata_button', component_property='children')
    ],
    Input(component_id='move_to_analysis_button', component_property='n_clicks'),
    State(component_id='manual_selected_papers', component_property='children')
)
def show_content_and_metadata_buttons_upon_analysis_start(analysis_clicks, selected_papers_string):
    if analysis_clicks!=0:
        return [
            fu.get_checkboxes_from_selected_papers(selected_papers_string, df_k),
            html.Button(id='content_comparison_button', n_clicks=0, children='Compare content of selected literature'), 
            html.Button(id='analyse_metadata_button', n_clicks=0, children='Analyse metadata of selected literature')]
    else: 
        raise PreventUpdate

@app.callback(
    Output(component_id='parallel_categories_overview', component_property='children'),
    Input(component_id='content_comparison_button', component_property='n_clicks'),
    State(component_id='analysis_papers_checklist', component_property='value')
)
def update_content_analysis(n_clicks, checked_paper_pks):
    if n_clicks==0:
        raise PreventUpdate
    else:
        fig=fu.generate_parallel_categories_overview_graph(checked_paper_pks, df_k)
        return(dcc.Graph(figure=fig))

@app.callback(
    Output(component_id='metadata_figures', component_property='children'),
    Input(component_id='analyse_metadata_button', component_property='n_clicks'),
    State(component_id='analysis_papers_checklist', component_property='value')
)
def update_metadata_analysis(n_clicks, checked_paper_pks):
    if n_clicks==0:
        raise PreventUpdate
    else:
        fig_time, fig_journals, fig_institutes=fu.generate_metadata_graphs(checked_paper_pks, df_k, engine)
        return [
            dcc.Graph(figure=fig_time, style={'width': '40%', 'vertical-align': 'top', 'display': 'inline-block'}), 
            dcc.Graph(figure=fig_journals, style={'width': '30%', 'vertical-align': 'top', 'display': 'inline-block'}), 
            dcc.Graph(figure=fig_institutes, style={'width': '30%', 'vertical-align': 'top', 'display': 'inline-block'})
            ]

if __name__ == '__main__':
    app.run_server(debug=True)