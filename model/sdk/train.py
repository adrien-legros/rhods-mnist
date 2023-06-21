import kfp.components as comp

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

