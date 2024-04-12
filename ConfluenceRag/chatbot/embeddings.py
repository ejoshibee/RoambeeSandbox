from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import os
from chatbot.chroma_db import ChromaDBStore  # Import the ChromaDBStore class

chroma_store = ChromaDBStore()  # Create a ChromaDBStore instance


# Load a pre-trained transformer model and tokenizer
model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)


def generate_embeddings(text):
    """Generates embeddings for the given text using the transformer model."""
    try:
        # Tokenize the text
        print("generating embeddings")
        inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")

        # Generate embeddings
        with torch.no_grad():
            embeddings = model(**inputs).pooler_output

        return np.array(embeddings)

    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None


def save_embeddings(file_path, embeddings):
    """Saves the embeddings to a file in NumPy's .npy format."""
    np.save(file_path, embeddings)


def load_embeddings(file_path):
    """Loads embeddings from a .npy file."""
    embeddings = np.load(file_path)
    return embeddings


def generate_and_store_embeddings(
    input_dir="data/confluence_data/", output_dir="data/embeddings/"
):
    """
    Generates embeddings for each text file in the input directory and stores them in the output directory.
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Loop through each spaceID directory
    for space_dir in os.listdir(input_dir):
        space_path = os.path.join(input_dir, space_dir)
        if os.path.isdir(space_path):
            # Process each pageID text file within the spaceID directory
            for text_file in os.listdir(space_path):
                text_path = os.path.join(space_path, text_file)
                with open(text_path, "r", encoding="utf-8") as file:
                    # TODO: CHUNK FILE READING AS FILES MAY BE LARGS
                    text_content = file.read()

                    # Generate embeddings
                    embeddings = generate_embeddings(text_content)
                    print(f"embeddings are: {embeddings}")
                    # print(type(embeddings))

                    if embeddings is not None:
                        # Save the embeddings
                        metadata = {
                            "space_key": space_dir,
                            "page_id": text_file.replace(".txt", ""),
                        }
                        print(f"metadata is: {metadata}")
                        try:
                            chroma_store.add_embeddings(
                                [text_file.replace(".txt", "")],
                                embeddings.tolist(),
                                [metadata],
                            )  # Note: single embedding, hence the list wrapping
                        except Exception as e:
                            print(f"Error adding embeddings to ChromaDB: {e}")

                        embedding_file_path = os.path.join(
                            output_dir, space_dir, text_file.replace(".txt", ".npy")
                        )  # Use .npy extension
                        os.makedirs(os.path.dirname(embedding_file_path), exist_ok=True)
                        save_embeddings(embedding_file_path, embeddings)
