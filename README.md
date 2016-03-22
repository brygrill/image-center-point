## Get Image Centerpoint
Create geodatabase of centerpoints to view georeferenced images a la [Penn Pilot](http://www.pennpilot.psu.edu/). Resize and prep images for viewing in web app. 

Crawl directory and add points to geodatabase
```
RasterCenterPoint.py
```

Once images are online, confirm each point's image has valid URL
```
checkURL.py
```



### To-do
- Clean up logic to reduce redundancy in dealing with images