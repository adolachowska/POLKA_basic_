import pandas as pd
import numpy as np
from functools import reduce

#DATA
#1. press_free
fp_id = pd.read_csv('data/world_press_freedom_Index.csv')
fp_id.drop(['STRUCTURE', 'STRUCTURE_ID', 'ACTION', 'FREQ', 'REF_AREA', 'INDICATOR', 'SEX', 'AGE', 'URBANISATION', 'UNIT_MEASURE', 'COMP_BREAKDOWN_1', 'COMP_BREAKDOWN_2', 'COMP_BREAKDOWN_3', 'UNIT_TYPE', 'DATABASE_ID', 'TIME_FORMAT', 'UNIT_MULT', 'DATA_SOURCE', 'OBS_CONF', 'OBS_STATUS', 'FREQ_LABEL', 'INDICATOR_LABEL', 'SEX_LABEL', 'AGE_LABEL', 'URBANISATION_LABEL', 'UNIT_MEASURE_LABEL', 'COMP_BREAKDOWN_1_LABEL', 'COMP_BREAKDOWN_2_LABEL', 'COMP_BREAKDOWN_3_LABEL', 'UNIT_TYPE_LABEL', 'DATABASE_ID_LABEL', 'TIME_FORMAT_LABEL', 'UNIT_MULT_LABEL', 'OBS_STATUS_LABEL', 'OBS_CONF_LABEL'], axis=1, inplace=True, errors='ignore')

fp_id = fp_id.rename(columns={'REF_AREA_LABEL': 'Country'})

fp_id = fp_id.melt(
    id_vars=['Country'],
    var_name='Year',
    value_name='press_free'
)
country_count = fp_id["Country"].nunique()
year_count = fp_id["Year"].nunique()
oldest_year = fp_id["Year"].min()
newest_year = fp_id["Year"].max()

print(f'World Press Free Index, number of countries: {country_count}, number of years: {year_count} from {oldest_year}-{newest_year}')

#2. freedom_index
free_id = pd.read_csv('V-Dem-CY-Core-v15.csv')
columns = ['country_name', 'year', 'v2x_polyarchy']
free_id = free_id[columns]

free_id.columns = free_id.columns.str.replace(r'v2x_polyarchy', 'freedom_index', regex=True)
free_id.columns = free_id.columns.str.replace(r'year', 'Year', regex=True)
free_id.columns = free_id.columns.str.replace(r'country_name', 'Country', regex=True)

country_count = free_id["Country"].nunique()
year_count = free_id["Year"].nunique()
oldest_year = free_id["Year"].min()
newest_year = free_id["Year"].max()

print(f'Freedom Index, number of countries: {country_count}, number of years: {year_count} from {oldest_year}-{newest_year}')

#3.gpd
gdp_id = pd.read_csv('data/world_gdp_data.csv', encoding='cp1250')
gdp_id = gdp_id.rename({'Annual GDP growth (percent change)': 'gdp'})
gdp_id = gdp_id.melt(
    id_vars=['country_name'],        # kolumna, która ma pozostać jako identyfikator
    value_vars=[str(y) for y in range(1980, 2025)],  # kolumny lat jako wartości
    var_name='Year',                  # nowa kolumna z nazwą roku
    value_name='gdp'                 # nowa kolumna z wartościami GDP
)
gdp_id = gdp_id.rename(columns={'country_name': 'Country'})

country_count = gdp_id["Country"].nunique()
year_count = gdp_id["Year"].nunique()
oldest_year = gdp_id["Year"].min()
newest_year = gdp_id["Year"].max()


print(f'GDP Index, number of countries: {country_count}, number of years: {year_count} from {oldest_year}-{newest_year}')

#4.Political Stability and Absence of Violence/Terrorism: Percentile Rank
#skala 1-100
absence_of_violence_id = pd.read_csv(
    'data/absence_of_violence.csv',
    skiprows=4,
    engine='python'
)
absence_of_violence_id = absence_of_violence_id.drop(
    ['Country Code', 'Indicator Name', 'Indicator Code', 'Unnamed: 69'],
    axis=1,
    errors='ignore'
)
absence_of_violence_id = absence_of_violence_id.rename(columns={'Country Name': 'Country'})
absence_of_violence_id = absence_of_violence_id.melt(
    id_vars=['Country'],
    value_vars=[str(y) for y in range(1960, 2024)],  # kolumny lat jako wartości
    var_name='Year',                  # nowa kolumna z nazwą roku
    value_name='absence_of_violence'                 # nowa kolumna z wartościami GDP
)

country_count = absence_of_violence_id["Country"].nunique()
year_count = absence_of_violence_id["Year"].nunique()
oldest_year = absence_of_violence_id["Year"].min()
newest_year = absence_of_violence_id["Year"].max()

print(f'Absence ofv Violence Index, number of countries: {country_count}, number of years: {year_count} from {oldest_year}-{newest_year}')


#5 civil_liberties
#scale 1-10
civil_liberties_id = pd.read_csv(
    'data/civil-liberties-index-eiu.csv',
    engine='python'
)
civil_liberties_id.drop(['World region according to OWID','Code'], axis=1, inplace=True)
civil_liberties_id = civil_liberties_id.rename(columns={'Entity': 'Country'})
civil_liberties_id = civil_liberties_id.rename(columns={'Civil liberties': 'civil_liberties'})

country_count = civil_liberties_id["Country"].nunique()
year_count = civil_liberties_id["Year"].nunique()
oldest_year = civil_liberties_id["Year"].min()
newest_year = civil_liberties_id["Year"].max()

print(f'Civil Liberties Index, number of countries: {country_count}, number of years: {year_count} from {oldest_year}-{newest_year}')

#6
#gov_stability
#scale 1-100
cor_per_id = pd.read_csv('data/ti-corruption-perception-index.csv')
cor_per_id.rename(columns={
    'Entity': 'Country',
    'Corruption Perceptions Index': 'gov_stability'
}, inplace=True)

cor_per_id.drop(
    columns=['Code', 'World region according to OWID'],
    axis=1,
    inplace=True,
    errors='ignore'
)

country_count = cor_per_id["Country"].nunique()
year_count = cor_per_id["Year"].nunique()
oldest_year = cor_per_id["Year"].min()
newest_year = cor_per_id["Year"].max()

print(f'Corruption Perceptions Index, number of countries: {country_count}, number of years: {year_count} from {oldest_year}-{newest_year}')

#7
#human_rights
#scale 0-1
hum_rig_id = pd.read_csv('data/human-rights-index-vdem.csv')
hum_rig_id.rename(columns={
    'Entity': 'Country',
    'Civil liberties index (central estimate)': 'human_rights'
}, inplace=True)
hum_rig_id.drop(
    columns=['Code', 'World region according to OWID'],
    axis=1,
    inplace=True,
    errors='ignore'
)

country_count = hum_rig_id["Country"].nunique()

year_count = hum_rig_id["Year"].nunique()
oldest_year = hum_rig_id["Year"].min()
newest_year = hum_rig_id["Year"].max()

print(f'Human Rights Index, number of countries: {country_count}, number of years: {year_count} from {oldest_year}-{newest_year}')

# 8. electoral_integrity
ele_int_id = pd.read_csv('data/electoral-democracy-index.csv')
ele_int_id.rename(columns={
    'Entity': 'Country',
    'Electoral democracy index (central estimate)': 'electoral_integrity'
}, inplace=True)
ele_int_id.drop(
    columns=['Code', 'World region according to OWID'],
    axis=1,
    inplace=True,
    errors='ignore'
)

country_count = ele_int_id["Country"].nunique()
year_count = ele_int_id["Year"].nunique()
oldest_year = ele_int_id["Year"].min()
newest_year = ele_int_id["Year"].max()

print(f'Electoral Integrity Index, number of countries: {country_count}, number of years: {year_count} from {oldest_year}-{newest_year}')

#Democracy index EIU
eiu_id = pd.read_csv('data/democracy-index-eiu.csv')
eiu_id.rename(columns={
    'Entity': 'Country',
    'Democracy Index': 'system_index',
}, inplace=True)
eiu_id.drop(
    columns=['Code', 'World region according to OWID'],
    axis=1,
    inplace=True,
    errors='ignore'
)
country_count = eiu_id["Country"].nunique()
year_count = eiu_id["Year"].nunique()
oldest_year = eiu_id["Year"].min()
newest_year = eiu_id["Year"].max()

print(f'Democracy Index EIU, number of countries: {country_count}, number of years: {year_count} from {oldest_year}-{newest_year}')


indicators_df = [fp_id, free_id, gdp_id, absence_of_violence_id, civil_liberties_id, cor_per_id, hum_rig_id, ele_int_id, eiu_id]

for df in indicators_df:
    if 'Country' in df.columns:
        df['Country'] = df['Country'].astype(str).str.strip()
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

indicators_csv = reduce(lambda left, right: pd.merge(left, right, on=['Country', 'Year'], how='outer'), indicators_df)
indicators_csv = indicators_csv.sort_values(by=['Country', 'Year']).reset_index(drop=True)

country_list = pd.read_csv('data/country_list.csv')
country_list_2025 = country_list["Name"].tolist()
indicators_csv = indicators_csv[indicators_csv["Country"].isin(country_list_2025)]

country_count = indicators_csv["Country"].nunique()
year_count = indicators_csv["Year"].nunique()
oldest_year = indicators_csv["Year"].min()
newest_year = indicators_csv["Year"].max()
print(f'Data, number of countries: {country_count}, number of years: {year_count} from {oldest_year}-{newest_year}')

print("Po:", len(indicators_csv))

full = indicators_csv

print(indicators_csv.columns.tolist())

import requests
import io

BASE_URL = "http://127.0.0.1:8000"

api_columns = [
    'year',
    'press_free',
    'freedom_index',
    'gdp',
    'absence_of_violence',
    'civil_liberties',
    'gov_stability',
    'human_rights',
    'electoral_integrity'
    'system_index'
]

for country_name, country_data in indicators_csv.groupby('Country'):
    if not country_name or str(country_name) == 'nan':
        continue

    try:

        requests.post(f"{BASE_URL}/countries", json={"name": country_name})
    except Exception:
        pass

    subset = country_data.copy()

    for col in api_columns:
        if col not in subset.columns:
            subset[col] = ""

    final_data = subset[api_columns]

    csv_buffer = io.StringIO()
    final_data.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()

    files = {'file': (f"{country_name}_data.csv", csv_content, "text/csv")}

    try:
        response = requests.post(f"{BASE_URL}/countries/{country_name}/upload-csv", files=files)

        if response.status_code == 200:
            print(f"✅ {country_name}: Wgrano pomyślnie.")
        else:
            print(f"❌ {country_name}: Błąd API -> {response.text}")

    except Exception as e:
        print(f"❌ {country_name}: Błąd połączenia: {e}")

