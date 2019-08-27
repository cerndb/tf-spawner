#Installation

Run `pip install kubernetes namesgenerator`

#Usage

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

```


### Old resources deletion
In order to delete the resources, you have to run `python launch.py -d random_name` where `random_name` is the value shown during creation

