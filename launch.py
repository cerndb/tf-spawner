#   Copyright 2019 Riccardo Castellotti
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import argparse
import json
import os
import yaml
from kubernetes import client, config
import namesgenerator

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("path", help="path of script to run", nargs="?")
parser.add_argument("-d", "--delete", help="delete resources")
parser.add_argument("-w", "--workers", help="number of workers", default="8", type=int)
parser.add_argument("-n", "--namespace", help="k8s namespace", default="default")
parser.add_argument("-p", "--port", help="grpc port", default="1999", type=int)
parser.add_argument("-e", "--entrypoint", help="pod entrypoint script path")
parser.add_argument(
    "-i",
    "--image",
    help="container image for the pod to use",
    default="tensorflow/tensorflow:2.0.0b1-py3",
)
args = parser.parse_args()

NAMESPACE = args.namespace
NUM_NODES = args.workers
GRPC_PORT = args.port

config.load_kube_config()

v1 = client.CoreV1Api()

names = [f"worker{i}:{GRPC_PORT}" for i in range(NUM_NODES)]


def gen_tfconfig(names, index):
    ###TF_CONFIG={"cluster": {"worker":
    ###     ["worker0:1999", "worker1:1999", "worker2:1999"]},
    ###   "task": {"type": "worker", "index": 0}}

    tfconfig = {}
    tfconfig["cluster"] = {}
    tfconfig["cluster"]["worker"] = names
    tfconfig["task"] = {"type": "worker", "index": index}
    return json.dumps(tfconfig)


def gen_cfmap(script_path, selector_name):
    with open(script_path) as script_file:
        v1.create_namespaced_config_map(
            NAMESPACE,
            client.V1ConfigMap(
                data={"training-script.py": script_file.read()},
                metadata=client.V1ObjectMeta(
                    name="script", labels={"training_attempt": selector_name}
                ),
            ),
        )


with open("service.yaml") as service_f:
    service_template = yaml.safe_load(service_f)

with open("pod.yaml") as pod_f:
    pod_template = yaml.safe_load(pod_f)


def gen_script(entrypoint_path):
    with open(entrypoint_path) as script_f:
        lines = script_f.read().splitlines()
        sh_script = ["/bin/bash", "-c", "&& ".join(lines)]
        return sh_script


def gen_services(n_services, selector_name):
    for i in range(n_services):
        service_body = service_template
        service_body["spec"]["selector"]["app"] = f"worker{i}"
        service_body["spec"]["ports"][0]["port"] = GRPC_PORT
        service_body["spec"]["ports"][0]["targetPort"] = GRPC_PORT
        service_body["metadata"]["name"] = f"worker{i}"
        service_body["metadata"]["labels"]["training_attempt"] = selector_name
        v1.create_namespaced_service(NAMESPACE, service_body)


def gen_pods(n_pods, selector_name):
    if args.entrypoint:
        entrypoint = gen_script(args.entrypoint)
    for i in range(n_pods):
        pod_body = pod_template
        pod_body["metadata"]["name"] = f"worker{i}"
        pod_body["metadata"]["labels"]["app"] = f"worker{i}"
        pod_body["metadata"]["labels"]["training_attempt"] = selector_name
        env = {
            "TF_CONFIG": gen_tfconfig(names, i),
            "WORKER_NUMBER": str(i),
            "TOT_WORKERS": str(NUM_NODES),
        }
        pod_body["spec"]["containers"][0]["env"] = []
        for k, v in env.items():
            pod_body["spec"]["containers"][0]["env"].append({"name": k, "value": v})
        if args.entrypoint:
            pod_body["spec"]["containers"][0]["command"] = entrypoint
        pod_body["spec"]["containers"][0]["image"] = args.image
        v1.create_namespaced_pod(NAMESPACE, pod_body)


if args.delete:
    services = v1.list_namespaced_service(
        NAMESPACE, label_selector=f"training_attempt={args.delete}"
    )
    for srv in services.items:
        v1.delete_namespaced_service(srv.metadata.name, NAMESPACE)
    cms = v1.list_namespaced_config_map(
        NAMESPACE, label_selector=f"training_attempt={args.delete}"
    )
    for cm in cms.items:
        v1.delete_namespaced_config_map(cm.metadata.name, NAMESPACE)
    pods = v1.list_namespaced_pod(
        NAMESPACE, label_selector=f"training_attempt={args.delete}"
    )
    for pod in pods.items:
        v1.delete_namespaced_pod(pod.metadata.name, NAMESPACE)
else:
    if not args.path:
        raise Exception("no script specified")
    selector_name = namesgenerator.get_random_name()
    print(f"generating with label training_attempt={selector_name}")
    gen_cfmap(args.path, selector_name)
    gen_pods(NUM_NODES, selector_name)
    gen_services(NUM_NODES, selector_name)
