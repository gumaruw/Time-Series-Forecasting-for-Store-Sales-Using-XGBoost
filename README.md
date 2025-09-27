# Store Sales Forecasting with XGBoost

- This project predicts store sales using the Kaggle Store Sales - Time Series Forecasting dataset. The approach combines structured feature engineering with the XGBoost Regressor for accurate forecasting.
- This project was developed as part of the Kaggle competition [Store Sales - Time Series Forecasting](https://www.kaggle.com/competitions/store-sales-time-series-forecasting).

## Workflow
- **Data Preparation:** Merge datasets (sales, stores, oil prices, holidays, transactions)
- **Feature Engineering:** Add calendar features and rolling statistics
- **Modeling:** Train and validate with XGBoost
- **Evaluation:** Model performance measured with RMSE

## Output
The final predictions are saved in submission.csv for Kaggle submission.

## Acknowledgements
- Dataset and competition by Kaggle
