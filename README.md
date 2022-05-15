1. Install MySQL and dependencies
2. Import search_engine.sql
3. Execute the following SQL statement
# GRANT ALL PRIVILEGES ON search_engine.* to 'search'@'localhost' identified by '';
4. Run indexer.py and wait for completion
5. Run search.py