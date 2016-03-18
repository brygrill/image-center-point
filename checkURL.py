
import urllib2, arcpy

def goToUrl(urlPath):
    try:
        urllib2.urlopen(urlPath)
        print "OK"
    except urllib2.HTTPError, e:
        print(urlPath,e.code)
    except urllib2.URLError, e:
        print(urlPath,e.args)

fc = "path\to\GDB\YourGDB.gdb\thepoints"
field = "URL"
cursor = arcpy.SearchCursor(fc)
for row in cursor:
    goToUrl(row.getValue(field))
