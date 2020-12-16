from google.cloud import storage
from google.cloud import pubsub_v1
import pandas as pd
import facebook
import os
import base64

def env_vars(var):
    return os.environ.get(var, 'Specified environment variable is not set.')

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Uploads a file from the bucket to a local file."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    with open(destination_file_name, 'wb') as file_obj:
        storage_client.download_blob_to_file(blob, file_obj)

    print(
        "File {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )

def publish_message(topic_name_in, msg):
    """Publish a message to a given topic."""
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
        topic=topic_name_in,
    )
    # message = base64.b64encode(str(msg))
    # body = {'messages': [{'data': message}]}
    publisher = pubsub_v1.PublisherClient()
    resp = publisher.publish(topic_name, msg, spam='eggs')
    print ('Published a message "{}" to a topic {}. The message_id was {}.'
           .format(msg, topic_name_in, resp.get('messageIds')[0]))

def fetch_fb_data_analyse(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    # Reading fb data
    apikey=env_vars('apikey')
    fb = facebook.GraphAPI(apikey)
    profile = fb.get_object("me", fields="name, birthday")
    likes = fb.get_object(
            "me", fields="likes.limit(100) {name,about,fan_count,category}")
    print("*****profile json*******")
    print(profile)
    print("*****Liked pages json*******")
    print(likes)
    print("*****preprocessing begin*******")

    pages = likes['likes']['data']
    pages_df = pd.DataFrame(pages)
    print(pages_df)

    bucket_name = "category-store"
    local_file_path = "/tmp/local_file.csv"
    download_blob(bucket_name, 'fb_page_category.csv', local_file_path)
    # reading category.csv file from storage
    category = pd.read_csv(local_file_path)
    category = pd.DataFrame(category)
    print(type(category))
    print(category.info())

    # merging category and likedpages
    merged_df = pd.merge(pages_df, category, how='left',
                     left_on='category', right_on='SubCategory')
    mainCategoryNo = merged_df['MainCategory'].value_counts()
    print(mainCategoryNo)
    cat_csv = mainCategoryNo.to_csv()
    destination_file_path = "/tmp/result.csv"
    with open(destination_file_path, 'w') as file_obj:
        file_obj.write(cat_csv)
    upload_blob(bucket_name, destination_file_path, 'write-file.csv')
    publish_message('fetch-data-trigger', b'test json msg 2020-12-13 21:47')