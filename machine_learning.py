# Import necessary libraries
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, recall_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

# Load the dataset
data = pd.read_csv("diabetes_prediction_dataset.csv")

# Remove duplicate rows
data = data.drop_duplicates()

# Define target and features
target = "diabetes"
x = data.drop(target, axis = 1)
y = data[target]

# Split the data (80% train, 20% test)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state=42, stratify=y)
print("Target value counts in test set:")
print(y_test.value_counts())

# Preprocessing for numerical features
num_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

# Preprocessing for nominal features
nom_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(sparse_output=False))
])

# Preprocessing for ordinal features
smoking_values = ['No Info', 'never', 'former', 'not current', 'ever', 'current']
ord_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OrdinalEncoder(categories=[smoking_values]))
])

# Combine all transformers
preprocessor = ColumnTransformer([
    ("num_feature", num_transformer, ["age", "hypertension", "heart_disease", "bmi", "HbA1c_level", "blood_glucose_level"]),
    ("nom_feature", nom_transformer, ["gender"]),
    ("ord_feature", ord_transformer, ["smoking_history"])
])

# Define the model with RandomForestClassifier
cls = ImbPipeline(steps=[
    ('preprocessor', preprocessor),
    ('smote', SMOTE(random_state=42)),  # SMOTE to handle class imbalance
    ('model', RandomForestClassifier(class_weight='balanced'))  # Adjust weights if needed
])

# Define parameters for GridSearchCV
params = {
    'model__criterion': ['gini', 'entropy', 'log_loss']
}

# Perform grid search for hyperparameter tuning
grid_search = GridSearchCV(estimator=cls, param_grid=params, cv=5, scoring='recall', verbose=3)

# Train the model using GridSearchCV
grid_search.fit(x_train, y_train)

# Predict on the test set
y_predict = grid_search.predict(x_test)

# Evaluate the model
print(classification_report(y_test, y_predict))
print("Recall Score:", recall_score(y_test, y_predict))

# Optionally: Display confusion matrix for more detailed evaluation
from sklearn.metrics import confusion_matrix
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_predict))
