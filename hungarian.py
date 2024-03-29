# Mengimpor library yang diperlukan
import itertools
import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score
import streamlit as st
import time
import pickle

# Membuka file data dan memasukkannya ke dalam list 'lines'
with open("data/hungarian.data", encoding='Latin1') as file:
  lines = [line.strip() for line in file]

# Mengelompokkan data ke dalam DataFrame dengan membaginya menjadi bagian-bagian tertentu
data = itertools.takewhile(
  lambda x: len(x) == 76,
  (' '.join(lines[i:(i + 10)]).split() for i in range(0, len(lines), 10))
)

# Mengonversi data ke dalam DataFrame pandas
df = pd.DataFrame.from_records(data)

# Menghapus kolom terakhir dan beberapa kolom yang tidak relevan
df = df.iloc[:, :-1]
df = df.drop(df.columns[0], axis=1)
df = df.astype(float)

# Mengganti nilai -9.0 dengan NaN (missing value)
df.replace(-9.0, np.NaN, inplace=True)

# Memilih kolom yang akan digunakan untuk analisis
df_selected = df.iloc[:, [1, 2, 7, 8, 10, 14, 17, 30, 36, 38, 39, 42, 49, 56]]

# Memberikan nama baru pada kolom menggunakan 'column_mapping'
column_mapping = {
  2: 'age',
  3: 'sex',
  8: 'cp',
  9: 'trestbps',
  11: 'chol',
  15: 'fbs',
  18: 'restecg',
  31: 'thalach',
  37: 'exang',
  39: 'oldpeak',
  40: 'slope',
  43: 'ca',
  50: 'thal',
  57: 'target'
}

df_selected.rename(columns=column_mapping, inplace=True)

# Menghapus kolom yang tidak diperlukan
columns_to_drop = ['ca', 'slope','thal']
df_selected = df_selected.drop(columns_to_drop, axis=1)

# Mengisi nilai yang hilang dengan mean dari setiap kolom tertentu
meanTBPS = df_selected['trestbps'].dropna()
meanChol = df_selected['chol'].dropna()
meanfbs = df_selected['fbs'].dropna()
meanRestCG = df_selected['restecg'].dropna()
meanthalach = df_selected['thalach'].dropna()
meanexang = df_selected['exang'].dropna()

meanTBPS = meanTBPS.astype(float)
meanChol = meanChol.astype(float)
meanfbs = meanfbs.astype(float)
meanthalach = meanthalach.astype(float)
meanexang = meanexang.astype(float)
meanRestCG = meanRestCG.astype(float)

meanTBPS = round(meanTBPS.mean())
meanChol = round(meanChol.mean())
meanfbs = round(meanfbs.mean())
meanthalach = round(meanthalach.mean())
meanexang = round(meanexang.mean())
meanRestCG = round(meanRestCG.mean())

# Menyiapkan dictionary 'fill_values' dengan rata-rata untuk menggantikan 
fill_values = {
  'trestbps': meanTBPS,
  'chol': meanChol,
  'fbs': meanfbs,
  'thalach':meanthalach,
  'exang':meanexang,
  'restecg':meanRestCG
}

df_clean = df_selected.fillna(value=fill_values)
df_clean.drop_duplicates(inplace=True)

X = df_clean.drop("target", axis=1)
y = df_clean['target']

# Melakukan SMOTE untuk menangani ketidakseimbangan kelas dalam target
smote = SMOTE(random_state=42)
X, y = smote.fit_resample(X, y)

# Memuat model yang sudah dilatih sebelumnya menggunakan pickle
model = pickle.load(open("model/xgb_model.pkl", 'rb'))

# Melakukan prediksi menggunakan model pada data yang telah diproses
y_predict = model.predict(X)
accuracy = accuracy_score(y, y_predict)
accuracy = round((accuracy * 100), 2)

df_final = X
df_final['target'] = y

# ========================================================================================================================================================================================

# Membuat tampilan Streamlit
# STREAMLIT
st.set_page_config(
  page_title = "Hungarian Heart Disease",
  page_icon = ":heart:"
)

# Mengatur konfigurasi halaman dan judul
st.title("Hungarian Heart Disease")
st.image('heart.jpg', width=400)
st.info(f"**_Model's Accuracy_** :  :green[**91.4**]%")
st.write("")

# Membuat tab untuk fungsionalitas Single-predict dan Multi-predict
tab1, tab2 = st.tabs(["Single-predict", "Multi-predict"])

with tab1:
  st.sidebar.header("**User Input** Sidebar")
  st.markdown(
      """
      <style>
      .st-dl { background-color: #FF5733; }
      </style>
      """,
      unsafe_allow_html=True
  )
  
  # Implementasi tab Single-predict untuk prediksi data tunggal berdasarkan input pengguna
  age = st.sidebar.number_input(label=":red[**Age**]", min_value=df_final['age'].min(), max_value=df_final['age'].max())
  st.sidebar.write(f":blue[Min] value: :blue[**{df_final['age'].min()}**], :violet[Max] value: :violet[**{df_final['age'].max()}**]")
  st.sidebar.write("")

  sex_sb = st.sidebar.selectbox(label=":red[**Sex**]", options=["Male", "Female"])
  st.sidebar.write("")
  st.sidebar.write("")
  if sex_sb == "Male":
    sex = 1
  elif sex_sb == "Female":
    sex = 0
  # -- Value 0: Female
  # -- Value 1: Male

  cp_sb = st.sidebar.selectbox(label=":red[**Chest pain type**]", options=["Typical angina", "Atypical angina", "Non-anginal pain", "Asymptomatic"])
  st.sidebar.write("")
  st.sidebar.write("")
  if cp_sb == "Typical angina":
    cp = 1
  elif cp_sb == "Atypical angina":
    cp = 2
  elif cp_sb == "Non-anginal pain":
    cp = 3
  elif cp_sb == "Asymptomatic":
    cp = 4
  # -- Value 1: typical angina
  # -- Value 2: atypical angina
  # -- Value 3: non-anginal pain
  # -- Value 4: asymptomatic

  trestbps = st.sidebar.number_input(label=":red[**Resting blood pressure** (in mm Hg on admission to the hospital)]", min_value=df_final['trestbps'].min(), max_value=df_final['trestbps'].max())
  st.sidebar.write(f":blue[Min] value: :blue[**{df_final['trestbps'].min()}**], :violet[Max] value: :violet[**{df_final['trestbps'].max()}**]")
  st.sidebar.write("")

  chol = st.sidebar.number_input(label=":red[**Serum cholestoral** (in mg/dl)]", min_value=df_final['chol'].min(), max_value=df_final['chol'].max())
  st.sidebar.write(f":blue[Min] value: :blue[**{df_final['chol'].min()}**], :violet[Max] value: :violet[**{df_final['chol'].max()}**]")
  st.sidebar.write("")

  fbs_sb = st.sidebar.selectbox(label=":red[**Fasting blood sugar > 120 mg/dl?**]", options=["False", "True"])
  st.sidebar.write("")
  st.sidebar.write("")
  if fbs_sb == "False":
    fbs = 0
  elif fbs_sb == "True":
    fbs = 1
  # -- Value 0: false
  # -- Value 1: true

  restecg_sb = st.sidebar.selectbox(label=":red[**Resting electrocardiographic results**]", options=["Normal", "Having ST-T wave abnormality", "Showing left ventricular hypertrophy"])
  st.sidebar.write("")
  st.sidebar.write("")
  if restecg_sb == "Normal":
    restecg = 0
  elif restecg_sb == "Having ST-T wave abnormality":
    restecg = 1
  elif restecg_sb == "Showing left ventricular hypertrophy":
    restecg = 2
  # -- Value 0: normal
  # -- Value 1: having ST-T wave abnormality (T wave inversions and/or ST  elevation or depression of > 0.05 mV)
  # -- Value 2: showing probable or definite left ventricular hypertrophy by Estes' criteria

  thalach = st.sidebar.number_input(label=":red[**Maximum heart rate achieved**]", min_value=df_final['thalach'].min(), max_value=df_final['thalach'].max())
  st.sidebar.write(f":blue[Min] value: :blue[**{df_final['thalach'].min()}**], :violet[Max] value: :violet[**{df_final['thalach'].max()}**]")
  st.sidebar.write("")

  exang_sb = st.sidebar.selectbox(label=":red[**Exercise induced angina?**]", options=["No", "Yes"])
  st.sidebar.write("")
  st.sidebar.write("")
  if exang_sb == "No":
    exang = 0
  elif exang_sb == "Yes":
    exang = 1
  # -- Value 0: No
  # -- Value 1: Yes

  oldpeak = st.sidebar.number_input(label=":red[**ST depression induced by exercise relative to rest**]", min_value=df_final['oldpeak'].min(), max_value=df_final['oldpeak'].max())
  st.sidebar.write(f":blue[Min] value: :blue[**{df_final['oldpeak'].min()}**], :violet[Max] value: :violet[**{df_final['oldpeak'].max()}**]")
  st.sidebar.write("")

  #Menyimpan hasil inputan kedalam 'data'
  data = {
    'Age': age,
    'Sex': sex_sb,
    'Chest pain type': cp_sb,
    'RPB': f"{trestbps} mm Hg",
    'Serum Cholestoral': f"{chol} mg/dl",
    'FBS > 120 mg/dl?': fbs_sb,
    'Resting ECG': restecg_sb,
    'Maximum heart rate': thalach,
    'Exercise induced angina?': exang_sb,
    'ST depression': oldpeak,
  }

  preview_df = pd.DataFrame(data, index=['input'])

  st.header("User Input as DataFrame")
  st.write("")
  st.dataframe(preview_df.iloc[:, :6])
  st.write("")
  st.dataframe(preview_df.iloc[:, 6:])
  st.write("")

  result = ":red[-]"

  #Membuat tombol prediction
  predict_btn = st.button("**predict**", type="primary")

  st.write("")
  if predict_btn:
    inputs = [[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak]]
    prediction = model.predict(inputs)[0]

    bar = st.progress(0)
    status_text = st.empty()

    for i in range(1, 101):
      status_text.text(f"{i}% complete")
      bar.progress(i)
      time.sleep(0.01)
      if i == 100:
        time.sleep(1)
        status_text.empty()
        bar.empty()

    if prediction == 0:
      result = ":green[**Healthy**]"
    elif prediction == 1:
      result = ":blue[**Heart disease level 1**]"
    elif prediction == 2:
      result = ":blue[**Heart disease level 2**]"
    elif prediction == 3:
      result = ":violet[**Heart disease level 3**]"
    elif prediction == 4:
      result = ":violet[**Heart disease level 4**]"

  # Menampilkan hasilnya pada interaksi pengguna
  st.write("")
  st.write("")
  st.subheader("prediction:")
  st.subheader(result)

with tab2:
  st.header("predict multiple data:")

  st.markdown(
      """
      <style>
      .st-dl { background-color: #3399FF; }
      </style>
      """,
      unsafe_allow_html=True
  )

  #Membuat sample csv
  sample_csv = df_final.iloc[:5, :-1].to_csv(index=False).encode('utf-8')

  #Membuat tombol download sample example
  st.write("")
  st.download_button("Download CSV Example", data=sample_csv, file_name='sample_heart_disease_parameters.csv', mime='text/csv')

  #Membuat section untuk mengupload file
  st.write("")
  st.write("")
  file_uploaded = st.file_uploader("Upload a CSV file", type='csv')

  #Membaca hasil upload-an user
  if file_uploaded:
    uploaded_df = pd.read_csv(file_uploaded)
    #Memprediksi data dari user
    prediction_arr = model.predict(uploaded_df)

    bar = st.progress(0)
    status_text = st.empty()

    for i in range(1, 70):
      status_text.text(f"{i}% complete")
      bar.progress(i)
      time.sleep(0.01)

    result_arr = []

    for prediction in prediction_arr:
      if prediction == 0:
        result = "Healthy"
      elif prediction == 1:
        result = "Heart disease level 1"
      elif prediction == 2:
        result = "Heart disease level 2"
      elif prediction == 3:
        result = "Heart disease level 3"
      elif prediction == 4:
        result = "Heart disease level 4"
      result_arr.append(result)

    uploaded_result = pd.DataFrame({'prediction Result': result_arr})

    for i in range(70, 101):
      status_text.text(f"{i}% complete")
      bar.progress(i)
      time.sleep(0.01)
      if i == 100:
        time.sleep(1)
        status_text.empty()
        bar.empty()

    col1, col2 = st.columns([1, 2])

    #Menampilkan hasil prediksi
    with col1:
      st.dataframe(uploaded_result)
    with col2:
      st.dataframe(uploaded_df)
