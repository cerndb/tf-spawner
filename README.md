# Installation

Run `pip install kubernetes namesgenerator`

# Usage

```
usage: launch.py [-h] [-d DELETE] [-w WORKERS] [-n NAMESPACE] [-p PORT] [path]

positional arguments:
  path                  path of script to run (default: None)

optional arguments:
  -h, --help            show this help message and exit
  -d DELETE, --delete DELETE
                        delete resources (default: None)
  -w WORKERS, --workers WORKERS
                        number of workers (default: 8)
  -n NAMESPACE, --namespace NAMESPACE
                        k8s namespace (default: default)
  -p PORT, --port PORT  grpc port (default: 1999)

  -e ENTRYPOINT, --entrypoint ENTRYPOINT
                          pod entrypoint script path (default: None)

```

## Example

In order to use the example in `examples/mnist.py` you will need to provide an image with the tensorflow_datasets package or to use the entrypoint specified in `examples/entrypoint.sh` which installs the package before running the script.

## Old resources deletion
In order to delete the resources, you have to run `python launch.py -d random_name` where `random_name` is the value shown during creation

