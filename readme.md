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
| DATE |office_name_cnt| Visitors |
| -------- | -------- | -------- |
| "2015-02-01"  | 10	| 197    | 
| "2015-02-02"  | 10	| 176    | 
| "2015-02-03"  | 10	| 347    | 
| "2015-02-04"  | 10	|  225   | 
| "2015-02-05"  | 10	|   197  | 
| "2015-02-06"  | 10	|  222   | 
| "2015-02-07"  | 10	|  270   | 