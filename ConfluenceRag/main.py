import streamlit as st
import os
from dotenv import load_dotenv
from chatbot.my_llama_index import LlamaIndex
import requests
from requests.auth import HTTPBasicAuth
from chatbot.confluence_api import (
    get_pages_for_space,
    process_page_content,
    save_processed_text_to_files,
    get_space_by_keys,
)

import logging

# Setup logging to capture stdout from the application
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()


def ensure_data_directories(data_directory, list_of_spaces, streamlit_component=None):
    """
    Ensures that the specified data directory and subdirectories for each space exist. This is
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


def main():
    st.title("The Interactive Roambee Bookipedia")

    info_placeholder = st.empty()

    username = os.getenv("username")
    confToken = os.getenv("confluenceToken")
    confluenceRestUrl = "https://roambee.atlassian.net/wiki/api/v2"
    auth = HTTPBasicAuth(username, confToken)
    headers = {"Accept": "application/json"}

    data_directory = "data/confluence_data"
    list_spaces = ["RKB", "BH"]

    # Check that the specified data directories exist
    data_exist = ensure_data_directories(data_directory, list_spaces, info_placeholder)

    if not data_exist:
        with st.spinner("Fetching and processing data..."):
            count = 0
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
                        count += 1
                        print(f"Document saved: {count}")
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")

    info_placeholder.info("Data fetched and processed successfully. Loading Llama...")

    @st.cache_resource(show_spinner=False)
    def load_data():
        # Display a spinner while loading data
        with st.spinner(text="Loading data..."):
            # Initialize the LlamaIndex with the specified data directory
            llama_index = LlamaIndex(
                "/Users/eshaan/Documents/Roambee/sandbox/ConfluenceRag/data/confluence_data"
            )
            # Load data into the LlamaIndex
            llama_index.load_data()
            
            # Define dictionary of usable transformer models for embedding documents
            transformers = {
                "MiniLM": "local:sentence-transformers/all-MiniLM-L6-v2",
                "BAAI": "local:BAAI/bge-small-en-v1.5",
                "T5Base": "local:sentence-transformers/gtr-t5-base"
            }
            # Set the embedding model to MiniLM
            llama_index.set_embed_model(transformers["T5Base"])
            # Set the ollama model with a specific version and threshold
            llama_index.set_ollama("mistral:latest", 59.0)
            # Create the index for the LlamaIndex, assuming it is not a node
            llama_index.create_index(False)
            # Create the query engine for the LlamaIndex, assuming streaming is enabled
            llama_index.create_query_engine(True)
            # Return the fully initialized LlamaIndex
            return llama_index

    llama_index = load_data()

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
                
                # Capture the streamed tokens to render the response in a streamed format to streamlit
                for chunk in response.response_gen:
                    full_response += chunk
                    message_placeholder.markdown(full_response + " ")

                
                additional_sources = (
                    "You can read these additional sources for more information:\n"
                )

                
                # FOR DEV: Iterate over the source nodes in the response to print relevant info
                for node in response.source_nodes:
                    print(node.metadata.get("page_title"))
                    print(f"{node.get_score()}")

                    # Access extracted keywords
                    keywords = node.metadata.get("excerpt_keywords")
                    if keywords:
                        print(f"Keywords: {keywords}")

                    # Handle cases where keywords might be missing
                    else:
                        print("Keywords not found")

                    print(f"{node.metadata}\n")

                # Initialize an empty set to store the seen links
                seen_links = set()
                
                # Iterate over the source nodes in the response to capture unique links to confluence sources
                for node in response.source_nodes:
                    webui_link = node.metadata.get("webui_link")
                    if webui_link not in seen_links:
                        additional_sources += f"- [{webui_link}]({webui_link})\n"
                        seen_links.add(webui_link)

                # append the additional sources string to the full response
                full_response_with_links = full_response + "\n\n" + additional_sources
                message_placeholder.markdown(full_response_with_links)

                # Add response to message history
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response_with_links}
                )


if __name__ == "__main__":
    main()
