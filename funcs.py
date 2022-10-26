from lib import *

def btr(df):
    df.loc[df['GolDrhRec'] == 'a positif', 'GolDrhRec'] = 'A Positif'
    df.loc[df['GolDrhRec'] == 'a negatif', 'GolDrhRec'] = 'A Negatif'
    df.loc[df['GolDrhRec'] == 'b positif', 'GolDrhRec'] = 'B Positif'
    df.loc[df['GolDrhRec'] == 'b negatif', 'GolDrhRec'] = 'B Negatif'
    df.loc[df['GolDrhRec'] == 'ab positif', 'GolDrhRec'] = 'AB Positif'
    df.loc[df['GolDrhRec'] == 'ab negatif', 'GolDrhRec'] = 'AB Negatif'
    df.loc[df['GolDrhRec'] == 'o positif', 'GolDrhRec'] = 'O Positif'
    df.loc[df['GolDrhRec'] == 'o negatif', 'GolDrhRec'] = 'O Negatif'
    return df

def changegol(df):
    df = df.loc[(df['Umur'] >= 16)]
    df['BloodType'] = df['BloodType'].str.lower()
    df.loc[df['BloodType'] == 'a positif', 'GolDrh'] = 'A Positif'
    df.loc[df['BloodType'] == 'a negatif', 'GolDrh'] = 'A Negatif'
    df.loc[df['BloodType'] == 'b positif', 'GolDrh'] = 'B Positif'
    df.loc[df['BloodType'] == 'b negatif', 'GolDrh'] = 'B Negatif'
    df.loc[df['BloodType'] == 'ab positif', 'GolDrh'] = 'AB Positif'
    df.loc[df['BloodType'] == 'ab negatif', 'GolDrh'] = 'AB Negatif'
    df.loc[df['BloodType'] == 'o positif', 'GolDrh'] = 'O Positif'
    df.loc[df['BloodType'] == 'o negatif', 'GolDrh'] = 'O Negatif'
    jenis = ['Triple', 'Quadruple', 'Single', 'Double Besar']
    df.JenisKantong = df.JenisKantong.str.title()
    df = df[df['JenisKantong'].isin(jenis)]
    return df


# RBC
def recency(df):
    df["TanggalDonor"] = pd.to_datetime(df["TanggalDonor"])
    tenddate = df.TanggalDonor.max()
    # tenddate = pd.to_datetime(date.today())
    copydf = df[['NomerDonor','TanggalDonor']]
    copydf.sort_values(by='TanggalDonor', ascending = True, inplace=True)
    copydf["Counter"] = copydf.groupby(['NomerDonor']).cumcount(ascending=False) + 1
    df_r = copydf.loc[copydf['Counter'] <= 3]
    df_r["TanggalDonor"] = pd.to_datetime(df_r["TanggalDonor"])
    df_r = df_r.drop_duplicates(["NomerDonor", "TanggalDonor"])
    df_r["Recency1"] = (tenddate - df_r['TanggalDonor']).dt.days
    df_r["Recency3"] = df_r["Recency1"]
    df_r1 = df_r.groupby(['NomerDonor'], as_index=False).agg({"Recency1": np.min, "Recency3": np.mean, "Counter":np.max})
    df_r1["Recency3"] = np.round(df_r1["Recency3"], decimals = 2)
    df_r1 = df_r1[['NomerDonor', 'Recency1', 'Recency3']]
    return df_r1

def frequency(df):
    df["TanggalDonor"] = pd.to_datetime(df["TanggalDonor"])
    df_f = df.sort_values(by="TanggalDonor",ascending=True) \
        .set_index('TanggalDonor') \
        .last("12M")
    df_f['TanggalDonor'] = df_f.index
    df_f1 = df_f.groupby(
        by=['NomerDonor'], as_index=False)['TanggalDonor'].count()
    df_f1.columns = ['NomerDonor', 'Frequency1']
    df_sorted = df.sort_values(by="TanggalDonor",ascending=True) \
        .set_index('TanggalDonor')
    df_sorted['TanggalDonor'] = df_sorted.index
    df_f2 = df_sorted.groupby(
        by=['NomerDonor'], as_index=False)['TanggalDonor'].count()
    df_f2.columns = ['NomerDonor', 'Frequency']
    df_f = pd.merge(df_f2, df_f1, on=['NomerDonor'], how='left').fillna(0)
    return df_f

def intervalmean(df):
    df.TanggalDonor = pd.to_datetime(df.TanggalDonor, errors='coerce')
    df["IVT"] = df.groupby(['NomerDonor'], as_index=False)["TanggalDonor"].transform(lambda x: abs(x.shift(1) - x))
    df["IVT"] = df["IVT"].dt.days
    df["Interval"] = df["IVT"]
    df_p = df.groupby(['NomerDonor'], as_index=False).agg({"IVT": [np.max,np.min],
                                                           "Interval": [np.mean]})
    df_p.columns = ["".join(col).strip() for col in df_p.columns.values]
    df_p = df_p.fillna(0)
    df_p = df_p[['NomerDonor', 'Intervalmean']]
    return df_p

def preprocrbc(df):
    df['TanggalDonor']= pd.to_datetime(df['TanggalDonor'])
    months = df["TanggalDonor"].dt.year * 12 + df["TanggalDonor"].dt.month  # series
    df["Bulan"] = months - min(months) + 1
    df = df.loc[(df['Bulan'] >= df.Bulan.max()-59) & (df['Bulan'] <= df.Bulan.max())]
    df['Bulan'] = df['Bulan']-48
    cdf = df[['NomerDonor', 'GolDrh']]
    cdf = cdf.drop_duplicates()
    cdf = pd.merge(cdf, recency(df), on=['NomerDonor'])
    cdf = pd.merge(cdf, frequency(df), on=['NomerDonor'])
    cdf = pd.merge(cdf, intervalmean(df), on=['NomerDonor'])
    return cdf

# RBC Implementation
def RBCimplementation(df):
    rbcdf = preprocrbc(df)
    for index, row in rbcdf.iterrows():
        if row.Recency1 <= 100 and row.Recency3 <= 182.0 and row.Intervalmean <= 120.0 and row.Frequency >= 3:
            rbcdf.at[index,'Category'] = 1
        elif row.Recency1 <= 182 and row.Recency3 <= 365.0 and row.Intervalmean <= 182.0 and row.Frequency >= 1:
            rbcdf.at[index,'Category'] = 2
        elif row.Recency1 <= 182:
            rbcdf.at[index,'Category'] = 3
        elif row.Recency1 <= 365:
            rbcdf.at[index,'Category'] = 4
        else:
            rbcdf.at[index,'Category'] = 5
    rbc = rbcdf[['NomerDonor', 'Category', 'Recency1']]
    rbc.rename(columns = {'Recency1':'Recency'}, inplace = True)
    return rbc


# ANN
def preprocann(df):
    df['TanggalDonor'] = pd.to_datetime(df['TanggalDonor'])
    months = df["TanggalDonor"].dt.year * 12 + \
             df["TanggalDonor"].dt.month  # series
    df["Bulan"] = months - min(months) + 1
    df = df.loc[(df['Bulan'] >= df.Bulan.max()-59)
                & (df['Bulan'] <= df.Bulan.max())]
    new_cols = pd.RangeIndex(df['Bulan'].min(), df['Bulan'].max()+1)
    res = (
        pd.crosstab(df['NomerDonor'], df['Bulan'])
            .reindex(columns=new_cols, fill_value=0)
    )
    max = df.Bulan.max()
    if max < 60:
        while (max < 60):
            max = max+1
            res.insert(0, 'a'+str(max), 0)
    return res

# prediction
def ANNpred(model, df):
    dfs = preprocann(df)
    preds = []
    for i, r in dfs.iterrows():
        # print(r)
        l = []
        l.append(r)
        pred = model(l)
        preds.append([pred.numpy()[0][0], pred.numpy()[0][1]])
    ndfp = pd.DataFrame(preds, columns=['No', 'Yes'])
    ndfp.loc[ndfp['No'] > ndfp['Yes'], 'Calon'] = 0
    ndfp.loc[ndfp['Yes'] >= ndfp['No'], 'Calon'] = 1
    # # calon -> 1, bkn -> 0
    dfs['Calon'] = ndfp['Calon'].values
    dfs['NomerDonor'] = dfs.index
    dfs = dfs[['NomerDonor', 'Calon']]
    dfs = dfs.rename_axis(index=None, columns=None)

    simpen = df.groupby(['NomerDonor', 'NamaDonor', 'JKel', 'GolDrh'], as_index=False,
                        sort=False)['TanggalDonor', 'Umur'].max()
    global annd
    annd = pd.merge(dfs, simpen, on='NomerDonor', how='left')
    # annd['TanggalDonor'] = pd.to_datetime(annd['TanggalDonor'])
    # today = pd.to_datetime(date.today())
    # annd['Recency'] = (today - annd['TanggalDonor']).dt.days
    ann = annd[['NomerDonor', 'Calon']]
    return ann

# classification
def ANNclass(model, df):
    dfs = preprocann(df)
    preds = []
    for i, r in dfs.iterrows():
        # print(r)
        l = []
        l.append(r)
        pred = model(l)
        preds.append([pred.numpy()[0][0], pred.numpy()[0][1], pred.numpy()[0][2], pred.numpy()[0][3], pred.numpy()[0][4]])
    ndfd = pd.DataFrame(preds, columns = ['Cat1', 'Cat2', 'Cat3', 'Cat4', 'Cat5'])
    ndfd['Category'] = (ndfd['Cat1']*0.2) + (ndfd['Cat2']*0.2) + (ndfd['Cat3']*0.2) + (ndfd['Cat4']*0.2) + (ndfd['Cat5']*0.2)
    oldmax = ndfd.Category.max()
    oldmin = ndfd.Category.min()
    OldRange = (oldmax - oldmin)
    NewRange = 4
    ndfd['Category'] = ((((ndfd['Category'] - oldmin) * NewRange)) / OldRange) + 1
    hasil = dfs
    hasil['Category'] = ndfd['Category'].values
    hasil['NomerDonor'] = hasil.index
    hasil = hasil[['NomerDonor', 'Category']]
    hasil = hasil.rename_axis(index=None, columns=None)
    ann = hasil
    simpen = df.groupby(['NomerDonor'], as_index=False, sort=False)['TanggalDonor'].max()
    annd = pd.merge(ann, simpen, on='NomerDonor', how='left')
    today = pd.to_datetime(date.today())
    annd['Recency'] = (today - annd['TanggalDonor']).dt.days
    ann = annd[['NomerDonor', 'Category', 'Recency']]
    return ann

# Read the model
modelpred = hub.load('model/modelpred')
modelclass = hub.load('model/modelann')
modelannrbc = hub.load('model/modelannrbc90')

# rating
def rating(df):
    donor = df[['NomerDonor', 'TanggalDonor',
                'GolDrh', 'JKel', 'Lokasi', 'Umur']]
    donor = donor.drop_duplicates()
    donor.loc[donor['Umur'] >= 65, 'AgeCat'] = 0
    donor.loc[donor['Umur'] < 65, 'AgeCat'] = 3
    donor.loc[donor['JKel'] == 'Pria', 'JKCat'] = 1
    donor.loc[donor['JKel'] == 'Wanita', 'JKCat'] = 0
    lok = 'UTD PMI SURABAYA'
    location = donor.query(str("Lokasi == '") +
        lok + "'").groupby('NomerDonor').count()
    location = location[['GolDrh']]
    location.columns = ['Loc']
    location['NomerDonor'] = location.index
    location = location.rename_axis(index=None, columns=None)
    donor = pd.merge(donor, location, on=['NomerDonor'])
    location = donor.groupby('NomerDonor').count()
    location = location[['GolDrh']]
    location.columns = ['Freq']
    location['NomerDonor'] = location.index
    location = location.rename_axis(index=None, columns=None)
    donor = pd.merge(donor, location, on=['NomerDonor'])
    donor['Loc'] = donor['Loc']/donor['Freq']
    donor = donor[['NomerDonor', 'TanggalDonor',
                   'GolDrh', 'AgeCat', 'JKCat', 'Loc']]
    return donor

# rate
def ratenopred(donor, classified):
    rated = pd.merge(donor, classified, on=['NomerDonor'])
    rated.loc[rated['Recency'] <= 60, 'Rating'] = 0
    rated.loc[rated['Recency'] > 60, 'Rating'] = ((6 - rated['Category']*rated['Loc']) + rated['AgeCat'] + rated['JKCat'])
    rated = rated[['NomerDonor', 'GolDrh', 'Rating']]
    oldmax = rated.Rating.max()
    oldmin = rated.Rating.min()
    OldRange = (oldmax - oldmin)
    NewRange = 4
    rated['Rating'] = ((((rated['Rating'] - oldmin) * NewRange)) / OldRange) + 1
    # rated['NomerDonor'] = rated.NomerDonor.astype(int)
    return rated


def ratewpred (donor, classified):
    rated = pd.merge(donor, classified, on=['NomerDonor'])
    rated.loc[rated['Recency'] <= 60, 'Rating'] = 0
    rated.loc[(rated['Recency'] > 60) & (rated['Calon'] == 0), 'Rating'] = ((6 - rated['Category'] * rated['Loc']) + rated['AgeCat'] + rated['JKCat'])
    rated.loc[(rated['Recency'] > 60) & (rated['Calon'] == 1), 'Rating'] = ((6 - rated['Category'] * 3 * rated['Loc']) + rated['AgeCat'] + rated['JKCat'])
    rated = rated[['NomerDonor', 'GolDrh', 'Rating']]
    oldmax = rated.Rating.max()
    oldmin = rated.Rating.min()
    OldRange = (oldmax - oldmin)
    NewRange = 4
    rated['Rating'] = ((((rated['Rating'] - oldmin) * NewRange)) / OldRange) + 1
    # rated['NomerDonor'] = rated.NomerDonor.astype(int)
    return rated

def _initialize_spark() -> SparkSession:
    """Create a Spark Session for Streamlit app"""
    conf = SparkConf().setAppName("skripsiwid").setMaster("local")
    spark = SparkSession.builder.config(conf=conf).getOrCreate()
    return spark, spark.sparkContext

def alsranking(rated):
    spark, sc = _initialize_spark()
    jum = rated.NomerDonor.nunique()
    annsdf = spark.createDataFrame(rated)

    indexer = StringIndexer(inputCol="NomerDonor", outputCol="NomerDonorIndex")
    transformed = indexer.fit(annsdf).transform(annsdf)

    indexer = StringIndexer(inputCol="GolDrh", outputCol="GolDrhIndex")
    transformed = indexer.fit(transformed).transform(transformed)

    als1=ALS(maxIter=10,regParam=0.01,rank=25,userCol="GolDrhIndex",itemCol="NomerDonorIndex",ratingCol="Rating",coldStartStrategy="drop",nonnegative=True)
    models=als1.fit(transformed)

    trans = transformed.toPandas()
    recs=models.recommendForAllUsers(150).toPandas()
    coba = pd.DataFrame()

    dfr = pd.DataFrame()
    for r in recs.itertuples():
        l = []
        c=1
        for i in r[2]:
            l.append([c, r[1], i[0], i[1]])
            c+=1
            # print()
        dd = pd.DataFrame(l)
        dfr = dfr.append(dd)
    dfr.columns = ['Ranking', 'GolDrhIndex', 'NomerDonorIndex', 'Rating']

    nd = trans[['NomerDonorIndex', 'NomerDonor']]
    nd = nd.drop_duplicates()
    comb = pd.merge(dfr, nd, on=['NomerDonorIndex'], how='left')
    bt = trans[['GolDrhIndex', 'GolDrh']]
    bt = bt.drop_duplicates()
    comb = pd.merge(comb, bt, on=['GolDrhIndex'], how='left')
    comb = comb[['Ranking', 'NomerDonor', 'GolDrh', 'Rating']]
    comb.rename(columns = {'GolDrh':'GolDrhRec'}, inplace = True)
    comb = btr(comb)
    return comb

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'})
    worksheet.set_column('A:A', None, format1)
    writer.save()
    processed_data = output.getvalue()
    return processed_data