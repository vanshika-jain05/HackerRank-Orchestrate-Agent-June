import pandas as pd

df = pd.read_csv("dataset/sample_claims.csv")

for i in range(5):
    print()
    print(df.iloc[i]["user_claim"])