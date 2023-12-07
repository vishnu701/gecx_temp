# Importing necessary libraries
from llama_index import SimpleDirectoryReader, GPTVectorStoreIndex, StorageContext, ServiceContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores import PineconeVectorStore
from llama_index.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.query_engine import SubQuestionQueryEngine

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
cvs_dir = "cvs"
pinecone_index_name = 'jds'
upload_path = "job_recommend"

def download():
    print("download")

    # Clear
    shutil.rmtree(cvs_dir, ignore_errors=True, onerror=None)
    os.makedirs(cvs_dir, exist_ok=True)

    storage_client = storage.Client(project=gcp_project)

    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=cvs_dir + "/")
    for blob in blobs:
        print(blob.name)
        if blob.name.endswith(".pdf"):
            blob.download_to_filename(blob.name)

def load_api_keys():
    load_dotenv(dotenv_path="secrets/keys.env")

def initialize_pinecone():
    # Initializing connection ot pinecone
    pinecone.init(
        api_key=os.getenv('PINECONE_API_KEY'),
        environment=os.getenv('PINECONE_ENVIRONMENT')
    )

def recommend_skill(id, job_title):
    # Reading the PDF files in the directory "JDs"
    cvs = SimpleDirectoryReader(input_files=[os.path.join(cvs_dir, f"{id}.pdf")]).load_data()
    
    initialize_pinecone()

    # Setting up the index/query process
    embed_model = OpenAIEmbedding(model='text-embedding-ada-002', embed_batch_size=100)

    llama_debug = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([llama_debug])
    service_context = ServiceContext.from_defaults(embed_model=embed_model, callback_manager=callback_manager)

    pinecone_index = pinecone.Index(pinecone_index_name)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    jd_index = GPTVectorStoreIndex.from_vector_store(vector_store)

    jd_engine = jd_index.as_query_engine(similarity_top_k=3)

    cv_index = GPTVectorStoreIndex.from_documents(cvs, use_async=True, service_context=service_context)
    cv_engine = cv_index.as_query_engine(similarity_top_k=3)
    
    query_engine_tools = [
        QueryEngineTool(
            query_engine=jd_engine,
            metadata=ToolMetadata(name="JDs", description="Contains JD information scraped from the company's career websites.")
        ),
        QueryEngineTool(
            query_engine=cv_engine,
            metadata=ToolMetadata(name="CV", description="Contains information about individual candidates")
        )
    ]

    s_engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=query_engine_tools, use_async=True)
    response = s_engine.query(f"What does the user with email {id} need to learn to become a {job_title}?")
    with open(f"{id}_recommended.txt", "w") as f:
        f.write(str(response))

def upload():
    print("upload")
    os.makedirs(cvs_dir, exist_ok=True)

    # Upload to bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)


    file_path = os.path.join(upload_path, text_file)

    destination_blob_name = file_path
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(file_path)

def main(args=None):
    print("Args:", args)

    if args.download:
        download()
    if args.recommend:
        load_api_keys()
        recommend_skill(args.id, args.jobtitle)
    if args.upload:
        upload()

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
        "-u",
        "--upload",
        action="store_true",
        help="Uploads the recommended job skills of a user to the GCS bucket",
    )


    parser.add_argument(
        "-r",
        "--recommend",
        action="store_true",
        help="Recommends skills to learn given user id and the target job title",
    )

    parser.add_argument(
        "-j",
        "--jobtitle",
        help="The job title that the user is targeting",
    )
    parser.add_argument(
        "-i",
        "--id",
        help="ID of the user",
    )

    args = parser.parse_args()

    if args.recommend or args.jobtitle or args.id:
        if args.recommend and args.jobtitle and args.id:
            pass
        else:
            parser.error("-r, -j, and -i needs to be passed together")

    main(args)