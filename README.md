# Generate Kubernetes Resource YAML 

A handy kubectl plugin that performs a walkthrough of a resource schema of a third-party API registered with the Kubernetes API server. The result yields a sample YAML of the resource. Since the core APIs generally follow a different specification, his plugin currently does not work with the core APIs and will not generate outputs for resources like Pods and Deployments. This plugin will not work for any APIs ending with `.k8s.io`.  

Example - 

```bash
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

### Limitations - 

WIP - This command currently does not work with the core APIs and will not generate outputs for resources like Pods and Deployments, etc

## Installation 

* Install pip dependencies 
```bash
pip install kubernetes
pip install requests
```

* Copy the Python file to a folder in your $PATH. For e.g.
```bash
sudo cp kubectl-genresourceyaml.py /usr/local/bin/kubectl-genresourceyaml
sudo chmod +x /usr/local/bin/kubectl-genresourceyaml
```

## Usage

You can run the following command to use the valid API version for a given resource.

```bash
kubectl api-resource|grep {{NAME_OF_RESOURCE}}
```
It should display the following columns -

```
NAME    SHORTNAMES    APIVERSION    NAMESPACED    KIND
```

 The `--api` command line argument uses the APIVERSION value, while the `--kind` command line argument uses the KIND value.

Execute the command using the following syntax - 
```
```bash
kubectl genresourceyaml --api {{APIVERSION}} --kind {{KIND}}
```
