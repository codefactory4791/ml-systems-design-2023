# ML in Production and ML Engineering Fundamentals

## Deploying an ML Model to Kubernetes

The reason we're all _actually_ here is to create real, ML deployments. In this section, we're going to breeze through a _purely practical_ exercise of:

1. Training a model
2. Packaging it in a Docker image behind a web server
3. Creating a Kubernetes cluster
4. Deploying the container to that cluster with a public endpoint

Let's start by training a toy model.

```shell
cd unit-1-ml-eng-fundamentals
python -m pip install -r requirements.txt
python train.py
```

`train.py` is a simple Python script that trains an ML model for binary classification using synthetic data:

```python
import pickle
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

x, y = make_classification(
    n_samples=100, 
    n_features=3, 
    n_informative=2, 
    n_classes=2, 
    n_redundant=0, 
    n_repeated=0,
)

lr = LogisticRegression()
lr.fit(x,y)
print("Training complete!")

with open('model.pickle', 'wb') as f:
    pickle.dump(lr, f)
```

The script dumps the model out to disk in a serialized `pickle` format. This allows us to load the model back into Python later to make predictions.

As discussed during the presentation, we typically use web apps and lightweight APIs to deploy machine learning models for real-time inference. The file `app.py` defines a simple API using Python's FastAPI library, loads our trained model into memory, and allows us to make predictions.

```python
import uvicorn
import pickle
import sklearn
from fastapi import FastAPI

with open('model.pickle','rb') as f:
    model = pickle.load(f)

app = FastAPI()

@app.get('/')
def index():
    return {
        'message': 'Hey look it\'s working'
    }

@app.get('/predict')
def predict(
        feature_1: int = 0, 
        feature_2: int = 0, 
        feature_3: int = 0
    ):
    return {
        'output': model.predict(
            [[feature_1, feature_2, feature_3]]
            ).tolist()
        }

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)
```

To make this service easily portable, we containerize it with Docker:

```shell
docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/ml-serving:0.0.1 .
```

We can also run this service in Cloud Shell and get a public endpoint to verify the container will work in production.

```shell
## run the container
docker run -it -p 5000:5000 -d gcr.io/$GOOGLE_CLOUD_PROJECT/ml-serving:0.0.1

## make a request from Cloud Shell
curl http://localhost:5000
```

We also can confirm it's working with Cloud Shell by checking a web preview on port 5000.

![](../img/web-preview.png)
![](../img/web-preview-success.png)

After verifying the container works - we can push it to Google Container Registry.

```shell
docker push gcr.io/$GOOGLE_CLOUD_PROJECT/ml-serving:0.0.1
```

Now, we can use Kubernetes objects to deploy these to our cluster! Our Kubernetes *Deployment* lets us specify an image and define how we use it. This object will create one of more *Pods* (smallest deployable unit in K8s) - each of which are basically running containers. 

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-app
  labels:
    app: ml-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ml-app
  template:
    metadata:
      labels:
        app: ml-app
    spec:
      containers:
      - name: ml-app
        image: IMAGE
        imagePullPolicy: Always
        ports:
        - containerPort: 5000
        resources:
          # You must specify requests for CPU to autoscale
          # based on CPU utilization
          requests:
            cpu: "1"
```

To use our recently built image in the Kubernetes manifest, run:

```shell
sed -i -e 's/IMAGE/gcr.io\/'"$GOOGLE_CLOUD_PROJECT"'\/ml-serving:0.0.1/g' k8s/deployment.yaml
```

In order to better scale our application, we also create a *HorizontalPodAutoscaler* (HPA) that scales our deployment between 1 and 5 replicas based on the CPU utilization.

This HPA uses an `averageUtilization` of 40 - meaning that it will attempt to keep our average CPU utilization at 40% of 1 CPU.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-app
spec:
minReplicas: 1
  maxReplicas: 5
  metrics:
  - resource:
      name: cpu
      target:
        averageUtilization: 40
        type: Utilization
    type: Resource
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-app
```

Lastly - we need an endpoint that maps to all of our potential backends. We can use a Kubernetes *Service* object to create a load balancer with a public IP address that maps to all of our backends.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ml-app
spec:
  selector:
    app: ml-app
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
  type: LoadBalancer
```

Finally - we're onto the cluster itself. We can create and connect to a simple cluster using `glcoud`:

```shell
gcloud container clusters create ml-cluster --region us-central1 --num-nodes=1
gcloud container clusters get-credentials ml-cluster --region us-central1 --project $GOOGLE_CLOUD_PROJECT
```

Once our cluster is created, we can use the Kubernetes CLI to create our ML deployment and expose it to the world!

```shell
kubectl apply -f k8s
```

We can watch pods come up with the Kubernetes API as well:

```shell
kubectl get po -w
```

The service object we created also added a public IP address. We can reach it and `curl` it to affirm the model is working.

```shell
LOADBALANCER_IP=$(kubectl get svc ml-app --no-headers | awk '{print $4}')
curl $LOADBALANCER_IP:5000
```

By visiting the HOST:PORT in browser, we can now get model predictions using GET requests and query parameters. We can also make prediction from the commands line.

```shell
curl "$LOADBALANCER_IP:5000/predict?feature_1=1&feature_2=1&feature_3=1"
```

To finish, let's make sure we clean up by deleting our cluster from the command line.

```shell
gcloud container clusters delete ml-cluster --region=us-central1
```

So yeah **that was probably a lot**. Don't worry if you don't understand what happened. The purpose of this exercise was more to _have fun_ and play with Cloud Shell and GKE. Next time, we'll explain more about these objects and how they work!

## Supplemental Reading

- [Kubernetes Practical Intro for Data Scientists](https://towardsdatascience.com/kubernetes-practical-intro-for-data-scientists-739c263efa06?sk=164bc0b36babe070eaea4cf655e99d48)