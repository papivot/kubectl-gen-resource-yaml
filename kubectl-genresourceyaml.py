#!/usr/bin/env python3

import os
import urllib3
import requests
import argparse
from kubernetes import client, config
from kubernetes.client import configuration

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description='A handy kubectl plugin that performs a walkthrough of a resource schema of a third-party API registered with the Kubernetes API server. This plugin currently does not work with the core APIs and will not generate outputs for resources like Pods and Deployments, etc. The result yields a sample YAML of the resource.')
parser.add_argument('--api', type=str, help='The APIVERSION in the following format: API/version. For reference, it is the APIVERSION field in the kubectl ap-resource command output.')
parser.add_argument('--kind',  type=str, help='The KIND value of the object/resource whose schema needs to be generated in the YAML format. For reference, it is the KIND field in the kubectl api-resource command output')
args = parser.parse_args()

if not (args.kind):
    print("error: the following arguments are required: kind")
    exit()
if not (args.api):
    print("error: the following arguments are required: api")
    exit()

apikind = args.kind
apidetail = args.api.split('/')[0] 
apiversion = args.api.split('/')[1] 
  
final_output = dict()

def get_kubeapi_request(httpsession,path,header):
    response = httpsession.get(path, headers=header, verify=False)
    if response.ok:
        response.encoding = 'utf-8'
        return response.json()
    else:
        return 0
    
def traverse_spec_objects(x, n):
    for key in x:
        if key not in ["description", "type"]:  
            if not x[key].get("type"):
                print(" " * n,key+": <>")
            elif   x[key]["type"] == "boolean":
                if "default" in x[key]:
                    print(" " * n,key+": <boolean> # Default: "+str(x[key]["default"]))
                else:
                    print(" " * n,key+": <boolean>")
            elif x[key]["type"] == "string":
                if "default" in x[key]:
                    print(" " * n, key+": <string> # Default: "+x[key]["default"])
                else:
                    print(" " * n, key+": <string>")  
            elif x[key]["type"] == "integer":
                if "default" in x[key]:
                    print(" " * n, key+": <integer> # Default: "+str(x[key]["default"]))
                else:
                    print(" " * n, key+": <integer>")  
            elif x[key]["type"] == "array":
                # An array of objects
                if x[key]["items"]["type"] == "object":
                    print(" " * n, key+":")
                    print(" " * n, "- ")
                    n +=2
                    if "properties" in x[key]["items"]:
                        traverse_spec_objects(x[key]["items"]["properties"], n)
                    else:
                    # Properties not found in object. Non standard api. Interate thru each key 
                        traverse_spec_objects(x[key]["items"], n)
                    n -=2
                else:
                    print(" " * n, key+": ")
                    if "default" in x[key]:
                        print(" " * n, "- "+ x[key]["items"]["type"] + "# Default: "+str(x[key]["default"]))
                    else:
                        print(" " * n, "- "+ x[key]["items"]["type"])
            else:
                # Type is object
                print(" " * n, key+":")
                n +=2
                if "properties" in x[key]:
                    traverse_spec_objects(x[key]["properties"], n)
                else:
                # Properties not found in object. Non standard api. Interate thru each key 
                    traverse_spec_objects(x[key], n)
                n -=2

def main():
    k8s_host = ""
    k8s_token = ""
    k8s_headers = ""
    defjson = dict()

    if not os.environ.get('INCLUSTER_CONFIG'):
        config.load_kube_config()
    else:  
        config.load_incluster_config()    

    k8s_host = configuration.Configuration()._default.host
    k8s_token = configuration.Configuration()._default.api_key['authorization']
    k8s_headers = {"Accept": "application/json, */*", "Authorization": k8s_token}
    k8s_session = requests.session()
   
    parts = apidetail.split(".")
    reversed_parts = ".".join(parts[::-1])

    apis = get_kubeapi_request(k8s_session,k8s_host+"/openapi/v3/apis/"+apidetail+"/"+apiversion, k8s_headers) 
    if (apis):
        defjson = apis["components"]["schemas"].get(reversed_parts+"."+apiversion+"."+apikind)
        if "spec" in defjson["properties"]:
            final_output["spec"] = defjson["properties"]["spec"]["properties"]
            print("apiVersion: "+apiversion)
            print("kind: "+apikind)
            print("metadata: ")
            print("  name: <string>")
            print("spec: ")
            traverse_spec_objects(final_output["spec"], 1)
        else:
            print("Missing spec in API. Exiting...")

if __name__ == "__main__":
    main()
