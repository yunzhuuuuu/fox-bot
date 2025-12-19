import os
import librosa
import numpy as np

DATASET_PATH = "dataset"  # <-- change to your path

def extract_mfcc(file_path, n_mfcc=13):
    signal, sr = librosa.load(file_path, sr=22050)
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=n_mfcc)
    return np.mean(mfcc.T, axis=0)  # average across time

X = []  # features
y = []  # labels

for genre in os.listdir(DATASET_PATH):              # each label folder
    genre_path = os.path.join(DATASET_PATH, genre)

    if not os.path.isdir(genre_path):
        continue

    for filename in os.listdir(genre_path):
        if filename.endswith(".wav"):
            file_path = os.path.join(genre_path, filename)
            features = extract_mfcc(file_path)
            X.append(features)
            y.append(genre)

X = np.array(X)
y = np.array(y)

print("Dataset Ready!")
print("Feature Shape:", X.shape)
print("Labels:", set(y))

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# split train and test data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# train classifier
model = RandomForestClassifier(n_estimators=200)
model.fit(X_train, y_train)

# predict
y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

def predict(file):
    features = extract_mfcc(file).reshape(1, -1)
    prediction = model.predict(features)
    return prediction[0]

print(predict("test.wav"))
