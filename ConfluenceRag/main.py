import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
from chatbot.confluence_api import get_pages_for_space, get_sanitized_next_link
from chatbot.processing import process_page_content, save_processed_text_to_files

load_dotenv()



def main():
    username = os.getenv("username")
    confToken = os.getenv("confluenceToken")
    confluenceRestUrl = "https://roambee.atlassian.net/wiki/api/v2"
    auth = HTTPBasicAuth(username, confToken)
    headers = {
        "Accept": "application/json"
    }
    
    
    try:
        # Fetch a list of spaces
        limit = 250
        spaces_url = f"{confluenceRestUrl}/spaces?limit={limit}"
        list_of_spaces = []
        
        response = requests.get(spaces_url, headers=headers, auth=auth)
        response.raise_for_status()
        
        headers = response.headers
        spaces_data = response.json()

        # Add the initial list of spaces to list_of_spaces
        list_of_spaces.extend(spaces_data['results'])
        print(f"list_of_spaces length is: {len(list_of_spaces)}")
        
        if 'Link' in headers:
            sanitized_link = get_sanitized_next_link(headers)

            print(f"Next URL (without overlapping '/wiki'): {sanitized_link}")
            
            # Fetch the remaining set of spaces 
            moreSpaces = requests.get(sanitized_link, headers=headers, auth=auth)
            moreSpaces.raise_for_status()
            moreSpaces = moreSpaces.json()
            
            # Add the additional list of spaces to list_of_spaces
            list_of_spaces.extend(moreSpaces['results'])

        print(f"\nTotal spaces retrieved: {len(list_of_spaces)}")

            
        # Check if a specific space exists
        space_key = "T2BTest"
        index_of_match = None
        for index, space in enumerate(list_of_spaces):
            if space['key'] == space_key:
                index_of_match = index
                break

        if index_of_match is not None:
            print(f"Index of space with key '{space_key}': {index_of_match}")
        else:
            print(f"Space with key '{space_key}' does not exist.")
        
        # loop through last 4 spaces, calling the fetch_pages_for_space function for each space. Passing in the auth, headers, confUrl, and the space_id     
        for space in list_of_spaces[-4:]:
            # print(f"space is: {space}\n")
            space_id = space.get('id')
            # print(f'space_id is: {space_id}')
            try:
                list_of_pages = get_pages_for_space(confluenceRestUrl, headers, auth, space_id)
                print(f"list_of_pages length is: {len(list_of_pages)}")
                # iterate through the list of pages to get text and process
                for page in list_of_pages:
                    # Process page content
                    processed_text = process_page_content(page)
                    print(f"Space Name is: {space.get('name')}")
                    print(f"Page Title is: {page.get('title')}")
                    print(f"processed_text is: {processed_text}")
                    print("")
                    # Store processed text in confluence_data/ (or use for embedding generation)
                    save_processed_text_to_files(processed_text, space.get('key'), page.get('id'))
                    # ... 

            except Exception as e:
                print(f"An error occurred while fetching pages for space ID {space_id}: {e}")

        
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching spaces: {e}")

if __name__ == "__main__":
    main()