# dashboard_for_SLR
Dashboard to search, filter and analyse scientific literature in a semi-automated way

### How to run:
1. Place a file called _credentials.py_ in the _utils_ subfolder. It should contain the variable DB_CONNECTION_PARAMS to successfully connect to the database of the underlying Data Warehouse.
   > DB_CONNECTION_PARAMS = {
    'username': '<your_username>',
    'password': '<your_password>',
    'host': '<IP_of_the_server>',
    'port': <your_db_port>,
    'database': '<your_db_name>'
}
2. Install the packages defined in _requirements.txt_ in a fresh Python 3.9 environment.
3. Run the _app.py_ file. The dashboard will be available at http://127.0.0.1:8050/. You can open it by accessing this address in your browser (Chrome works best).

### Where is the data:
The data used in this dashboard comes from a data warehouse of scientific literature. For more information on this, please check out https://github.com/luisa2795/datawarehouse_for_SLR.git. The data warehouse is located in a local PostgreSQL database, provided for this thesis.

### How does the logic work:
- The dashboard layout is defined in the _app.py_ file. It
- The first tab (_Info_) is a static info tab.
- All features are in the second tab (_Publication analysis_):
  - The paper data is loaded first from the database. It is the aggregation table of papers joined with the respective keywords. This global dataframe is not altered during a session. 
  - 

