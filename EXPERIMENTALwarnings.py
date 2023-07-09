import pandas as pd
import requests
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon, Polygon

url = 'https://mesonet.agron.iastate.edu/api/1/cow.json?wfo=DTX&begints=2023-06-25T12:00:00Z&endts=2023-06-26T12:00:00Z&hailsize=1&wind=58&phenomena=TO&phenomena=SV&phenomena=MA&phenomena=FF&phenomena=DS&lsrbuffer=15&warningbuffer=1'
response = requests.get(url)
data = response.json()

events = data['events']['features']

warning_data = []

for event in events:
    properties = event['properties']
    geometry = event['geometry']
    
    id = event['id']
    year = properties['year']
    wfo = properties['wfo']
    phenomena = properties['phenomena']
    eventid = properties['eventid']
    issue = properties['issue']
    expire = properties['expire']
    statuses = properties['statuses']
    fcster = properties['fcster']
    significance = properties['significance']
    parea = properties['parea']
    ar_ugcname = properties['ar_ugcname']
    status = properties['status']
    stormreports = properties['stormreports']
    stormreports_all = properties['stormreports_all']
    verify = properties['verify']
    lead0 = properties['lead0']
    areaverify = properties['areaverify']
    sharedborder = properties['sharedborder']

    warning_data.append([id, year, wfo, phenomena, eventid, issue, expire, statuses, fcster, significance,
                         parea, ar_ugcname, status, stormreports, stormreports_all, verify, lead0, areaverify,
                         sharedborder, geometry])

df = pd.DataFrame(warning_data, columns=['id', 'year', 'wfo', 'phenomena', 'eventid', 'issue', 'expire', 'statuses',
                                         'fcster', 'significance', 'parea', 'ar_ugcname', 'status', 'stormreports',
                                         'stormreports_all', 'verify', 'lead0', 'areaverify', 'sharedborder',
                                         'geometry'])

mapcrs = ccrs.LambertConformal(central_longitude=-85.6, central_latitude=44.3, standard_parallels=(30, 60))
datacrs = ccrs.PlateCarree()

fig = plt.figure(figsize=(16, 12))
ax = fig.add_subplot(1, 1, 1, projection=mapcrs)
ax.set_extent([-85.5, -82, 41.5, 44.0], datacrs)
ax.add_feature(cfeature.COASTLINE.with_scale('50m'))
ax.add_feature(cfeature.STATES.with_scale('50m'), alpha=.75)
ax.add_feature(cfeature.BORDERS.with_scale('50m'), linestyle=':', linewidth=0.5)

colors = {'SV': 'yellow', 'TO': 'red', 'FF': 'green', 'MA': 'orange', 'DS': 'brown'}

for index, row in df.iterrows():
    geometry = row['geometry']
    if geometry:
        if geometry['type'] == 'Polygon':
            coordinates = geometry['coordinates']
            if isinstance(coordinates[0][0], float):  # Handle single coordinate pair
                coordinates = [coordinates]
            polygon = Polygon(coordinates[0])
            phenomena = row['phenomena']
            color = colors.get(phenomena)
            if color:
                ax.add_patch(Polygon(polygon.exterior, fc=color, ec='black', lw=1, transform=datacrs))
        elif geometry['type'] == 'MultiPolygon':
            polygons = geometry['coordinates']
            valid_polygons = []
            for coords in polygons:
                if coords and isinstance(coords[0][0], float):  # Filter out empty or invalid polygons
                    valid_polygons.append(coords)
            if not valid_polygons:
                continue
            multipolygon = MultiPolygon(valid_polygons)
            phenomena = row['phenomena']
            color = colors.get(phenomena)
            if color:
                for polygon in multipolygon:
                    ax.add_patch(Polygon(polygon.exterior, fc=color, ec='black', lw=1, transform=datacrs))

plt.show()