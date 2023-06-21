import kfp.components as comp

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
