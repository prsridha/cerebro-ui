import os
import json
import time
import zipfile
import utilities
from pathlib import Path
from urllib.parse import urlparse
from flask import Flask, request
from kubernetes import client, config
from flask_cors import CORS

S3_POLICY_ARN = "arn:aws:iam::782408612084:policy/AmazonEKS_S3_Policy"

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

def copyFilesToPods(cli):
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
    if not cli:
        utilities.run(cmd1.format(controller_pod, "cerebro-controller-container", codeToPath))
    for pod in etl_pods:
        utilities.run(cmd1.format(pod, "cerebro-worker-etl-container", codeToPath))
    
    # copy to pods
    if not cli:
        utilities.run(cmd2.format("cerebro-controller-container", paramsFromPath, controller_pod, paramsToPath))
        utilities.run(cmd2.format("cerebro-controller-container", codeFromPath, controller_pod, codeToPath))
    for pod in etl_pods:
        utilities.run(cmd2.format("cerebro-worker-etl-container", codeFromPath, pod, codeToPath))

    # move and delete extra dir
    if not cli:
        utilities.run(cmd3.format(controller_pod, "cerebro-controller-container", codeToPath, codeToPath))
        utilities.run(cmd4.format(controller_pod, "cerebro-controller-container", codeToPath))
    for pod in etl_pods:
        utilities.run(cmd3.format(pod, "cerebro-worker-etl-container", codeToPath, codeToPath))
        utilities.run(cmd4.format(pod, "cerebro-worker-etl-container", codeToPath))

def add_s3_creds(s3_url):
    bucket_name = urlparse(s3_url, allow_fragments=False).netloc
    print("Got S3 bucket name:", bucket_name)

    with open("misc/iam-policy-eks-s3.json", "r+") as f:
        policy = f.read()
        policy = policy.replace("<s3Bucket>", bucket_name)

        f.seek(0)
        f.write(policy)
        f.truncate()

    # delete existing policy versions for older S3s
    list_policy = "aws iam list-policy-versions --policy-arn {}".format(S3_POLICY_ARN)
    delete_policy = """ aws iam delete-policy-version \
            --policy-arn {} \
            --version-id {}
    """
    policies = json.loads(utilities.run(list_policy))
    for i in policies["Versions"]:
        ver = i["VersionId"]
        if not i["IsDefaultVersion"]:
            utilities.run(delete_policy.format(S3_POLICY_ARN, ver))
            print("Deleted old policy version", ver)

    # create new policy version for new S3
    cmd = """ aws iam create-policy-version \
            --policy-arn {} \
            --policy-document file://misc/iam-policy-eks-s3.json  \
            --set-as-default
        """.format(S3_POLICY_ARN)
    utilities.run(cmd)
    print("Created IAM read-only policy for S3")

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

    s3_url = params["train"]["metadata_url"]
    add_s3_creds(s3_url)
        
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

    if "cli" in request.json:
        cli = request.json["cli"]
    else:
        cli = False
    
    # extract zip file contents
    filepath = os.path.join(utilities.ROOT_PATH, "code.zip")
    extractPath = os.path.join(utilities.ROOT_PATH, "code")
    Path(extractPath).mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(filepath, "r") as f:
        f.extractall(extractPath)
    
    cmd = "rm {}".format(os.path.join(utilities.ROOT_PATH, "code.zip"))
    utilities.run(cmd)
    
    copyFilesToPods(cli)

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