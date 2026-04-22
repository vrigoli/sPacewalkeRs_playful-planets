# NASA Spacewalk Analysis — Python
# https://data.nasa.gov/resource/eva.json (with modifications)
# Generates three figures for the manuscript

import json
import csv
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np

# Load data
output_dir = '/home/sarah/Projects/spacewalk-analysis/results/figures/'

data_f = open('data/data.json', 'r')
raw = json.load(data_f)
data_f.close()

records = []
for entry in raw:
    records.append(entry)

df = pd.DataFrame(records)
df['date'] = pd.to_datetime(df['date'].str[:10], errors='coerce')
df['year'] = df['date'].dt.year
df['country'] = df['country'].str.strip()

# Parse duration from H:MM string to decimal hours
def parseDuration(d):
    # converts H:MM to decimal hours
    try:
        parts = d.split(':')
        return int(parts[0]) + int(parts[1]) / 60
    except:
        return None

# df['duration_hrs'] = df['duration'].apply(parseDuration)

colour_usa = '#e41a1c'
colour_russia = '#4daf4a'

# --------------------------------------------------
# Figure 1: Cumulative EVA hours over time
# --------------------------------------------------

df_dur = df.copy()
df_dur['duration_hrs'] = df_dur['duration'].apply(parseDuration)
df_dur = df_dur.dropna(subset=['duration_hrs', 'date'])
df_dur = df_dur.sort_values('date')
df_dur['cumulative_hrs'] = df_dur['duration_hrs'].cumsum()

fig1, ax1 = plt.subplots(figsize=(8, 4))
ax1.plot(df_dur['date'], df_dur['cumulative_hrs'], color='black', linewidth=1.5)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('results/figures/fig_cumulative_hours.png', dpi=150)
plt.close()

# --------------------------------------------------
# Figure 2: EVA duration distribution by country
# --------------------------------------------------

df_dist = df.copy()
df_dist['duration_hrs'] = df_dist['duration'].apply(parseDuration)
df_dist = df_dist.dropna(subset=['duration_hrs', 'country'])
df_dist = df_dist[df_dist['country'].isin(['USA', 'Russia'])]

usa_dur = df_dist[df_dist['country'] == 'USA']['duration_hrs']
rus_dur = df_dist[df_dist['country'] == 'Russia']['duration_hrs']

fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.hist(usa_dur, bins=25, alpha=0.6, color=colour_usa, label='USA')
ax2.hist(rus_dur, bins=25, alpha=0.6, color=colour_russia, label='Russia')
ax2.legend()
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('results/figures/fig_duration_distribution.png', dpi=150)
plt.close()

# --------------------------------------------------
# Figure 3: Top 10 astronauts by total EVA time
# --------------------------------------------------

df_crew = df.copy()
df_crew['duration_hrs'] = df_crew['duration'].apply(parseDuration)
df_crew = df_crew.dropna(subset=['duration_hrs', 'crew'])

astronaut_list = []
for _, row in df_crew.iterrows():
    names = row['crew'].split(';')
    for n in names:
        n = n.strip()
        if n != '':
            astronaut_list.append({'astronaut': n, 'duration_hrs': row['duration_hrs']})

df_astro = pd.DataFrame(astronaut_list)
df_astro = df_astro.groupby('astronaut')['duration_hrs'].sum().reset_index()
df_astro = df_astro.sort_values('duration_hrs', ascending=False).head(10)
df_astro = df_astro.sort_values('duration_hrs', ascending=True)

fig3, ax3 = plt.subplots(figsize=(8, 5))
ax3.barh(df_astro['astronaut'], df_astro['duration_hrs'], color=colour_usa)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.set_xlabel('Total Duration (Hours)', fontsize=10)
ax3.set_ylabel('Astronaut', fontsize=10)
plt.tight_layout()
plt.savefig('results/figures/fig_top_astronauts.png', dpi=150)
plt.close()

print("Python figures generated.")
