tensorflow/tensorflow:2.0.0b1-py3# TF-Spawner
tf-spawner is a tool to run TensorFlow training distributed on a Kubernetes clusters using 
multi worker TensorFlow strategy.
The changes to TensorFlow code to use distributed strategy are minor in TF 2.0, see 
documentation on [Multi-worker Training with Keras](https://www.tensorflow.org/beta/tutorials/distribute/multi_worker_with_keras)

Author and contact: Riccardo.Castellotti@cern.ch

## Installation

Install the required package with: `pip install kubernetes namesgenerator`

## Usage

```
usage: launch.py [-h] [-d DELETE] [-w WORKERS] [-n NAMESPACE] [-p PORT] [script_full_path]

positional arguments:
  script_full_path     path of script to run (default: None)

optional arguments:
  -h, --help            show this help message and exit
  -d KEY, --delete KEY
                        delete resources with key value KEY (default: None)
  -w NUM_WORKERS, --workers NUM_WORKERS
                        number of workers (default: 8)
  -n NAMESPACE, --namespace NAMESPACE
                        existing k8s namespace (default: default)
  -p PORT, --port PORT  grpc port (default: 1999)

  -e ENTRYPOINT_SCRIPT, --entrypoint ENTRYPOINT_SCRIPT
                          pod entrypoint optional script path (default: None)

  -i IMAGE_NAME, --image-name IMAGE_NAME
                        image name to run in the pods, default is tensorflow/tensorflow:2.0.0b1-py3                          
Note: launch.py will output a randomly-generated run_name (to be used with the delete statement)                       
```

## Example

This runs an mnist example
```
export KUBECONFIG=<path_to_kubectl config file>
python launch.py -w 2 -e examples/entrypoint.sh examples/mnist.py
```

Note: In order to use the example in `examples/mnist.py` you will need to provide an image with the 
TensorFlow_datasets package or to use the entrypoint specified in
`examples/entrypoint.sh` which installs the package before running the script.

## Old resources deletion
In order to delete the resources, you have to run `python launch.py -d run_name`
where `run_name` is the value shown during creation

