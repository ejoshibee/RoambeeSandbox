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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


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
    data_exist = True

    # Check if the data directory exists
    if not os.path.exists(data_directory):
        data_exist = False
        info_placeholder.info(f"Directory {data_directory} does not exist.")
    else:
        # Check for the presence of each space's subdirectory
        missing_directories = [
            space
            for space in list_spaces
            if not os.path.exists(os.path.join(data_directory, space))
        ]
        if missing_directories:
            data_exist = False
            info_placeholder.info(
                f"Missing directories for spaces: {', '.join(missing_directories)}"
            )
        else:
            info_placeholder.info("All necessary directories are present.")

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
        with st.spinner(text="Loading data..."):
            llama_index = LlamaIndex(
                "/Users/eshaan/Documents/Roambee/sandbox/ConfluenceRag/data/confluence_data"
            )
            llama_index.load_data()
            transformers = {"MiniLM": "local:sentence-transformers/all-MiniLM-L6-v2", "BAAI": "local:BAAI/bge-small-en-v1.5"}
            llama_index.set_embed_model(transformers["MiniLM"])
            llama_index.set_ollama("mistral", 30.0)
            llama_index.create_index(False)  # Assuming isNode is False
            llama_index.create_query_engine(True)  # Assuming stream is True
            return llama_index

    llama_index = load_data()
    info_placeholder.info("For more reading, check out [Roambee's Knowledge Base](https://roambee.atlassian.net/wiki/spaces/RKB/overview)")    
    if "messages" not in st.session_state:  # Initialize the chat message history
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

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = llama_index.query(user_query)
                message_placeholder = st.empty()
                full_response = ""
                for chunk in response.response_gen:
                    full_response += chunk
                    message_placeholder.markdown(full_response + " ")

                seen_links = set()
                additional_sources = (
                    "You can read these additional sources for more information:\n"
                )

                for node in response.source_nodes:
                    print(node.metadata.get("page_title"))  
                    print(f"{node.get_score()}")

                    # Access extracted keywords
                    keywords = node.metadata.get("excerpt_keywords")
                    if keywords:
                        print(f"Keywords: {keywords}")
                    else:
                        print("Keywords not found")  # Handle cases where keywords might be missing

                    print(f"{node.metadata}\n")

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
