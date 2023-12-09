import os
import shutil
from google.cloud import storage

gcp_project = "neat-tempo-403105"

csv_dir = "scraped"
bucket_name = "jds_gecx"
filtered_csv = "jobs_filtered"

# Downloads a particular CV
def download_csv():
    print("downloading filtered JDs")

    # Clear
    shutil.rmtree(cvs_dir, ignore_errors=True, onerror=None)
    os.makedirs(cvs_dir, exist_ok=True)

    storage_client = storage.Client(project=gcp_project)

    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=cvs_dir + "/")
    for blob in blobs:
        print(blob.name)
        if blob.name.endswith(f"{filtered_csv}.csv"):
            blob.download_to_filename(blob.name)

# Downloads a particular CV
def download_cv(id):
    print("downloading CV")

    # Clear
    shutil.rmtree(cvs_dir, ignore_errors=True, onerror=None)
    os.makedirs(cvs_dir, exist_ok=True)

    storage_client = storage.Client(project=gcp_project)

    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=cvs_dir + "/")
    for blob in blobs:
        print(blob.name)
        if blob.name.endswith(f"{id}.pdf"):
            blob.download_to_filename(blob.name)


def main(args=None):
    print("Args:", args)

    if args.jobs:
        download_csv()
    if args.cv:
        download_cv(args.id)


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Generate text from prompt")

    parser.add_argument(
        "-j",
        "--jobs",
        action="store_true",
        help="Download Job Descriptions from GCS bucket",
    )

    parser.add_argument(
        "-c",
        "--cv",
        action="store_true",
        help="Uploads the recommended job skills of a user to the GCS bucket",
    )

    parser.add_argument(
        "-i",
        "--id",
        help="ID of the user",
    )

    args = parser.parse_args()
    main(args)