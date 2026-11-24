import pandas as pd
import pyreadstat

df, meta = pyreadstat.read_sav("peerj-10-12836-s001.sav")

print("Dataset shape:", df.shape)
print("Columns:")
print(df.columns.tolist())
# ASRS questions as input features
asrs_columns = [f"ASRS_{i}" for i in range(1, 19)]

X = df[asrs_columns]

# ADHD diagnosis as target
y = df["ADHDdiagnosis"]

print("Input shape:", X.shape)
print("Target distribution:")
print(y.value_counts())
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training data:", X_train.shape)
print("Testing data:", X_test.shape)
from sklearn.linear_model import LogisticRegression

# Create the model
model = LogisticRegression(max_iter=1000)

# Train the model
model.fit(X_train, y_train)

print("Model training completed!")
# Make predictions on unseen test data
y_pred = model.predict(X_test)

print("Predictions:")
print(y_pred)
from sklearn.metrics import accuracy_score

accuracy = accuracy_score(y_test, y_pred)

print("Accuracy:", accuracy)
from sklearn.metrics import confusion_matrix, classification_report

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))
from sklearn.ensemble import RandomForestClassifier

# Create Random Forest model
rf_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train the model
rf_model.fit(X_train, y_train)

print("Random Forest training completed!")
# Make predictions using Random Forest
rf_pred = rf_model.predict(X_test)

print("Random Forest Predictions:")
print(rf_pred)
from sklearn.metrics import accuracy_score

rf_accuracy = accuracy_score(y_test, rf_pred)

print("Random Forest Accuracy:", rf_accuracy)
from sklearn.metrics import confusion_matrix

rf_cm = confusion_matrix(y_test, rf_pred)

print("Random Forest Confusion Matrix:")
print(rf_cm)
from sklearn.metrics import classification_report

print("Random Forest Classification Report:")
print(classification_report(y_test, rf_pred))
from sklearn.model_selection import cross_val_score

cv_scores = cross_val_score(
    rf_model,
    X,
    y,
    cv=5,
    scoring="accuracy"
)

print("Cross-validation scores:", cv_scores)
print("Average CV Accuracy:", cv_scores.mean())
cv_scores_train = cross_val_score(
    rf_model,
    X_train,
    y_train,
    cv=5,
    scoring="accuracy"
)

print("Training CV scores:", cv_scores_train)
print("Average Training CV Accuracy:", cv_scores_train.mean())
import joblib

# Save the trained Random Forest model
joblib.dump(rf_model, "model/adhd_model.pkl")

print("Model saved successfully!")
import joblib

# Load the saved model
loaded_model = joblib.load("model/adhd_model.pkl")

print("Saved model loaded successfully!")
# Prediction Function

def predict_adhd(answers):
    input_data = pd.DataFrame(
        [answers],
        columns=asrs_columns
    )

    prediction = loaded_model.predict(input_data)

    return prediction[0]


# Test with 18 ASRS answers

answers = [
    3, 4, 2, 5, 3, 4,
    2, 3, 4, 2, 5, 3,
    4, 2, 3, 4, 2, 3
]

result = predict_adhd(answers)

print("Prediction:", result)
# Convert model prediction into a user-friendly result

if result == 1.0:
    screening_result = "Screening result indicates a possibility of ADHD symptoms."
else:
    screening_result = "Screening result does not indicate a strong possibility of ADHD symptoms."

print("Screening Result:", screening_result)