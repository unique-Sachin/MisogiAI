import pandas as pd
import seaborn as sns
import matplotlib as plt


df = pd.read_csv("laptop.csv")

df.drop(columns=["Unnamed: 0"], inplace=True)




df.drop_duplicates(inplace=True)
# print(df.duplicated().sum())

describe = df.describe()

displot = sns.displot(df["Price"]) # type: ignore

company_price = df[["Company","Price"]].groupby("Company").mean().reset_index().sort_values(by="Price", ascending=False)

# print(df[["Company","Price"]].groupby("Company").mean().reset_index())

sns.barplot(x="Company", y="Price", data=company_price)

print(plt.pyplot.xticks(rotation=90)) # type: ignore

# print(df[["Company"]].value_counts())

(df["Ram"].apply(lambda x: x[:-2]))
print(df["Weight"].apply(lambda x: x[:-2]))

df[["Ram","Weight","Price"]].corr()

sns.scatterplot(x="Weight", y="Price", data=df[["Ram","Weight","Price"]])

ram_data = df[["Ram","Price"]].groupby("Ram").mean().reset_index().sort_values(by="Price", ascending=False)

sns.barplot(x="Ram", y="Price", data=ram_data)

df["ScreenResolution"].value_counts()

def fetch_screen_type(value):
    if "Touchscreen" in value:
        return "Touchscreen"
    elif "IPS" in value:
        return "IPS"
    else:
        return "Others"

df["screen"] = df["ScreenResolution"].apply(fetch_screen_type)
df["screen"].value_counts()

df[["screen","Price"]].groupby("screen").mean().reset_index()

def fetch_screen_size(value):
    return value.split(" ")[-1]

df["screen_size"] = df["ScreenResolution"].apply(fetch_screen_size)
df["screen_size"].value_counts()

df[["screen_size","Price"]].groupby("screen_size").mean().reset_index()


df["x_size"] = df["screen_size"].apply(lambda x: x.split("x")[0])
df["y_size"] = df["screen_size"].apply(lambda x: x.split("x")[1])

df["diagonal_pixels"] = ((df["x_size"].astype(int) ** 2 + df["y_size"].astype(int) ** 2) ** 0.5)
df["ppi"] = df["diagonal_pixels"] / df["Inches"]

df["Inches"] = df["diagonal_pixels"] / df["ppi"]

df[["Inches","diagonal_pixels","ppi","Price"]].corr()

sns.scatterplot(x="ppi", y="Price", data=df)

sns.lineplot(x="ppi", y="Price", data=df)

df["OpSys"].value_counts()

def fetch_os(value):
    if "windows" in value.lower():
        return "Windows"
    elif "mac" in value.lower():
        return "MacOS"
    elif "linux" in value.lower():
        return "Linux"
    else:
        return "Others"

df["OS"] = df["OpSys"].apply(fetch_os)

df[["OS","Price"]].groupby("OS").mean().reset_index().sort_values(by="Price", ascending=False)

