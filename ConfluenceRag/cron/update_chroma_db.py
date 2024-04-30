# from atlassian import Confluence
from llama_index.readers.confluence import ConfluenceReader
import chromadb

# import os
import dotenv
from datetime import datetime
# import logging

# # Setup logging to capture stdout from the application
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

dotenv.load_dotenv()

def fetch_conf_data():
    print("in fetch_conf_data")
    # conf_username = os.getenv("CONFLUENCE_USERNAME")
    # conf_api_token = os.getenv("CONFLUENCE_API_TOKEN")
    # conf_client_id = os.getenv("CONFLUENCE_CLIENT_ID")
    # # conf_client_secret = os.getenv("CONFLUENCE_CLIENT_SECRET")
    # # redirect_uri = os.getenv("REDIRECT_URI")
    # space_key = "BH"

    # # Normal confluence api
    # confluence = Confluence(
    #     url="https://roambee.atlassian.net/wiki",
    #     username=conf_username,
    #     password=conf_api_token,
    # )
    # space_keys = ["BH","RKB"]
    # list_of_pages = []
    # for space_key in space_keys:
    #     list_of_pages.extend(confluence.get_all_pages_from_space(space_key))

    # # LlamaIndex Confluence Api
    reader = ConfluenceReader(base_url="https://roambee.atlassian.net/wiki", cloud=True)

    # for space_key in space_keys:
    #     documents = reader.load_data(
    #         space_key=space_key,
    #         include_attachments=False,
    #         page_status="current",
    #         start=0,
    #     )
    #     for document in documents:
    #         print(f"document:\n{document}")
    #         if not os.path.exists(f"data/conf_reader_data/{space_key}"):
    #             os.makedirs(f"data/conf_reader_data/{space_key}")
    #         file_path = f"data/conf_reader_data/{space_key}/{document.metadata.get('title').replace('/','-')}.txt"
    #         try:
    #             if len(document.text.split("\n")) > 4:
    #                 with open(file_path, "w") as file:
    #                     file.write(f"{space_key}\n")
    #                     file.write(f"{document.metadata.get('title')}\n")
    #                     file.write(f"{document.metadata.get('url')}\n")
    #                     file.write(f"{document.text}")
    #                 print(f"Data successfully written to {file_path}")
    #         except Exception as e:
    #             print(f"An error occurred while writing to the file: {e}")
    #     print(f"documents hopefully: {documents}")

def test_confluence_api():
    print("in test_confluence_py")
    print("Our test works at", datetime.now())
    db = chromadb.HttpClient(host="chromadb", port=8000)
    chroma_collection = db.get_collection("llama_index_False")
    print(f"chroma_collection count: {chroma_collection.count()}")

    # link_to_authenticate = f"""https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id={conf_client_id}&scope=read%3Apage%3Aconfluence%20read%3Aattachment%3Aconfluence%20read%3Aspace-details%3Aconfluence%20read%3Acontent-details%3Aconfluence%20read%3Acontent%3Aconfluence%20read%3Acustom-content%3Aconfluence%20read%3Aspace%3Aconfluence&redirect_uri=http%3A%2F%2Flocalhost%3A8501&state=$ragpath1234&response_type=code&prompt=consent
    #         """


test_confluence_api()
