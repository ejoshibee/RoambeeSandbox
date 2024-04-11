from chatbot.confluence_api import parseADF
import os

def process_page_content(page) -> list[str]:
  # page_id = page.get("id")
  # page_title = page.get("title")
      
  # TODO: FIX PAGE CONTENT PARSING CURRENTLY BROKEN
  
  # Store page details in a list or database
  page_content = page.get("body")
  parsed_page_content = parseADF(page_content)
  return parsed_page_content

def save_processed_text_to_files(processed_text, space_key, page_id):
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
    file_path = f"{directory_path}/{page_id}.txt"

    # Write processed text to file
    with open(file_path, 'w') as file:
        for sentence in processed_text:
            file.write(sentence + '\n')