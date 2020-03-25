# TF-Spawner

TF-Spawner is an experimental tool for running TensorFlow distributed training on Kubernetes clusters using 
tf.distributed multi worker strategy (more info at [multi-worker training with Keras](https://www.tensorflow.org/tutorials/distribute/multi_worker_with_keras)).  
TF-Spawner has been developed and used originally for the work on
[Distributed Deep Learning for Physics with TensorFlow and Kubernetes]( https://db-blog.web.cern.ch/blog/luca-canali/2020-03-distributed-deep-learning-physics-tensorflow-and-kubernetes)

Main author and maintainer: Riccardo.Castellotti@cern.ch  
Contacts: Riccardo.Castellotti@cern.ch, Luca.Canali@cern.ch

## Installation

Download the package: `git clone https://github.com/cerndb/tf-spawner`  
Install the dependencies: `pip3 install kubernetes`  
Requirement: TF-Spawner needs access to a Kubernetes cluster, check this with `kubectl get nodes`

## Getting Started

This shows a toy example, it attempts to run the MNIST training script with 2 workers:
```
./tf-spawner examples/mnist.py
```

When GPU resources are available in the Kubernetes cluster:
```
./tf-spawner -w 2 -i tensorflow/tensorflow:2.1.0-gpu-py3 --pod-file pod-gpu.yaml examples/mnist.py
```

**Monitor execution:** After launching the training, you can follow the creation of the pods and the training progress with:
```
kubectl get pods #you will see your pods called worker{0,1...}
kubectl logs -f worker0 #to follow the training execution
```
**Clean up:** Free the used resources with `./tf-spawner -d`

**Note:** 
See [training a Particle Classifier](https://github.com/cerndb/SparkDLTrigger/tree/master/Training_TFKeras_CPU_GPU_K8S_Distributed)
for a full-scale example of how to use TF-Spawner.
  
---
## TF-Spawner usage

```
usage: tf-spawner [-h] [-d] [-w WORKERS] [-n NAMESPACE] [-p PORT] [-c COMMAND]
                  [--pod-file POD_FILE] [-t TAG] [-r] [-e ENV_FILE] [-i IMAGE]
                  [training_script_path]

positional arguments:
  training_script_path  path to the TensorFlow script to run (default: None)

optional arguments:
  -h, --help            show this help message and exit
  -d, --delete          delete resources matching RUN_LABEL (default: False)
  -w WORKERS, --workers WORKERS
                        number of workers (default: 2)
  -n NAMESPACE, --namespace NAMESPACE
                        k8s namespace (if different than the one specified in your
                        kubeconfig) (default: None)
  -p PORT, --port PORT  grpc port (default: 1999)
  -c COMMAND, --command COMMAND
                        path to script to use as pod command/ entrypoint (default: None)
  --pod-file POD_FILE   path to pod yaml file (default: pod.yaml)
  -t TAG, --tag TAG     tag resources (default: tf-spawner)
  -r, --randomize-tag   create random tag for resources (this overrides the -t option)
                        (default: False)
  -e ENV_FILE, --env-file ENV_FILE
                        path to file containing environment variables to be sourced into
                        every worker (default: None)
  -i IMAGE, --image IMAGE
                        container image for the pod to use (default:
                        tensorflow/tensorflow:2.1.0-py3)

```

## Access to cloud storage resources
To read data from S3-compatible storage, make sure that you are setting in the environment
`S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `AWS_LOG_LEVEL`.
You can do so editing `envfile.example` in the `examples` folder, and passing it via the `-e` option 
as `-e examples/envfile.example`.

## TF.distribute variables
TF-Spawner sets the "TF_CONFIG" envirnonment variable in each container as needed by tf.distribute to create its internal cluster.
Similarly it also sets the environment variables "WORKER_NUMBER" and "TOT_WORKERS"

## Labeling and deletion
Resources are tagged by TF-Spawner with a label `training_attempt=RUN_LABEL`.
This `RUN_LABEL` has a default value, `tf-spawner`.
You can decide to override it with the `-t` option or to generate a random one with `-r`.
If both options are present, `-r` is applied.

Once the training is done, or in case you wish to run a new job, you will need to remove the reosurces that are in the cluster. You can do this with: `./tf-spawner -d RUN_LABEL`. There are two ways you can get the RUN\_LABEL:

1. from the output that `tf-spawner` printed when it spawned the training
2. from the description of any of the created resources, e.g. `kubectl describe pod worker0|grep training_attempt | cut -d= -f2`

## Resources cleanup
To free up the used resources (pods, services and configmaps), you have to run `./tf-spawner -d -t run_name` where `run_name` is the value shown during creation. By default, the tag `tf-spawner` is used.

## Customization 

A few important customizations are possible:
* specifying a file where environment variables are specified as an argument to `-e/--env-file`. The format is one couple 'key=value' per line
* modifying the command executed by the TensorFlow containers with the `-c/--command` argument.
This can be used, for example, to add an entrypoint script for environment configuration, such as running pip install.
Note that, as the script that you pass to tf-spawner is mounted in `/script/training-script.py`, you need to have a line to run it in your entrypoint file
* modifying the template for the pods and the services: `pod.yaml` and `pod-gpu.yaml` are provided as example. Review and edit,
in particular the container resource limit requested.

## Limitations and Caveats
TF-Spawner is currently an experimental tool.
- There is no validation of the user-provided training script, it is simply passed to Python.
- Users will need to make sure that all the requested pods are effectively running, and will have to manually take care of possible failures.
- At the end of the training, the pods will be found in "Completed" state, users will need then to manually get the information they need, such as training time, from the pods' log file.
- Similarly, other common operations, such fetching the saved file with trained model or monitoring with TensorBoard will need to be performed manually.
- These are all relatively easy tasks, but require additional effort and some familiarity with the Kubernetes environment. 
