# TF-Spawner
tf-spawner is a tool to run TensorFlow training distributed on a Kubernetes clusters using 
multi worker TensorFlow strategy.
TF-spawner assumes the use of tf.distribute, see this link for details on how to use [Multi-worker Training with Keras](https://www.tensorflow.org/beta/tutorials/distribute/multi_worker_with_keras)

Author and contact: Riccardo.Castellotti@cern.ch

## Installation

Install the required package with: `pip3 install kubernetes`

## Usage

```
usage: tf-spawner [-h] [-d] [-w WORKERS] [-n NAMESPACE] [-p PORT]
                  [-e ENTRYPOINT] [--pod-file POD_FILE] [-t TAG] [-r]
                  [--env-file ENV_FILE] [-i IMAGE]
                  [path]

positional arguments:
  path                  path to the TensorFlow script to run (default: None)

optional arguments:
  -h, --help            show this help message and exit
  -d, --delete          delete resources matching RUN_LABEL (default: False)
  -w WORKERS, --workers WORKERS
                        number of workers (default: 8)
  -n NAMESPACE, --namespace NAMESPACE
                        k8s namespace (default: None)
  -p PORT, --port PORT  grpc port (default: 1999)
  -e ENTRYPOINT, --entrypoint ENTRYPOINT
                        pod entrypoint script path (default: None)
  --pod-file POD_FILE   path to pod yaml file (default: pod.yaml)
  -t TAG, --tag TAG     tag resources (default: tf-spawner)
  -r, --randomize-tag   create random tag for resources (this overrides the -t
                        option) (default: False)
  --env-file ENV_FILE   path to file containing environment variables to be
                        sourced into every worker (default: None)
  -i IMAGE, --image IMAGE
                        container image for the pod to use (default:
                        tensorflow/tensorflow:2.1.0-py3)
```

In order to read data from S3-compatible storage, make sure that you are setting in the environment `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `AWS_LOG_LEVEL`. You can do so modifying the `s3.secrets.example` in the `examples` folder and sourcing it.


## Example

This runs an mnist example
```
export KUBECONFIG=<path_to_kubectl config file>
./tf-spawner -w 2 -e examples/entrypoint.sh examples/mnist.py
#this will output the RUN_LABEL that you will need later for the cleanup of resources
```

After launching the training, you can follow the creation of the pods and the training progress with:

```
kubectl get pods #you will see your pods called worker{0,1...}
kubectl logs -f worker0 #to follow the training execution
```

## Labeling and deletion
Resources are tagged by the script with a label `training_attempt=RUN_LABEL`. This `RUN_LABEL` has a default value, `tf-spawner`. You can decide to override it with the `-t` option or to generate a random one with `-r`. If both options are present, `-r` is applied.

Once the training is done, or in case you wish to run a new job, you will need to remove the reosurces that are in the cluster. You can do this with: `./tf-spawner -d RUN_LABEL`. There are two ways you can get the RUN\_LABEL:

1. from the output that `tf-spawner` printed when it spawned the training
2. from the description of any of the created resources, e.g. `kubectl describe pod worker0|grep training_attempt | cut -d= -f2`

Note: In order to use the example in `examples/mnist.py` you will need to provide an image with the 
TensorFlow_datasets package or to use the entrypoint specified in
`examples/entrypoint.sh` which installs the package before running the script.

## Old resources deletion
In order to delete the resources, you have to run `./tf-spawner -d RUN_LABEL`
where `run_name` is the value shown during creation

