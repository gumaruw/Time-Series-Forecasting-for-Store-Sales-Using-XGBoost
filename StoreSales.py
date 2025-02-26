from google.colab import files
files.upload()  # Upload the kaggle.json file

# Move the kaggle.json file to the correct directory
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

# Download the competition data using Kaggle API
!kaggle competitions download -c store-sales-time-series-forecasting

import zipfile
import pandas as pd
import numpy as np

# Extract the zip file
with zipfile.ZipFile('store-sales-time-series-forecasting.zip', 'r') as zip_ref:
    zip_ref.extractall('data')

# Load the datasets
train_df = pd.read_csv('data/train.csv')
test_df = pd.read_csv('data/test.csv')
stores_df = pd.read_csv('data/stores.csv')
oil_df = pd.read_csv('data/oil.csv')
holidays_df = pd.read_csv('data/holidays_events.csv')
transactions_df = pd.read_csv('data/transactions.csv')

# Display the first few rows of each dataset
print(train_df.head())
print(test_df.head())
print(stores_df.head())
print(oil_df.head())
print(holidays_df.head())
print(transactions_df.head())

# Convert the 'date' column to datetime format
train_df['date'] = pd.to_datetime(train_df['date'])
test_df['date'] = pd.to_datetime(test_df['date'])
transactions_df['date'] = pd.to_datetime(transactions_df['date'])
oil_df['date'] = pd.to_datetime(oil_df['date'])
holidays_df['date'] = pd.to_datetime(holidays_df['date'])

# Fill missing values in the oil price data
oil_df['dcoilwtico'] = oil_df['dcoilwtico'].fillna(method='ffill')

print("train_df columns:", train_df.columns)
print("stores_df columns:", stores_df.columns)
print("transactions_df columns:", transactions_df.columns)

# Merge datasets
train_df = train_df.merge(stores_df, on='store_nbr', how='left')
train_df = train_df.merge(transactions_df, on=['store_nbr', 'date'], how='left')
train_df = train_df.merge(oil_df, on='date', how='left')
train_df = train_df.merge(holidays_df, on='date', how='left')

test_df = test_df.merge(stores_df, on='store_nbr', how='left')
test_df = test_df.merge(transactions_df, on=['store_nbr', 'date'], how='left')
test_df = test_df.merge(oil_df, on='date', how='left')
test_df = test_df.merge(holidays_df, on='date', how='left')

# Display the first few rows of the merged train and test data
print(train_df.head())
print(test_df.head())

# Extract date features
train_df['year'] = train_df['date'].dt.year
train_df['month'] = train_df['date'].dt.month
train_df['week'] = train_df['date'].dt.isocalendar().week
train_df['day_of_week'] = train_df['date'].dt.dayofweek

test_df['year'] = test_df['date'].dt.year
test_df['month'] = test_df['date'].dt.month
test_df['week'] = test_df['date'].dt.isocalendar().week
test_df['day_of_week'] = test_df['date'].dt.dayofweek

# Calculate rolling mean and standard deviation for sales in train data
train_df['rolling_mean_7'] = train_df.groupby(['store_nbr', 'family'])['sales'].transform(lambda x: x.rolling(window=7).mean())
train_df['rolling_std_7'] = train_df.groupby(['store_nbr', 'family'])['sales'].transform(lambda x: x.rolling(window=7).std())

# Fill NA values in rolling features
train_df['rolling_mean_7'] = train_df['rolling_mean_7'].fillna(0)
train_df['rolling_std_7'] = train_df['rolling_std_7'].fillna(0)

# Add these features to the test set (without the actual sales data)
test_df['rolling_mean_7'] = train_df.groupby(['store_nbr', 'family'])['sales'].transform(lambda x: x.rolling(window=7).mean()).fillna(0)
test_df['rolling_std_7'] = train_df.groupby(['store_nbr', 'family'])['sales'].transform(lambda x: x.rolling(window=7).std()).fillna(0)

print("train_df columns:", train_df.columns)
print("stores_df columns:", stores_df.columns)
print("transactions_df columns:", transactions_df.columns)

from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# Select features and target
features = ['store_nbr', 'family', 'onpromotion', 'transactions', 'dcoilwtico', 'year', 'month', 'week', 'day_of_week', 'rolling_mean_7', 'rolling_std_7']
target = 'sales'

# Encode categorical features
train_df['family'] = train_df['family'].astype('category').cat.codes
test_df['family'] = test_df['family'].astype('category').cat.codes

# Split the data into training and validation sets
X = train_df[features]
y = train_df[target]
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the model
model = XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, max_depth=5)
model.fit(X_train, y_train)

# Make predictions and evaluate the model
y_pred = model.predict(X_val)
rmse = np.sqrt(mean_squared_error(y_val, y_pred))
print(f'Validation RMSE: {rmse}')

# Make predictions on the test set
test_df['sales'] = model.predict(test_df[features])

# Create a submission dataframe
submission = test_df[['id', 'sales']]
submission.to_csv('submission.csv', index=False)

# Download the submission file
files.download('submission.csv')


