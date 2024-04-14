import os
from dotenv import load_dotenv
from chatbot.my_llama_index import LlamaIndex
import requests
from requests.auth import HTTPBasicAuth
from chatbot.confluence_api import (
    get_pages_for_space,
    get_sanitized_next_link,
    process_page_content,
    save_processed_text_to_files,
)
from chatbot.embeddings import generate_embeddings


load_dotenv()


def main():
    username = os.getenv("username")
    confToken = os.getenv("confluenceToken")
    confluenceRestUrl = "https://roambee.atlassian.net/wiki/api/v2"
    auth = HTTPBasicAuth(username, confToken)
    headers = {"Accept": "application/json"}

    try:
        # Fetch a list of spaces
        limit = 250
        spaces_url = f"{confluenceRestUrl}/spaces?keys={'RKB'}"
        print(f"spaces_url is: {spaces_url}")
        list_of_spaces = []

        response = requests.get(spaces_url, headers=headers, auth=auth)
        response.raise_for_status()

        headers = response.headers
        spaces_data = response.json()

        # Add the initial list of spaces to list_of_spaces
        list_of_spaces.extend(spaces_data["results"])
        print(list_of_spaces)
        print(f"list_of_spaces length is: {len(list_of_spaces)}")

        if "Link" in headers:
            sanitized_link = get_sanitized_next_link(headers)

            print(f"Next URL (without overlapping '/wiki'): {sanitized_link}")
        try:
            # Fetch the remaining set of spaces
            moreSpaces = requests.get(sanitized_link, headers=headers, auth=auth)
            moreSpaces.raise_for_status()
            moreSpaces = moreSpaces.json()

            # Add the additional list of spaces to list_of_spaces
            list_of_spaces.extend(moreSpaces["results"])
        except Exception as e:
            print(f"An error occurred while fetching more spaces: {e}")

        print(f"\nTotal spaces retrieved: {len(list_of_spaces)}")

        # Check if a specific space exists
        space_key = "T2BTest"
        index_of_match = None
        for index, space in enumerate(list_of_spaces):
            if space["key"] == space_key:
                index_of_match = index
                break

        if index_of_match is not None:
            print(f"Index of space with key '{space_key}': {index_of_match}")
        else:
            print(f"Space with key '{space_key}' does not exist.")

        # loop through last 2 spaces, calling the fetch_pages_for_space function for each space. Passing in the auth, headers, confUrl, and the space_id
        for space in list_of_spaces:
            # print(f"space is: {space}\n")
            space_id = space.get("id")
            # print(f'space_id is: {space_id}')
            try:
                list_of_pages = get_pages_for_space(
                    confluenceRestUrl, headers, auth, space_id
                )
            except Exception as e:
                print(
                    f"An error occurred while fetching pages for space ID {space_id}: {e}"
                )
            # print(f"list_of_pages is: {list_of_pages}")
            print(f"list_of_pages length is: {len(list_of_pages)}")
            # iterate through the list of pages to get text and process
            for page in list_of_pages:
                # Process page content
                print(f"space name is: {page.get('title')}")
                processed_text = process_page_content(page)
                # print(f"Space Name is: {space.get('name')}")
                # print(f"Page Title is: {page.get('title')}")
                # print(f"processed_text is: {processed_text}")
                # print("")
                # Store processed text in confluence_data/ (or use for embedding generation)
                save_processed_text_to_files(
                    processed_text,
                    space.get("key"),
                    space.get("name"),
                    page.get("title"),
                )

                # generate_and_store_embeddings(
                #     input_dir="data/confluence_data/", output_dir="data/embeddings/"
                # )
                # ...

        llama_index = LlamaIndex(
            "/Users/eshaan/Documents/Roambee/sandbox/ConfluenceRag/data/confluence_data"
        )

        llama_index.init_chroma_client()

        isNode = False
         # Check if collection exists in ChromaDB
        if f"llama_index_{isNode}" not in llama_index.chroma_client.list_collections():
            print("Collection does not exist, loading data...")
            llama_index.load_data()  # Load data only if not already in Chroma

            llama_index.set_embed_model("local:BAAI/bge-small-en-v1.5")
            llama_index.set_ollama("mistral", 30.0)
            llama_index.create_index(isNode)  # Create index only once
        # load data client contained documents
        # llama_index.load_data()

        # # set the embedding model to use for embed TODO: move to default value in my_llama_index class
        # llama_index.set_embed_model("local:BAAI/bge-small-en-v1.5")

        # # set the ollama model to use for querying TODO: move to default value in my_llama_index class
        # llama_index.set_ollama("mistral", 30.0)

        # # create index (Param isNode is a toggleable for testing auto metadata extraction via indexing as nodes vs documents)
        # llama_index.create_index(isNode=True)

        # create query engine
        llama_index.create_query_engine()

        while True:
            user_query = input("Enter your query: ")
            print(f"user_query is: {user_query}")

            # TODO: call the llama_index function to get the response
            store_results = llama_index.query(user_query, isNode)
            print(f"store_results are: {store_results}")
            # TODO: print the response

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching spaces: {e}")


if __name__ == "__main__":
    main()
