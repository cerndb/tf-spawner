# TF-Spawner
tf-spawner is a tool to run TensorFlow training distributed on a Kubernetes clusters using 
multi worker TensorFlow strategy.
The changes to TensorFlow code to use distributed strategy are minor in TF 2.0, see 
documentation on [Multi-worker Training with Keras](https://www.tensorflow.org/beta/tutorials/distribute/multi_worker_with_keras)

Author and contact: Riccardo.Castellotti@cern.ch

## Installation

Install the required package with: `pip install kubernetes namesgenerator`

## Usage

```
usage: launch.py [-h] [-d RUN_LABEL] [-w WORKERS] [-n NAMESPACE] [-p PORT]
                 [-e ENTRYPOINT] [-i IMAGE]
                 [path]

positional arguments:
  path                  full path of the TensorFlow script to run (default:
                        None)

optional arguments:
  -h, --help            show this help message and exit
  -d RUN_LABEL, --delete RUN_LABEL
                        delete resources matching RUN_LABEL (default: None)
  -w WORKERS, --workers WORKERS
                        number of workers (default: 8)
  -n NAMESPACE, --namespace NAMESPACE
                        k8s namespace (default: None)
  -p PORT, --port PORT  grpc port (default: 1999)
  -e ENTRYPOINT, --entrypoint ENTRYPOINT
                        pod entrypoint script path (default: None)
  -i IMAGE, --image IMAGE
                        container image for the pod to use (default:
                        tensorflow/tensorflow:2.0.0b1-py3)
```

In order to read data from S3-compatible storage, make sure that you are setting in the environment `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `AWS_LOG_LEVEL`. You can do so modifying the `s3.secrets.example` in the `examples` folder and sourcing it.


## Example

This runs an mnist example
```
export KUBECONFIG=<path_to_kubectl config file>
python launch.py -w 2 -e examples/entrypoint.sh examples/mnist.py
#this will output the RUN_LABEL that you will need later for the cleanup of resources
```

After launching the training, you can follow the creation of the pods and the training progress with:

```
kubectl get pods #you will see your pods called worker{0,1...}
kubectl logs -f worker0 #to follow the training execution
```

Once the training is done, or in case you wish to run a new job, you will need to remove the reosurces that are in the cluster. You can do this with: `python launch.py -d RUN_LABEL`. There are two ways you can get the RUN\_LABEL:

1. from the output that `launch.py` printed when it spawned the training
2. from the description of any of the created resources, e.g. `kubectl describe pod worker0|grep training_attempt | cut -d= -f2`

Note: In order to use the example in `examples/mnist.py` you will need to provide an image with the 
TensorFlow_datasets package or to use the entrypoint specified in
`examples/entrypoint.sh` which installs the package before running the script.

## Old resources deletion
In order to delete the resources, you have to run `python launch.py -d run_name`
where `run_name` is the value shown during creation

