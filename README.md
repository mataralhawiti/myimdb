# myimdb
A simple Flask app to pull movies that I rated on IMDB and present them in better view with the ratings.
The main goal of this project to practice containers and Kubernetes.
- Flask app to scrape IMDB using BeautifulSoup.
- containeriz the app using Docker.
- Deoply to Azure Kubernetes Service (AKS)
- Make the app depoluable on any K8 distributaion
- restructure the app layout follwoing best practicess from Flas official website  
- Make the app interactive using JS to enable filtering by rating, then redoply the new app (container)
- Implement refresh functionality
- Try different settings and concepts of Kubernetes

## Run it on Minikube (Manually)

**First**, in a terminal window  :

``` kubectl apply -f .\k8\deployment.yaml ```

``` kubectl apply -f .\k8\service.yaml ```

**Then**, in a separate terminal window start minibuke tunnling :

``` minikube tunnel ```

The app should be accessable on :

``` http://127.0.0.1:5000/ ``` 


## Run it on Minikube (Helm Chart)

``` helm install movies .\charts\myimdb ``` 

**Then**, in a separate terminal window start minibuke tunnling :

``` minikube tunnel ```

The app should be accessable on :

``` http://127.0.0.1:5000/ ``` 
