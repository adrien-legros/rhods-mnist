import argparse
import kfp
import kfp.components as comp
import kfp_tekton
import kubernetes
import os

from kfp.dsl import data_passing_methods
from kubernetes.client.models import V1Volume, V1PersistentVolumeClaimVolumeSource, \
    V1PersistentVolumeClaimSpec, V1ResourceRequirements

# os.environ["DEFAULT_STORAGE_CLASS"] = "my-local-storage"
# os.environ["DEFAULT_ACCESSMODES"] = "ReadWriteOnce"
# os.environ["DEFAULT_ARTIFACT_BUCKET"] = "rhods"
# os.environ["DEFAULT_ARTIFACT_ENDPOINT"] = "minio-ds-pipeline.ds-testings.svc.cluster.local"
# os.environ["DEFAULT_ARTIFACT_ENDPOINT_SCHEME"] = "http://"

def pre_process(
        train_path: str,
        test_path: str,
        X_train_file: comp.OutputPath(),
        y_train_file: comp.OutputPath(),
        X_val_file: comp.OutputPath(),
        y_val_file: comp.OutputPath(),
        X_test_file: comp.OutputPath()
):
    import numpy as np
    import pandas as pd
    from matplotlib import pyplot as plt
    import tensorflow as tf
    from tensorflow import keras
    import seaborn as sns

    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.base import BaseEstimator, TransformerMixin
    from sklearn.preprocessing import OneHotEncoder
    
    import pickle
    
    train_local_path = '/tmp/train.csv'
    test_local_path = '/tmp/test.csv'

    def save_pickle(object_file, target_object):
        with open(object_file, "wb") as f:
            pickle.dump(target_object, f)

    def init_s3_connection():
        import boto3
        from boto3 import session
        import os
        key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        bucket_name = os.environ.get("AWS_S3_BUCKET")
        host = os.environ.get("AWS_S3_HOST")
        port = os.environ.get("AWS_S3_PORT")
        s3_endpoint = 'http://' + host + ":" + port
        s3_client = boto3.client("s3", aws_access_key_id=key_id, aws_secret_access_key=secret_key, endpoint_url=s3_endpoint)
        return s3_client

    s3_client = init_s3_connection()
    s3_client.download_file('rhods', train_path, train_local_path)
    s3_client.download_file('rhods', test_path, test_local_path)

    df_train = pd.read_csv(train_local_path)
    df_test = pd.read_csv(test_local_path)

    X = df_train.iloc[:,1:]
    y = df_train.iloc[:, 0]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1, random_state=15)

    class ReshapeFunc(BaseEstimator, TransformerMixin):
        def __init__(self):
            pass
        def fit(self, X, y=None):
            return self
        def transform(self, X, y=None):
            X = X.reshape((-1,28,28,1))
            return X
    features_pipeline = Pipeline(steps=[
        ('Normalize', MinMaxScaler()),
        ('Reshape', ReshapeFunc())
    ])
    target_pipeline = Pipeline(steps=[
        ('OneHot', OneHotEncoder())
    ])

    X_train = features_pipeline.fit_transform(X_train)
    y_train = target_pipeline.fit_transform(y_train.values.reshape(-1,1))
    y_train = y_train.toarray()
    X_val = features_pipeline.fit_transform(X_val)
    y_val = target_pipeline.fit_transform(y_val.values.reshape(-1, 1))
    y_val = y_val.toarray()
    X_test = features_pipeline.fit_transform(df_test)

    save_pickle(X_train_file, X_train)
    save_pickle(y_train_file, y_train)
    save_pickle(X_val_file, X_val)
    save_pickle(y_val_file, y_val)
    save_pickle(X_test_file, X_test)


def train(
        X_train_file: comp.InputPath(),
        y_train_file: comp.InputPath(),
        X_val_file: comp.InputPath(),
        y_val_file: comp.InputPath(),
        X_test_file: comp.InputPath(),
        model_file: comp.OutputPath()
):
    import numpy as np
    import pandas as pd
    import tensorflow as tf
    from tensorflow import keras
    import subprocess
    import pickle

    def save_pickle(object_file, target_object):
        with open(object_file, "wb") as f:
            pickle.dump(target_object, f)

    def load_pickle(object_file):
        with open(object_file, "rb") as f:
            target_object = pickle.load(f)
        return target_object            
    
    X_train = load_pickle(X_train_file)
    y_train = load_pickle(y_train_file)
    X_val = load_pickle(X_val_file)
    y_val = load_pickle(y_val_file)
    X_test = load_pickle(X_test_file)

    def build_model():
        inp = keras.Input(shape=(28,28,1), name="input_1")
        x = keras.layers.Conv2D(filters=32, kernel_size=(5,5), strides=(1,1),padding='SAME', 
                                activation='relu')(inp)
        x = keras.layers.MaxPool2D(pool_size=(2,2))(x)
        x = keras.layers.BatchNormalization()(x)
        x = keras.layers.Dropout(0.25)(x)
        x = keras.layers.Conv2D(filters=64, kernel_size=(5,5), padding='SAME', activation='relu')(x)
        x = keras.layers.MaxPool2D(pool_size=(2,2))(x)
        x = keras.layers.BatchNormalization()(x)
        x = keras.layers.Dropout(0.25)(x)
        x = keras.layers.Flatten()(x)
        x = keras.layers.Dense(256, activation='relu')(x)
        x = keras.layers.Dropout(0.5)(x)
        output = keras.layers.Dense(10, activation='softmax')(x)

        model = keras.Model(inputs=inp, outputs=output)
        model.compile(
            loss=keras.losses.CategoricalCrossentropy(),
            optimizer=keras.optimizers.Adam(learning_rate=0.0001),
            metrics=['accuracy'])
        return model, inp, output

    model, inp, out = build_model()
    model.summary()

    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=1, batch_size=32,
                    callbacks=[keras.callbacks.EarlyStopping(monitor='val_loss',mode='min',patience=10, 
                                                            min_delta=0.005, restore_best_weights=True),
                            keras.callbacks.ReduceLROnPlateau(monitor = 'val_loss', patience = 3)])
    model_path_local = '/tmp/saved_model'
    onnx_path_local = '/tmp/model.onnx'
    tf.saved_model.save(model, model_path_local)
    
    cmd = 'python -m tf2onnx.convert --saved-model ' + model_path_local + ' --output ' + onnx_path_local + ' --opset 13'

    proc = subprocess.run(cmd.split(), capture_output=True)
    print(proc.returncode)
    print(proc.stdout.decode('ascii'))
    print(proc.stderr.decode('ascii'))
    
    def init_s3_connection():
        import boto3
        from boto3 import session
        import os
        key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        bucket_name = os.environ.get("AWS_S3_BUCKET")
        host = os.environ.get("AWS_S3_HOST")
        port = os.environ.get("AWS_S3_PORT")
        s3_endpoint = 'http://' + host + ":" + port
        s3_client = boto3.client("s3", aws_access_key_id=key_id, aws_secret_access_key=secret_key, endpoint_url=s3_endpoint)
        return s3_client

    s3_client = init_s3_connection()
    bucket_name = "rhods"
    s3_client.upload_file(onnx_path_local, bucket_name, "onnx/model-v2.onnx")
    save_pickle(model_file, model)


def evaluate(
    X_val_file: comp.InputPath(),
    y_val_file: comp.InputPath(),
    X_test_file: comp.InputPath(),
    model_file: comp.InputPath()
):
    import numpy as np
    import pandas as pd
    import pickle
    import tensorflow as tf
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

    from sklearn.metrics import confusion_matrix
    from keras import backend as K

    def load_pickle(object_file):
        with open(object_file, "rb") as f:
            target_object = pickle.load(f)
        return target_object

    def init_s3_connection():
        import boto3
        from boto3 import session
        import os
        key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        bucket_name = os.environ.get("AWS_S3_BUCKET")
        host = os.environ.get("AWS_S3_HOST")
        port = os.environ.get("AWS_S3_PORT")
        s3_endpoint = 'http://' + host + ":" + port
        s3_client = boto3.client("s3", aws_access_key_id=key_id, aws_secret_access_key=secret_key, endpoint_url=s3_endpoint)
        return s3_client

    X_val = load_pickle(X_val_file)
    y_val = load_pickle(y_val_file)
    X_test = load_pickle(X_test_file)
    model = load_pickle(model_file)

    # Precision (using keras backend)
    def precision_metric(y_true, y_pred):
        threshold = 0.5  # Training threshold 0.5
        y_pred_y = K.cast(K.greater(K.clip(y_pred, 0, 1), threshold), K.floatx())

        true_positives = K.sum(K.clip(y_true * y_pred, 0, 1))
        false_negatives = K.sum(K.clip(y_true * (1-y_pred), 0, 1))
        false_positives = K.sum(K.clip((1-y_true) * y_pred, 0, 1))
        true_negatives = K.sum(K.clip((1 - y_true) * (1-y_pred), 0, 1))

        precision = true_positives / (true_positives + false_positives + K.epsilon())
        return precision

    # Recall (using keras backend)
    def recall_metric(y_true, y_pred):
        threshold = 0.5 #Training threshold 0.5
        y_pred = K.cast(K.greater(K.clip(y_pred, 0, 1), threshold), K.floatx())

        true_positives = K.sum(K.clip(y_true * y_pred, 0, 1))
        false_negatives = K.sum(K.clip(y_true * (1-y_pred), 0, 1))
        false_positives = K.sum(K.clip((1-y_true) * y_pred, 0, 1))
        true_negatives = K.sum(K.clip((1 - y_true) * (1-y_pred), 0, 1))

        recall = true_positives / (true_positives + false_negatives + K.epsilon())
        return recall

    # F1-score (using keras backend)
    def f1_metric(y_true, y_pred):
        precision = precision_metric(y_true, y_pred)
        recall = recall_metric(y_true, y_pred)
        f1 = 2 * ((precision * recall) / (recall+precision+K.epsilon()))
        return f1

    y_val_pred = np.argmax(model.predict(X_val), axis=1)
    y_val_pred
    y_val_true = np.argmax(y_val,axis=1)
    y_val_true

    acc = accuracy_score(y_val_true, y_val_pred)
    f1_macro = f1_score(y_val_true, y_val_pred, average="macro")
    rec = recall_score(y_val_true, y_val_pred, average="macro")
    prec = precision_score(y_val_true, y_val_pred, average="macro")
    print(f'accuracy_score: {acc}')
    print(f'f1_score_macro: {f1_macro}')
    print(f'precision_score: {prec}')
    print(f'recall_score: {rec}')


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
    accesskey = kubernetes.client.V1EnvVar(
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