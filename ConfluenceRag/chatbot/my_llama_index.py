from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core import StorageContext
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.ingestion import IngestionPipeline


from llama_index.extractors.entity import EntityExtractor
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.ollama import Ollama

from llama_index.vector_stores.chroma import ChromaVectorStore

from chromadb.config import Settings as ChromaSettings
import chromadb as cdb


class LlamaIndex:
    def __init__(self, data_path):
        self.data_path = data_path
        self.documents = None
        self.index = None
        self.query_engine = None
        self.nodes = None
        self.chroma_client = None

    def init_chroma_client(self):
        chroma_settings = ChromaSettings(persist_directory="chroma_db")
        self.chroma_client = cdb.Client(settings=chroma_settings)

    def load_data(self):
        def get_meta(file_path):
            with open(file_path, "r") as file:
                lines = file.readlines()
                space_name = lines[0].strip()
                page_title = lines[1].strip()
            return {
                "space_name": space_name,
                "page_title": page_title,
                "file_name": file_path,
            }

        # reads and loads documents objects from the data path
        self.documents = SimpleDirectoryReader(
            self.data_path, recursive=True, file_metadata=get_meta
        ).load_data()

    def doc_to_node(self):
        entity_extractor = EntityExtractor(
            prediction_threshold=0.5,
            label_entities=False,  # include the entity label in the metadata (can be erroneous)
            device="cpu",  # set to "cuda" if you have a GPU
        )

        node_parser = SentenceSplitter()

        transformations = [node_parser, entity_extractor]
        # turn documents to nodes and process for metadata extraction
        pipeline = IngestionPipeline(transformations=transformations)

        self.nodes = pipeline.run(documents=self.documents)

    def set_embed_model(self, model_path):
        Settings.embed_model = resolve_embed_model(model_path)

    def set_ollama(self, model, request_timeout):
        Settings.llm = Ollama(model=model, request_timeout=request_timeout)

    def create_index(self, isNode):
        if isNode:
            # convert documents to nodes
            self.doc_to_node()

            # Check if collection exists, create if not
            if f"llama_index_{isNode}" not in self.chroma_client.list_collections():
                self.chroma_client.create_collection(name=f"llama_index_{isNode}")

            collection = self.chroma_client.get_collection(name=f"llama_index_{isNode}")
            # Add embeddings to ChromaDB
            for node in self.nodes:
                print(f"Adding node to collection: {node.get_embedding()}")
                embedding = node.embedding
                metadata = {"text": node.get_content()}
                collection.add(
                    ids=[node.get_metadata_str()],
                    embeddings=[embedding],
                    metadatas=[metadata],
                )

            # self.index = VectorStoreIndex(nodes=self.nodes)
        else:
            # Check if collection exists, create if not
            if f"llama_index_{isNode}" not in self.chroma_client.list_collections():
                self.chroma_client.create_collection(name=f"llama_index_{isNode}")

            vector_store = ChromaVectorStore(chroma_collection=self.chroma_client.get_collection(name=f"llama_index_{isNode}"))
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            self.index = VectorStoreIndex.from_documents(self.documents, storage_context=storage_context, embed_model=Settings.embed_model)


            # collection = self.chroma_client.get_collection(name=f"llama_index_{isNode}")
            # # Add embeddings to ChromaDB
            # print(f"Adding documents to collection: {self.documents}")
            # for document in self.documents:
            #     embedding = document.embedding
            #     metadata = {"text": document.get_content()}
            #     collection.add(
            #         ids=[document.get_metadata_str()],
            #         embeddings=[embedding],
            #         metadatas=[metadata],
            #     )
            # self.index = VectorStoreIndex.from_documents(self.documents)

    def create_query_engine(self):
        self.query_engine = self.index.as_query_engine()

    def query(self, query_str, isNode):
        # collection = self.chroma_client.get_collection(name=f"llama_index_{isNode}")
        # query_result = collection.query(
        #     query_embeddings=[self.embed_model.get_text_embedding(query_str)],
        #     n_results=5,
        # )
        # results = []
        # for hit in query_result["distances"]:
        #     # Access metadata (replace 'text' with your actual metadata key)
        #     text = hit["metadatas"][0]["text"]
        #     # Access distance score
        #     distance = hit["distances"][0]

        #     # Create a result object or format as needed
        #     result = {"text": text, "distance": distance}
        #     results.append(result)

        # return results

        if self.query_engine is None:
            raise ValueError(
                "Query engine is not created. Call create_query_engine first."
            )
        return self.query_engine.query(query_str)
