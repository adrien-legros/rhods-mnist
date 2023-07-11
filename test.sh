#!/usr/bin/env sh
# Variables
OWNER=data-scientist-1
OWNER_PWD=rhods
REPO=digit-recognition
GITEA_ENDPOINT="https://gitea-gitea.apps.cluster-82pm2.82pm2.sandbox518.opentlc.com"
API_ENDPOINT=${GITEA_ENDPOINT}/api/v1/repos/migrate
EL_ENDPOINT="http://el-ds-pipeline-trigger-listener.mnist.svc.cluster.local:8080"
# Clone git repo
oc exec -it 
# Add the webhook
migrate_payload() {
    cat <<EOF
{
    "clone_addr": "https://github.com/adrien-legros/rhods-mnist-model",
    "repo_name": "digit-recognition",
    "repo_owner": "data-scientist-1"
}
EOF
}
curl -X POST -H "Content-Type: application/json" -u ${OWNER}:${OWNER_PWD} --data "$(migrate_payload)" ${API_ENDPOINT}