import kfp
import kfp.dsl as dsl
from kfp.v2.dsl import component

@component
def pre_process(
        train: Input[Dataset],
        test: Input[Dataset],
        x_train: Output[Dataset],
        y_train: Output[Dataset],
        x_val: Output[Dataset],
        y_val: Output[Dataset],
        x_test: Output[Dataset]):
    
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
    from sklearn.preprocessing import OneHotEncoder

    df_train = pd.read_csv(train.path)
    df_test = pd.read_csv(test.path)

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

    np.save(x_train.path, X_train)
    np.save(y_train.path, y_train)
    np.save(x_val.path, X_val)
    np.save(y_val.path, y_val)
    np.save(x_test.path, X_test)

@component
def train(
        x_train: Input[Dataset],
        y_train: Input[Dataset],
        x_val: Input[Dataset],
        y_val: Input[Dataset],
        x_test: Input[Dataset]):
    

@dsl.pipeline(
  name='mnist-pipeline',
  description='Minst use case pipeline',
  # pipeline_root='gs://my-pipeline-root/example-pipeline'
)
def pipeline(train, test):
  pre_process_task = pre_process(train, test)
  train_task = train()