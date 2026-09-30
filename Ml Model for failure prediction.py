import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

# Loading of healthy satellite structure data
healthy_data = pd.read_csv(add healthy data file.csv')

# Loading of unhealthy satellite structure data
unhealthy_data = pd.read_csv(add unhealthy data file.csv')

# Extracting the features of data of healthy data
healthy_data['current_voltage'] = healthy_data['current'] * healthy_data['voltage']
healthy_data['stress_strain'] = healthy_data['stress'] * healthy_data['strain']

# Extracting the features of data of un-healthy data
unhealthy_data['current_voltage'] = unhealthy_data['current'] * unhealthy_data['voltage']
unhealthy_data['stress_strain'] = unhealthy_data['stress'] * unhealthy_data['strain']

# Extract features (including gyroscopic values)
features = [
    'time',
    'current',
    'voltage',
    'stress',
    'strain',
    'gx',
    'gy',
    'gz',
    'current_voltage',
    'stress_strain'
]

# Standardize the healthy data
scaler = StandardScaler()
X_healthy_scaled = scaler.fit_transform(healthy_data[features])

# Standardize the unhealthy data using the same scaler
X_unhealthy_scaled = scaler.transform(unhealthy_data[features])

# Hyperparameter tuning for Isolation Forest
param_grid_if = {
    'n_estimators': [100, 200, 300],
    'max_samples': [0.5, 0.75],
    'contamination': [0.05, 0.1],
    'max_features': [0.5, 0.90]
}

grid_search_if = GridSearchCV(
    IsolationForest(random_state=42),
    param_grid_if,
    scoring='f1',
    cv=5,
    n_jobs=-1
)

grid_search_if.fit(X_healthy_scaled)
best_model_if = grid_search_if.best_estimator_

# Hyperparameter tuning for Local Outlier Factor (LOF)
param_grid_lof = {
    'n_neighbors': [20, 30, 40],
    'contamination': [0.05, 0.1]
}

grid_search_lof = GridSearchCV(
    LocalOutlierFactor(),
    param_grid_lof,
    scoring='f1',
    cv=5,
    n_jobs=-1
)

grid_search_lof.fit(X_healthy_scaled)
best_model_lof = grid_search_lof.best_estimator_

# Train the best Isolation Forest model on the healthy data
best_model_if.fit(X_healthy_scaled)

# Train the best LOF model on the healthy data
best_model_lof.fit(X_healthy_scaled)

# Use the models to predict anomalies in the unhealthy data
anomaly_scores_if_unhealthy = best_model_if.decision_function(X_unhealthy_scaled)
anomalies_if_unhealthy = best_model_if.predict(X_unhealthy_scaled)

anomaly_scores_lof_unhealthy = best_model_lof.negative_outlier_factor_
anomalies_lof_unhealthy = best_model_lof.fit_predict(X_unhealthy_scaled)

# Anomalies are marked as -1, normal data points are marked as 1
unhealthy_data['anomaly_if'] = anomalies_if_unhealthy
unhealthy_data['anomaly_score_if'] = anomaly_scores_if_unhealthy
unhealthy_data['anomaly_lof'] = anomalies_lof_unhealthy
unhealthy_data['anomaly_score_lof'] = anomaly_scores_lof_unhealthy

# Print the anomalies detected by Isolation Forest for unhealthy data
anomalies_detected_if_unhealthy = unhealthy_data[
    unhealthy_data['anomaly_if'] == -1
]

print("Anomalies detected by Isolation Forest (Unhealthy Data):")
print(anomalies_detected_if_unhealthy)

# Print the anomalies detected by Local Outlier Factor for unhealthy data
anomalies_detected_lof_unhealthy = unhealthy_data[
    unhealthy_data['anomaly_lof'] == -1
]

print("Anomalies detected by Local Outlier Factor (Unhealthy Data):")
print(anomalies_detected_lof_unhealthy)

# Plotting time series of features for healthy and unhealthy data
fig = make_subplots(
    rows=4,
    cols=1,
    subplot_titles=('Current', 'Voltage', 'Stress', 'Strain'),
    shared_xaxes=True
)

fig.add_trace(
    go.Scatter(
        x=healthy_data['time'],
        y=healthy_data['current'],
        mode='lines',
        name='Current (Healthy)'
    ),
    row=1,
    col=1
)

fig.add_trace(
    go.Scatter(
        x=unhealthy_data['time'],
        y=unhealthy_data['current'],
        mode='lines',
        name='Current (Unhealthy)'
    ),
    row=1,
    col=1
)

fig.add_trace(
    go.Scatter(
        x=healthy_data['time'],
        y=healthy_data['voltage'],
        mode='lines',
        name='Voltage (Healthy)'
    ),
    row=2,
    col=1
)

fig.add_trace(
    go.Scatter(
        x=unhealthy_data['time'],
        y=unhealthy_data['voltage'],
        mode='lines',
        name='Voltage (Unhealthy)'
    ),
    row=2,
    col=1
)

fig.add_trace(
    go.Scatter(
        x=healthy_data['time'],
        y=healthy_data['stress'],
        mode='lines',
        name='Stress (Healthy)'
    ),
    row=3,
    col=1
)

fig.add_trace(
    go.Scatter(
        x=unhealthy_data['time'],
        y=unhealthy_data['stress'],
        mode='lines',
        name='Stress (Unhealthy)'
    ),
    row=3,
    col=1
)

fig.add_trace(
    go.Scatter(
        x=healthy_data['time'],
        y=healthy_data['strain'],
        mode='lines',
        name='Strain (Healthy)'
    ),
    row=4,
    col=1
)

fig.add_trace(
    go.Scatter(
        x=unhealthy_data['time'],
        y=unhealthy_data['strain'],
        mode='lines',
        name='Strain (Unhealthy)'
    ),
    row=4,
    col=1
)

fig.update_layout(
    title_text='Time Series of Features (Healthy vs Unhealthy Data)',
    height=1000,
    width=800,
    showlegend=True
)

fig.update_xaxes(title_text='Time', row=4, col=1)
fig.update_yaxes(title_text='Current', row=1, col=1)
fig.update_yaxes(title_text='Voltage', row=2, col=1)
fig.update_yaxes(title_text='Stress', row=3, col=1)
fig.update_yaxes(title_text='Strain', row=4, col=1)

fig.show()

# Plotting anomaly scores with histograms for unhealthy data
fig = make_subplots(
    rows=2,
    cols=1,
    subplot_titles=(
        "Isolation Forest Anomaly Scores (Unhealthy Data)",
        "Local Outlier Factor Anomaly Scores (Unhealthy Data)"
    )
)

fig.add_trace(
    go.Histogram(
        x=anomaly_scores_if_unhealthy,
        nbinsx=50,
        histnorm='probability',
        name='Isolation Forest'
    ),
    row=1,
    col=1
)

fig.add_trace(
    go.Histogram(
        x=anomaly_scores_lof_unhealthy,
        nbinsx=50,
        histnorm='probability',
        name='Local Outlier Factor'
    ),
    row=2,
    col=1
)

fig.update_layout(
    title_text='Anomaly Score Distributions (Unhealthy Data)',
    height=800,
    width=800,
    showlegend=True
)

fig.update_xaxes(title_text='Anomaly Score', row=1, col=1)
fig.update_xaxes(title_text='Anomaly Score', row=2, col=1)
fig.update_yaxes(title_text='Probability', row=1, col=1)
fig.update_yaxes(title_text='Probability', row=2, col=1)

fig.show()
