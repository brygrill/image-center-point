#import modules
import arcpy, os, shutil

""" Prep """
root = r"path\to\project"
pathImgFolder = os.path.join(root, "Name")
pathImgFolder2 = os.path.join(root, "Name2")

pathGDB = os.path.join(root, "YourGDB.gdb")
pathTbl = os.path.join(root, "YourGDB.gdb\thepoints_tbl")
pathPts = os.path.join(root, "YourGDB.gdb\thepointsTEMP")

noMapTxt = os.path.join(root, "NotMapped.txt")

#target folder
targetFolder = r"path\to\images"

#image lists
imgList = []

#Muni District Dictionary
muniDictionary = {"010" : "ADAMSTOWN BOROUGH", "020" : "AKRON BOROUGH", "030" : "BART TOWNSHIP", "040" : "BRECKNOCK TOWNSHIP", "050" : "CAERNARVON TOWNSHIP", "060" : "CHRISTIANA BOROUGH", "070" : "CLAY TOWNSHIP", "080" : "EAST COCALICO TOWNSHIP",
        "090" : "WEST COCALICO TOWNSHIP", "100" : "COLERAIN TOWNSHIP", "110" : "COLUMBIA BOROUGH", "120" : "CONESTOGA TOWNSHIP", "130" : "CONOY TOWNSHIP", "140" : "DENVER BOROUGH", "150" : "EAST DONEGAL TOWNSHIP", "160" : "WEST DONEGAL TOWNSHIP",
        "170" : "DRUMORE TOWNSHIP", "180" : "EAST DRUMORE TOWNSHIP", "190" : "EARL TOWNSHIP", "200" : "EAST EARL TOWNSHIP", "210" : "WEST EARL TOWNSHIP", "220" : "EAST PETERSBURG BOROUGH", "230" : "EDEN TOWNSHIP", "240" : "ELIZABETH TOWNSHIP",
        "250" : "ELIZABETHTOWN BOROUGH", "260" : "EPHRATA BOROUGH", "270" : "EPHRATA TOWNSHIP", "280" : "FULTON TOWNSHIP", "290" : "EAST HEMPFIELD TOWNSHIP", "300" : "WEST HEMPFIELD TOWNSHIP", "310" : "EAST LAMPETER TOWNSHIP", "320" : "WEST LAMPETER TOWNSHIP",
        "330" : "LANCASTER CITY", "340" : "LANCASTER TOWNSHIP", "350" : "LEACOCK TOWNSHIP", "360" : "UPPER LEACOCK TOWNSHIP", "370" : "LITITZ BOROUGH", "380" : "LITTLE BRITAIN TOWNSHIP", "390" : "MANHEIM TOWNSHIP", "400" : "MANHEIM BOROUGH",
        "410" : "MANOR TOWNSHIP", "420" : "MARIETTA BOROUGH", "430" : "MARTIC TOWNSHIP", "440" : "MILLERSVILLE BOROUGH", "450" : "MOUNT JOY BOROUGH", "460" : "MOUNT JOY TOWNSHIP", "470" : "MOUNTVILLE BOROUGH", "480" : "NEW HOLLAND BOROUGH",
        "490" : "PARADISE TOWNSHIP", "500" : "PENN TOWNSHIP", "510" : "PEQUEA TOWNSHIP", "520" : "PROVIDENCE TOWNSHIP", "530" : "QUARRYVILLE BOROUGH", "540" : "RAPHO TOWNSHIP", "550" : "SADSBURY TOWNSHIP", "560" : "SALISBURY TOWNSHIP",
        "570" : "STRASBURG BOROUGH", "580" : "STRASBURG TOWNSHIP", "590" : "TERRE HILL BOROUGH", "600" : "WARWICK TOWNSHIP"}

""" Functions to Call """
# get image center points
def getCenter(path):

    xmin = arcpy.GetRasterProperties_management(path,'LEFT')
    xmax = arcpy.GetRasterProperties_management(path,'RIGHT')
    ymin = arcpy.GetRasterProperties_management(path,'BOTTOM')
    ymax = arcpy.GetRasterProperties_management(path,'TOP')

    centerX = (float(xmax.getOutput(0)) + float(xmin.getOutput(0))) / 2
    centerY = (float(ymax.getOutput(0)) + float(ymin.getOutput(0))) / 2

    print centerX, centerY

def getCenterX(path):

    try:
        xmin = arcpy.GetRasterProperties_management(path,'LEFT')
        xmax = arcpy.GetRasterProperties_management(path,'RIGHT')

        centerX = (float(xmax.getOutput(0)) + float(xmin.getOutput(0))) / 2

        return centerX
    except Exception:
        centerX = 0

def getCenterY(path):

    try:
        ymin = arcpy.GetRasterProperties_management(path,'BOTTOM')
        ymax = arcpy.GetRasterProperties_management(path,'TOP')

        centerY = (float(ymax.getOutput(0)) + float(ymin.getOutput(0))) / 2

        return centerY
    except Exception:
        centerY = 0

# popluate fields
def addRow(pathTbl, dist, muni, picID, imgPath, imgURL):
    rows = arcpy.InsertCursor(pathTbl)
    row = rows.newRow()
    row.setValue("DIST", dist)
    row.setValue("MUNI", muni)
    row.setValue("PICID", picID)
    row.setValue("CENTER_X", getCenterX(imgPath))
    row.setValue("CENTER_Y", getCenterY(imgPath))
    row.setValue("URL", imgURL)
    rows.insertRow(row)

    del row
    del rows

# do work on each image
def loopImgList(theList, theTxtFile):
    print "About To Map This Many Images:", len(theList)
    for item in theList:
        #item is path to image
        print "Found Image: ", item
        imgDist = item.split('\\')[-2][0:3]
        imgMuni = muniDictionary[imgDist]
        imgID = item.split('\\')[-1].translate(None, '.jpg')
        imgURL = "http://wwww.example.com/images/%s.jpg" %(imgID)
        addRow(pathTbl, imgDist, imgMuni, imgID, item, imgURL)

""" Script Fuctions """
def makeGDB():
    print "Running makeGDB"
    if os.path.exists(root):
        pass
    else:
        os.makedirs(root)
        arcpy.CreateFileGDB_management(root, "RasterCenterPoints", "")

    arcpy.CreateTable_management(pathGDB, "Aerials1988tbl")

def addFields():
    print "Running addFields"
    fieldNames = ["DIST", "MUNI", "PICID", "CENTER_X", "CENTER_Y", "URL"]
    for field in fieldNames:
        if field == "URL":
            length = "150"
        elif field == "MUNI":
            length = "40"
        else:
            length = "50"

        if field == "CENTER_X" or field == "CENTER_Y":
            fieldType = "FLOAT"
        else:
            fieldType = "TEXT"

        arcpy.AddField_management(pathTbl, field, fieldType, "", "", length)

def getTheImages(folder):
    print "Running getTheImages"
    for dirpath, subdirs, files in os.walk(folder, topdown=False):
        imgList.extend(os.path.join(dirpath, x) for x in files if x.endswith(".jpg"))

    loopImgList(imgList, noMapTxt)

def mapTable():
    print "Running mapTable"
    nad83south = "path\to\NAD 1983 (2011) StatePlane Pennsylvania South FIPS3702 (US Feet).prj"
    arcpy.MakeXYEventLayer_management(pathTbl, "CENTER_X", "CENTER_Y", "thepointsTEMP", nad83south)
    arcpy.CopyFeatures_management("thepointsTEMP", pathPts)

def copyRenameImages():
    print "Running copyRenameImages"
    os.makedirs(pathImgFolder)

    for image in imgList:
        imgName = image.split('\\')[-1]
        imgMuni = image.split('\\')[-2][0:3]
        imgID = imgMuni + "_" + image.split('\\')[-1]
        #copy from nq-cluster to c drive
        shutil.copy(image, pathImgFolder)
        oldName = pathImgFolder + '\\' + imgName
        newName = pathImgFolder + '\\' + imgID
        #rename image
        os.rename(oldName, newName)

def deleteDuplicateImages():
    print "Running deleteDuplicateImages"
    os.makedirs(pathImgFolder2)

    imgOneCopy = []

    for dirpath, subdirs, files in os.walk(pathImgFolder, topdown=False):
        imgOneCopy.extend(os.path.join(dirpath, x) for x in files if x.endswith(".jpg"))

    for image in imgOneCopy:
        imgID = image.split('\\')[-1]
        imgIDnew = imgID[4:]
        if imgIDnew not in os.listdir(pathImgFolder2):
            shutil.copy(image, pathImgFolder2)
            oldName = pathImgFolder2 + '\\' + imgID
            newName = pathImgFolder2 + '\\' + imgIDnew
            #rename image
            os.rename(oldName, newName)
        else:
            print "Here is a duplicate:", image

    print "All Images:", len(os.listdir(pathImgFolder))
    print "One Copy of Images:", len(os.listdir(pathImgFolder2))

    try:
        os.remove(pathImgFolder)
    except WindowsError:
        print "Couldnt delete:", pathImgFolder

def resizeImages():
    print "Running resizeImages"
    import PIL
    from PIL import Image

    resizeImgList = []

    for dirpath, subdirs, files in os.walk(pathImgFolder2, topdown=False):
        resizeImgList.extend(os.path.join(dirpath, x) for x in files if x.endswith(".jpg"))

    basewidth = 2000
    for pic in resizeImgList:
        img = Image.open(pic)
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
        img.save(pic)

def cleanPts():
    print "Running cleanPts"
    arcpy.env.workspace = pathGDB
    countyBound = r"apth\to\CntyBndry"
    muniBound = r"path\to\Muni"

    #remove any points that arent georeferenced
    arcpy.MakeFeatureLayer_management('thepointsTEMP', 'thepointsTEMP_lyr')
    arcpy.SelectLayerByLocation_management('thepointsTEMP_lyr', 'within', countyBound)
    arcpy.CopyFeatures_management('thepointsTEMP_lyr', 'thepointsTEMP2')
    arcpy.Delete_management('thepointsTEMP')

    #remove duplicate points
    arcpy.DeleteIdentical_management('thepointsTEMP2', ["CENTER_X", "CENTER_Y"])

    #recalc muni field
    arcpy.SpatialJoin_analysis('thepointsTEMP2', muniBound, 'thepointsFINAL')
    arcpy.Delete_management('thepointsTEMP2')
    arcpy.DeleteField_management('thepointsFINAL', ["Join_Count", "TARGET_FID", "MUNI", "DIST", "ABBREVIATION"])


""" Run It """
#main function
def main():
    makeGDB()
    addFields()
    getTheImages(targetFolder)
    mapTable()
    copyRenameImages()
    deleteDuplicateImages()
    resizeImages()
    cleanPts()


#run script
if __name__ == '__main__':
    main()