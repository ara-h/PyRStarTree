from numpy.random import default_rng
import pandas as pd

rng = default_rng()

# data = rng.uniform( low = -60.0, high = 60.0, size = (500,2) )
data = rng.normal( loc=0.0, scale = 32.0, size = (1000,2) )

df = pd.DataFrame(data)

df.to_csv('visual/generated_data.csv')
