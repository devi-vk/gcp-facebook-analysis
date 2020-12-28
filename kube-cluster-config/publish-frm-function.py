import facebook
import pandas as pd
from google.cloud import storage
from google.cloud import pubsub_v1
import os
from io import StringIO
import gcsfs

apikey = "EAAFhij0hmUMBAN99mNbHeKb0GLV8MVE6rPOPsAXLhpQzyvn8J7TQfo5BMcARdPh7SA7SVooHWzr5RnRXVb47ZBmbntFQ3TgZCpZAXsmC6ljV36I6DKCzhIbA9SW4bwQn8qF2ipJQZBL1yu0fKnHvYwkSJxda3eGBEs6Ni7XOBFzGZAz2AGpCj"

def read_write_gcs(event, context):

    #Reading fb data
    fb = facebook.GraphAPI(apikey)
    #profile = fb.get_object ("me", fields = "name, birthday")
    likes = fb.get_object("me", fields = "likes.limit(100) {name,about,fan_count,category}")
    
    """
    print("*****profile json*******")
    print(profile)
    print("*****Liked pages json*******")
    print(likes)
    print("*****preprocessing begin*******")
    """
    pages = likes['likes']['data']
    pages_df = pd.DataFrame(pages)
    #print(pages_df)

    
    #reading category.csv file from storage
    storage_client = storage.Client()
    bucket_name = "category_csv_file"

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.get_blob("fb_page_category.csv")

    category = pd.read_csv("gs://category_csv_file/fb_page_category.csv")
    category = pd.DataFrame(category)
    #print(type(category))
    #print(category.info())

    #merging category and likedpages
    merged_df = pd.merge(pages_df, category, how='left', left_on='category', right_on='SubCategory')
    mainCategoryNo = merged_df['MainCategory'].value_counts()
    
    #Writing the DF as csv file in gcs bucket
    cat_json = StringIO()
    mainCategoryNo.to_json(cat_json)
    cat_json.seek(0)
    storage_client.get_bucket('category_csv_file').blob('category_count.json').upload_from_file(cat_json, content_type='text/json')

    #top 10 pages based on fan count
    top_ten = pages_df.nlargest(10, 'fan_count')[["name","fan_count"]]
    top_ten_json = StringIO()
    top_ten.to_json(top_ten_json)
    top_ten_json.seek(0)
    storage_client.get_bucket('category_csv_file').blob('top_ten_pages.json').upload_from_file(top_ten_json, content_type='text/json')


    #analysis of liked pages based on fan count
    df_fan_count = merged_df[["name","fan_count","MainCategory"]]
    df_fan_count["fan_count"] = pd.cut(df_fan_count["fan_count"], [0,500,5000,10000,100000000],labels= ['low(<500)','average(501-5000)','high(5001-10000)','very high(>10000)'])
    fan_count_group = df_fan_count.groupby("MainCategory").fan_count.value_counts()
    
    #Writing fan counf DF into csv file in gcs bucket
    fan_df = pd.DataFrame(fan_count_group)
    fan_df.columns=['page_counts']
    fan_count = StringIO()
    fan_df.to_json(fan_count)
    fan_count.seek(0)
    storage_client.get_bucket('category_csv_file').blob('fan_count.json').upload_from_file(fan_count, content_type='text/json')

    #Publishing message in pubsub topic

    topic_name = "projects/iot-project-group6/topics/data-raw"
   
    publisher = pubsub_v1.PublisherClient()
    publisher.publish(topic_name, b"gs://category_csv_file/fan_count.csv", spam='eggs')