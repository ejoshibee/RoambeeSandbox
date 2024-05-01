import os
import dotenv

# import logging
import chromadb

from datetime import datetime
from atlassian import Confluence
from markdownify import markdownify as md
# from llama_index.readers.confluence import ConfluenceReader

# # Setup logging to capture stdout from the application
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

dotenv.load_dotenv()


def fetch_conf_data():
    """
    Fetches and processes Confluence page data from specified spaces, converts HTML content to Markdown,
    and sorts the pages by the last updated timestamp in descending order.

    Returns:
        list: A list of dictionaries, each containing the markdown content and last updated timestamp of a page.
    """
    print("in fetch_conf_data")
    # Retrieve Confluence credentials from environment variables
    conf_username = os.getenv("CONFLUENCE_USERNAME")
    conf_api_token = os.getenv("CONFLUENCE_API_TOKEN")

    # conf_client_id = os.getenv("CONFLUENCE_CLIENT_ID")
    # # conf_client_secret = os.getenv("CONFLUENCE_CLIENT_SECRET")
    # # redirect_uri = os.getenv("REDIRECT_URI")

    # Initialize Confluence API client with credentials
    confluence = Confluence(
        url="https://roambee.atlassian.net/wiki",
        username=conf_username,
        password=conf_api_token,
    )

    # Define the space keys to fetch data from
    space_keys = ["BH", "RKB"]
    list_of_pages = []
    # Fetch all pages from each space and accumulate them
    for space_key in space_keys:
        list_of_pages.extend(confluence.get_all_pages_from_space(space_key, limit=255))

    list_of_page_content = []

    # Process each page to extract required information
    for page in list_of_pages:
        page_struct = {}
        print(f"page: {page}\n")

        # Fetch the page content by ID and expand to get storage format body
        page_content = confluence.get_page_by_id(
            # 771325956,
            page.get("id"),
            expand="body.storage",
        )
        print("CONTENT OF PAGE ----------------------", page_content)

        # Convert HTML body to Markdown
        body_html = page_content["body"]["storage"]["value"]
        body_markdown = md(body_html)
        print(f"body_markdown: {body_markdown}")
        page_struct["body_content"] = body_markdown

        # Fetch page properties to determine the last updated timestamp
        page_properties = confluence.get_page_properties(page.get("id"))
        page_property: list = page_properties.get("results")
        print(f"page_properties: {page_property}\n")

        # Check if page properties are not empty and extract last updated timestamp
        if len(page_property) != 0:
            time_last_updated = page_property[0].get("version").get("when")
            print(
                f"page {page.get('id')} was last updated at : {time_last_updated}\n\n\n"
            )
            page_struct["last_updated"] = time_last_updated
        else:
            continue
        list_of_page_content.append(page_struct)
    print(list_of_page_content)

    # Sort the pages by last updated timestamp in descending order
    sorted_data = sorted(
        list_of_page_content,
        key=lambda x: datetime.fromisoformat(x["last_updated"].replace("Z", "+00:00")),
        reverse=True,
    )

    print(f"sorted_data: {sorted_data}")
    return sorted_data


def test_confluence_api():
    print("in test_confluence_py")
    print("Our test works at", datetime.now())
    db = chromadb.HttpClient(host="0.0.0.0", port=8000)
    collection = db.get_collection("llama_index_False")
    print(f"collection count: {collection.count()}")

    print(
        f"peek at the collection: {collection.get(limit=1, include=["embeddings", "documents", "metadatas"])}"
    )
    fetch_conf_data()

    # link_to_authenticate = f"""https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id={conf_client_id}&scope=read%3Apage%3Aconfluence%20read%3Aattachment%3Aconfluence%20read%3Aspace-details%3Aconfluence%20read%3Acontent-details%3Aconfluence%20read%3Acontent%3Aconfluence%20read%3Acustom-content%3Aconfluence%20read%3Aspace%3Aconfluence&redirect_uri=http%3A%2F%2Flocalhost%3A8501&state=$ragpath1234&response_type=code&prompt=consent
    #         """


test_confluence_api()
