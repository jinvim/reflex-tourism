import os
import ast
import pandas as pd
from utills import pad_fips, cbg_to_county

DATA_PATH = "source/ADVAN/cbg/"
OUTPUT_PATH = "source/ADVAN/processed/us-vst/"


def get_files(month):
    month_path = os.path.join(DATA_PATH, month)
    files = os.listdir(month_path)
    return [os.path.join(month_path, f) for f in files]


# expand ADVAN format VST data for each origin into long format
def expand_vst(df, col, name):
    vst_df = df[["dstcbg", col]].copy()
    vst_df[name] = vst_df[col].apply(lambda x: x.values())
    vst_df = vst_df.apply(pd.Series.explode).rename(columns={col: "orgcbg"})
    # remove cases where orgcbg is Canadian DA. Also drop rows with NaN values
    vst_df = vst_df[~vst_df["orgcbg"].str.contains("CA:", na=True)]
    vst_df["orgcbg"] = vst_df["orgcbg"].astype(int)
    return vst_df


# get list of folders in the data directory of a given year, each folder corresponds to a month
def get_folders(year):
    folders = os.listdir(DATA_PATH)
    folders.sort()
    return [f for f in folders if f"{year}" in f]


# process data for a given month
# this saves the processed data to a csv file (temporarily)
def process_data(month):
    print(f"Processing {month}")
    # columns to keep
    keep_cols = [
        "AREA",
        "RAW_DEVICE_COUNTS",
        "DEVICE_HOME_AREAS",
        "WORK_BEHAVIOR_DEVICE_HOME_AREAS",
    ]

    # read all files for the month
    files = get_files(month)

    dfs = [pd.read_csv(f, compression="gzip", usecols=keep_cols)
           for f in files]
    # concatenate all files
    df = pd.concat(dfs).reset_index(drop=True)
    # rename columns
    df.columns = ["dstcbg", "rawinflow", "byhome", "byhomewrk"]
    # convert dict stored as string to dict
    df["byhome"] = df["byhome"].apply(ast.literal_eval)
    df["byhomewrk"] = df["byhomewrk"].apply(ast.literal_eval)
    # expand VST data
    byhome = expand_vst(df, "byhome", "home")
    byhomewrk = expand_vst(df, "byhomewrk", "homewrk")

    # merge byhome and byhomewrk
    vstcomb = pd.merge(byhome, byhomewrk, how="left", on=["dstcbg", "orgcbg"])
    for col in ["home", "homewrk"]:
        vstcomb[col] = vstcomb[col].infer_objects(copy=False).fillna(0)
    # calculate flow (travel from org to dst that is not home and not work related)
    vstcomb["flow"] = vstcomb["home"] - vstcomb["homewrk"]

    # resample to county level
    vstcomb["dst"] = vstcomb["dstcbg"].apply(cbg_to_county)
    vstcomb["org"] = vstcomb["orgcbg"].apply(cbg_to_county)
    vstcomb = (
        vstcomb.drop(columns=["dstcbg", "orgcbg"])
        .groupby(["dst", "org"])
        .sum()
        .reset_index()
    )

    # add datetime column
    vstcomb.to_csv(os.path.join(OUTPUT_PATH, f"{month}.csv"), index=False)


# merge data for a given year
def merge_data(year, delete=True):
    months = get_folders(year)
    print(f"Merging data for {year}...")
    dfs = []
    for month in months:
        df = pd.read_csv(os.path.join(OUTPUT_PATH, f"{month}.csv"))
        df["date"] = month + "-01"
        dfs.append(df)

    df = pd.concat(dfs)
    df.to_csv(os.path.join(OUTPUT_PATH, f"{year}.csv.gz"), index=False, compression='gzip')

    # delete individual month files if delete is True
    if delete:
        for month in months:
            os.remove(os.path.join(OUTPUT_PATH, f"{month}.csv"))


if __name__ == "__main__":
    for year in range(2018, 2024):
        if year != 2019:
            months = get_folders(year)
            for month in months:
                process_data(month)
            merge_data(year)