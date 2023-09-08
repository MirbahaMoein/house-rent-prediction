from Model.Crawler.crawler import crawl_links, get_data, clean_data
import joblib
import time
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
import tqdm

def percentage_rmse(X_val, y_val, estimator, labels,
        X_train, y_train, weight_val=None, weight_train=None,
        config=None, groups_val=None, groups_train=None):
    start = time.time()
    y_pred = estimator.predict(X_val)
    pred_time = (time.time() - start) / len(X_val)
    val_rmsep = np.sqrt(np.mean(np.square(((y_val - y_pred) / np.minimum(y_val, y_pred)))))
    y_pred = estimator.predict(X_train)
    train_rmsep = np.sqrt(np.mean(np.square(((y_train - y_pred) / np.minimum(y_train, y_pred)))))
    return val_rmsep, {
        "val_rmsep": val_rmsep,
        "train_rmsep": train_rmsep,
        "pred_time": pred_time,
    }

def save_new_cases():
    fullurl = "https://divar.ir/s/tehran/rent-apartment?sort=sort_date"
    ostad_zanjan_url = "https://divar.ir/s/tehran/rent-apartment/tehran-zanjan?districts=195&sort=sort_date"
    clean_data(get_data(crawl_links(ostad_zanjan_url))).to_excel("newcases.xlsx")

def read_trained_objects():
    automl_model = joblib.load("./Model/objs/trained_model.joblib")
    x_scaler = joblib.load("./Model/objs/x_scaler.joblib")
    X_cols = joblib.load("./Model//objs/x_columns.jobllib")
    outlier_detection_model = joblib.load("./Model//objs/outlier_model.jobllib")
    return automl_model, x_scaler, X_cols, outlier_detection_model

def read_new_cases():
    return pd.read_excel("newcases.xlsx", index_col= 0)

def preprocess_cases(df):
    df["full mortgage"] = df["pish1"].astype(float) + df["rent1"].astype(float) * 100/3
    df = df[(df["full mortgage"] > 10000000)].reset_index(drop= True)
    prediction_array = pd.DataFrame(columns = X_cols)
    poly = PolynomialFeatures(degree=3)
    year_poly = pd.DataFrame(poly.fit_transform(df[["year"]]), columns= ["intercept", "year", "year2", "year3"])
    area_poly = pd.DataFrame(poly.fit_transform(df[["area"]]), columns= ["intercept_area", "area", "area2", "area3"]).drop(["intercept_area"], axis = 1)
    df = pd.concat([df.drop(["year", "area"], axis = 1).reset_index(drop= True), year_poly, area_poly], axis= 1)
    X_df = df.drop(["full mortgage", "title", "description", "url", "number of rooms", "area3", "pish1", "pish2", "rent1", "rent2"], axis = 1)
    prediction_array = pd.DataFrame(columns = X_cols)
    for index in tqdm.tqdm(range(len(X_df))):
        zone = X_df['zone'][index]
        for col in X_cols:
            try:
                prediction_array.loc[index, col] = X_df[col][index]
            except:
                prediction_array.loc[index, col] = 0
        prediction_array.loc[index, zone] = True
    prediction_array.fillna(0)
    return prediction_array, df

def predict_new_cases(prediction_array):
    scaled_X = x_scaler.fit_transform(prediction_array)
    return automl_model.predict(scaled_X)

def save_results(df, auto_pred):
    df.drop(["area3", "area2", "year3", "year2", "intercept"], axis= 1, inplace= True)
    df_column_order = df.columns.tolist()
    df_column_order.remove("full mortgage")
    df_column_order.append("full mortgage")
    df = df[df_column_order]
    conc = pd.concat([df, pd.Series(auto_pred)], axis= 1)
    conc.columns = conc.columns.tolist()[:-1] + ["prediction"]
    conc["error percentage"] = (conc["full mortgage"] - conc["prediction"]).abs() / pd.concat([conc["prediction"], conc["full mortgage"]], axis=1).min(axis=1) * 100
    conc.to_excel("new_results.xlsx")
    
save_new_cases()
automl_model, x_scaler, X_cols, outlier_detection_model = read_trained_objects()
df = read_new_cases()
prediction_array, df = preprocess_cases(df)
auto_pred = predict_new_cases(prediction_array)
save_results(df, auto_pred)

