import sys

filename = sys.argv[1]
id = int(filename[:filename.find('.')])
with open(filename, 'r') as file:
    l = file.readline()
    while l and l.find(f'latlngs{id}') <= 0: l = file.readline()
    coords = eval(l[l.find(' = ')+3:l.find(';')])
    print (coords[:3])

with open(f'{id}.kml', 'w') as file:
    file.write("<Document>\n")
    file.write("<Placemark>\n")
    file.write(f"  <LineString>\n")
    file.write(f"    <coordinates>\n")
    for lat, lon in coords:
        file.write(f"      {lon},{lat}\n")
    file.write(f"    </coordinates>\n")
    file.write(f"  </LineString>\n")
    file.write("</Placemark>\n")
    file.write("</Document>\n")
