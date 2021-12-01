import pandas as pd
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

predict_count = 5
figure_size = 8
dataset = pd.read_csv('game_stats.csv')[['is_win', 'score', 'time']]
dataset, test_data = dataset.iloc[:-predict_count], dataset.iloc[-predict_count:]

x_col = ['is_win', 'time']
X = dataset[x_col]
Y = dataset.score

lose_dataset = dataset[dataset.is_win == False]

pca = PCA(n_components=2, random_state=42)
fit_x, fit_y = pca.fit_transform(X, Y).T

fit_lose_x, _ = pca.fit_transform(lose_dataset[x_col]).T

figure = plt.figure(figsize=(figure_size, figure_size))
m2 = plt.scatter(fit_lose_x, lose_dataset.score, figure_size, "red")
plt.show()

model = linear_model.LinearRegression()

model.fit(X, Y)

y_prediction_line_lose = model.predict(lose_dataset[x_col])

fit_prediction_lose_X, fit_prediction_lose_Y = pca.fit_transform(lose_dataset[x_col], pd.DataFrame(y_prediction_line_lose)[0]).T

figure = plt.figure(figsize=(figure_size, figure_size))
m2 = plt.scatter(fit_lose_x, lose_dataset.score, figure_size, color="red")
plt.plot(fit_prediction_lose_X, y_prediction_line_lose, color="red", linewidth=2, label="Prediction")
plt.show()

output_grid = pd.DataFrame(columns=['is_win', 'score', 'time', 'predicted_score'])

output_grid.is_win = test_data.is_win
output_grid.time = test_data.time
output_grid.score = test_data.score 
output_grid.predicted_score = output_grid.apply(lambda row: model.predict(pd.DataFrame(columns = x_col).append(row[x_col]))[0], axis=1)

print(output_grid)
