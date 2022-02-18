# dashboard_for_SLR
Dashboard to search, filter and analyse scientific literature in a semi-automated way

## How to run:
1. First of all, ssh to zeno and clone the repository here. (We are using a database which does not expose a web-socket to the internet, therefore the code has to be executed on the same machine as the DB..)
2. Place a file called _credentials.py_ in the _utils_ subfolder. It should contain the variable DB_CONNECTION_PARAMS to successfully connect to the database of the underlying Data Warehouse.
   ```
   DB_CONNECTION_PARAMS = {
    'username': '<your_username>',
    'password': '<your_password>',
    'host': '<IP_of_the_server>',
    'port': <your_db_port>,
    'database': '<your_db_name>'
   }
   ``` 
2. Install the packages defined in _requirements.txt_ in a fresh Python 3.9 environment. 
   ```
   python3.9 -m venv dashvenv
   source dashvenv/bin/activate
   pip install -r requirements.txt
   ```
   Check if all packages have been installed completely with ```pip freeze```. There is an odd issue that sometimes, the package psycopg2 does not get installed from the requirements. If this is the case run ```pip install psycopg2-binary```.
3. Run the _app.py_ file. The dashboard will be available at http://127.0.0.1:8050/. You can open it by accessing this address in your browser (Chrome works best).

## Where is the data:
The data used in this dashboard comes from a data warehouse of scientific literature. For more information on this, please check out https://github.com/luisa2795/datawarehouse_for_SLR.git. The data warehouse is located in a local PostgreSQL database on zeno, provided for this thesis.

## How does the logic work:
- The dashboard layout is defined in the _app.py_ file. After package and stylesheet import, the DB engine is initialized and all required data (some modified paper table, entities and the entity hierarchy) is loaded from the DB into dataframes. These global dataframes are not altered during a session.
- The app is initialized as Dash app and the layout of the two tabs of the application is defined. The first tab (_Info_) is a static info tab, all advanced features are in the second tab (_Publication analysis_). The layout is defined as dash components, which wrap HTML in Python code.
- All interactions that are possible in the interface are defined via callbacks. 
  - A callback is defined with the decorator @callback and then the Input and Output components in parentheses behind. 
  - An Input/Output component is identified via its id. To determine which property triggers an execution of the callback or which proerty is changed by the callback function, the property of each Input or Output is specified.
  - After the callback decorator a Python function is defined. Its parameters are the defined Input component properties in the respective order. This is the function that is always executed when a callback is triggered.
  - The order in which callbacks are defined in the app script does not matter but it was tried to order them in their natural execution order.

- For better readability, longer function definitions have been outsourced into the file _utils/functions.py_
- At the end of the app definition script, the server is started with ```app.run_server()```.
