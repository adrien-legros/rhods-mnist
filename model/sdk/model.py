
import argparse
import kfp
import kfp.components as comp
import kfp_tekton
import kubernetes
import os

import pre_process
import train
import evaluate

pre_process_op = kfp.components.create_component_from_func(
    pre_process,
    base_image="quay.io/alegros/runtime-image:cuda-ubi8-py38",
    #packages_to_install=["pandas", "scikit-learn"],
)

train_op = kfp.components.create_component_from_func(
    train,
    base_image="quay.io/alegros/runtime-image:cuda-ubi8-py38",
    #packages_to_install=["pandas", "scikit-learn"],
)

evalue_op = kfp.components.create_component_from_func(
    evaluate,
    base_image="quay.io/alegros/runtime-image:cuda-ubi8-py38",
    #packages_to_install=["pandas", "scikit-learn"],
)

@kfp.dsl.pipeline(
    name="Mnist Pipeline",
)
def mnist_pipeline(model_obc: str = "mnist-model"):
    accesskey = kubernetes.client.V1EnvVaTr(
        name="AWS_ACCESS_KEY_ID",
        value_from=kubernetes.client.V1EnvVarSource(
            secret_key_ref=kubernetes.client.V1SecretKeySelector(
                name="mlpipeline-minio-artifact", key="accesskey"
            )
        ),
    )
    host = kubernetes.client.V1EnvVar(
        name="AWS_S3_HOST",
        value_from=kubernetes.client.V1EnvVarSource(
            secret_key_ref=kubernetes.client.V1SecretKeySelector(
                name="mlpipeline-minio-artifact", key="host"
            )
        ),
    )
    port = kubernetes.client.V1EnvVar(
        name="AWS_S3_PORT",
        value_from=kubernetes.client.V1EnvVarSource(
            secret_key_ref=kubernetes.client.V1SecretKeySelector(
                name="mlpipeline-minio-artifact", key="port"
            )
        ),
    )
    secretkey = kubernetes.client.V1EnvVar(
        name="AWS_SECRET_ACCESS_KEY",
        value_from=kubernetes.client.V1EnvVarSource(
            secret_key_ref=kubernetes.client.V1SecretKeySelector(
                name="mlpipeline-minio-artifact", key="secretkey"
            )
        ),
    )
    bucket = kubernetes.client.V1EnvVar(name="AWS_S3_BUCKET", value="rhods")
    train_path = "data/train.csv"
    test_path = "data/test.csv"
    pre_process_task = pre_process_op(
        train_path = train_path,
        test_path = test_path
    ).add_env_variable(accesskey).add_env_variable(host).add_env_variable(port).add_env_variable(secretkey).add_env_variable(bucket)
    train_task = train_op(
        pre_process_task.outputs["X_train"],
        pre_process_task.outputs["y_train"],
        pre_process_task.outputs["X_val"],
        pre_process_task.outputs["y_val"],
        pre_process_task.outputs["X_test"]
    ).add_env_variable(accesskey).add_env_variable(host).add_env_variable(port).add_env_variable(secretkey).add_env_variable(bucket)
    evaluate_task = evalue_op(
        pre_process_task.outputs["X_val"],
        pre_process_task.outputs["y_val"],
        pre_process_task.outputs["X_test"],
        train_task.outputs["model"]
    ).add_env_variable(accesskey).add_env_variable(host).add_env_variable(port).add_env_variable(secretkey).add_env_variable(bucket)

if __name__ == '__main__':
    host = "http://ds-pipeline-pipelines-definition:8888"
    # mlflow.set_tracking_uri("http://mlflow-server.mlflow.svc.cluster.local:8080")
    # parser = argparse.ArgumentParser(
    #                     prog='Model.py',
    #                     description='Digit recognition model and pipeline triggering')
    # parser.add_argument('-t', '--tag')
    # args = parser.parse_args()
    # tag = args.tag
    volume_based_data_passing_method = data_passing_methods.KubernetesVolume(
        volume=V1Volume(
            name='data',
            persistent_volume_claim=V1PersistentVolumeClaimVolumeSource(
                claim_name='ml-pipeline'),
        )    
    )
    pipeline_conf = kfp.dsl.PipelineConf()
    pipeline_conf.data_passing_method = volume_based_data_passing_method
    
    client = kfp_tekton.TektonClient(host=host)
    # mlflow.log_param("git.commit", tag)
    # mlflow.end_run()
    # with mlflow.start_run():
    result = client.create_run_from_pipeline_func(
        mnist_pipeline, arguments={}, experiment_name="mnist_kfp", pipeline_conf=pipeline_conf
    )
    print(f"Starting pipeline run with run_id: {result.run_id}")