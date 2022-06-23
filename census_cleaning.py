# -*- coding: utf-8 -*-

# Replication Script for data cleaning: "Historical Census of Monks and Nuns in Tibetan Monasteries, ca. 1642-1923"
# Repository doi: https://doi.org/10.7910/DVN/DUGC7Z
# Author: Rocco Bowman
# Contact: rbowman2@ucmerced.edu
# Article Citation: Ryavec, Karl E. and Rocco N. Bowman. 2021. "Comparing Historical Population Estimates with the
#    Monks and Nuns: What was the Clerical Proportion?", Revue d’Etudes Tibetaines. 

import os
import pandas as pd

# Setting Working Directory (set your own here)
os.chdir(r'C:\Users\Me\Documents\MainDirectory')
os.getcwd()

# Load Monk census data
CTMdata = pd.DataFrame(pd.read_excel(r"https://dataverse.harvard.edu/api/access/datafile/4789503"))
print (CTMdata)

# Remove unwanted columns
cols = [0,3,4,7]
CTMdata.drop(CTMdata.columns[cols],axis=1,inplace=True)

CTMdata.columns = ["gisid","dzong","monks","nuns"]

# Fill NA with zero for further math

CTMdata = CTMdata.fillna(0)

# Trim white space in dzong names that leads to one of them counting as two factor levels

CTMdata['dzong'] = CTMdata['dzong'].str.strip()

# Some consolidation of dzong names to better match GIS data
CTMdata = CTMdata.replace("Sreng dang E khul", "Nedong")
CTMdata = CTMdata.replace("U khul (Potala)", "Potala")
CTMdata = CTMdata.replace("Shigatse dang Rinchen", "Shigatse")
CTMdata = CTMdata.replace("Tsang khul dang Tod khul Rinpung khul", "Rinpung")
CTMdata = CTMdata.replace("Dakpo - Chokhorgyal", "Chokhorgyal")
CTMdata = CTMdata.replace("Dzonga / Saga", "Dzongka")

# Create a new column to hold a total of the two census columns of the original

CTMdata['totalcensus'] = CTMdata['monks'] + CTMdata['nuns']

# Write out the cleaned and updated version of the census data

CTMdata.to_csv(r'\Output\CTMdata_edit.csv', index = False)

# Load spatial point data for the fortresses (monastery area proxy)

spatial = pd.DataFrame(pd.read_csv(r'..\Data\fortress_coords.csv'))
print(spatial)

# Join CTM data to spatial points by name

join = pd.merge(CTMdata, spatial, on='dzong', how='outer', indicator= True)
cols = ['gisid_y','altgisid','xcoord','ycoord','_merge']
join.drop(cols,axis=1,inplace=True)
join.columns = ['gisid','dzong','monks','nuns','totalcensus']
# Providing an unique numeric id for each unique dzong name for aggregation
join = join.sort_values(['dzong'])
join['gisid'] = pd.factorize(join['dzong'])[0]


# Aggregate census data on dzong (one entry per unique id)

agg = join.groupby(
   ['gisid']
).agg(
    {
         'gisid':'first',
         'dzong': 'first',
         'monks': sum,
         'nuns': sum,
         'totalcensus': sum,    
    }
)


# Copy data for Shigatse to Rinchentse

agg.loc[agg['dzong'] == 'Rinchentse', 'totalcensus'] = agg.iloc[52,2]

# Make Phari "no data"

agg.loc[agg['dzong'] == 'Phari', 'totalcensus'] = 0

# Creating and filling a column for ecoregional grouping

agg['ecoregion'] = "Not Assigned"

agg.loc[(agg['dzong'] == 'Zhokha') | (agg['dzong'] == 'Gyamda') | (agg['dzong'] == 'Jomo') | (agg['dzong'] == 'Tsegang') | (agg['dzong'] == 'Kyimtong') | (agg['dzong'] == 'Kunam') | (agg['dzong'] == 'Gyamda') | (agg['dzong'] == 'Chokhorgyal') | (agg['dzong'] == 'Olkha') | (agg['dzong'] == 'Lhagyari') , 'ecoregion'] = 'Dokpo and Kongpo'

agg.loc[(agg['dzong'] == 'Dowa') | (agg['dzong'] == 'Senge') | (agg['dzong'] == 'Darma') | (agg['dzong'] == 'Lhakhang') | (agg['dzong'] == 'Tsona') | (agg['dzong'] == 'Lhuntse'), 'ecoregion'] = 'Lhokha'

agg.loc[(agg['dzong'] == 'Drigu'), 'ecoregion'] = 'Drigu'

agg.loc[(agg['dzong'] == 'Nakhartse'), 'ecoregion'] = 'Yamdrok Yumtso'

agg.loc[(agg['dzong'] == 'Nyemo') | (agg['dzong'] == 'Zadam') | (agg['dzong'] == 'Khartse') | (agg['dzong'] == 'Chushur') | (agg['dzong'] == 'Langtang') | (agg['dzong'] == 'Lhundrub') | (agg['dzong'] == 'Tagtse') | (agg['dzong'] == 'Malgung') | (agg['dzong'] == 'Potala') | (agg['dzong'] == 'Samye') | (agg['dzong'] == 'Gongkar') | (agg['dzong'] == 'Dol') | (agg['dzong'] == 'Chongye') | (agg['dzong'] == 'Nedong') | (agg['dzong'] == 'On') , 'ecoregion'] = 'U'

agg.loc[(agg['dzong'] == 'Dzongka') | (agg['dzong'] == 'Kyirong') | (agg['dzong'] == 'Nyanang') | (agg['dzong'] == 'Shelkar') | (agg['dzong'] == 'Tingkye') | (agg['dzong'] == 'Gampa') | (agg['dzong'] == 'Phari') | (agg['dzong'] == 'Ciblung'), 'ecoregion'] = 'Himalayan'

agg.loc[(agg['dzong'] == 'Shigatse') | (agg['dzong'] == 'Rinpung') | (agg['dzong'] == 'Lhunrab') | (agg['dzong'] == 'Panam') | (agg['dzong'] == 'Gyangtse') | (agg['dzong'] == 'Namling') | (agg['dzong'] == 'Gyatso') | (agg['dzong'] == 'Lhabu') | (agg['dzong'] == 'Tanak Rinchetse') | (agg['dzong'] == 'Shetongmon') | (agg['dzong'] == 'Puntsokling') | (agg['dzong'] == 'Sakya') | (agg['dzong'] == 'Lhatse') | (agg['dzong'] == 'Ngamring') | (agg['dzong'] == 'Lingkar') | (agg['dzong'] == 'Rinchentse'), 'ecoregion'] = 'Tsang'

# Remove remaining dzong with missing data

agg = agg.drop(agg.index[agg.ecoregion == 'Not Assigned'])

# Make Phari 0 given historical circumstances
agg.loc[(agg['dzong'] == 'Phari'), 'monks'] = 0

# Export final data for spatial join

agg.to_csv(r'..\Output\datajoin.csv', index = False)

print('Script completed!')



