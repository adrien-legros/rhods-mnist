# Lab Instructions

Follow the deployment instructions [here](https://github.com/adrien-legros/rhods-mnist) before running the lab.

## Log in to Red Hat OpenShift Data Science (RHODS)

On the top right of the OpenShift console click on the Application Launcher button and click on the Red Hat OpenShift Data Science (RHODS) managed service. Connect to the RHODS console with an existing user that has admin right on mnist namespace. Note that we might reduce admin permission for that user, but for now let's simplify things.

![launch-dashboard](./screenshots/launch-dashboard.png)

## Start a new data science project

### Create the workbench

Go to the **Data Science projects** tab and click on the pre-created **mnist** project.

![data-science-project](./screenshots/ds-project.png)

This project has been created with a pvc for the notebook filesystem (i.e the jupyterlab notebooks). It also has a data connection, which is a secret containing the minio credentials for the S3 storage. We will connect those 2 storages to the workbench we are about to create.  
Click on *create workbench* and fill up the form:
- Add a name (we choose *notebook*)
- Select a notebook image
  - **If you have GPU available and want to use it inside your notebook**, please select: "Custom Datascience Notebook Cuda 11.4" image.
  - **Otherwise**, please select: "Custom Datascience Notebook" image.
- Choose a container size (*small* is suffisent in our example)
- Select a persistent storage. Use an existing one and select the one that has been created for you during the lab initialization. (named *notebook*).
- Select a data connection (S3 storage). Use an existing one and select the one that has been created for you during the lab initialization. (named *s3-creds*).

Refer to the bellow example where we deploy a notebook able to use GPU:

![create-workbench-1](./screenshots/create-notebook-1.png)

![create-workbench-2](./screenshots/create-notebook-2.png)

RHODS is going to pull a few container images especially the one used for the jupyterlab notebook server. The "Custom Datascience Notebook Cuda 11.4" notebook image is quite heavy (~ 6GB) as it contains the cuda library required to use the GPU in the model training. It can take a few moment for the first pull only (the image is copied in your openshift internal registry). Checkout the notebook status and click on the *open* link.

![create-workbench-3](./screenshots/create-notebook-3.png)

## JupyterLab notebooks

You are now in the jupyterlab interface.
On the left side click on the git clone button and clone this repository: https://github.com/adrien-legros/rhods-mnist-model.git. 

![git-clone](./screenshots/git-clone.png)

Navigate to *./notebooks/todo*. Check the following files:

### Notebooks

There are 4 notebooks and 1 pipeline available. Navigate to each of the notebooks to understand what's going on.

#### Pre-process

Load and pre-process the data. The data used to train and test the model are loaded from the minio s3 bucket. In this notebook, we are describing the data and running basic analysis such as counting the number of observation per label. We also transform the data by normalizing and reshaping them. We store the python numpy objects in a persistent volume so it is available to the others notebooks (i.e available to next pipeline steps).

#### Train

We load the processed data, the we create and train a model. The model is a convolutional neural network. See the architecture of the model and the different layers. Once the model is trained, we test it and display few metrics such as the f1 score or the confusion matrix.  
The model is saved in the minio bucket in onnx format so that we can serve it later on this lab.

#### Evaluate

Retrieve and test the saved model. Declare prediction score so it is available through output metadata in kubeflow pipeline.

#### Review

Analyse misclassification

### Elyra pipeline

Display the pipeline by openning the file *mnist.pipeline*.
It is a pipeline generated thanks to Elyra visual editor. You can see how the notebooks are linked together.
If you right click on a "node" you can open the properties tab. You can check that there are some envrionemental variables referenced by a secret name and key. The environment variables are passed to the notebook so it can store artifacts to the minio S3 bucket.
See also that we need to reference a Runtime Image where the python code will run. You will have to choose the runtime image, depending if you selected the CUDA notebook image or not.

## Review the pipeline

### Runtime image

Open the pipeline properties panel by clicking on the *Open Panel* button, or right clicking to a node, select *Open Properties* and switch tab to *Pipeline Properties*. The runtime image is used to execute your notebook inside a container on Openshift.

![pipeline-properties](./screenshots/pipeline-properties.png)

Available pipeline runtime on this lab:
- **For GPU user**: Ensure the "Custom Runtime for mnist : CUDA11.4/Py38" runtime image is selected
- **For CPU user**: Ensure the "Custom Runtime for mnist : Py38" runtime image is selected

### Add a pipeline step

#### Add a node

Open the *mnist.pipeline* file. You can add a step by grabbing a playbook from the file browser to the UI. See the animation bellow. Add the *Review.ipynb* notebook to the pipeline. Link it to both *Pre-process.ipynb* and *Train.ipynb*. You should have a similar picture at the end:

![pipeline-completed](./screenshots/pipeline-completed.png)


#### Add properties

We need to pass the processed data to the *Review.ipynb* notebook. We will use a volume to share data between pipeline steps. *Pre-process.ipynb* will write data to this volume and *Review.ipynb* notebook will read data from it.

Open the properties menu. Choose node properties. Scroll down to *Data Volumes*. Complete the following information:

- **Mount Path**: /tmp/ml-pipeline
- **Persistent Volume Claim Name**: ml-pipeline

### Add the Kubeflow Runtime

We need to add a Kuflow Runtime so Elyra can trigger Kubeflow Pipeline API to run a data science pipeline. On the left navigation bar, click on Runtimes icon. Create a runtime as follow:

- **Display Name**: Kubeflow Runtime
- **Kubeflow Pipelines API Endpoint**: http://ds-pipeline-ds-pipeline.mnist.svc.cluster.local:8888
- **Public Kubeflow Pipelines API Endpoint**: @TODO
- **Kubeflow Pipelines engine**: Tekton
- **Cloud Object Storage Endpoint**: http://minio-ds-pipeline.mnist.svc.cluster.local:9000
- **Public Cloud Object Storage Endpoint**: @TODO
- **Cloud Object Storage Bucket Name**: rhods
- **Cloud Object Storage Authentication Type**: USER_CREDENTIALS
- **Cloud Object Storage Username**: minio
- **Cloud Object Storage Password**:  minio123

![kf-values]()

### Run the pipeline

Go back to mnist.pipeline. Click on the run button. Choose *Kubeflow Pipelines* as the Runtime Plateform. Then click OK. 

![run-pipeline](./screenshots/run-pipeline.png)

![run-success]()

Click on the *Run Details* link to go to Kubeflow Pipeline dashboard. This dashboard enables you to see your pipeline runs.

## Navigate to Kubeflow Pipeline

Once in the Kubeflow Pipeline dashboard navigate to the **Runs** tab. A new run has been launched for you by Elyra. Click on it. You can see a graph with your pipeline steps.  
Check out the logs by clicking on a step, then on the log tab.

![pipeline-logs](./screenshots/pipeline-logs.png)

The pipeline completed after approximatively 5 minutes.

Click on the **Run Ouput** tab. Notice that few metadata artifacts has been created throughout the pipeline. By default, you can retrieve all logs in html or ipynb format. Click on a link to redirect to minio bucket.  

![artifacts](./screenshots/artifacts.png) //TODO//

## Model Serving

Now it is time to serve our model using modelmesh serving. Go back to RHODS dashboard. Click on **Configure server**. Secure the model with a **token authorization**. The token authorization uses oauth proxy as backend. You don't need an external route. Choose *model-mesh* as the service account name. Finally click on configure:

![model-serving](./screenshots/serving-no-route.png)

Then click on **Deploy model**. Enter **mnist** as model name. Select **onnx - 1** as model framework. In the *Train.ipynb* notebook we trained and saved a model in the onnx format. We converted a tensorflow model in the onnx format. The onnx model is saved in the minio S3 bucket at the path **onnx/model-v2.onnx**. Let's add **s3-creds** as the data connection and *onnx/model-v2.onnx* as the folder path. Deploy the model. 

![deploy-model](./screenshots/deploy-model.png)

Wait for the model deployment to complete. You can now see the model delpoyment status as well as the token associated with the service account created.  
**NOTE:** The service account resource as not been created. The model server has created a service-account-token sercret named *model-mesh* containing the token, certificate etc.

![model-serving-token](./screenshots/model-serving-status.png)
![model-serving-endpoint](./screenshots/model-serving-token.png)

## Interact with the model

### Deploy the webapp and the serverless function

The goal of this serverless function is to act as a lightweight pre-processing function between the web interface (that acts as a frontend) and the model serving. We need a pre processing function to transform the data drown in the UI that are in png format into a tensor understandable by the model. Recall that we defined our neural network that way:

![model-zoom](./screenshots/model-zoom.png)

The ONNX framework is adequation with this architecutre. Therefore the model server is expecting as input a [1, 28, 28, 1] shape tensor nammed *input_1*.  
For more information conerning the serverless function check out the openshift-serverless/functions/app-src directory. The file *preprocessing.py* contains the 2 most important functions:
- process_data: convert the png format to a well shaped tensor
- process_payload: take the template expected by modelmesh serving and add the processed data

Now deploy the serverless function and the frontend web application:
```shell
oc apply -k ./inference/
```

Get the route endpoint and visit the url!

```shell
echo http://$(oc -n mnist get route mnist-webapp -ojsonpath='{.status.ingress[0].host}')
```

Draw a digit between 1 and 9. Click on predict and see te ouput. Note: the first prediction can take more time as the serverless function might not be running. The following predictions will be much faster.