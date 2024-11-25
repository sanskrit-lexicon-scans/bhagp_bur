# coding=utf-8
""" make_js_index.py for bhagp_bur
"""
from __future__ import print_function
import sys, re,codecs
import json

class Pagerec(object):
 """
Format of Burnouf.BhP.index.txt
volume	page	sk.	adhy.	from v.	to v.				
I	1	(I)	1	1	2ab
""" 
 def __init__(self,line,iline):
  line = line.rstrip('\r\n')
  parts = line.split('\t')
  assert len(parts) == 6
  self.line = line
  self.iline = iline
  partsnum = []
  flagnum = True
  vol_raw = parts[0]  #I,II,III
  page_raw = parts[1] # internal to volume. digits
  kanda_raw = parts[2] # skandha (I,II,...,IX)
  sarga_raw = parts[3] # adhy
  verse1_raw = parts[4] 
  verse2_raw = parts[5]
  droman_int = {'I':1, 'II':2, 'III':3, 'IV':4,
                'V':5, 'VI':6, 'VII':7, 'VIII':8, 'IX':9}
  self.vol = droman_int[vol_raw]  # 1,2,3
  assert self.vol in (1,2,3)
  self.page = int(page_raw)
  kanda_raw_noparen = kanda_raw[1:-1]
  assert kanda_raw == '(' + kanda_raw_noparen + ')'
  self.kanda = droman_int[kanda_raw_noparen]  # 1,...,9
  self.sarga = int(sarga_raw)
  try:
   m = re.search(r'^([0-9]+)([abcd]*)$',verse1_raw)
   self.verse1 = int(m.group(1))
   self.verse1x = m.group(2)
  except:
   print('problem with verse1 (iline = %s):' % iline)
   print(line)
   print('verse1_raw="%s"' % (verse1_raw))
   exit(1)
  m = re.search(r'^([0-9]+)([abcd]*)$',verse2_raw)
  self.verse2 = int(m.group(1))
  self.verse2x = m.group(2)
  self.flagnum = True  # used?
  ###  vol 1, page1 : 1193.pdf
  #    vol 2, page1 : 2031.pdf
  #    vol 3, page1 : 3121.pdf
  dvolpage0 = {1:193-1, 2:31-1, 3:121-1} 
  page_offset = dvolpage0[self.vol]
  extpage = self.page + page_offset # int
  vpstr = '%s%03d' %(self.vol,extpage)
  self.vp = vpstr
 def todict(self):
  e = {
   'v':self.vol, 'page':int(self.page), 'k':int(self.kanda),
   's':int(self.sarga),
   'v1':int(self.verse1), 'v2':int(self.verse2),
   'x1':self.verse1x, 'x2':self.verse2x, 'vp':self.vp
  }
  return e
def init_pagerecs(filein):
 """ filein is a csv file, with tab-delimiter and with first line as fieldnames
 """
 recs = []
 with codecs.open(filein,"r","utf-8") as f:
  for iline,line in enumerate(f):
   if (iline == 0):
    assert line.startswith('volume') # skip column-title line
    continue
   pagerec = Pagerec(line,iline)
   if pagerec.flagnum:
    # skip some records
    recs.append(pagerec)
 print(len(recs),'Page records read from',filein)
 return recs

def init_kandasargadict(pagerecs):
 d = {}
 for rec in pagerecs:
  key = "%s.%s" %(rec.kanda,rec.sarga)
  #assert 1 <= key <= 18
  if key not in d:
   d[key] = []
  recobj = rec.todict()
  d[key].append(recobj)
 return d

def init_kandadict(pagerecs):
 d = {}
 kold = None
 for rec in pagerecs:
  k = rec.kanda;
  s = rec.sarga
  key = "%s.%s" %(rec.kanda,rec.sarga)
  if k not in d:
   d[k] = {}
  if s not in d[k]:
   d[k][s] = []
  recobj = rec.todict()
  d[k][s].append(recobj)
 return d

def write_kanda(fileout,d):
 # d is a dictionary of kandas,
 # and each value is a dictionary
 # Generate a javascript file setting value of a global indexdata
 outarr = []
 outarr.append('indexdata = {')
 for k in d:
  # key has form k  (1 to 9)  
  outarr.append(' %s: {' % k)
  sd = d[k] # dictionary of sargas
  for s in sd:
   outarr.append('  %s: [' % s)
   pagerecs = sd[s]  # array of dictionaries
   for pagerec in pagerecs:
    # pagerec is a dict
    jsonstring = json.dumps(pagerec)
    outarr.append('    %s,' % jsonstring)
   outarr.append(' ], ') # end of pagerecs
  outarr.append(' },') # end of sarga dictionary
 outarr.append('};') # end of kanda dictionary
 with codecs.open(fileout,"w","utf-8") as f:
  for out in outarr:
   f.write(out + '\n')
 print(len(outarr),'lines written to',fileout)

def write_kandasarga(fileout,d):
 # d is a dictionary, and each value is an array of dictionaries
 # Generate a javascript file setting value of a global indexdata
 outarr = []
 outarr.append('indexdata = {')
 for key in d:
  # key has form k.s  (kanda,sarga)
  arr = d[key] # an array
  outarr.append(' "%s": [' % key)
  for a in arr:
   # a is a dict
   jsonstring = json.dumps(a)
   outarr.append('  %s,' % jsonstring)
  outarr.append(' ], ') # end of array arr
 outarr.append('};') 
 with codecs.open(fileout,"w","utf-8") as f:
  for out in outarr:
   f.write(out + '\n')
 print(len(outarr),'lines written to',fileout)

if __name__ == "__main__":
 filein=sys.argv[1]  # tab-delimited index file
 fileout = sys.argv[2]
 pagerecs = init_pagerecs(filein)
 #kandasargadict = init_kandasargadict(pagerecs)
 #write_kandasarga(fileout,kandasargadict)
 kandadict = init_kandadict(pagerecs)
 write_kanda(fileout,kandadict)
 
