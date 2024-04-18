import phoenix as px
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    set_global_handler,
    get_response_synthesizer,
)
from llama_index.core import StorageContext
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter


from llama_index.core.extractors import (
    SummaryExtractor,
    QuestionsAnsweredExtractor,
    TitleExtractor,
    KeywordExtractor,
)

from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.extractors.entity import EntityExtractor

from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI

from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb


# To view traces in Phoenix, you will first have to start a Phoenix server. You can do this by running the following:
session = px.launch_app()

# Once you have started a Phoenix server, you can start your LlamaIndex application and configure it to send traces to Phoenix. To do this, you will have to add configure Phoenix as the global handler
set_global_handler("arize_phoenix")


class LlamaIndex:
    def __init__(self, data_path):
        """
        Initialize the LlamaIndex class with the specified data path.

        Args:
        data_path (str): The path to the directory where the documents are stored.
        """
        print("Initializing LlamaIndex and persistent_ChromaDB clients")
        self.data_path = data_path
        self.documents = None
        self.index = None
        self.query_engine = None
        self.nodes = None
        self.db = chromadb.PersistentClient(
            path="/Users/eshaan/Documents/Roambee/sandbox/ConfluenceRag/data/chroma_db"
        )
        self.chroma_collection = None

    def load_data(self):
        """
        Load data from the specified directory and store it in the documents attribute.
        """
        print(f"Loading data from documents in folder: {self.data_path}")

        def get_meta(file_path):
            """
            Extract metadata from the file.

            Args:
            file_path (str): Path to the file from which metadata is extracted.

            Returns:
            dict: A dictionary containing metadata about the file.
            """
            with open(file_path, "r") as file:
                lines = file.readlines()
                space_name = lines[0].strip()
                page_title = lines[1].strip()
                webui_link = lines[2].strip()
            return {
                "space_name": space_name,
                "page_title": page_title,
                "file_name": file_path,
                "webui_link": webui_link,
            }

        # Read and load document objects from the data path adding metadata to each document in the process
        # TODO: Investigate reimplementation of doc_to_node (Bottom of file) method for more granular control on node pre-processing
        self.documents = SimpleDirectoryReader(
            self.data_path, recursive=True, file_metadata=get_meta
        ).load_data()
        print(f"Number of documents loaded: {len(self.documents)}")

    def set_embed_model(self, model_path):
        """
        Set the embedding model path in LlamaIndex settings.

        Args:
        model_path (str): The path to the embedding model set in main.py set_embed_model execution.
        """
        # TODO: Investigate moving param model_path to client initialization
        print(f"Setting embed model to {model_path[6:]}")
        Settings.embed_model = resolve_embed_model(model_path)

    def set_llm(self, model, request_timeout=None, api_token=None):
        """
        Configure the LLM to OpenAI or Local Ollama instance with the specified model and timeout.

        Args:
        model (str): The model name or identifier.
        request_timeout (int): Timeout in seconds for the model requests.
        api_token (str): OpenAI API key for authentication. Defaults to none -> Ollama setup
        """
        if api_token is None:
            print(
                f"setting Ollama model to {model} with a request timeout of {request_timeout} seconds"
            )
            Settings.llm = Ollama(model=model, request_timeout=request_timeout)
        else:
            print("Using OpenAI model to gpt-3.5-turbo with a temperature of 0.7")
            Settings.llm = OpenAI(
                model=model, temperature=0.7, timeout=request_timeout, api_key=api_token
            )

    def create_index(self, isNode):
        """
        Create an index based on whether the index is for nodes or documents.

        Args:
        isNode (bool): Flag to determine if the index is for nodes.
        """
        # Determine the collection name based on the node flag
        # TODO: Change to a static name as Doc_to_node is not being tested
        collection_name = f"llama_index_{isNode}"
        self.chroma_collection = self.db.get_or_create_collection(name=collection_name)

        # Check the current size of the collection
        collection_size = self.chroma_collection.count()

        # check if the collection is empty
        # TODO: IMPLEMENT A REAL CHECK
        if collection_size == 0:
            print(f"collection {collection_name} is empty. Populating collection...")

            # Create a vector store using the Chroma collection from the database
            vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)

            # Initialize storage context with default settings overiding vector_store with the specified vector store
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            # Create a new index from the documents using the specified vector store and embedding model
            self.index = VectorStoreIndex.from_documents(
                self.documents,
                storage_context=storage_context,
                embed_model=Settings.embed_model,
                transformations=[
                    # SentenceSplitter(),
                    # Add more transformations if necessary or IMPLEMENT DOC_TO_NODE 
                    KeywordExtractor(keywords=10)
                ],
            )
        else:
            print(
                f"collection {collection_name} is already populated. Loading index from vector store..."
            )
            # Load the existing index from the vector store
            vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store, storage_context=storage_context
            )

    def create_query_engine(self, stream):
        """
        Create a query engine for processing queries using the index.

        Args:
        stream (bool): Determines if the response synthesizer should operate in streaming mode.
        """
        print(f"Creating query engine, with response streaming: {stream}")
        # Initialize the retriever with the index and set the number of top similar items to retrieve
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=6,
        )
        # Configure the response synthesizer based on the streaming flag
        response_synthesizer = get_response_synthesizer(
            streaming=stream, structured_answer_filtering=False
        )

        # Set up the query engine with the configured retriever and response synthesizer
        self.query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=[],
        )

    def query(self, query_str):
        """
        Execute a query using the query engine.

        Args:
        query_str (str): The query string to be processed.

        Returns:
        object: The result of the query.

        Raises:
        ValueError: If the query engine has not been created.
        """
        if self.query_engine is None:
            raise ValueError(
                "Query engine is not created. Call create_query_engine first."
            )

        response = self.query_engine.query(query_str)
        px.active_session().url
        return response

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # UNUSED
    def doc_to_node(self):
        """
        Convert documents to nodes by applying various transformations for metadata extraction.
        """
        print("converting documents to nodes")

        # Define the transformations to be applied to the documents
        transformations = [
            SentenceSplitter(),
            TitleExtractor(nodes=5),
            QuestionsAnsweredExtractor(questions=3),
            SummaryExtractor(summaries=["prev", "self"]),
            KeywordExtractor(keywords=10),
            EntityExtractor(prediction_threshold=0.5),
        ]

        # Apply transformations to the first 10 documents
        print(f"applying transformations: {transformations}")
        pipeline = IngestionPipeline(transformations=transformations)

        # Apply transformations to the first 10 documents
        print("running Ingestion Pipeline")
        self.nodes = pipeline.run(documents=self.documents[0:10])
