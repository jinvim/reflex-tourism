# %%
import pandas as pd
import numpy as np
from utills import pad_fips, get_region

DATA_PATH = "../source/ADVAN/processed/us-vst/"
FIPS_PATH = "../resources/fips2021.csv"
OUTPUT_FILE = "../data/reflex1.0.csv"

# %%
# read processed data of the given years
def read_data(years):
    keep_cols = ['dst', 'org', 'flow', 'date']
    dfs = [pd.read_csv(f"{DATA_PATH}{year}.csv.gz", compression='gzip', dtype={'flow': 'Int64'}, usecols=keep_cols) for year in years]
    return pd.concat(dfs).reset_index(drop=True)


# generate lits of fips to keep
def gen_keep_fips(territories=False, contiguous=True):
    fips = pd.read_csv(FIPS_PATH)
    # exclude the territories
    if not territories:
        fips = fips[fips['STATEFP'] < 60]
    # keep contiguos US
    if contiguous:
        # Alaska == 2, Hawaii == 15
        fips = fips[fips['STATEFP'] != 2]
        fips = fips[fips['STATEFP'] != 15]

    return fips['GEOID'].unique()


# clean the data for calculating REFLEX index
def clean_data(df, fips):
    # exclude travel to self
    clean_df = df[df['dst'] != df['org']].copy()

    # Prepare the data for processing
    clean_df['date'] = pd.to_datetime(clean_df['date'])

    # filter the data
    clean_df = clean_df[clean_df['dst'].isin(fips)]
    clean_df = clean_df[clean_df['org'].isin(fips)]
    return clean_df


# funtion to calculate REFLEX index
def calc_reflex(demand_df, calc_year):
    df = demand_df.copy()
    # drop observations with zero demand
    df = df[df['flow'] > 0]

    # filter by calc_year
    ent = df[df['date'].dt.year == calc_year]
    # resample to yearly
    ent = ent.groupby(['dst', 'org']).agg({'flow': 'sum'}).reset_index()
    
    # calculate total demand for each destination
    ent_total = ent.groupby('dst')['flow'].sum().reset_index()
    ent_total = ent_total.rename(columns={'flow': 'flowtot'})

    # merge the total demand with the original data
    ent = ent.merge(ent_total, on='dst')

    # calculate the proportion of demand
    ent['prop'] = ent['flow'] / ent['flowtot']
    # calculate surprise value -ln(p) * p
    ent['surp'] = -np.log(ent['prop']) * ent['prop']
    # calculate entropy by summing the surprise values
    result = ent.groupby('dst')['surp'].sum().reset_index().rename(columns={'surp': f'reflex{calc_year - 2000}'})
    result = result.set_index('dst')
    return result


# funtion to calculate REFLEX index over given years
def calc_reflex_years(demand_df, calc_years):
    ent_list = []
    for year in calc_years:
        print(f'Calculating index for {year}')
        ent_list.append(calc_reflex(demand_df, year))
    return pd.concat(ent_list, axis=1).reset_index(drop=False)

# %%
if __name__ == '__main__':
    years = range(2018, 2024)
    print('Reading data...')
    df = read_data(years)

    keep_fips = gen_keep_fips() 
    df = clean_data(df, gen_keep_fips())

    reflex = calc_reflex_years(df, years)
    reflex['dst'] = reflex['dst'].apply(pad_fips)
    reflex.to_csv(OUTPUT_FILE, index=False)
# %%
