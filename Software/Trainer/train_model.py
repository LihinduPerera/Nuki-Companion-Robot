# train_model.py
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import joblib

data_path = "data"
X = []
y = []

for label, folder in enumerate(os.listdir(data_path)):
    gesture_path = os.path.join(data_path, folder)
    for file in os.listdir(gesture_path):
        if file.endswith('.npy'):
            sample = np.load(os.path.join(gesture_path, file))
            X.append(sample)
            y.append(label)

X = np.array(X)
y = np.array(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)

acc = model.score(X_test, y_test)
print(f"Model accuracy: {acc*100:.2f}%")

# Save model and labels
joblib.dump(model, "gesture_model.pkl")
np.save("labels.npy", np.array(os.listdir(data_path)))
