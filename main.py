import facebook
import pandas as pd
import matplotlib.pyplot as plt

from google.cloud import storage

apikey = "EAAFhij0hmUMBAN99mNbHeKb0GLV8MVE6rPOPsAXLhpQzyvn8J7TQfo5BMcARdPh7SA7SVooHWzr5RnRXVb47ZBmbntFQ3TgZCpZAXsmC6ljV36I6DKCzhIbA9SW4bwQn8qF2ipJQZBL1yu0fKnHvYwkSJxda3eGBEs6Ni7XOBFzGZAz2AGpCj"

def collector(event, context):
"""
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
    mainCategoryNo = mainCategoryNo.to_dict()
    print(mainCategoryNo)

    #analysis of liked pages based on fan count
    df_fan_count = merged_df[["name","fan_count","MainCategory"]]
    df_fan_count["fan_count"] = pd.cut(df_fan_count["fan_count"], [0,500,5000,10000,100000000],labels= ['low(<500)','average(501-5000)','high(5001-10000)','very high(>10000)'])
    fan_count_group = df_fan_count.groupby("MainCategory").fan_count.value_counts()
    print(fan_count_group)
    fan_count_group.unstack().plot(kind='bar')
"""

    storage_client = storage.Client()
    bucket = storage_client.get_bucket('categoty_csv_file')
    blob = bucket.blob('fb_page_category.csv')  
    df = pd.read_csv("gs://category_csv_file/fb_page_category.csv")

    print(df.info())