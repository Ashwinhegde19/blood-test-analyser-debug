import sqlalchemy

# The task ID from our test
TASK_ID = "d64f2dc0-b732-4018-9ea6-ee07fb3c999e"

# Connect to the database
engine = sqlalchemy.create_engine("sqlite:///./blood_test_analyser.db")
connection = engine.connect()

# Execute a raw SQL query
query = sqlalchemy.text(f"SELECT * FROM analysis_results WHERE id = '{TASK_ID}'")
result = connection.execute(query).fetchone()

# Print the result
if result:
    print("--- Record Found in Database ---")
    print(f"ID:     {result[0]}")
    print(f"Status: {result[1]}")
    print(f"Result: {result[2]}")
    print(f"Error:  {result[3]}")
    print("--------------------------------")
else:
    print(f"No record found for task ID: {TASK_ID}")

connection.close()
