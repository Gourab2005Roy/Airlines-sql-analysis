# Importing libraries.
import sqlite3 # Connects Python to SQLite databases.
import pandas as pd  # Provides DataFrames for data analysis.
import matplotlib.pyplot as plt  # Visualization
import warnings # Controls warning message.
warnings.filterwarnings('ignore') # Suppress warning message.

# Database Connection.
connection = sqlite3.connect("airlines.db")
# Connects to the airlines database.
cursor = connection.cursor() # cursor is used for executing the SQL query.

# Check available tables
# "Show me the names of all tables present in this database."
cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table';
""")

print('List of tables present in the database')
table_list = [table[0] for table in cursor.fetchall()] # List comprehension.
print(table_list)



# Data Exploration of aircraft.
aircraft = pd.read_sql_query("SELECT * FROM aircraft", connection)  # "Retrieve every column and every record from the aircraft table."
print(aircraft.head())       # First five rows.
print(aircraft)              # Display the DataFrame.
print(aircraft.to_string())  # Display all rows and columns.

# Data Exploration of airports.
airports = pd.read_sql_query("SELECT * FROM airports", connection)  # "Retrieve every column and every record from the airports table."
print(airports.head())       # First five rows.
print(airports)              # Display the DataFrame.
print(airports.to_string())  # Display all rows and columns.

# Data Exploration of airlines.
airlines = pd.read_sql_query("SELECT * FROM airlines", connection)  # "Retrieve every column and every record from the airlines table."
print(airlines.head())       # First five rows.
print(airlines)              # Display the DataFrame.
print(airlines.to_string())  # Display all rows and columns.

# Data Exploration of flights.
flights = pd.read_sql_query("SELECT * FROM flights", connection)  # "Retrieve every column and every record from the flights table."
print(flights.head())       # First five rows.
print(flights)              # Display the DataFrame.
print(flights.to_string())  # Display all rows and columns.

# Data Exploration of passengers.
passengers = pd.read_sql_query("SELECT * FROM passengers", connection) # "Retrieve every column and every record from the passengers table."
print(passengers.head())    # First five rows.
print(passengers)           # Display the DataFrame.
print(passengers.to_string()) # Display all rows and columns.

# Data Exploration of bookings.
bookings = pd.read_sql_query("SELECT * FROM bookings", connection) # "Retrieve every column and every record from teh bookings table."
print(bookings.head())      # First five rows.
print(bookings)             # Display the DataFrame.
print(bookings.to_string()) # Display all rows and columns.