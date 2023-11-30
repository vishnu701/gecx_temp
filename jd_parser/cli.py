# Importing necessary libraries
from llama_index import SimpleDirectoryReader, GPTVectorStoreIndex, StorageContext, ServiceContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores import PineconeVectorStore
from llama_index.callbacks import CallbackManager, LlamaDebugHandler

from google.cloud import storage
import shutil
import pinecone
import argparse
import os

from dotenv import load_dotenv
import nest_asyncio

nest_asyncio.apply()


gcp_project = "neat-tempo-403105"
bucket_name = "jds_gecx"
jds_dir = "jds"
pinecone_index_name = 'jds'

def download():
    print("download")

    # Clear
    shutil.rmtree(jds_dir, ignore_errors=True, onerror=None)
    os.makedirs(jds_dir, exist_ok=True)

    storage_client = storage.Client(project=gcp_project)

    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=jds_dir + "/")
    for blob in blobs:
        print(blob.name)
        if blob.name.endswith(".pdf"):
            blob.download_to_filename(blob.name)

def load_api_keys():
    load_dotenv(dotenv_path="secrets/keys.env")

def initialize_pinecone(index_name):
    # Initializing connection ot pinecone
    pinecone.init(
        api_key=os.getenv('PINECONE_API_KEY'),
        environment=os.getenv('PINECONE_ENVIRONMENT')
    )

    # Creating index if it does not already exists
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            index_name,
            dimension=1536,
            metric='cosine'
        )

    # Connecting to the index
    pinecone_index = pinecone.Index(index_name)

    # Creating a vector store from the index
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    return vector_store

def jd_parser():
    # Reading the PDF files in the directory "JDs"
    docs = SimpleDirectoryReader(jds_dir).load_data()
    vector_store = initialize_pinecone(pinecone_index_name)
    # Setting up our storage(vector DB)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    # Setting up the index/query process
    embed_model = OpenAIEmbedding(model='text-embedding-ada-002', embed_batch_size=100)

    llama_debug = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([llama_debug])
    service_context = ServiceContext.from_defaults(embed_model=embed_model, callback_manager=callback_manager)

    GPTVectorStoreIndex.from_documents(
        docs, storage_context=storage_context, use_async=True,
        service_context=service_context
    )

def main(args=None):
    print("Args:", args)

    if args.download:
        download()
    if args.process:
        load_api_keys()
        jd_parser()

if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Generate text from prompt")

    parser.add_argument(
        "-d",
        "--download",
        action="store_true",
        help="Download Job Descriptions from GCS bucket",
    )

    parser.add_argument(
        "-p",
        "--process",
        action="store_true",
        help="Parse the Job Descriptions and upload to Pinecone Vector Store",
    )

    args = parser.parse_args()

    main(args)