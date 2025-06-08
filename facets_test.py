import os
import math
import pandas as pd
import gpxpy
import fit2gpx
import matplotlib.pyplot as plt
import seaborn as sns

# === 1. A fájlokat tartalmazó mappa ===
folder = r"C:\Users\emese\Documents\ErasmusGIS\semester_2\SoftwareDev\Strava\strava_py\tests\gpx"  # <- IDE írd a saját mappád nevét

# === 2. Csak a .gpx és .fit fájlok kiválogatása ===
all_files = os.listdir(folder)
gpx_fit_files = [os.path.join(folder, f) for f in all_files if f.endswith((".gpx", ".fit"))]

# === 3. Üres lista az összes feldolgozott DataFrame-hez ===
dfs = []

# === 4. Fájlok feldolgozása egyesével ===
for filepath in gpx_fit_files:
    print(f"Feldolgozás: {filepath}")
    
    if filepath.endswith(".gpx"):
        with open(filepath, encoding="utf-8") as f:
            try:
                activity = gpxpy.parse(f)
            except Exception as e:
                print(f"Hiba a fájlban ({filepath}): {e}")
                continue

        lon, lat, ele, time, name, dist = [], [], [], [], [], []

        for track in activity.tracks:
            for segment in track.segments:
                if not segment.points:
                    continue
                x0, y0, d0 = segment.points[0].longitude, segment.points[0].latitude, 0
                for point in segment.points:
                    x, y, z, t = point.longitude, point.latitude, point.elevation, point.time
                    d = d0 + math.sqrt((x - x0) ** 2 + (y - y0) ** 2)
                    lon.append(x)
                    lat.append(y)
                    ele.append(z)
                    time.append(t)
                    name.append(os.path.basename(filepath))
                    dist.append(d)
                    x0, y0, d0 = x, y, d

        df = pd.DataFrame({
            "lon": lon, "lat": lat, "ele": ele,
            "time": time, "name": name, "dist": dist
        })

    elif filepath.endswith(".fit"):
        try:
            conv = fit2gpx.Converter()
            df_lap, df = conv.fit_to_dataframes(fname=filepath)
        except Exception as e:
            print(f"Hiba a FIT fájlban ({filepath}): {e}")
            continue

        df["name"] = os.path.basename(filepath)
        dist = []

        for i in range(len(df)):
            if i < 1:
                x0, y0, d0 = df["longitude"].iloc[0], df["latitude"].iloc[0], 0
            x, y = df["longitude"].iloc[i], df["latitude"].iloc[i]
            d = d0 + math.sqrt((x - x0) ** 2 + (y - y0) ** 2)
            dist.append(d)
            x0, y0, d0 = x, y, d

        df["dist"] = dist
        df = df.rename(columns={
            "longitude": "lon", "latitude": "lat",
            "altitude": "ele", "timestamp": "time"
        })
        df = df[["lon", "lat", "ele", "time", "name", "dist"]]

    else:
        continue

    dfs.append(df)

# === 5. Összefűzés és időoszlopok ===
if not dfs:
    print("Nincs feldolgozható fájl!")
    exit()

df_all = pd.concat(dfs, ignore_index=True)
df_all["time"] = pd.to_datetime(df_all["time"], utc=True)
df_all["date"] = df_all["time"].dt.date
df_all["hour"] = df_all["time"].dt.hour

# === 6. Plotolás FacetGrid-del tevékenységenként ===
sns.set(style="whitegrid")

start_times = (
    df_all.groupby("name").agg({"time": "min"}).reset_index().sort_values("time")
)
ncol = math.ceil(math.sqrt(len(start_times)))

g = sns.FacetGrid(
    data=df_all,
    col="name",
    col_wrap=ncol,
    col_order=start_times["name"],
    sharex=False,
    sharey=False,
    height=2.5
)

g.map_dataframe(sns.scatterplot, x="lon", y="lat", hue="hour", palette="viridis")
g.set(xlabel=None, ylabel=None, xticks=[], yticks=[], xticklabels=[], yticklabels=[])
g.set_titles(col_template="", row_template="")
sns.despine(left=True, bottom=True)
plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)


# === 7. Mentés fájlba ===
output_file = os.path.join(r"C:\Users\emese\Documents\ErasmusGIS\semester_2\SoftwareDev\py_packages_strava\results\output_plot.png")
plt.savefig(output_file)
plt.close()

print(f"Plot sikeresen elmentve: {output_file}")

