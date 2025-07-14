import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Load the aggregated features
data_file = r"C:\Users\M S I\PycharmProjects\chreck\data\knee_angle_features_all.csv"
df = pd.read_csv(data_file)
if df.empty or 'Name' not in df.columns or any(col not in df.columns for col in ['Right_Mean_Angle', 'Right_Std_Angle', 'Right_Skewness', 'Right_Kurtosis', 'Left_Mean_Angle', 'Left_Std_Angle', 'Left_Skewness', 'Left_Kurtosis']):
    print("Error: Invalid or empty data file. Check columns.")
    exit(1)

# Prepare features and labels
X = df[['Right_Mean_Angle', 'Right_Std_Angle', 'Right_Skewness', 'Right_Kurtosis',
        'Left_Mean_Angle', 'Left_Std_Angle', 'Left_Skewness', 'Left_Kurtosis']]
y = df['Name']

# Filter out classes with fewer than 2 samples
class_counts = df['Name'].value_counts()
valid_classes = class_counts[class_counts >= 2].index
if not valid_classes.any():
    print("Error: No classes have 2 or more samples. Add more data or correct names.")
    exit(1)
X = X[df['Name'].isin(valid_classes)]
y = y[df['Name'].isin(valid_classes)]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate the model
accuracy = model.score(X_test_scaled, y_test)
print(f"Model accuracy: {accuracy:.2f}")

# Save the scaler and model
joblib.dump(scaler, r"C:\Users\M S I\PycharmProjects\chreck\scaler.pkl")
joblib.dump(model, r"C:\Users\M S I\PycharmProjects\chreck\model.pkl")
print("Model and scaler saved successfully.")

# Print some details for debugging
print(f"Training data shape: {X_train.shape}")
print(f"Test data shape: {X_test.shape}")
print(f"Unique labels in training: {y_train.unique()}")
print(f"Unique labels in test: {y_test.unique()}")
print(f"Filtered out classes with < 2 samples: {set(class_counts[class_counts < 2].index)}")