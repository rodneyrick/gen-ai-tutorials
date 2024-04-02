from dotenv import load_dotenv
load_dotenv()

from langchain_community.llms import Ollama
llm = Ollama(model="tinyllama", base_url='http://ollama:11434')
llm.invoke("Tell me a joke")

from langchain.document_loaders import GitLoader
loader = GitLoader(
    clone_url="https://github.com/Mause/duckdb_engine",
    repo_path="/tmp/data/duckdb_engine/",
    branch="main",
)
docs = loader.load()

# All the Database files will be saved in this directory on your local machine
persist_directory = 'db'

from langchain.embeddings import OllamaEmbeddings
embedding_model = OllamaEmbeddings(
    model='nomic-embed-text', 
    base_url='http://ollama:11434'
)

import qdrant_client
client = qdrant_client.QdrantClient(
    "http://qdrant:6333", 
    api_key='qdrant',
    prefer_grpc=True
)
# client.get_collections()

vectorstore = Qdrant.from_documents(
    documents=docs,
    collection_name="test",
    embedding=embedding_model
)




embedding_model
# https://stackoverflow.com/questions/78162485/problems-with-python-and-ollama