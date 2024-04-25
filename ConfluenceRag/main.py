import os
import logging
import requests
import streamlit as st
from dotenv import load_dotenv

from chatbot.my_llama_index import LlamaIndex
from requests.auth import HTTPBasicAuth
from chatbot.confluence_api import (
    get_pages_for_space,
    process_page_content,
    save_processed_text_to_files,
    get_space_by_keys,
)
# from llama_index.readers.confluence import ConfluenceReader

from streamlit_keycloak import login


# Setup logging to capture stdout from the application
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Data Directory Management
def ensure_data_directories(data_directory, list_of_spaces, streamlit_component=None):
    """
    Ensures that the specified data persistence directory and subdirectories for each space exist. This is
    because confluence data is partitioned by space key, thus can have as many subdirectories as there are keys in list_of_spaces

    Args:
        data_directory (str): The path to the main data directory.
        list_of_spaces (list): A list of space keys for which subdirectories are expected.
        streamlit_component (streamlit.empty(), optional):
            Streamlit component used to display information messages. Defaults to None.

    Returns:
        bool: True if the data directory and all subdirectories exist, False otherwise.
    """

    # Check if the data directory exists
    if not os.path.exists(data_directory):
        os.mkdir(data_directory)
        if streamlit_component:
            streamlit_component.info(f"Directory {data_directory} does not exist.")
        return False

    # Check for missing space subdirectories (spaces from list_of_spaces)
    missing_directories = [
        space
        for space in list_of_spaces
        if not os.path.exists(os.path.join(data_directory, space))
    ]
    if missing_directories:
        if streamlit_component:
            streamlit_component.info(
                f"Missing directories for spaces: {', '.join(missing_directories)}"
            )
        return False

    # data exists
    if streamlit_component:
        streamlit_component.info("All necessary directories are present.")
    return True


# Llama Index Initializer
@st.cache_resource(show_spinner=False)
def init_llama_index(data_directory: str, stream: bool, isNode: bool, isHTTP: bool) -> LlamaIndex:
    """
    Initializes the LlamaIndex Class with the specified data directory and embedding model.
    Handles all setup for the query engine and data stores.

    Args:
        data_directory (str): The path to the main data directory.
        stream (bool): Whether to use streaming for the query response.
        isNode (bool): Whether to use nodes for document pre-processing instead of default document pre-processing in LlamaIndex.
        isHTTP (bool): Whether to use the HTTP version of the LLaMA index.

    Returns:
        LlamaIndex: The initialized LLaMA index.
    """
    # Display a spinner while loading data
    with st.spinner(text="Loading data..."):
        # Initialize the LlamaIndex with the specified data directory
        # print(os.path.dirname(__file__))
        llama_index = LlamaIndex(
            os.path.join(os.path.dirname(__file__), data_directory),
            isNode,
            isHTTP,
        )
        # Load data into the LlamaIndex
        llama_index.load_data()

        # Define dictionary of usable embedding models for embedding documents
        embeddings = {
            "MiniLM": "local:sentence-transformers/all-MiniLM-L6-v2",
            "BAAI": "local:BAAI/bge-small-en-v1.5",
            "T5Base": "local:sentence-transformers/gtr-t5-base",
        }
        # Set the embedding model to MiniLM
        llama_index.set_embed_model(embeddings["T5Base"])
        # Set the llm to use for querying (Default to OpenAI). set api_token to None for Ollama querying (naturally change the llms[MODEL_NAME] as well)
        llms = {
            "wizard": "wizardlm2:7b",
            "mistral": "mistral:latest",
            "dolphin": "dolphin-mixtral:latest",
            "openai35turbo": "gpt-3.5-turbo",
            "openai4turbo": "gpt-4-turbo",
        }
        request_timeout = 59.0
        llama_index.set_llm(
            llms["openai35turbo"], request_timeout, api_token=OPENAI_API_KEY
        )

        # Create the index for the LlamaIndex, assuming it is not a node
        llama_index.create_index()

        # Create the query engine for the LlamaIndex, assuming streaming is enabled
        llama_index.create_query_engine(stream)

        # Return the fully initialized LlamaIndex
        return llama_index


# Configuration for the streamlit app
def configure_streamlit_app():
    """
    Configures the Streamlit app with a title, favicon, and layout.
    """
    st.set_page_config(
        page_title="Artemis",
        page_icon="public/favicon.ico",
    )
    st.title("💬   with Beekipedia")


# Authentication and Authorization
def authenticate_and_authorize():
    """
    Returns the authentication and headers object for the Confluence API methods, and the Confluence REST URL.
    """
    conf_username = os.getenv("CONFLUENCE_USERNAME")
    conf_token = os.getenv("CONFLUENCE_API_TOKEN")

    auth = HTTPBasicAuth(conf_username, conf_token)

    headers = {"Accept": "application/json"}
    confluenceRestUrl = "https://roambee.atlassian.net/wiki/api/v2"

    return auth, headers, confluenceRestUrl


def main():
    
    # keycloak = login(
    #     url=os.getenv("KC_URL"),
    #     realm=os.getenv("KC_REALM"),
    #     client_id=os.getenv("KC_CLIENT_ID"),
    # )

    # if keycloak.authenticated:
        # conf_client_id = os.getenv("CONFLUENCE_CLIENT_ID")

        # link_to_authenticate=f"""https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id={conf_client_id}&scope=read%3Apage%3Aconfluence%20read%3Aattachment%3Aconfluence%20read%3Aspace-details%3Aconfluence%20read%3Acontent-details%3Aconfluence%20read%3Acontent%3Aconfluence%20read%3Acustom-content%3Aconfluence%20read%3Aspace%3Aconfluence&redirect_uri=https%3A%2F%2Flocalhost%3A8501&state=$ragpath1234&response_type=code&prompt=consent
        #         """

        # try:
        #     conf_response = requests.get(
        #         link_to_authenticate
        #     )
        #     conf_response.raise_for_status()
        #     st.info(f"response from initial confluence request: {conf_response}")
        #     processed_conf_response = conf_response.text
        #     st.info(f"processed confluence response: {processed_conf_response}")
        # except requests.exceptions.RequestException as e:
        #     st.error(f"An error occurred making a confluence request for authentication: {e}")

        # Configure the Streamlit app with pre-set settings
        configure_streamlit_app()

        info_placeholder = st.empty()

        # Authenticate and authorize the user
        auth, headers, confluenceRestUrl = authenticate_and_authorize()

        # Ensure that the specified data directories exist
        data_directory = "data/confluence_data"
        list_spaces = ["RKB", "BH"]
        directories_exist = ensure_data_directories(
            data_directory, list_spaces, info_placeholder
        )

        # If necessary directories are not present, data is missing so fetch it
        if not directories_exist:
            print("data doesnt exist")
            with st.spinner("Fetching and processing data..."):
                try:
                    list_of_spaces = get_space_by_keys(
                        confluenceRestUrl, headers, auth, list_spaces
                    )
                    for space in list_of_spaces:
                        space_id = space.get("id")
                        list_of_pages = get_pages_for_space(
                            confluenceRestUrl, headers, auth, space_id
                        )
                        for page in list_of_pages:
                            processed_text = process_page_content(page)
                            save_processed_text_to_files(
                                processed_text,
                                space.get("key"),
                                space.get("name"),
                                page.get("title"),
                                page.get("_links").get("webui"),
                            )
                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred: {e}")

        info_placeholder.info("Data fetched and processed successfully. Loading Llama...")

        # Set response streaming on or off
        stream = True

        # DEFAULT DON'T CHANGE
        # SET TRUE FOR EXPIREMENTAL NODES
        isNode = False

        # FOR DEV TESTING HTTP CLIENT:
        isHTTP = True

        # Initialize all LlamaIndex related things
        llama_index = init_llama_index(data_directory, stream, isNode, isHTTP)

        info_placeholder.info(
            "For more reading, check out [Roambee's Knowledge Base](https://roambee.atlassian.net/wiki/spaces/RKB/overview)"
        )

        # Initialize the chat message history
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Ask me anything about Roambee and our services!",
                }
            ]

        # Iterate over session_state.messages and display the chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # print(st.session_state.messages)
                st.markdown(message["content"])

        # Capture user input and save to chat history. Trigger llm query
        if user_query := st.chat_input("Your query:"):
            st.chat_message("user").markdown(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})

            # Assigning this response to the assistant role
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Query the llama index to build a streamed response
                    response = llama_index.query(user_query)
                    # Initialize an empty placeholder for the displayed response
                    message_placeholder = st.empty()
                    # Initialize an empty string for the full response
                    full_response = ""

                    # If stream was set True, capture the streamed tokens to build the response chunk-by-chunk in streamlits chat interface
                    # Else, render the full response in the chat interface
                    if stream:
                        for chunk in response.response_gen:
                            full_response += chunk
                            message_placeholder.markdown(full_response + " ")
                    else:
                        full_response = response.response
                        message_placeholder.markdown(full_response)

                    additional_sources = "If you would like to know more, visit the following reference sources for more detailed information:\n"

                    # Initialize an empty set to store unique confluence links
                    seen_links = set()

                    # Iterate over the source nodes in the response to capture confluence page links from node metadata
                    for node in response.source_nodes:
                        webui_link = node.metadata.get("webui_link")
                        if webui_link not in seen_links:
                            additional_sources += f"- [{node.metadata.get('page_title')}]({webui_link})\n"
                            seen_links.add(webui_link)

                    # append the additional sources string to the full response
                    full_response_with_links = full_response + "\n\n" + additional_sources
                    message_placeholder.markdown(full_response_with_links)

                    # Add response to message history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response_with_links}
                    )

                    # FOR DEV: Print relevant node information after response for inspection
                    for node in response.source_nodes:
                        print(f"Page Title: {node.metadata.get('page_title')}")
                        print(f"Score: {node.get_score()}")
                        print(f"Metadata: {node.metadata}\n")

                        # Access extracted keywords
                        keywords = node.metadata.get("excerpt_keywords")

                        if keywords:
                            print(f"Keywords: {keywords}")

def auth_layer():
    # a front request endpoint check for active session
    session = requests.Session()

    # REPLACE THIS URLWITH A NETWORK REQUEST TO THE USERS API
    # OR CHECK FOR PRESENCE OF CERTAIN COOKIES
    response = session.get(f"https://jsonplaceholder.typicode.com/todos/{1 + 1}")
    print(f"FINDME: {response.json()}")

    if response.ok:
        print("User is authenticated")
        main()
    else:
        print("User is not authenticated")


if __name__ == "__main__":
    auth_layer()
