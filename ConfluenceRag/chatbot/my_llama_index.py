# import phoenix as px
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    # set_global_handler,
    get_response_synthesizer,
)
from llama_index.core import StorageContext
from llama_index.core.embeddings import resolve_embed_model

# from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter

# from llama_index.core.extractors import (
#     SummaryExtractor,
#     QuestionsAnsweredExtractor,
#     TitleExtractor,
#     KeywordExtractor,
# )

from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
# from llama_index.extractors.entity import EntityExtractor
from llama_index.core.schema import IndexNode

from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI

from llama_index.vector_stores.chroma import ChromaVectorStore
from chromadb import chromadb, Settings as ChromaSettings


# To view traces in Phoenix, you will first have to start a Phoenix server. You can do this by running the following:
# session = px.launch_app()

# Once you have started a Phoenix server, you can start your LlamaIndex application and configure it to send traces to Phoenix. To do this, you will have to add configure Phoenix as the global handler
# set_global_handler("arize_phoenix")


class LlamaIndex:
    def __init__(self, data_path, isNode, isHTTP):
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
        self.isNode = isNode
        self.isHTTP = isHTTP
        self.chroma_collection = None
        if isHTTP is True:
            self.db = chromadb.HttpClient(
                # host="localhost"
                # chroma host for container
                host="chromadb",
                port=8000,
                settings = ChromaSettings(allow_reset=True, anonymized_telemetry=True)
            )
        else:
            self.db = chromadb.PersistentClient(
                path="./data/chroma_db"
            )

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
                # print(file_path)
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
        if self.isHTTP is not True:
            self.documents = SimpleDirectoryReader(
                self.data_path, recursive=True, file_metadata=get_meta
            ).load_data()
            print(f"Number of documents loaded: {len(self.documents)}")
        else:
            # TODO: Cloud data storage for documents to be loaded from
            self.documents = SimpleDirectoryReader(
                self.data_path, recursive=True, file_metadata=get_meta
            ).load_data()

    def set_embed_model(self, model_path):
        """
        Set the embedding model path in LlamaIndex settings.

        Args:
        model_path (str): The path to the embedding model set in main.py set_embed_model execution.
        """
        # TODO: Investigate moving param model_path to client initialization
        print(f"Setting embed model to {model_path}")
        Settings.embed_model = resolve_embed_model(model_path)

    def set_llm(self, model, request_timeout=None, api_token=None):
        """
        Configure the querying LLM to OpenAI or Local Ollama instance with the specified model and timeout.

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

    def create_index(self):
        """
        Create an index based on whether the index is for nodes or documents.
        """
        # Determine the collection name based on the node flag
        # TODO: Change to a static name as Doc_to_node is not being tested
        collection_name = f"llama_index_{self.isNode}"
        self.chroma_collection = self.db.get_or_create_collection(name=collection_name)

        # Check the current size of the collection
        collection_size = self.chroma_collection.count()

        # check if the collection is empty
        # TODO: IMPLEMENT A REAL CHECK
        if collection_size == 0:
            print(f"collection {collection_name} is empty. Populating collection...")
            # TODO: FIX LOGIC INSIDE THIS IF,
            if self.isNode is True:
                print("Building Nodes")
                # build parent chunks via NodeParser
                node_parser = SentenceSplitter(chunk_size=1024)
                base_nodes = node_parser.get_nodes_from_documents(self.documents)

                # define smaller child chunks
                sub_chunk_sizes = [256, 512]
                sub_node_parsers = [
                    SentenceSplitter(chunk_size=c, chunk_overlap=20)
                    for c in sub_chunk_sizes
                ]

                all_nodes = []
                for base_node in base_nodes:
                    for n in sub_node_parsers:
                        sub_nodes = n.get_nodes_from_documents([base_node])
                        sub_inodes = [
                            IndexNode.from_text_node(sn, base_node.node_id)
                            for sn in sub_nodes
                        ]
                        all_nodes.extend(sub_inodes)
                    # also add original node to node
                    original_node = IndexNode.from_text_node(
                        base_node, base_node.node_id
                    )
                    print(f"original_node after processing: {original_node}")
                    all_nodes.append(original_node)

                self.nodes = all_nodes

                # TODO: Debug the index creation from nodes
                # (chromaDB related, when adding nodes to collection, the node_id contains a full NodeWithScore object, not the NodeWithScore.node-id)
                self.index = VectorStoreIndex(
                    nodes=self.nodes,
                    embed_model=Settings.embed_model,
                    storage_context=StorageContext.from_defaults(
                        vector_store=self.chroma_collection
                    )
                )
            else:
                print("initializing Chroma Vector Store")
                # Create a vector store using the Chroma collection from the database
                vector_store = ChromaVectorStore(
                    chroma_collection=self.chroma_collection
                )

                print("Initializing Storage Context")
                # Initialize storage context with default settings overiding vector_store with the specified vector store
                storage_context = StorageContext.from_defaults(
                    vector_store=vector_store
                )

                print(f"Initializing a vector store Index from our documents, and embedding with the Settings.embed {Settings.embed_model}")
                # Create a new index from the documents using the specified vector store and embedding model
                # embedding_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
                self.index = VectorStoreIndex.from_documents(
                    self.documents,
                    show_progress=True,
                    storage_context=storage_context,
                    embed_model=Settings.embed_model,
                    # transformations=[
                    #     # SentenceSplitter(),
                    #     # Add more transformations if necessary or IMPLEMENT DOC_TO_NODE
                    #     KeywordExtractor(keywords=10)
                    # ],
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
        if self.isNode is True:
            all_nodes = self.nodes
            vector_retriever_chunk = self.index.as_retriever(similarity_top_k=2)

            # build RecursiveRetriever
            all_nodes_dict = {n.node_id: n for n in all_nodes}
            retriever_chunk = RecursiveRetriever(
                "vector",
                retriever_dict={"vector": vector_retriever_chunk},
                node_dict=all_nodes_dict,
                verbose=True,
            )
            # build RetrieverQueryEngine using recursive_retriever
            query_engine_chunk = RetrieverQueryEngine.from_args(
                retriever=retriever_chunk,
            )
            self.query_engine = query_engine_chunk
        else:
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=6,
            )
            # Configure the response synthesizer based on the streaming flag
            response_synthesizer = get_response_synthesizer(
                streaming=stream,
                structured_answer_filtering=False,
            )

            # Set up the query engine with the configured retriever and response synthesizer
            self.query_engine = RetrieverQueryEngine(
                retriever=retriever,
                response_synthesizer=response_synthesizer,
                # node_postprocessors=[],
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
        # px.active_session().url
        return response

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # UNUSED
    # def doc_to_node(self):
    #     """
    #     Convert documents to nodes by applying various transformations for metadata extraction.
    #     """
    #     print("converting documents to nodes")

    #     # Define the transformations to be applied to the documents
    #     transformations = [
    #         SentenceSplitter(),
    #         TitleExtractor(nodes=5),
    #         QuestionsAnsweredExtractor(questions=3),
    #         SummaryExtractor(summaries=["prev", "self"]),
    #         KeywordExtractor(keywords=10),
    #         EntityExtractor(prediction_threshold=0.5),
    #     ]

    #     # Apply transformations to the first 10 documents
    #     print(f"applying transformations: {transformations}")
    #     pipeline = IngestionPipeline(transformations=transformations)

    #     # Apply transformations to the first 10 documents
    #     print("running Ingestion Pipeline")
    #     self.nodes = pipeline.run(documents=self.documents[0:10])
