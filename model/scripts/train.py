def train():
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
    
    DIR = "/tmp/ml-pipeline/"
    X_train = load_pickle(DIR + "data/X_train")
    y_train = load_pickle(DIR + "data/y_train")
    X_val = load_pickle(DIR + "data/X_val")
    y_val = load_pickle(DIR + "data/y_val")
    X_test = load_pickle(DIR + "data/X_test")

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
    model_path_local = DIR + 'model/saved_model'
    onnx_path_local = DIR + 'model/model.onnx'
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
        s3_endpoint = os.environ.get("AWS_S3_ENDPOINT")
        s3_client = boto3.client("s3", aws_access_key_id=key_id, aws_secret_access_key=secret_key, endpoint_url=s3_endpoint)
        return s3_client

    s3_client = init_s3_connection()
    bucket_name = "rhods"
    s3_client.upload_file(onnx_path_local, bucket_name, "onnx/model-v2.onnx")
    save_pickle(DIR + "model.onnx", model)

if __name__ == "__main__":
    train()