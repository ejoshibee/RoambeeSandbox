import os
import requests
from requests.utils import parse_header_links
import json


def get_space_by_key(confluenceRestUrl, headers, auth, space_key):
    """
    Fetches details of a specific space by its key from the Confluence REST API.

    Args:
        confluenceRestUrl (str): The base URL of the Confluence REST API.
        headers (dict): The headers to be sent with the request.
        auth (tuple): The authentication credentials, typically (username, password).
        space_key (str): The key of the space to fetch details for.

    Returns:
        None: Prints the formatted JSON response containing space details or an error message.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the network request.
    """

    try:
        keys: list[str] = [space_key]
        # Network request to fetch the space details
        response = requests.request(
            "GET", f"{confluenceRestUrl}/spaces?keys={keys}", headers=headers, auth=auth
        )
        print(
            f"response is: {json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(',', ': '))}"
        )
        print("")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching space details: {e}")


def get_sanitized_next_link(headers):
    """
    Extracts and sanitizes the 'next' URL from the Link header if present.

    Args:
        headers (dict): The headers dictionary from an HTTP response.

    Returns:
        str or None: The sanitized 'next' URL if present, otherwise None.
    """
    header_content = headers["Link"]
    parsed_links = parse_header_links(header_content)

    base_url = ""
    next_url = ""

    # Extract the base and next URLs from the parsed links
    for link in parsed_links:
        url = link["url"]
        rel = link["rel"]
        if rel == "base":
            base_url = url
        elif rel == "next":
            next_url = url

    # Remove the overlapping '/wiki' part from the next URL if necessary
    next_url = next_url.replace("/wiki", "", 1)
    sanitized_link = base_url.rstrip("/") + next_url
    return sanitized_link


# Define function to fetch all pages for a given space
def get_pages_for_space(url, headers, auth, space_id) -> list:
    """
    Fetches all pages for a given space from the Confluence REST API.

    This function sends a GET request to the Confluence REST API to retrieve all pages
    associated with a specific space. It expects the response to be in the 'atlas_doc_format',
    which is a JSON representation of the page content.

    Args:
        url (str): The base URL of the Confluence REST API.
        headers (dict): The headers to be sent with the request.
        auth (tuple): The authentication credentials, typically (username, password).
        space_id (str): The ID of the space for which to fetch pages.

    Returns:
        list: A list of dictionaries, each representing a page within the specified space.
              If an error occurs, an empty list is returned.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the network request.
    """
    try:
        # Fetch pages for the given space
        pages_url = f"{url}/spaces/{space_id}/pages?limit=250&body-format=atlas_doc_format"
        response = requests.get(pages_url, headers=headers, auth=auth)
        response.raise_for_status()

        # Parse response JSON
        pages_data = response.json()
        # print(f"pages_data is: {pages_data}")

        # Extract page details from response
        pages = pages_data.get("results", [])
        # print(f"pages is: {pages}")
        return pages

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching pages for space '{space_id}': {e}")


def parseADF(page_content) -> list[str]:
    """
    Extracts text objects from the 'atlas_doc_format' JSON object.

    Args:
        json_object (dict): The JSON object containing 'atlas_doc_format' representation.

    Returns:
        list: A list containing all the text objects extracted from the 'atlas_doc_format'.
    """
    # Access the "value" key within "atlas_doc_format"
    atlas_doc_value = page_content["atlas_doc_format"]["value"]

    # Parse the JSON string within the "value" key
    parsed_atlas_doc = json.loads(atlas_doc_value)
    # print(f"parsed_atlas_doc is: {parsed_atlas_doc}")
    # Extract text objects from the parsed JSON
    page_content_body = []

    # Function to recursively extract text objects
    def extract_text_objects(content):
        # print(f'accessing content: {content}')
        if isinstance(content, dict):
            # print('content is a dict')
            if content.get("type") == "text":
                # print(f'content found: {content["text"]}')
                page_content_body.extend([content["text"]])
            elif content.get("content"):
                for item in content["content"]:
                    extract_text_objects(item)
        elif isinstance(content, list):
            # print('list found')
            for item in content:
                extract_text_objects(item)

    # Extract text objects and store page content in text_object
    extract_text_objects(parsed_atlas_doc["content"])

    return page_content_body

def process_page_content(page) -> list[str]:
    # page_id = page.get("id")
    # page_title = page.get("title")

    # TODO: FIX PAGE CONTENT PARSING CURRENTLY BROKEN

    # Store page details in a list or database
    page_content = page.get("body")
    parsed_page_content = parseADF(page_content)
    return parsed_page_content


def save_processed_text_to_files(processed_text, space_key, space_name, page_title):
    """
    Saves processed text to files in the data/confluence_data/ directory.

    Args:
        processed_text (list): List of strings/sentences making up the content of the page.
        space_key (str): Space key of the Confluence space.
        page_id (str): ID of the Confluence page.
    """
    # Define directory path for the unique space named by its key
    directory_path = f"data/confluence_data/{space_key}"

    # Create directory if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Define file path
    file_path = f"{directory_path}/{page_title.replace('/', '-')}.txt"

    # Write processed text to file
    with open(file_path, "w") as file:
        file.write(f"Space: {space_name}\n")
        file.write(f"Page Title: {page_title}\n")
        for sentence in processed_text:
            file.write(sentence + "\n")
