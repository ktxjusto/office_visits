# Step 1 installations
- Ensure you have brew installed on your local machine
- `$brew install postgresql@18`
- `$brew install python`
- Create a virtual environment `$source .venv/bin/activate`
- Install the dependencies `$python -m pip install -r requirements.txt`

# Step 2
- Start local postgresql server in your terminal `$brew services start postgresql`
- Extend createdb privileges to the postgres user in your terminal with this command `$psql postgres -c "ALTER USER postgres CREATEDB;"`
- Run the script to create the tables and load the data `$python3 etl.py`


# Answer to the problem
