'''
Equations used here are derived from http://www.velomath.fr/dossier_velo_equation/velo_equation.html
The parameters used are roughly Cx = 0.2, f = 1, weight = 72
So that the final equation is power = 2*(1+slope)*speed+0.005*speed^3
'''

def powerFromSpeed(speed, slope):
  '''
  computes power for a given speed on a given slope
  speed is in km/h, slope in %, result in Watts
  '''
  return (2*(1+slope)+0.005*speed*speed)*speed

def speedFromPower(power, slope):
  '''
  computes speed for a given power on a given slope
  power is in Watts, slope in %, result in km/h
  '''
  # operates by dichotomy
  smin = 0
  smax = 80
  pmin = powerFromSpeed(smin, slope)
  pmax = powerFromSpeed(smax, slope)
  while pmax - pmin > 1:
    smid = (smin+smax)/2
    pmid = powerFromSpeed(smid, slope)
    if pmid < power:
      pmin = pmid
      smin = smid
    else:
      pmax = pmid
      smax = smid
  return smid

# build table of values for speed vs slope
speedForSlopeTable = {}
for n in range(-30,31):
  slope = n/2
  speedForSlopeTable[slope] = speedFromPower(250, slope)

def speedForSlope(slope):
  '''gives the speed for a given slope'''
  slope = max(-15, min(14.5, slope))
  smin = int(slope*2)/2
  smax = smin+0.5
  sdelta = slope - smin
  delta = speedForSlopeTable[smax] - speedForSlopeTable[smin]
  return speedForSlopeTable[smin] + sdelta*2*delta

#for n in range(10):
#  slope = -7 + n/5
#  print (slope, speedForSlope(slope))

def timeForSegment(length, slope):
  '''
  Computes time for biking a segment of given length and average slope
  length should be in km, time will be in seconds
  '''
  return 3600 * length / speedForSlope(slope)

import requests

altitudeTable = {}
def getAltitude(n):
  if n not in altitudeTable:
    r = requests.get('http://0.0.0.0:8080/api/v1/lookup?locations=%f,%f' %
                     (g._node[n]['y'], g._node[n]['x']),
                     headers={'Accept': 'application/json'})
    altitudeTable[n] = r.json()['results'][0]['elevation']
  return altitudeTable[n]

import pickle
import networkx
with open('SwissDump.pkl', 'rb') as file:
  g = pickle.load(file)

for u,v,k,data in g.edges(keys=True, data=True):
  au = getAltitude(u)
  av = getAltitude(v)
  l = data['length']
  slope = (av-au)/l*100
  t = timeForSegment(l/1000, slope)
  # add penalty for paths
  if data['highway'] == 'path':
    t = t * 1.5
  if 'slowFactor' in data:
    t = t * data['slowFactor']
  networkx.set_edge_attributes(g, {(u,v,k):{"duration":t}})

with open('SwissDumpTime.pkl', 'wb') as file:
  pickle.dump(g, file)
