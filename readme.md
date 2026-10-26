# Step 1 installations
- Ensure you have brew installed on your local machine
- `$brew install postgresql@18`
- `$brew install python`
- `$pip3 install psycopg`

# Step 2
- Start local postgresql server in your terminal `$brew services start postgresql`
- Extend createdb privileges to the postgres user in your terminal with this command `$psql postgres -c "ALTER USER postgres CREATEDB;"`
- To start the pipeline first in your terminal create a virtual environment `$python3 -m venv .venv`
- Run the script to create the tables and load the data `$python3 etl.py`

