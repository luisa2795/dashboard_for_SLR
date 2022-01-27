import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
#from dash_extensions.enrich import DashProxy, MultiplexerTransform
#import plotly.express as px
import pandas as pd
import utils.functions as fu
from utils.db_credentials import dwh_db_connection_params
from dash.exceptions import PreventUpdate
#import dash_daq as daq
import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.FLATLY ] # dbc.themes.QUARTZ is the most beautiful one but less serious, FLATLY https://codepen.io/chriddyp/pen/bWLwgP.css

engine=fu.initialize_engine(dwh_db_connection_params)
dim_ent=fu.load_full_table(engine, 'dim_entity')
ent_hierarchy=fu.load_full_table(engine, 'map_entity_hierarchy')
#df=fu.load_full_table(engine, 'aggregation_paper')
df_k=fu.prep_df_for_display(engine)

#app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])
app=dash.Dash(__name__ , external_stylesheets=external_stylesheets, suppress_callback_exceptions=True) #prevent_initial_callbacks=True


tab_info_content=dbc.Card(
    dbc.CardBody(
        [
            html.H1('Welcome to the Systematic Review Dashboard'),
            html.P(
                'This Dashboard was designed on top of a Data-Warehouse of Scientific Literature and can help you understand the current state of research '
                'or to find suitable papers to quote for a specific methodology. Try it out!',
                className='lead'), 
            html.Hr(),
            dcc.Markdown(
                '''Under the tab **Publication analysis** you can search publications by keyword or by entities (such as topic, region or conceptual method) and visualize
                similarities and differences between publications, analyse publications metadata and see detailed infos about a specific paper.    
                The tab **Reference search** is designed to help you for example with your theoretical concepts / methodology chapter. Which paper and which authors have been quoted often
                for your concept of interest? '''
            ),
            dbc.Button('Learn more', id='collapse_project_info', n_clicks=0),
            html.Br(),
            dbc.Collapse(
                id='project_info',
                is_open=False,
                children=[
                    html.Div(children=[
                        html.Div([
                            html.Div([
                                dbc.Button('Corpus', color='success', id='corpus_btn', n_clicks=0, style={'width': '100%'}),
                                dbc.Collapse(
                                    id='corpus_info',
                                    children=['The included papers are taken from the top eight journals in the domain of information systems and were published between 1989 and September 2021.'],
                                    is_open=False
                                )
                            ],
                            style={'padding': '10px', 'display': 'inline-block', 'width': '50%', 'vertical-align': 'top'}),
                            html.Div([
                                dbc.Button('Knowledge extraction', color='success', id='know_btn', n_clicks=0, style={'width': '100%'}),
                                dbc.Collapse(
                                    id='ke_info',
                                    children=[
                                        dcc.Markdown(
                                            '''Prior project work developed CauseMiner2, an analysis pipeline to transform the paper PDFs to XML and embed citations. 
                                            With an IS Research Ontology and a custom sentence tagging module, entities (= structured domain knowledge) can be recognized 
                                            in the preprocessed corpus. The analysed papers with recognized entities for each sentence were stored in CSV files of 
                                            different aggregation level.'''
                                        )
                                    ],
                                    is_open=False
                                )
                            ],
                            style={'padding': '10px', 'display': 'inline-block', 'width': '50%', 'vertical-align': 'top'}),
                        ]),
                        html.Div([
                            html.Div([
                                dbc.Button('Data warehouse', color='success', id='dwh_btn', n_clicks=0, style={'width': '100%'}),
                                dbc.Collapse(
                                    id='dwh_info',
                                    children=[
                                        dcc.Markdown(
                                            '''The CSV files have been transformed and loaded into a Data Warehouse with a snowflake schema around the fact of an entity 
                                            detection. The schema was designed to answer typical questions that have to be answered during a literature review. It shall 
                                            provide the option to quickly grasp the current body of knowledge around a topic of interest and be able to compare publications 
                                            around this topic. At the same time it shall provide enough details to drill down to the detailed content of one paper, in order 
                                            to provide explainability for the user.'''
                                        )
                                    ],
                                    is_open=False
                                )
                            ],
                            style={'padding': '10px', 'display': 'inline-block', 'width': '50%', 'vertical-align': 'top'}),
                            html.Div([
                                dbc.Button('This dashboard', color='success', id='dashb_btn', n_clicks=0, style={'width': '100%'}),
                                dbc.Collapse(
                                    id='da_info',
                                    children=[
                                        dcc.Markdown(
                                            '''This dashboard was designed to help users interact with the data warehouse easily. It provides abstractions of probable 
                                            SQL statements that users would want to execute on the DWH in a literature review situation. 
                                            Results are displayed in visually appealing manner.'''
                                        ) 
                                    ],
                                    is_open=False
                                )
                            ],
                            style={'padding': '10px', 'display': 'inline-block', 'width': '50%', 'vertical-align': 'top'}),
                        ]),
                        html.Br(),
                        html.Div([html.Img(src=app.get_asset_url('architecture.png'))],style={'width':'80%', 'margin': 'auto'}),
                        html.Br(),
                        dcc.Markdown(
                            '''_For feedback on this tool or if you would need to extract different data from the DWH, 
                            please contact s_waack20@stud.hwr-berlin.de_''')
                
                    ],
                    style={'padding': '10px', 'width': '80%', 'margin': 'auto'})
                ]
            )
        ]
    )
)

tab_paper_analysis=dbc.Card(
    dbc.CardBody(
        [
            html.Div(id='search papers', children=[
                html.H2('Understand the current body of knowledge for your topic'),
                dcc.Markdown('_Either search a phrase to find papers containing the terms of your interest **OR** directly search a paper by an entity._'),
                html.Hr(),
                html.Div(children=[
                    html.Div([
                        html.H5("Search phrase in column: "),
                        dbc.Input(id='search_term', type='text', placeholder='Type something', style={'width': '80%'}),#, value='ontology'
                        html.Br(),
                        "Select Column: ",
                        dbc.Checklist(id='columns_to_search',
                            options=[
                                {'label': 'Title', 'value': 'title'},
                                {'label': 'Keywords', 'value': 'keywords'},
                                {'label': 'Abstract', 'value': 'abstract'},
                                {'label': 'search all fields', 'value': 'entire_df'},
                            ],
                            value=['keywords']
                        ),
                        html.Br(),
                        dbc.Button(id='submit_search_strings_button', n_clicks=0, children='Submit keyword search')
                        ],
                        style={'width': '30%', 'display': 'inline-block', 'padding': '10px', 'border-right-style': 'solid', 'border-right-color': 'lightgrey', 'border-right-width': 'thin' } #, 'border-style': 'solid', 'border-width': '1px', 'border-color': '#b1dcfa'
                    ),
                    html.Div(children=[
                        html.H5("Search entities: "),
                        html.Div([
                            html.Div([
                                'entity category: ',
                                dbc.Select(id='dropdown_labels', options=fu.get_label_options(dim_ent),
                                    )#value='TOPIC'
                            ],
                            style={'width': '29%','padding': '10px', 'vertical-align': 'top', 'display': 'inline-block'}),
                            html.Div([
                                'available entities: ',
                                dbc.Select(id='entity_name')
                            ],
                            style={'width': '29%', 'padding': '10px', 'vertical-align': 'top', 'display': 'inline-block'}),
                            html.Div([
                                'include child entities?',
                                dbc.RadioItems(id='include_child_ents',
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
                        dbc.Button(id='submit_entity_search', n_clicks=0, children='Submit Entity Search')
                        ], 
                        style={'width': '60%', 'float': 'right', 'display': 'inline-block', 'padding': '10px'}
                        )
                ]),   
                    html.Br(),
                    dcc.Markdown(id='searched_term'),
                    dcc.Markdown(id='filter_info'),
                    html.Br(),
                    dcc.Loading(id='loading1', type='cube', color='#18bc9c',children=[
                        html.Div(id='search_output', children=dash_table.DataTable(id='search_result_table')),
                        html.Div(id='for_select_all_btn')
                        ])
            ]),
            html.Div(id='analyse_papers', children=[
                html.Div(id='manual_selected_papers'),
                html.Br(),
                html.Div(id='for_analysis_button'),#, style={'padding': '10px', 'display':'inline-block'}),
                #html.Div(id='for_reset_selection_button', style={'padding': '10px', 'display':'inline-block'}),
                html.Br(),
                html.Div(id='for_paper_checkboxes'),
                html.Div(id='for_accordion_div')
            ]),
        ]
    )
)

tab_ref_analysis=dbc.Card(
    dbc.CardBody(
        [
            html.H2('Which sources have been referenced often for your topic?'),
            html.Div(
                [
                    html.Div([
                        'Entity Label: ',
                        dcc.Dropdown(id='dropdown_labels_ref', options=fu.get_label_options(dim_ent),
                            )#value='TOPIC'
                    ],
                    style={'width': '29%','padding': '10px', 'vertical-align': 'top', 'display': 'inline-block'}),
                    html.Div([
                        'available entities: ',
                        dcc.Dropdown(id='entity_name_ref', 
                        )#value='open source'
                    ],
                    style={'width': '29%', 'padding': '10px', 'vertical-align': 'top', 'display': 'inline-block'}),
                    html.Div([
                        'include child entities?',
                        dbc.RadioItems(
                            id='include_child_ents_ref',
                            options=[
                                {'label': 'Yes', 'value': 1},
                                {'label': 'No', 'value': 0}
                            ],
                            value=0
                        ),
                        html.Div(id='implied_child_entities_ref')
                    ],
                    style={'width': '22%', 'padding': '10px', 'vertical-align': 'top', 'display': 'inline-block'})
                ]
            ),
            dbc.Button(id='entity_search_ref_btn', n_clicks=0, children='Submit entity search'),
            html.Br(),
            html.Div(id='for_ref_results')
        ]
    )
)

app.layout=dbc.Container(
    [
        dbc.Tabs(
            [
                dbc.Tab(tab_info_content, label='Info'),
                dbc.Tab(tab_paper_analysis, label='Publication analysis'),
                dbc.Tab(tab_ref_analysis, label='Reference search')
            ]
        )    
    ],
    fluid=True
       
)
#CALLBACK FUNCTIONS FOR INFO TAB
@app.callback(
    Output(component_id='project_info', component_property='is_open'), 
    [Input(component_id='collapse_project_info', component_property='n_clicks')],
    [State(component_id='project_info', component_property='is_open')]
)
def toggle_project_info(open_click, is_open):
    if open_click:
        return not is_open
    return is_open

@app.callback(
    Output(component_id='corpus_info', component_property='is_open'),
    [Input(component_id='corpus_btn', component_property='n_clicks')],
    [State(component_id='corpus_info', component_property='is_open')]
)
def toggle_corpus_info(open_click, is_open):
    if open_click:
        return not is_open
    return is_open

@app.callback(
    Output(component_id='ke_info', component_property='is_open'),
    [Input(component_id='know_btn', component_property='n_clicks')],
    [State(component_id='ke_info', component_property='is_open')]
)
def toggle_knowledge_extraction_info(open_click, is_open):
    if open_click:
        return not is_open
    return is_open

@app.callback(
    Output(component_id='dwh_info', component_property='is_open'),
    [Input(component_id='dwh_btn', component_property='n_clicks')],
    [State(component_id='dwh_info', component_property='is_open')]
)
def toggle_dwh_info(open_click, is_open):
    if open_click:
        return not is_open
    return is_open

@app.callback(
    Output(component_id='da_info', component_property='is_open'),
    [Input(component_id='dashb_btn', component_property='n_clicks')],
    [State(component_id='da_info', component_property='is_open')]
)
def toggle_dashboard_info(open_click, is_open):
    if open_click:
        return not is_open
    return is_open

#CALLBACK FUNCTIONS FOR PUBLICATION ANALYSIS TAB
@app.callback(
    [
        Output(component_id='searched_term', component_property='children'),
        Output(component_id='filter_info', component_property='children'),
        Output(component_id='for_select_all_btn', component_property='children'),
        Output(component_id='search_output', component_property='children'),
        #Output(component_id='for_reset_selection_button', component_property='children')
    ],
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
                result_df=fu.filter_df_columns_by_searchterm(df_k, search_term, columns_to_search)
            searchterm='##### You searched the **phrase:** {}'.format(search_term)
            table=fu.generate_result_table(result_df) 
        else:
            result_df=fu.filter_df_by_entity(df_k, dropdown_labels, implied_child_entities, entity_name, include_child_ents)
            if include_child_ents==1:
                entity_name=str(implied_child_entities)
            searchterm='##### You searched the **entity:** {}'.format(entity_name)
            table=fu.generate_result_table(result_df)
        filter_info='_You can further **filter** the data by any column to find relevant papers. To analyse papers further, **select them with a checkbox** and click the button to **move to analysis**_.'
        return [
            searchterm, 
            filter_info, 
            dbc.Button(id='select_all_button', n_clicks=0, children='Select all', color='info'), 
            table
            #dbc.Button(id='reset_selection_btn', n_clicks=0, children='Reset selection')
        ]
    

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
    if chosen_entity is None:
        raise PreventUpdate
    else:
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
    Input(component_id='search_result_table', component_property='derived_virtual_selected_rows'),
    #Input(component_id='reset_selection_btn', component_property='n_clicks')
)

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
        return dbc.Button(id='move_to_analysis_button', n_clicks=0, children='Search finished, move to analysis')
    else: 
        raise PreventUpdate


@app.callback(
    [
        Output(component_id='for_paper_checkboxes', component_property='children'),
        Output(component_id='for_accordion_div', component_property='children')
    ],
    Input(component_id='move_to_analysis_button', component_property='n_clicks'),
    State(component_id='manual_selected_papers', component_property='children')
)
def show_accordion(analysis_clicks, selected_papers_string):
    if analysis_clicks!=0:
        return [
            [
                dbc.Offcanvas(children=[
                    html.H3('Your selected Papers'),
                    html.Hr(),
                    html.P('When you feel that some papers from your initial selection seem not to fit anymore after you have seen more details, uncheck them here to remove them from the analysis.'),
                    html.Div(children=[
                        dcc.Markdown('_To come back here click  _', style={'display':'inline-block'}),
                        dbc.Button('edit selection of papers', color='secondary', size='sm', style={'display':'inline-block'}),
                        dcc.Markdown('_in the main page._', style={'display':'inline-block'})
                    ]),
                    html.Br(),
                    fu.get_checkboxes_from_selected_papers(selected_papers_string, df_k) 
                    ],
                    id='selection_offcanvas', is_open=True),
                dbc.Button(id='open_offcanvas_1', children='edit selection of papers', color='secondary', n_clicks=0),
                html.Br(),
                html.Br(),
                html.H4('Analysis Options:')
            ],
            dbc.Accordion(
                id='analysis_accordion',
                children=[
                    dbc.AccordionItem(
                        title='Compare all categories in an overview',
                        children=[
                            html.Div(id='too_many_papers_warning'),
                            dbc.Button(id='open_offcanvas', children='edit selection of papers', color='secondary', n_clicks=0),
                            dbc.Button(id='content_comparison_button', n_clicks=0, children='Okay, go!'),
                            html.Br(),
                            html.Div(id='parallel_categories_overview'),
                            html.Br(),
                        ],
                        item_id='parcats_item'
                    ),
                    dbc.AccordionItem(
                        title='Compare categories in detail',
                        children=[
                            html.Div(
                                [
                                    html.P('Select x-axis and drill down or roll up the selected category. Highest aggregation: 0'),
                                    dbc.Select(id='x_axis', placeholder='Select x-axis category', options=fu.get_label_options(dim_ent), style={'width': '20%', 'display':'inline-block', 'padding': '5px'}),
                                    dbc.Input(id='x_level', type='number', min=0, max=8, step=1, value=1, style={'width': '10%', 'display':'inline-block', 'padding': '5px'}),
                                ],
                                style={'padding': '10px'}
                            ),
                            html.Div(
                                [
                                    
                                    html.P('Select y-axis and drill down or roll up the selected category. Highest aggregation: 0'),
                                    dbc.Select(id='y_axis', placeholder='Select x-axis category', options=fu.get_label_options(dim_ent), style={'width': '20%', 'display':'inline-block', 'padding': '5px'}),
                                    dbc.Input(id='y_level', type='number', min=0, max=8, step=1, value=1, style={'width': '10%', 'display':'inline-block', 'padding': '5px'}),
                                ],
                                style={'padding': '10px'}
                            ),
                            dbc.Button(id='submit_axes', children='Go!', n_clicks=0),
                            html.Div(
                                [
                                    dbc.Spinner(html.Div(id='div_for_bubblechart'))
                                ]
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title='Compare metadata (publishing year, main journals and institutes)',
                        children=[
                            dbc.Spinner(html.Div(id='metadata_figures')),
                            html.Br(),
                            dbc.Button(id='analyse_metadata_button', n_clicks=0, children='update metadata figures')
                        ],
                        item_id='metadata_item'
                    ),
                    dbc.AccordionItem(
                        title='Analyse a paper in detail',
                        children=[
                            html.Div(children=[
                                'Select Paper for Detail Analysis',
                                dbc.Select(
                                    id='detail_pk_sel',
                                    options=fu.get_title_dropdown(selected_papers_string, df_k),
                                    style={'width': '80%'}
                                ),
                                html.Div(id='for_detail_analysis')
                            ])
                        ]
                    )
                ],
                start_collapsed=True,
                flush=True
            )
        ]
    else: 
        raise PreventUpdate

@app.callback(
    Output(component_id='selection_offcanvas', component_property='is_open'),
    Input(component_id='open_offcanvas', component_property='n_clicks'),
    Input(component_id='open_offcanvas_1', component_property='n_clicks'),
    [State(component_id='selection_offcanvas', component_property='is_open')]
)
def toggle_offcanvas(n_clicks, n_clicks1, is_open):
    if n_clicks or n_clicks1:
        return not is_open
    return is_open

@app.callback(
    Output(component_id='too_many_papers_warning', component_property='children'),
    Input(component_id='analysis_accordion', component_property='active_item'),
    State(component_id='analysis_papers_checklist', component_property='value')
)
def update_too_many_papers_warning(item, checked_papers):
    if item=='parcats_item':
        no_papers=len(checked_papers)
        if no_papers>15:
            warning_message=html.P('You selected more than 15 papers. The following diagram will be hard to read and will probably take long to compute. Consider reducing your selection or rather use the function to compare only two categories in detail.', style={'color': '#e74c3c'})
        else:
            warning_message=html.P('You will get an overview over the the papers similarities and differences in the different content categories (entities) :-)', style={'color':'#18bc9c'})
        return warning_message
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
    Output(component_id='div_for_bubblechart', component_property='children'),
    Input(component_id='submit_axes', component_property='n_clicks'),
    State(component_id='x_axis', component_property='value'),
    State(component_id='x_level', component_property='value'),
    State(component_id='y_axis', component_property='value'),
    State(component_id='y_level', component_property='value'),
    State(component_id='analysis_papers_checklist', component_property='value')
)
def update_category_bubbles(n_clicks, x_value, x_level, y_value, y_level, checked_paper_pks):
    if not n_clicks:
        raise PreventUpdate
    else: 
        if not x_value:
            return 'Select x-axis first.'
        elif not y_value:
            return 'Select y-axis first.'
        else:
            fig_bubble=fu.generate_bubblechart(x_value.lower(), y_value.lower(), checked_paper_pks, df_k, dim_ent, ent_hierarchy, x_level=x_level, y_level=y_level)
            return dcc.Graph(figure=fig_bubble)


@app.callback(
    Output(component_id='metadata_figures', component_property='children'),
    Input(component_id='analyse_metadata_button', component_property='n_clicks'),
    Input(component_id='analysis_accordion', component_property='active_item'),
    State(component_id='analysis_papers_checklist', component_property='value')
)
def update_metadata_analysis(n_clicks, active_accordion_item, checked_paper_pks):
    if n_clicks==0 and active_accordion_item!='metadata_item':
        raise PreventUpdate
    else:
        fig_time, fig_journals, fig_institutes=fu.generate_metadata_graphs(checked_paper_pks, df_k, engine)
        return [
           dcc.Graph(figure=fig_time, style={'width': '40%', 'vertical-align': 'top', 'display': 'inline-block'}), 
           dcc.Graph(figure=fig_journals, style={'width': '30%', 'vertical-align': 'top', 'display': 'inline-block'}), 
           dcc.Graph(figure=fig_institutes, style={'width': '30%', 'vertical-align': 'top', 'display': 'inline-block'})
        ]

@app.callback(
    Output(component_id='for_detail_analysis', component_property='children'),
    Input(component_id='detail_pk_sel', component_property='value')
)
def update_detail_analysis(paper_key):
    if not paper_key:
        raise PreventUpdate
    else:
        summary_div=fu.get_summary_fields(paper_key, engine, dim_ent)
        return summary_div

@app.callback(
    Output(component_id='for_detail_pie', component_property='children'),
    Input(component_id='pie_label_sel', component_property='value'),
    Input(component_id='pie_level', component_property='value'),
    Input(component_id='detail_pk_sel', component_property='value')
)
def update_pie_details(category_label, level, paper_pk):
    if not category_label:
        raise PreventUpdate
    elif not level:
        raise PreventUpdate
    else:
        return fu.generate_detail_piechart_or_hist(paper_pk, category_label, level, engine, dim_ent, ent_hierarchy, fig_type='pie')

@app.callback(
    Output(component_id='for_detail_hist', component_property='children'),
    Input(component_id='hist_label_sel', component_property='value'),
    Input(component_id='hist_level', component_property='value'),
    Input(component_id='detail_pk_sel', component_property='value')
)
def update_hist_details(category_label, level, paper_pk):
    if not category_label:
        raise PreventUpdate
    elif not level:
        raise PreventUpdate
    else:
        return fu.generate_detail_piechart_or_hist(paper_pk, category_label, level, engine, dim_ent, ent_hierarchy, fig_type='hist')


#CALLBACK FUNCTIONS FOR REFERENCE SEARCH TAB
@app.callback(
    Output(component_id='entity_name_ref', component_property='options'),
    Input(component_id='dropdown_labels_ref', component_property='value')
)
def update_entity_options_ref(dropdown_label):
    options=[]
    for ent_name in dim_ent[dim_ent['entity_label']==dropdown_label]['entity_name'].to_list():
        options.append({'label': ent_name, 'value': ent_name})
    return options

@app.callback(
    Output(component_id='implied_child_entities_ref', component_property='children'),
    Input(component_id='entity_name_ref', component_property='value'),
    Input(component_id='include_child_ents_ref', component_property='value')
)
def display_included_entitiy_children_ref(chosen_entity, include_child_ents):
    if chosen_entity is None:
        raise PreventUpdate
    else:
        if include_child_ents==1:
            child_ents=fu.find_child_entities(dim_ent, ent_hierarchy, chosen_entity)
        else:
            child_ents=[]
        return (', '.join(child_ents))

@app.callback(
    Output(component_id='for_ref_results', component_property='children'),
    Input(component_id='entity_search_ref_btn', component_property='n_clicks'),
    State(component_id='entity_name_ref', component_property='value'),
    State(component_id='implied_child_entities_ref', component_property='children')
)
def update_reference_results(button_submit, ent_name, child_entities):
    if button_submit==0:
        raise PreventUpdate
    else:
        if child_entities:
            search_ents=child_entities.split(', ')
        else:
            search_ents=[ent_name]
        title_fig=fu.get_barchart_of_most_relevant_citations(search_ents, engine, 15)
        aut_fig=fu.get_barchart_of_most_influential_authors(search_ents, engine, 15)
        return html.Div([
            dcc.Graph(id='most_pop_ref', figure=title_fig),
            dcc.Graph(id='most_influential_authors', figure=aut_fig)
        ])


if __name__ == '__main__':
    app.run_server(debug=True)