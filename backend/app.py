import os
import json
import time
import zipfile
import utilities
from pathlib import Path
from flask import Flask, request
from kubernetes import client, config
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

def saveFile(request, filename, relativePath):
    # check if the post request has the file part
    file = request.files['file']
    path = os.path.join(utilities.ROOT_PATH, relativePath, filename)
    file.save(path)
    resp = {
        "message": "File saved",
        "status": 200
    }
    return resp

def copyFilesToPods():
    valuesYaml = utilities.readValuesYAML()
    codeFromPath = os.path.join(utilities.ROOT_PATH, "code")
    codeToPath = valuesYaml["controller"]["volumes"]["userRepoMountPath"]
    paramsFromPath = os.path.join(utilities.ROOT_PATH, "params.json")
    paramsToPath = valuesYaml["controller"]["volumes"]["dataMountPath"]

    p = utilities.getPodNames()
    controller_pod, etl_pods, mop_pods = p["controller"], p["etl_workers"], p["mop_workers"]
    cmd1 = "kubectl exec -t {} -c {} -- bash -c 'rm -rf {}/*' "
    cmd2 = "kubectl cp -c {} {} {}:{}"
    cmd3 = "kubectl exec -t {} -c {} -- bash -c 'mv {}/code/* {}' "
    cmd4 = "kubectl exec -t {} -c {} -- bash -c 'rm -rf {}/code' "

    # remove existing files in codeToPath
    # controller
    utilities.run(cmd1.format(controller_pod, "cerebro-controller-container", codeToPath))
    for pod in etl_pods:
        utilities.run(cmd1.format(pod, "cerebro-worker-etl-container", codeToPath))
    
    # copy to pods
    utilities.run(cmd2.format("cerebro-controller-container", paramsFromPath, controller_pod, paramsToPath))
    utilities.run(cmd2.format("cerebro-controller-container", codeFromPath, controller_pod, codeToPath))
    for pod in etl_pods:
        utilities.run(cmd2.format("cerebro-worker-etl-container", codeFromPath, pod, codeToPath))

    # move and delete extra dir
    utilities.run(cmd3.format(controller_pod, "cerebro-controller-container", codeToPath, codeToPath))
    utilities.run(cmd4.format(controller_pod, "cerebro-controller-container", codeToPath))
    for pod in etl_pods:
        utilities.run(cmd3.format(pod, "cerebro-worker-etl-container", codeToPath, codeToPath))
        utilities.run(cmd4.format(pod, "cerebro-worker-etl-container", codeToPath))

@app.route("/initialize", methods=["POST"])
def initialize():
    filename = "values.yaml"
    resp = saveFile(request, filename, ".")
    return resp

@app.route("/params", methods=["POST"])
def saveParams():
    valuesYaml = utilities.readValuesYAML()
    params = request.json
    path = os.path.join(utilities.ROOT_PATH, "params.json")
    
    with open(path, "w") as f:
        json.dump(params, f, indent=2)
        
    resp = {
        "message": "Saved params json file",
        "status": 200
    }
    return resp

@app.route("/save-code", methods=["POST"])
def saveCode():
    # save zip file
    filename = "code.zip"
    resp = saveFile(request, filename, ".")
    if resp["status"] != 200:
        return resp
    
    # extract zip file contents
    filepath = os.path.join(utilities.ROOT_PATH, "code.zip")
    extractPath = os.path.join(utilities.ROOT_PATH, "code")
    Path(extractPath).mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(filepath, "r") as f:
        f.extractall(extractPath)
    
    cmd = "rm {}".format(os.path.join(utilities.ROOT_PATH, "code.zip"))
    utilities.run(cmd)
    
    valuesYaml = utilities.readValuesYAML()
    codeFromPath = os.path.join(utilities.ROOT_PATH, "code")
    codeToPath = valuesYaml["controller"]["volumes"]["userRepoMountPath"]
    paramsFromPath = os.path.join(utilities.ROOT_PATH, "params.json")
    paramsToPath = valuesYaml["controller"]["volumes"]["dataMountPath"]

    p = utilities.getPodNames()
    controller_pod, etl_pods, mop_pods = p["controller"], p["etl_workers"], p["mop_workers"]
    cmd1 = "kubectl exec -t {} -c {} -- bash -c 'rm -rf {}/*' "
    cmd2 = "kubectl cp -c {} {} {}:{}"
    cmd3 = "kubectl exec -t {} -c {} -- bash -c 'mv {}/code/* {}' "
    cmd4 = "kubectl exec -t {} -c {} -- bash -c 'rm -rf {}/code' "

    # remove existing files in codeToPath
    # controller
    utilities.run(cmd1.format(controller_pod, "cerebro-controller-container", codeToPath))
    for pod in etl_pods:
        utilities.run(cmd1.format(pod, "cerebro-worker-etl-container", codeToPath))
    
    # copy to pods
    utilities.run(cmd2.format("cerebro-controller-container", paramsFromPath, controller_pod, paramsToPath))
    utilities.run(cmd2.format("cerebro-controller-container", codeFromPath, controller_pod, codeToPath))
    for pod in etl_pods:
        utilities.run(cmd2.format("cerebro-worker-etl-container", codeFromPath, pod, codeToPath))

    # move and delete extra dir
    utilities.run(cmd3.format(controller_pod, "cerebro-controller-container", codeToPath, codeToPath))
    utilities.run(cmd4.format(controller_pod, "cerebro-controller-container", codeToPath))
    for pod in etl_pods:
        utilities.run(cmd3.format(pod, "cerebro-worker-etl-container", codeToPath, codeToPath))
        utilities.run(cmd4.format(pod, "cerebro-worker-etl-container", codeToPath))

    copyFilesToPods()

    resp = {
        "message": "Extracted and saved code zip file",
        "status": 200
    }

    return resp

@app.route("/get-urls", methods=["GET"])
def getURLs():
    valuesYaml = utilities.readValuesYAML()
    publicDNS = valuesYaml["cluster"]["networking"]["publicDNSName"]
    
    # get jupyter string
    j = valuesYaml["creds"]["jupyterTokenSting"]
    j_bin = j.encode("utf-8")
    jToken = j_bin.hex().upper()
    
    jupyterP = valuesYaml["controller"]["services"]["jupyterNodePort"]
    tensorboardP = valuesYaml["controller"]["services"]["tensorboardNodePort"]
    prometheusP = valuesYaml["cluster"]["networking"]["prometheusNodePort"]
    lokiP = valuesYaml["cluster"]["networking"]["lokiPort"]
    grafanaP = valuesYaml["cluster"]["networking"]["grafanaNodePort"]

    jupyterURL = "http://" + publicDNS + ":" + str(jupyterP) + "/?token=" + jToken
    tensorboardURL = "http://" + publicDNS + ":" + str(tensorboardP)
    prometheusURL = "http://" + publicDNS + ":" + str(prometheusP)
    grafanaURL = "http://" + publicDNS + ":" + str(grafanaP)
    lokiURL = "http://loki" + ":" + str(lokiP)
    
    message = {
        "jupyterURL": jupyterURL,
        "tensorboardURL": tensorboardURL,
        # "prometheusURL": prometheusURL,
        "grafanaURL": grafanaURL,
        # "lokiURL": lokiURL
    }
    
    return {
        "message": message,
        "status": 200
    }

@app.route("/health", methods=["GET"])
def hello_world():
    resp = {
        "message": "Hello World! This is the Cerebro backend webserver",
        "status": 200
    }
    return resp

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=False)