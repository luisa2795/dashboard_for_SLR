import pandas as pd
from sqlalchemy import create_engine, text
#import re

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

def get_papers_with_keywords(engine):
    query="select * from aggregation_paper ap left join (select keywordgroup_pk, keyword_string from bridge_paper_keyword bpk join dim_keyword dk on bpk.keyword_pk =dk.keyword_pk) as kg_join on ap.keywordgroup_pk = kg_join.keywordgroup_pk"
    return(load_df_from_query(engine, query))

def search_papers_by_title(engine, keyword, searchtitle=True, searchabstract=False, searchkeywords=False): 
    if searchtitle:
        query="select * from aggregation_paper ap where title ilike '%{}%'".format(keyword)
        result=load_df_from_query(engine,query)
    return(result)

def filter_df_by_title(df, keyword):
    matches=df[df['title'].str.contains(".*{}.*".format(keyword), case=False)]
    return matches

def filter_df_by_keyword(df, keyword):
    matches=df[df['keyword_string'].str.contains(".*{}.*".format(keyword), case=False)]
    return matches

def filter_df_by_title_keywords_and_abstract(df, keyword):
    #TODO
    matches=df[df['title'].str.contains(".*{}.*".format(keyword), case=False)]
    return matches