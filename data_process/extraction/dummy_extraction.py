__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import numpy as np
import matplotlib.pyplot as plt

# RiBuild Modules

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def compute_cdf(mu, sigma):
    curve = np.random.normal(mu, sigma, 200)
    hist, edges = np.histogram(curve, density=True, bins=50)
    dx = edges[1] - edges[0]
    cdf = np.cumsum(hist) * dx

    return edges[1:], cdf


# Filter 1
x1, y1 = compute_cdf(3, 0.5)
a1 = np.nonzero(x1 < 2.0)
height1 = y1[a1][-1]
print(height1)
plt.figure()
plt.plot(x1, y1)
plt.xlim(0, 4)
plt.title('Filter 1')
plt.xlabel('Mould Index')
plt.ylabel('Cumulated Probability')
plt.axvline(x=2.0, color='k', linestyle=':', linewidth=1)
plt.axhline(y=height1, color='k', linestyle=':', linewidth=1)
plt.show()

# Filter 2
x2, y2 = compute_cdf(2, 1)
a2 = np.nonzero(x2 < 2.0)
height2 = y2[a2][-1]
print(height2)
plt.figure()
plt.plot(x2, y2)
plt.xlim(0, 4)
plt.title('Filter 2')
plt.xlabel('Mould Index')
plt.ylabel('Cumulated Probability')
plt.axvline(x=2.0, color='k', linestyle=':', linewidth=1)
plt.axhline(y=height2, color='k', linestyle=':', linewidth=1)
plt.show()

# Filter 3
x3, y3 = compute_cdf(1.50, 0.3)
a3 = np.nonzero(x3 < 2.0)
height3 = y3[a3][-1]
print(height3)
plt.figure()
plt.plot(x3, y3)
plt.xlim(0, 4)
plt.title('Filter 3')
plt.xlabel('Mould Index')
plt.ylabel('Cumulated Probability')
plt.axvline(x=2.0, color='k', linestyle=':', linewidth=1)
plt.axhline(y=height3, color='k', linestyle=':', linewidth=1)
plt.show()
