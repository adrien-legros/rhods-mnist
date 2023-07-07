#!/usr/bin/env sh

wait_for_exists () {
    # Arg1: selector
    # Arg2: namespace
    while true; do
        pod_exists=$(oc -n $2 get po -oname -l $1 | wc -l)
        if [ $pod_exists -gt 0 ]; then
            echo "Selector $1 found in namespace $2"
            break
        fi
        echo "Wait for selector $1 in namspace $2"
        sleep 5
    done;
}
wait_for_exists "name=rhods-operator" "redhat-ods-operator"
oc -n redhat-ods-operator wait --for=condition=Ready=true po -l name=rhods-operator --timeout=10m
wait_for_exists "app=model-mesh" "redhat-ods-applications"
oc -n redhat-ods-applications wait --for=condition=Ready=true po -l app=model-mesh --timeout=10m
wait_for_exists "control-plane=controller-manager" "redhat-ods-applications"
oc -n redhat-ods-applications wait --for=condition=Ready=true po -l control-plane=controller-manager --timeout=10m
wait_for_exists "control-plane=odh-model-controller" "redhat-ods-applications"
oc -n redhat-ods-applications wait --for=condition=Ready=true po -l control-plane=odh-model-controller --timeout=10m
wait_for_exists "app=notebook-controller" "redhat-ods-applications"
oc -n redhat-ods-applications wait --for=condition=Ready=true po -l app=notebook-controller --timeout=10m
wait_for_exists "app=rhods-dashboard" "redhat-ods-applications"
oc -n redhat-ods-applications wait --for=condition=Ready=true po -l app=rhods-dashboard --timeout=10m