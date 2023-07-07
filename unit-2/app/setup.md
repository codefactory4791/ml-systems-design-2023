## Course Setup

### Setup a personal Google Cloud account for $300 in credits (preferred)

[![Signup](https://res.cloudinary.com/marcomontalbano/image/upload/v1681813869/video_to_markdown/images/google-drive--1F4GLHXFJu68yrEgucK9TeHixatGYGQxC-c05b58ac6eb4c4700831b2b3070cd403.jpg)](https://drive.google.com/file/d/1F4GLHXFJu68yrEgucK9TeHixatGYGQxC/preview "Signup") pull

1. If you've not already, create a new gmail address for this course
2. Go to https://cloud.google.com
3. Click "Start Free" in the upper-righthand corner
4. Fill in form info using a fake business name and real credit card info (you won't be charged beyond the $300 of free credits used during this course)
5. Click "Start my free trial!"

*Alternatives*

Understandably, not everyone will be comfortable putting in their credit card info or claiming another $300 credits if they've already used theirs. In those instances, you can:

- request access to an Etsy sandbox project and develop there instead
- ask your manager for permission to expense any costs from this course (well below $100)

If your team doesn't have their own sandbox, you may use the ML platform one. *There is no guarantee commands run in this project will work - you may run into quota issues*.
1. Join [this group](https://groups.google.com/a/etsy.com/g/gcp-ml-users)
2. Go to the [etsy-mlinfrasb-sandbox project in the console](https://console.cloud.google.com/welcome?project=etsy-mlinfrasb-sandbox)

If you see this select condition 3.

![condition](../img/condition.png)

### Setup cloud shell for this course

To start a Cloud Shell session, click the terminal button in the upper right of the cloud console.

![cloud-shell-1](../img/cloud-shell-1.png)

To authenticate with Google run `gcloud auth login`.

![cloud-shell-2](../img/cloud-shell-2.png)

There is a [cloud shell guide](../guides/cloud-shell.md) for information on setting up your cloud shell environment to work with `git` and this repo - however you won't actually need to maintain a Github repo in this course. Unless you're interested in having your own git workflow, you can proceed to the next step.

### Setup permissions used in this course

We'll use a number of Google Cloud tools in this course, including but not limited to:

- Compute engine
- Cloud build
- Kubernetes engine
- Cloud storage
- Cloud functions
- Vertex Pipelines

We need to make sure our account has the proper permissions necessary to develop in the course. Though we'll add permissions throughout, the first permissions we need to add are for our own account. Run the following in Cloud Shell:

```shell
# get project number
export PROJECT_NUMBER=$(gcloud projects list --filter="$(gcloud config get-value project)" --format="value(PROJECT_NUMBER)")

# enable the necessary APIs
gcloud services enable compute.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com

# give ourselves admin perms for cloud storage and kubernetes
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT --member="user:$USER_EMAIL" --role="roles/container.admin"
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT --member="user:$USER_EMAIL" --role="roles/storage.admin"

# give the default compute SA storage perms
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" --role="roles/storage.admin"
```

### Setup budget and billing alerts

To avoid being charged unkowingly should you forget to scale resources down, it's wise to set both a _project budget_ and any billing alerts you want in the Billing console.

![budget](../img/budget.png)

![billing](../img/billing.png)
