import facebook
import pandas as pd
from google.cloud import storage
import os
from io import StringIO

apikey = "EAAFhij0hmUMBAN99mNbHeKb0GLV8MVE6rPOPsAXLhpQzyvn8J7TQfo5BMcARdPh7SA7SVooHWzr5RnRXVb47ZBmbntFQ3TgZCpZAXsmC6ljV36I6DKCzhIbA9SW4bwQn8qF2ipJQZBL1yu0fKnHvYwkSJxda3eGBEs6Ni7XOBFzGZAz2AGpCj"

def category_count(event, context):

    #Reading fb data
    fb = facebook.GraphAPI(apikey)
    profile = fb.get_object ("me", fields = "name, birthday")
    likes = fb.get_object("me", fields = "likes.limit(100) {name,about,fan_count,category}")
    print("*****profile json*******")
    print(profile)
    print("*****Liked pages json*******")
    print(likes)
    print("*****preprocessing begin*******")

    pages = likes['likes']['data']
    pages_df = pd.DataFrame(pages)
    print(pages_df)

    #reading category.csv file from storage
    category = pd.read_csv("https://storage.googleapis.com/category_csv_file/fb_page_category.csv")
    category = pd.DataFrame(category)
    print(type(category))
    print(category.info())

    #merging category and likedpages
    merged_df = pd.merge(pages_df, category, how='left', left_on='category', right_on='SubCategory')
    mainCategoryNo = merged_df['MainCategory'].value_counts()
    #mainCategoryNo = mainCategoryNo.to_dict()
    print(mainCategoryNo)
    
    """
    #conveting into csv
    cat_csv = mainCategoryNo.to_csv()

    #GCS bucket upload
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('category_csv_file')
    blob = bucket.blob('fb_category_count.csv')
    blob.upload_from_filename(cat_csv)
    """
    gcs = storage.Client()
    cat_csv = StringIO()
    mainCategoryNo.to_csv(cat_csv)
    cat_csv.seek(0)
    gcs.get_bucket('category_csv_file').blob('fb_category_count.csv').upload_from_file(cat_csv, content_type='text/csv')

