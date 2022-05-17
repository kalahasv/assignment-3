# Million Searches per Second (MSPS not related to MIPS i swear)
## Installation Instructions
1. Install MySQL >= 8.0 or MariaDB >= 10.0
2. Install dependencies from requirements.txt
3. Import search_engine.sql
4. Execute the following SQL statement
> GRANT ALL PRIVILEGES ON search_engine.* to 'search'@'localhost' identified by '';
4. Run indexer.py and wait for completion
5. Run search.py or webserver.py