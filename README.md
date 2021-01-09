# myimdb
Simple Flask app to pull movies that I rated on IMDB and present them in better view with the rating.
The main goal of this project to practice containers and Kubernetes.
- Flask app to scrape IMDB using BeautifulSoup.
- containeriz the app using Docker.
- Deoply to Azure Kubernetes Service (AKS)
- restructure the app layout follwoing best practicess from Flas official website  
- Make the app interactive using JS to enable filtering by rating, then redoply the new app (container)
- Implement refresh functionality
- Try different settings and concepts of Kubernetes

# Run in on Minikube
First, in seprated window start minibuke tunnling :

> minikube tunnel

Then :

> kubectl apply -f myimdb-deployment.yaml

> kubectl apply -f myimdb-service.yaml


The app should be accessable on :

``` http://127.0.0.1:5000/ ``` 