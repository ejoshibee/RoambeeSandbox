import chromadb

class ChromaDBStore:
    def __init__(self, collection_name: str = "confluence_embeddings"):
        # Updated client initialization 
        self.client = chromadb.Client()  
        self.collection_name = collection_name
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        if self.collection_name not in self.client.list_collections():
            self.client.create_collection(self.collection_name)

    def add_embeddings(self,id: list, embeddings: list[list[float]], metadatas: list[dict] = None):
        """
        Adds a batch of embeddings to the Chroma collection.

        Args:
            embeddings (list[list[float]]): A list of embedding vectors.
            metadatas (list[dict], optional): A list of metadata dictionaries for each embedding. Defaults to None.
        """
        if metadatas is None:
            metadatas = [{} for _ in range(len(embeddings))]
        self.client.get_collection(self.collection_name).add(
            ids=id, embeddings=embeddings, metadatas=metadatas
        )

    def query_embeddings(self, query_embedding: list[float], k: int = 5) -> list[dict]:
        """
        Queries the Chroma collection for the k nearest neighbors to the query embedding.

        Args:
            query_embedding (list[float]): The query embedding vector.
            k (int, optional): The number of nearest neighbors to return. Defaults to 5.

        Returns:
            list[dict]: A list of dictionaries containing the metadata and distances of the k nearest neighbors.
        """
        results = self.client.get_collection(self.collection_name).query(
            query_embeddings=[query_embedding], n_results=k
        )
        return results

    # ... (add more methods as needed) ...
