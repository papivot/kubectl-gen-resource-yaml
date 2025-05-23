#!/usr/bin/env python3

import os
import argparse
import urllib3
import requests
from kubernetes import config
from kubernetes.client import configuration

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description='A handy kubectl plugin that performs a walkthrough of a resource schema of a third-party API registered with the Kubernetes API server. This plugin currently does not work with the core APIs and will not generate outputs for resources like Pods and Deployments, etc. The result yields a sample YAML of the resource.')
parser.add_argument('--api', type=str, help='The APIVERSION in the following format: API/version. For reference, it is the APIVERSION field in the kubectl ap-resource command output.')
parser.add_argument('--kind',  type=str, help='The KIND value of the object/resource whose schema needs to be generated in the YAML format. For reference, it is the KIND field in the kubectl api-resource command output')
args = parser.parse_args()

if not args.kind:
    print("error: the following arguments are required: kind")
    exit()
if not args.api:
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
    # Iterate through each key in the current schema object
    for key in x:
        # Skip keys that are not relevant to the schema structure
        if key not in ["description", "type", "x-kubernetes-preserve-unknown-fields"]:
            # Handle cases where the type is not defined in the schema
            if not x[key].get("type"):
                print(" " * n,key+": <no_type_specified>")
            # Handle boolean type
            elif x[key]["type"] == "boolean":
                if "default" in x[key]:
                    print(" " * n,key+": <boolean> # Default: "+str(x[key]["default"]))
                else:
                    print(" " * n,key+": <boolean>")
            # Handle string type
            elif x[key]["type"] == "string":
                if "default" in x[key]:
                    print(" " * n, key+": <string> # Default: "+x[key]["default"])
                else:
                    print(" " * n, key+": <string>")
            # Handle integer type
            elif x[key]["type"] == "integer":
                if "default" in x[key]:
                    print(" " * n, key+": <integer> # Default: "+str(x[key]["default"]))
                else:
                    print(" " * n, key+": <integer>")
            # Handle number type
            elif x[key]["type"] == "number":
                if "default" in x[key]:
                    print(" " * n, key+": <number> # Default: "+str(x[key]["default"]))
                else:
                    print(" " * n, key+": <number>")
            # Handle array type
            elif x[key]["type"] == "array":
                # Check if the array contains objects
                if x[key]["items"].get("type") == "object":
                    print(" " * n, key+":")
                    print(" " * n, "- ")
                    # Increase indentation for nested elements
                    n +=2
                    # Recursively call traverse_spec_objects for the items in the array
                    if "properties" in x[key]["items"]:
                        traverse_spec_objects(x[key]["items"]["properties"], n)
                    else:
                        # Properties not found in object. Non standard api. Iterate thru each key 
                        traverse_spec_objects(x[key]["items"], n)
                    # Decrease indentation after processing nested elements
                    n -=2
                # Handle arrays of other types (e.g. string, integer)
                else:
                    print(" " * n, key+": ")
                    if "default" in x[key]:
                        # Ensure default is a list for arrays if specified
                        default_value = x[key]["default"]
                        if isinstance(default_value, list):
                            print(" " * n, "- "+ x[key]["items"].get("type", "<unknown_type_in_schema>") + " # Default: "+str(default_value))
                        else:
                             print(" " * n, "- "+ x[key]["items"].get("type", "<unknown_type_in_schema>") + " # Default: ["+str(default_value)+"]")
                    else:
                        print(" " * n, "- "+ x[key]["items"].get("type", "<unknown_type_in_schema>"))
            # Explicitly handle object type
            elif x[key]["type"] == "object":
                print(" " * n, key+":")
                # Increase indentation for nested elements
                n +=2
                # Recursively call traverse_spec_objects for the properties of the object
                if "properties" in x[key]:
                    traverse_spec_objects(x[key]["properties"], n)
                else:
                    # Properties not found in object. Non standard api. Iterate thru each key
                    traverse_spec_objects(x[key], n)
                 # Decrease indentation after processing nested elements
                n -=2
            # Handle any other types not explicitly covered (though ideally all should be)
            else:
                print(" " * n, key+": <unknown_type_in_schema>")

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
    if apis:
        defjson = apis["components"]["schemas"].get(reversed_parts+"."+apiversion+"."+apikind)
        if not defjson:
            print("error: Object " +apikind+" not found in "+apidetail+"/"+apiversion+". Exiting...")
        else:
            if "spec" in defjson["properties"]:
                print("apiVersion: "+apiversion)
                print("kind: "+apikind)
                print("metadata: ")
                print("  name: <string>")
                print("spec: ")
                if "properties" in defjson["properties"]["spec"]: 
                    final_output["spec"] = defjson["properties"]["spec"]["properties"]
                    traverse_spec_objects(final_output["spec"], 1)
            else:
                print("error: The requested object does not have a spec section in the registered API. Exiting...")

if __name__ == "__main__":
    main()
