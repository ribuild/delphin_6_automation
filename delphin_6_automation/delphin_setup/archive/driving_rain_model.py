__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import PolynomialFeatures
from sklearn.neighbors import KNeighborsRegressor
from sklearn.externals import joblib

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger()

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


catch_ratio = np.load(os.path.join(os.path.dirname(__file__), 'catch_ratio.npy'))

height = np.array([0.0, 5.0, 8.0, 8.5, 9.0, 9.25, 9.5, 9.75, 10.0])
horizontal_rain_intensity = np.array(
    [0.0, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0])
width = np.array([0.0, 2.5, 5.0, 7.5, 10.0])
wind_speed = np.array([0, 1, 2, 3, 4, 5, 6, 8, 10])

print('Catch Ratio shape:', catch_ratio.shape)
print('Wind Speed:', len(wind_speed))
print('Rain:', len(horizontal_rain_intensity))
print('Height:', len(height))
print('Width:', len(width))

catch_ratio_list = []
height_list = []
horizontal_rain_intensity_list = []
width_list = []
wind_speed_list = []

for wind_index in range(len(wind_speed)):

    for rain_index in range(len(horizontal_rain_intensity)):

        for height_index in range(len(height)):

            for width_index in range(len(width)):
                catch_ratio_list.append(catch_ratio[wind_index, rain_index, height_index, width_index])
                height_list.append(height[height_index])
                horizontal_rain_intensity_list.append(horizontal_rain_intensity[rain_index])
                wind_speed_list.append(wind_speed[wind_index])
                width_list.append(width[width_index])

print('')
print('Catch Ratio:', len(catch_ratio_list))
print('Height:', len(height_list))
print('Rain:', len(horizontal_rain_intensity_list))
print('Wind Speed:', len(wind_speed_list))
print('Width:', len(width_list))
print('')

y_data = np.array(catch_ratio_list)
x_data = np.vstack(np.array([wind_speed_list, horizontal_rain_intensity_list, height_list, width_list]).T)
X_train, X_test, y_train, y_test = train_test_split(x_data, y_data, random_state=0)


# Models

linreg = linear_model.LinearRegression(normalize=True)
linreg.fit(X_train, y_train)

print('Linear Model')
print('linear model intercept: {}'.format(linreg.intercept_))
print('linear model coeff:\n{}'.format(linreg.coef_))
print('R-squared score (training): {:.3f}'.format(linreg.score(X_train, y_train)))
print('R-squared score (test): {:.3f}'.format(linreg.score(X_test, y_test)))
print('')

linridge = linear_model.Ridge(alpha=20.0).fit(X_train, y_train)

print('Ridge Model')
print('ridge regression linear model intercept: {}'.format(linridge.intercept_))
print('ridge regression linear model coeff:\n{}'.format(linridge.coef_))
print('R-squared score (training): {:.3f}'.format(linridge.score(X_train, y_train)))
print('R-squared score (test): {:.3f}'.format(linridge.score(X_test, y_test)))
print('Number of non-zero features: {}'.format(np.sum(linridge.coef_ != 0)))
print('')

scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

linridge_normal = linear_model.Ridge(alpha=20.0).fit(X_train_scaled, y_train)

print('Ridge Model Normalized')
print('ridge regression linear model intercept: {}'.format(linridge_normal.intercept_))
print('ridge regression linear model coeff:\n{}'.format(linridge_normal.coef_))
print('R-squared score (training): {:.3f}'.format(linridge_normal.score(X_train_scaled, y_train)))
print('R-squared score (test): {:.3f}'.format(linridge_normal.score(X_test_scaled, y_test)))
print('Number of non-zero features: {}'.format(np.sum(linridge_normal.coef_ != 0)))
print('')

poly = PolynomialFeatures(degree=2)
X_F1_poly = poly.fit_transform(x_data)

X_train, X_test, y_train, y_test = train_test_split(X_F1_poly, y_data, random_state=0)
linreg_poly = linear_model.LinearRegression().fit(X_train, y_train)

print('(poly deg 2) linear model coeff (w):\n{}'.format(linreg_poly.coef_))
print('(poly deg 2) linear model intercept (b): {:.5f}'.format(linreg_poly.intercept_))
print('(poly deg 2) R-squared score (training): {:.5f}'.format(linreg_poly.score(X_train, y_train)))
print('(poly deg 2) R-squared score (test): {:.5f}\n'.format(linreg_poly.score(X_test, y_test)))

print('\nAddition of many polynomial features often leads to\n\
overfitting, so we often use polynomial features in combination\n\
with regression that has a regularization penalty, like ridge\n\
regression.\n')

linridge_poly = linear_model.Ridge().fit(X_train, y_train)

print('(poly deg 2 + ridge) linear model coeff (w):\n{}'.format(linridge_poly.coef_))
print('(poly deg 2 + ridge) linear model intercept (b): {:.5f}'.format(linridge_poly.intercept_))
print('(poly deg 2 + ridge) R-squared score (training): {:.5f}'.format(linridge_poly.score(X_train, y_train)))
print('(poly deg 2 + ridge) R-squared score (test): {:.5f}'.format(linridge_poly.score(X_test, y_test)))
print('')

poly_3 = PolynomialFeatures(degree=3)
X_poly_3 = poly.fit_transform(x_data)

X_train, X_test, y_train, y_test = train_test_split(X_poly_3, y_data, random_state=0)
poly_reg_3 = linear_model.LinearRegression().fit(X_train, y_train)

print('(poly deg 3) linear model coeff (w):\n{}'.format(poly_reg_3.coef_))
print('(poly deg 3) linear model intercept (b): {:.5f}'.format(poly_reg_3.intercept_))
print('(poly deg 3) R-squared score (training): {:.5f}'.format(poly_reg_3.score(X_train, y_train)))
print('(poly deg 3) R-squared score (test): {:.5f}\n'.format(poly_reg_3.score(X_test, y_test)))

ridge_poly_3 = linear_model.Ridge().fit(X_train, y_train)

print('(poly deg 3 + ridge) linear model coeff (w):\n{}'.format(ridge_poly_3.coef_))
print('(poly deg 3 + ridge) linear model intercept (b): {:.5f}'.format(ridge_poly_3.intercept_))
print('(poly deg 3 + ridge) R-squared score (training): {:.5f}'.format(ridge_poly_3.score(X_train, y_train)))
print('(poly deg 3 + ridge) R-squared score (test): {:.5f}'.format(ridge_poly_3.score(X_test, y_test)))
print('')

X_train, X_test, y_train, y_test = train_test_split(x_data, y_data, random_state=0)

knn_reg5_uni = KNeighborsRegressor(n_neighbors=5).fit(X_train, y_train)

print('K-nearest regression (5 neighbors)')
print(knn_reg5_uni.predict(X_test))
print('R-squared train score: {:.5f}'.format(knn_reg5_uni.score(X_train, y_train)))
print('R-squared test score: {:.5f}'.format(knn_reg5_uni.score(X_test, y_test)))
print('')

knn_reg5_dis = KNeighborsRegressor(n_neighbors=5, weights='distance').fit(X_train, y_train)

print('K-nearest regression (5 neighbors, Weights = Distance)')
print(knn_reg5_dis.predict(X_test))
print('R-squared train score: {:.5f}'.format(knn_reg5_dis.score(X_train, y_train)))
print('R-squared test score: {:.5f}'.format(knn_reg5_dis.score(X_test, y_test)))
print('')

knn_reg3_uni = KNeighborsRegressor(n_neighbors=3).fit(X_train, y_train)

print('K-nearest regression (3 neighbors)')
print(knn_reg3_uni.predict(X_test))
print('R-squared train score: {:.5f}'.format(knn_reg3_uni.score(X_train, y_train)))
print('R-squared test score: {:.5f}'.format(knn_reg3_uni.score(X_test, y_test)))


knn_reg3_dis = KNeighborsRegressor(n_neighbors=3, weights='distance').fit(X_train, y_train)

print('K-nearest regression (3 neighbors, Weights = Distance)')
print(knn_reg3_dis.predict(X_test))
print('R-squared train score: {:.5f}'.format(knn_reg3_dis.score(X_train, y_train)))
print('R-squared test score: {:.5f}'.format(knn_reg3_dis.score(X_test, y_test)))

# Save final model
filename_kn = 'k_nearest_3_model.joblib'
#joblib.dump(knn_reg3_uni, filename_kn)
