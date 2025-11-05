# Script to retrain the model with all enhanced features
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score
import joblib

print("="*70)
print("RETRAINING MODEL WITH ENHANCED FEATURES")
print("="*70)

# Load preprocessed data
print("\n[1/6] Loading preprocessed data...")
ml_data = pd.read_csv("ml_preprocessed_data.csv", parse_dates=["Date"])
print(f"   ✓ Loaded {len(ml_data)} rows")

# Create enhanced dataset with technical indicators
print("\n[2/6] Creating technical indicators...")
ml_data_enhanced = ml_data.copy()

# 1. Moving Averages (trend indicators)
ml_data_enhanced['MA_5'] = ml_data_enhanced['Close'].rolling(window=5).mean()
ml_data_enhanced['MA_20'] = ml_data_enhanced['Close'].rolling(window=20).mean()

# 2. Rate of Change (momentum indicator)
ml_data_enhanced['ROC'] = ml_data_enhanced['Close'].pct_change(periods=5) * 100

# 3. Price Range (volatility indicator)
ml_data_enhanced['Price_Range'] = ml_data_enhanced['High'] - ml_data_enhanced['Low']

# 4. Volume Change (trading activity indicator)
ml_data_enhanced['Volume_Change'] = ml_data_enhanced['Volume'].pct_change() * 100

# Remove NaN values created by rolling/pct_change
ml_data_enhanced.dropna(inplace=True)

# Remove infinity and extreme values
ml_data_enhanced.replace([np.inf, -np.inf], np.nan, inplace=True)
ml_data_enhanced.dropna(inplace=True)

# Cap extreme values (outliers beyond 3 standard deviations)
for col in ['ROC', 'Volume_Change']:
    mean = ml_data_enhanced[col].mean()
    std = ml_data_enhanced[col].std()
    ml_data_enhanced[col] = ml_data_enhanced[col].clip(lower=mean - 3*std, upper=mean + 3*std)

print(f"   ✓ Created 5 new technical indicators")
print(f"   ✓ Dataset shape after cleaning: {ml_data_enhanced.shape}")

# Prepare training data
print("\n[3/6] Preparing training data...")
feature_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Gold_Close', 
                'MA_5', 'MA_20', 'ROC', 'Price_Range', 'Volume_Change']

X = ml_data_enhanced[feature_cols]
y = ml_data_enhanced['Volatility_Label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"   ✓ Training set: {len(X_train)} samples")
print(f"   ✓ Test set: {len(X_test)} samples")
print(f"   ✓ Features: {len(feature_cols)}")

# Train the model
print("\n[4/6] Training Random Forest model...")
clf_enhanced = RandomForestClassifier(n_estimators=100, random_state=42, verbose=0)
clf_enhanced.fit(X_train, y_train)
print("   ✓ Model training complete")

# Evaluate the model
print("\n[5/6] Evaluating model performance...")
y_pred = clf_enhanced.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"   ✓ Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"   ✓ F1-Score: {f1:.4f} ({f1*100:.2f}%)")

print("\n   Detailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Low', 'Medium', 'High']))

# Feature importance
print("\n   Feature Importance Ranking:")
feature_importances = clf_enhanced.feature_importances_
feature_importance_dict = dict(zip(feature_cols, feature_importances))
sorted_features = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)
for i, (feature, importance) in enumerate(sorted_features, 1):
    print(f"   {i}. {feature:15s} → {importance:.4f} ({importance*100:.2f}%)")

# Save the model
print("\n[6/6] Saving enhanced model...")
model_filename = "rf_volatility_model_enhanced.pkl"
joblib.dump(clf_enhanced, model_filename)
print(f"   ✓ Model saved as '{model_filename}'")

print("\n" + "="*70)
print("MODEL TRAINING COMPLETE!")
print("="*70)
print(f"\nTo use this enhanced model:")
print(f"1. Backup the old model: rename 'rf_volatility_model.pkl' to 'rf_volatility_model_old.pkl'")
print(f"2. Rename '{model_filename}' to 'rf_volatility_model.pkl'")
print(f"3. Update app.py to use all 11 features instead of 6")
print("="*70)
