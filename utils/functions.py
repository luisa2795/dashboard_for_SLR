import pandas as pd
import numpy as np
import re
from sqlalchemy import create_engine, text
from dash import dash_table, dcc
import plotly.graph_objects as go
import plotly.subplots as sub
import plotly.express as px

#DB
def initialize_engine(connection_params):
    """Initializes SQLAlchemy engine with given connection parameters, 
    enable logging the SQL output and use the future version  (2.0)
    
    Args:
        connection_params (dict): The connection parameters for the database. 
            Must contain username, password, host, port and database values.
            
    Returns:
        An SQL Alchemy engine object.
        A Psycop2 connect object.
    """
    engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        connection_params['username'], connection_params['password'], connection_params['host'], connection_params['port'], connection_params['database']), 
        future=True) 
    return engine

def load_full_table(engine, table):
    """Loads full table that is existing in the specified database table and returns it as dataframe.
    
    Args: 
        engine (SQL Alchemy engine object): The engine for the target database.
        table (str): The name of the DB table to load.
        
    Returns: 
        A pandas dataframe of the entire table.
    
    Raises:
        ValueError: If the table does not exist in the DB.
        """
    return (pd.read_sql_table(table, engine.connect()))

def load_df_from_query(engine, querystring):
    """Loads full table that is existing in the specified database table and returns it as dataframe.
    
    Args: 
        engine (SQL Alchemy engine object): The engine for the target database.
        querystring (str): The SQL SELECT statement to load the data.
        
    Returns: 
        A pandas dataframe of the selected data.
    """
    return (pd.read_sql_query(text(querystring), engine.connect()))
    
#entrypoint functions

def load_papers_with_keywords(engine):
    query="select * from aggregation_paper ap left join (select keywordgroup_pk, keyword_string from bridge_paper_keyword bpk join dim_keyword dk on bpk.keyword_pk =dk.keyword_pk) as kg_join on ap.keywordgroup_pk = kg_join.keywordgroup_pk"
    pap_kw=load_df_from_query(engine, query)
    pap_kw.drop(columns=['keywordgroup_pk'], inplace=True)
    return pap_kw

def prep_df_for_display(engine):
    pap=load_papers_with_keywords(engine)
    pap_kw=pap[['paper_pk','keyword_string']]
    #put together the keywords to a keyword string
    pap_kw=pap_kw.groupby('paper_pk')['keyword_string'].apply(', '.join).reset_index()
    final_df=pd.merge(pap_kw, pap.drop(columns='keyword_string'), how='left', on='paper_pk').rename(columns={'keyword_string': 'keywords'}).drop_duplicates().drop(columns=['citekey', 'article_source_id', 'authorgroup_pk', 'journal_pk'])
    return final_df

def search_papers_by_title(engine, keyword, searchtitle=True, searchabstract=False, searchkeywords=False): 
    if searchtitle:
        query="select * from aggregation_paper ap where title ilike '%{}%'".format(keyword)
        result=load_df_from_query(engine,query)
    return(result)

def filter_df_columns_by_keyword(df, keyword, columns_to_search):
    matches=pd.DataFrame()
    for col in columns_to_search:
        matches_col=df[df[col].str.contains(".*{}.*".format(keyword), case=False)]
        matches=pd.concat([matches, matches_col])
    return matches

def filter_entire_df_by_searchterm(df, searchterm):
    pattern=".*{}.*".format(searchterm)
    regsearch=np.vectorize(lambda x: bool(re.search(pattern, x, re.IGNORECASE)))
    dfs=df.astype(str, copy=True, errors='raise')
    res=regsearch(dfs.values).any(1)
    return df[res]

def find_child_entities(dim_ents, entity_hierarchy, parent_ent):
    children_ents=dim_ents[dim_ents['entity_pk'].isin(entity_hierarchy[entity_hierarchy['parent_entity_pk']==(dim_ents[dim_ents['entity_name']==parent_ent]['entity_pk'].values[0])]['child_entity_pk'].to_list())]
    children_names=children_ents['entity_name'].to_list()
    #escape single quotes with another single quote to avoid mistakes when querying these values from postgres
    children_names=[s.translate(str.maketrans({"'" : ""}, )) for s in children_names]
    return children_names

def filter_df_by_entity(df, dropdown_labels, implied_child_entities, entity_name, include_child_ents):
    if include_child_ents==1:
        search_ents=implied_child_entities.split(', ')
    else:
        search_ents=[entity_name]
    result_df=pd.DataFrame()
    for ent in search_ents:
        matches=df[df[dropdown_labels.lower()]==ent]
        result_df=pd.concat([result_df, matches])
    return result_df

def drill_to_level(ent_name, level, dim_ent, ent_hierarchy):
    if ent_name=='MISSING':
        return 'MISSING'
    else:
        ent_pk=dim_ent[dim_ent['entity_name']==ent_name]['entity_pk'].values[0]
        #get depth from level 0 (the maximum depth for this entity)
        all_parents=ent_hierarchy[ent_hierarchy['child_entity_pk']==ent_pk]
        depth_from_level_zero=all_parents['depth_from_parent'].max()
        #now try drill down to desired level, if that is not possible return last possible level (the initial ent itself)
        try:
            return dim_ent[dim_ent['entity_pk']==(all_parents[all_parents['depth_from_parent']==(depth_from_level_zero-level)]['parent_entity_pk'].values[0])]['entity_name'].values[0]
        except:
            return ent_name
    

#VISUALIZATION

def get_label_options(dim_entitiy_df):
    options=[]
    for ent_label in list(dim_entitiy_df.entity_label.unique()):
        options.append({'label': ent_label, 'value': ent_label})
    return options

def generate_result_table(result_df):
    return(dash_table.DataTable(
        id='search_result_table',
        columns=[{"name": i, "id": i, "selectable": True} for i in result_df.columns], #"deletable": True, 
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

def get_filtered_df_from_string_of_paper_pks(selected_pks_string, df_complete):
    #transform string back to list of integer paper_pks
    pks=selected_pks_string.split(', ')
    int_pks=[int(pk) for pk in pks]
    #get df entries of selected keys
    filtered_df=df_complete[df_complete.paper_pk.isin(int_pks)]
    return filtered_df

def get_checkboxes_from_selected_papers(selected_pks_string, df_complete):
    filtered_df=get_filtered_df_from_string_of_paper_pks(selected_pks_string, df_complete)
    options=filtered_df[['paper_pk', 'title']].apply(lambda row: {'label': str(row['paper_pk']) + ' - ' + row['title'], 'value': row['paper_pk']}, axis=1).to_list()
    return dcc.Checklist(id='analysis_papers_checklist', options=options, value=filtered_df['paper_pk'].to_list(), labelStyle={'font-size': '11px'})

def generate_parallel_categories_overview_graph(selected_pks_list, df_complete):
    filtered_df=df_complete[df_complete.paper_pk.isin(selected_pks_list)]
    #build dimensions for 3 subplots
    subject_labels=['paper_pk', 'topic', 'technology', 'theory', 'paradigm']
    subject_dimensions=[dict(values=filtered_df[label], label=label) for label in subject_labels]

    scope_labels=['paper_pk', 'sector', 'region', 'level', 'company_type', 'collection_method', 'participants']
    scope_dimensions=[dict(values=filtered_df[label], label=label) for label in scope_labels]

    methodology_labels=['paper_pk', 'conceptual_method', 'model_element', 'sampling', 'analysis_method', 'validity', 'metric']
    methodology_dimensions=[dict(values=filtered_df[label], label=label) for label in methodology_labels]

    #define figure and subplots
    fig=go.FigureWidget(sub.make_subplots(
        rows=3, cols=1, 
        specs=[[{"type": "domain"}], [{"type": "domain"}], [{"type": "domain"}]],
        subplot_titles=("Subjects", "Scope", "Methodology")
        ))

    fig.add_trace(go.Parcats(
            dimensions=subject_dimensions,
            line={'color': filtered_df.paper_pk, 'colorscale': 'turbo', 'shape':'hspline'},
            hoveron='color',
            arrangement='freeform',
        ), row=1, col=1)

    fig.add_trace(go.Parcats(
            dimensions=scope_dimensions,
            line={'color': filtered_df.paper_pk,'colorscale': 'turbo', 'shape':'hspline'},
            hoveron='color',
            arrangement='freeform'
        ), row=2, col=1)

    fig.add_trace(go.Parcats(
            dimensions=methodology_dimensions,
            line={'color': filtered_df.paper_pk, 'colorscale': 'turbo','shape':'hspline'},
            hoveron='color',
            arrangement='freeform'
        ), row=3, col=1)

    fig.update_layout(height=800)
    #fig3.update_traces(line_colorbar_showticklabels=True)

    fig.layout.annotations[0].update(y=1.05, font={'size': 18}, x=0.05, xanchor= 'left')
    fig.layout.annotations[1].update(y=0.66, font={'size': 18}, x=0.05, xanchor= 'left')
    fig.layout.annotations[2].update(y=0.275, font={'size': 18}, x=0.05, xanchor= 'left')
    return fig

def generate_bubblechart(x_value, y_value, checked_paper_pks, df_complete, dim_ent, ent_hierarchy, x_level=0, y_level=0):
    filtered_df=df_complete[df_complete.paper_pk.isin(checked_paper_pks)][[x_value, y_value]]
    filtered_df=filtered_df[(filtered_df[x_value]!='MISSING') & (filtered_df[y_value]!='MISSING')]
    #aggregate the axes to the desired level
    filtered_df[x_value]=filtered_df[x_value].apply(lambda x: drill_to_level(x, x_level, dim_ent, ent_hierarchy))
    filtered_df[y_value]=filtered_df[y_value].apply(lambda y: drill_to_level(y, y_level, dim_ent, ent_hierarchy))
    #groupby selected categories and count group sizes, then remove MISSING
    df_grouped=filtered_df.groupby([x_value, y_value]).size().reset_index(name='counts')
    #df_grouped=df_grouped[(df_grouped[x_value]!='MISSING') & (df_grouped[y_value]!='MISSING')]
    #make from long format df a wide format df
    fig=px.scatter(data_frame=df_grouped, x=x_value, y=y_value, size='counts')
    return fig


def generate_metadata_graphs(checked_paper_pks, df_complete, engine):
    filtered_df=df_complete[df_complete.paper_pk.isin(checked_paper_pks)]
    #time histogram
    nbins=round(((filtered_df.year.max()-filtered_df.year.min()).days)/365.24259)
    fig_time=go.Figure()
    fig_time.add_trace(go.Histogram(x=filtered_df.year, y=filtered_df.title, nbinsx=nbins, marker_color='#000099', opacity=0.75))
    fig_time.update_layout(bargap=0.2, title_text='Publications over time')
    #journals pie chart
    #first, get journal information for each paper in the selection
    jour_sql='select * from (select journal_pk, paper_pk, title as paper_title from dim_paper dp where paper_pk in {}) as pap left join dim_journal dj on pap.journal_pk = dj.journal_pk '.format(tuple(checked_paper_pks))
    journals_filtered=load_df_from_query(engine, querystring=jour_sql)
    fig_journals=px.pie(journals_filtered, names='title', color_discrete_sequence=px.colors.sequential.Plasma, title='Publications per journal')
    fig_journals.update_traces(textinfo='value')
    fig_journals.update_layout(
        legend=dict(
            font=dict(
                size=9
            ),
            orientation='h'
        )
    )
    #institutes pie chart
    #which authors are involved?
    auth_sql='select * from (select * from (select authorgroup_pk, paper_pk, title as paper_title from dim_paper dp where paper_pk in {}) as pap left join bridge_paper_author bpa on pap.authorgroup_pk = bpa.authorgroup_pk) as agr left join dim_author da on agr.author_pk=da.author_pk'.format(tuple(checked_paper_pks))
    authors_filtered=load_df_from_query(engine, querystring=auth_sql)
    fig_institutes=px.pie(authors_filtered, names='institution', color_discrete_sequence=px.colors.sequential.Plasma, hover_data=['country'], title='Publications per institute')
    fig_institutes.update_traces(textinfo='value')
    fig_institutes.update_layout(
        legend=dict(
            font=dict(
                size=9
            ),
            orientation='h'
        )
    )
    #fig_institutes.update_layout(uniformtext_minsize=9, uniformtext_mode='hide')
    return fig_time, fig_journals, fig_institutes



###########################
#REFERENCES VISUALIZATION
###########################

def get_barchart_of_most_relevant_citations(entity_list, engine, n_ref=15):
    #ref_topic_sql='select count(*), paper_pk, title, year, citekey from dim_paper dp where paper_pk in (select paper_pk from bridge_sentence_citation bsc where citationgroup_pk in (select citationgroup_pk from dim_sentence where sentence_pk in (select sentence_pk from fact_entity_detection fed where entity_pk in (select entity_pk from dim_entity where entity_name in {})))) group by dp.paper_pk order by count(*) desc'
    para_sql='select count(*), paper_pk, title, year, citekey from dim_paper dp where paper_pk in (select paper_pk from bridge_sentence_citation bsc where citationgroup_pk in (select citationgroup_pk from dim_sentence where paragraph_pk in (select paragraph_pk from dim_sentence ds where sentence_pk in (select sentence_pk from fact_entity_detection fed where entity_pk in (select entity_pk from dim_entity where entity_name in {}))))) group by dp.paper_pk order by count(*) desc'
    if len(entity_list)==1:
        df_ref=load_df_from_query(engine, para_sql.format("('" + entity_list[0] + "')"))
    else:
        df_ref=load_df_from_query(engine, para_sql.format(tuple(entity_list)))
    #drop missing titles
    df_ref=df_ref[~(df_ref['title']=='MISSING')]
    #aggregate the same titles by their sum of count
    for_bar=df_ref.groupby(by='title')['count'].agg('sum').reset_index()
    #get the n_ref most popular titles
    for_bar=for_bar.sort_values(by='count', ascending=True, ignore_index=True)[-n_ref:]
    fig_bar=px.bar(
        for_bar, x='count', y='title', 
        color_discrete_sequence=px.colors.sequential.Plasma, 
        text='title',
        labels={'title': 'reference title', 'count': 'times referenced for selected entities'}) #, height=600
    fig_bar.update_yaxes(showticklabels=False)
    fig_bar.update_traces(textfont_size=10, textposition='inside')
    return fig_bar

def non_missing_longest(ser):
    ser=ser[~ser.str.contains('MISSING')]
    if ser.size!=0:
        return max(ser, key=len)
    else:
        return 'MISSING'

def get_barchart_of_most_influential_authors(entity_list, engine, n_ref=15):
    auth_sql='''
    select *, count(*) from dim_author da where author_pk in (
    select author_pk from bridge_paper_author bpa where authorgroup_pk in (
    select authorgroup_pk from dim_paper where paper_pk in (
    select paper_pk from bridge_sentence_citation bsc where citationgroup_pk in (
    select citationgroup_pk from dim_sentence where paragraph_pk in (
    select paragraph_pk from dim_sentence ds where sentence_pk in (
    select sentence_pk from fact_entity_detection fed where entity_pk in (
    select entity_pk from dim_entity where entity_name in {})))))))
    group by da.author_pk 
    order by count(*) desc'''
    if len(entity_list)==1:
        df_aut=load_df_from_query(engine, auth_sql.format("('" + entity_list[0] + "')"))
    else:
        df_aut=load_df_from_query(engine, auth_sql.format(tuple(entity_list)))
    aut_gr=df_aut.groupby(['surname']).agg({
        'firstname': non_missing_longest,
        'middlename': non_missing_longest,
        'email': non_missing_longest,
        'department': non_missing_longest,
        'institution': non_missing_longest,
        'country': non_missing_longest,
        'count': 'sum'
    }).reset_index()
    aut_gr=aut_gr.sort_values(by='count', ascending=True, ignore_index=True)[-15:]
    aut_fig=px.bar(
        aut_gr, x='count', y='surname', 
        color_discrete_sequence=px.colors.sequential.Plasma, 
        #text='firstname', 
        hover_data=['surname', 'firstname', 'middlename', 'email', 'department', 'institution', 'country']
        )
    aut_fig.update_traces(textangle=0)
    return aut_fig
