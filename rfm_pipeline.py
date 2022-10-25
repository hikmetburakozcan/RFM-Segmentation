import pandas as pd
from datetime import timedelta

df = pd.read_excel("/Users/hikmetburakozcan/Data Science Documents/dsmlbc_9_abdulkadir/Moduls/2_CRM_Analitigi/Datasets/online_retail_II.xlsx", sheet_name="Year 2009-2010")
df = df.copy()

def get_info_about_dataset(dataframe):
    print(39*"#", "THE FIRST 5 OBSERVATIONS IN THE DATASET", 39*"#", dataframe.head(), sep='\n', end = '\n\n')
    print(38*"#", "THE LAST 5 OBSERVATIONS IN THE DATASET", 38*"#", dataframe.tail(), sep='\n', end = '\n\n')
    print(40*"#", f"THE TOTAL NUMBER OF OBSERVATIONS: {dataframe.shape[0]}", 40*"#", sep='\n', end = '\n\n')
    print(26*"#", f"THE NUMBER OF VARIABLES: {dataframe.shape[1]}", 26*"#", sep='\n', end = '\n\n')
    print(47*"#", "THE NUMBER OF MISSING VALUES FOR EACH VARIABLES", 47*"#", dataframe.isnull().sum(), sep='\n', end='\n\n')
    print(22*"#", "THE TYPES OF VARIABLES", 22*"#", dataframe.dtypes, sep='\n', end = '\n\n')
    print(45*"#", "DESCRIPTIVE STATISTICS OF NUMERICAL VARIABLES", 45*"#", dataframe.describe(percentiles=[0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99]).T, sep='\n', end='\n\n')
    print(47*"#", "DESCRIPTIVE STATISTICS OF CATEGORICAL VARIABLES", 47*"#", dataframe.describe(include=object).T, sep='\n', end ='\n\n')

def rfm(dataframe, analysis_date=df["InvoiceDate"].max() + timedelta(days=2)):
    #Preparing the dataset
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.drop(dataframe[dataframe["Invoice"].str.contains("C", na=False)].index, axis=0, inplace=True)
    dataframe.drop(dataframe[(dataframe['Quantity'] < 0)].index, axis=0, inplace=True)
    dataframe.dropna(inplace=True, axis=0)

    #Calculation of RFM metrics
    rfm_df = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda x: (analysis_date - x.max()).days,
                                                'Invoice': lambda x: x.nunique(),
                                                "TotalPrice": lambda x: x.sum()})

    rfm_df.columns = ['recency', 'frequency', "monetary"]

    #Calculation of RFM scores
    rfm_df["recency_score"] = pd.qcut(rfm_df['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm_df["frequency_score"] = pd.qcut(rfm_df["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm_df["monetary_score"] = pd.qcut(rfm_df['monetary'], 5, labels=[1, 2, 3, 4, 5])
    rfm_df["RFM_SCORE"] = rfm_df['recency_score'].astype(str) + rfm_df['frequency_score'].astype(str)

    #Defining segments
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm_df['segment'] = rfm_df['RFM_SCORE'].replace(seg_map, regex=True)

    #Saving customers' info
    rfm_df[["recency", "frequency", "monetary", "segment"]].to_csv("rfm.csv")
    return rfm_df[["recency", "frequency", "monetary", "segment"]]

if __name__ == "__main__":
    get_info_about_dataset(df)
    rfm(df, analysis_date=df["InvoiceDate"].max() + timedelta(days=2))
