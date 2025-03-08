import sumolib
from lxml import etree

# Load the network
net = sumolib.net.readNet('bangalore_reduced.net.xml.gz')

# Parse the polygon file to extract coordinates
polygon_file = 'route.poly.xml'
tree = etree.parse(polygon_file)
root = tree.getroot()

coords = []
for point in root.find('.//polygon').findall('point'):
    coords.append((float(point.get('x')), float(point.get('y'))))

# Map coordinates to edges
route_edges = []
for x, y in coords:
    edge = net.getNearestEdge(net.convertLonLat2XY(x, y))
    route_edges.append(edge.getID())

# Remove duplicate consecutive edges
clean_edges = [route_edges[0]]
for e in route_edges[1:]:
    if e != clean_edges[-1]:
        clean_edges.append(e)

# Generate route file (rou.xml)
with open('route.rou.xml', 'w') as f:
    f.write('''<routes>
    <route id="route0" edges="{}"/>
    <vehicle id="veh0" type="DEFAULT_VEHTYPE" route="route0" depart="0"/>
</routes>'''.format(' '.join(clean_edges)))