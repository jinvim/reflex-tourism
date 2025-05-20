# pad fips code with leading zeros
def pad_fips(fips):
    return f"{fips:05d}"

# funtion to extract region from a 5 digit fips/sig code
def get_region(code):
    return code // 1000

# convert census block group to county fips code by taking the first 5 digits
def cbg_to_county(cbg):
    # this is about twice faster than the commented code
    return int(cbg / 1_000000_0)
    # return int(f"{cbg:012d}"[:5])