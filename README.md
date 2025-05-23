# Generate Kubernetes Resource YAML 

A handy `kubectl plugin` that performs a walkthrough of a resource schema of a ***third-party*** API registered with the Kubernetes API server. The result yields a sample YAML of the resource as described in the example below.  

Example - 

```shell
kubectl genresourceyaml --api run.tanzu.vmware.com/v1alpha3 --kind kappControllerConfig 
```

results in an output similar to this - 

```yaml
apiVersion: v1alpha3
kind: KappControllerConfig
metadata:
  name: <string>
spec:
  kappController:
    config:
      caCerts: <string>
      dangerousSkipTLSVerify: <string>
      httpProxy: <string>
      httpsProxy: <string>
      noProxy: <string>
    createNamespace: <boolean> # Default: False
    deployment:
      apiPort: <integer> # Default: 10100
      concurrency: <integer> # Default: 4
      hostNetwork: <boolean> # Default: True
      metricsBindAddress: <string> # Default: 0
      priorityClassName: <string> # Default: system-cluster-critical
      tolerations:
      -
        additionalProperties: <string>
    globalNamespace: <string> # Default: tkg-system
  namespace: <string> # Default: tkg-system
```

### How it Works

This plugin interacts with your Kubernetes cluster to provide information about Custom Resource Definitions (CRDs). It works by:
1. Querying the Kubernetes API server for the OpenAPI v3 schema of the specified CRD. This schema defines the structure, data types, and validation rules for the custom resource.
2. Traversing this retrieved schema. The script navigates through the different fields and their definitions.
3. Generating a sample YAML output based on the schema structure. This output provides a template that you can adapt for creating actual resource instances.

Default values specified in the CRD schema are indicated in the output YAML with a comment, for example: `# Default: <value>`.

### Limitations - 

- **Core Kubernetes APIs**: This plugin is designed for third-party APIs (Custom Resources) and currently does not work with core Kubernetes APIs like Pods, Deployments, Services, etc. (typically those under `*.k8s.io` API groups).
    - **Reasoning**: Core API schemas are often accessed via different API endpoints (e.g., `/openapi/v2` for some core components) or have a more complex structure than the `/openapi/v3/apis/{group}/{version}` path pattern primarily used for CRDs and aggregated APIs. Additionally, the schemas for core resources are extensive and are already well-documented in the official Kubernetes documentation, which is the recommended source for their specifications.
- **Schema Variations**: While the plugin attempts to handle various CRD schema structures, some highly complex or non-standard schemas might not be rendered perfectly.

### Output Data Types

The generated YAML uses placeholders to indicate the expected data type for each field. Here's how to interpret them:

- `<string>`: Expects a string value.
- `<integer>`: Expects an integer value.
- `<boolean>`: Expects a boolean value (`true` or `false`).
- `<number>`: Expects a numerical value (can be integer or float).
- `key:` (followed by indented fields): Represents an `object` with nested key-value pairs.
- `- <type>` or `- `: Represents an `array`.
    - If the array items are simple types, it might look like `- <string>`.
    - If the array items are objects, it will show `- ` followed by indented fields for that object.
- `<no_type_specified>`: Indicates that the schema did not explicitly define a type for this field. You may need to consult the CRD's documentation.
- `<unknown_type_in_schema>`: Indicates an unexpected or unrecognized type definition within the schema for this field.

## Installation

This plugin has been tested on Linux and MacOS-based systems and may need additional validation on the Windows environment. 

Requirements - Python3 installed. 

* Install pip dependencies 
```bash
pip install kubernetes
pip install requests
# or
sudo apt install python3-kubernetes
```

* Copy the Python file to a folder in your $PATH. For e.g.
```bash
sudo cp kubectl-genresourceyaml.py /usr/local/bin/kubectl-genresourceyaml
sudo chmod +x /usr/local/bin/kubectl-genresourceyaml
```

## Usage

You can run the following command to get a given resource's valid API version and other details.

```bash
kubectl api-resources|grep {{NAME_OF_RESOURCE}}
```
It should display the following columns -

```
NAME    SHORTNAMES    APIVERSION    NAMESPACED    KIND
```

 The `--api` command line argument uses the *APIVERSION* value, while the `--kind` command line argument uses the ***KIND*** value. Note that ***KIND*** value may differ from the *NAME* value. 

Execute the command using the following syntax - 

```bash
kubectl genresourceyaml --api {{APIVERSION}} --kind {{KIND}}
```
