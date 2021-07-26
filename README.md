# Facebook data analysis in GCP

The primary platform used for this project is Google Cloud Platform (GCP) using the runtime Python. For data visualization, the platforms used are Data Studio, Node-red, and Blynk app. The node-red application is deployed in Google kubernetes Engine(GKE). The application fetches the liked pages from the user’s profile and then analyses the main categories of the liked pages as per their fan_counts. The project structure can be visualized in the below picture.

     
<img width="402" alt="gcp" src="https://user-images.githubusercontent.com/53037645/105612604-9f6f3680-5dbd-11eb-893d-57a4702b65be.PNG">


## Project structure
    The cloud function source code is in the all-complete.py
    The requirements for the cloud function is in the requirements.txt
    The YAML files need to create a kubernetes deployment is in the k8s folder
    The noder-red flows are in the node-red-flows folder
    
## Deploy in GCP

The application is deployed in GCP. The API key in the source code needs to be updated with the API token generated from facebook developers page. The trigger for the cloud function is PubSub topic. It stores resulting CSV and JSON files in a GCS bucket and publishes the JSON file names in two PubSub topics. The topics triggers the node-red GCP subscribers node to fetch the data from GCP bucket.
