# Chat with Beekipedia: A Confluence RAG chat client 

This client is designed to enable easier access to information and knowledge stored in Roambee's vast Confluence knowledge base. Currently, the only indexed spaces are the Roambee Beekipedia and BeeHow spaces, but as the pages get fleshed out and uneneccessary documents are pruned, additional spaces will be added. 

## FOR DEVOPS:
* **Python Version:** Project developed and built on Python 3.12, and uses the python:3.12-slim docker image.
* **Images:** The project uses the following docker images:
  * **streamlit_app**: The streamlit_app image is defined in the root directory, /ConfluenceRag. This image is built on top of the python:3.12-slim image, and includes all the necessary packages for running the streamlit app.
  * **chroma**: The chroma image runs the remote ChromaDB server. Currently the host defined as "chromadb", as per the service name in docker-compose. In deployment, the environment variable ```CHROMADB_HOST``` should be the url the application is deployed too. This image is built on top of the python:3.12-slim image, and includes all the necessary packages for running a chroma db.
  * **cron_job**: The cron_job image executes the ```update_chroma_db.py``` script every 24 hours via a Crontab. There was an issue in running both the Cronjob and the Streamlit application from the same command, hence the individual image. This image is built on top of the python:3.9-slim image, and installs ```chromadb``` and ```atlassian-python-api```.


## Features

- **Chat with Beekipedia:** Simply put, a chat UI for the Beekipedia and Beehow spaces. Ask any general question and get a response complete with relevant sources for deeper dives into your queries.  


## Roadmap (Future Development):

- **SSO Integration for Protected Client:** Integrate with existing Keycloak endpoint to authorize the user prior to access of chat. 



## ENV:
Set the following environment variables in a .env file before executing the ```docker-compose up --build``` command
```shell
- CONFLUENCE_USERNAME: Your Atlassian email
- CONFLUENCE_API_TOKEN: Your Atlassian API token
- CONFLUENCE_CLIENT_ID: Your Atlassian client id

- OPENAI_API_KEY: Your OpenAI API key
- CHROMADB_PORT: The port for the ChromaDB instance (default: 8000)
- CHROMADB_HOST: The host URL for the ChromaDB instance (default: chromadb)
- STREAMLIT_PORT: The port for the streamlit instance (default: 8501)
```

```bash
docker-compose up --build
```

## Contribution:

Contributions are welcome! Feel free to submit issues or pull requests on the GitHub repository.

To locally develop on this tool, fork this repository and run the following commands after setting the environment variables.

```bash
git clone <REPO_URL>
cd ConfluenceRag
pip install --upgrade pip
pip install -r requirements.txt
streamlit run streamlit_app.py
```

> Note: This tool is in its early stages of development. While it offers basic functionality, it may not yet cover all possible use cases.
