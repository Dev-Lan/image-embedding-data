from typing import List, IO, TextIO, Dict
import json
import os
import shutil
import urllib.parse

IN_FOLDER: str = './in/'
TOP_LEVEL_STRUCTURE_FILENAME: str = 'examples.json'
PROCESSED_FOLDER: str = './processed/'


def main():
    filename = 'justPCA.csv'
    topLevelStructure = json.load(open(TOP_LEVEL_STRUCTURE_FILENAME))

    for filename in os.listdir(IN_FOLDER):
        print('Processing File: ' + filename)
        baseName, extension = os.path.splitext(filename)
        if extension in {'.txt', '.csv'}:
            addFile(IN_FOLDER + filename, topLevelStructure)
            shutil.move(IN_FOLDER + filename, PROCESSED_FOLDER + filename)

    saveTopLevelStructure(topLevelStructure)
    return

def saveTopLevelStructure(topLevelStructure: List) -> None:
    outfile = open(TOP_LEVEL_STRUCTURE_FILENAME, 'w')
    outfile.write(json.dumps(topLevelStructure, indent=4))
    return

def addFile(filename: str, topLevelStructure: List) -> None:
    baseName: str = os.path.basename(filename)
    baseNameNoExt = baseName.split('.')[0]
    datasetName,  projectionDisplayName = baseNameNoExt.split('*')
    datasetObj = findDataset(datasetName, topLevelStructure)
    folderName = urllib.parse.unquote(datasetObj['folderName'])
    projectionFilename = findFilename(projectionDisplayName, datasetObj)

    csvFile = open(IN_FOLDER + baseName, 'rt')
    count = 0
    line = csvFile.readline()
    while line:
        line = csvFile.readline()
        count += 1
        
    csvFile.close()
    csvFile = open(IN_FOLDER + baseName, 'rt')
    csvToJson(csvFile, count, folderName + "/" + projectionFilename)
    return

def findDataset(displayName: str, topLevelStructure: List) -> Dict:
    for dataset in topLevelStructure:
        if dataset['displayName'] == displayName:
            return dataset
    newDataset = {}
    newDataset['displayName'] = displayName
    folderName = displayName
    index = 2
    while os.path.exists(folderName):
        folderName = displayName + " (" + str(index) + ")"
        index += 1
    os.mkdir(folderName)
    folderName = urllib.parse.quote(folderName)
    newDataset['folderName'] = folderName
    newDataset['imageWidth'] = 80
    newDataset['imageHeight'] = 80
    newDataset['projectionList'] = []
    topLevelStructure.append(newDataset)
    printNewFolderMessage(folderName)
    return newDataset

def findFilename(displayName: str, datasetObj: Dict) -> str:
    folderName = datasetObj['folderName']
    for projection in datasetObj['projectionList']:
        if projection['displayName'] == displayName:
            return urllib.parse.unquote(projection['filename'])
    newProj = {}
    newProj['displayName'] = displayName
    filename = displayName
    index = 2
    while os.path.exists(folderName + "/" + filename + ".json"):
        filename = displayName + " (" + str(index) + ").json"
        index += 1
    filename = filename + ".json"
    newProj['filename'] = urllib.parse.quote(filename)
    datasetObj['projectionList'].append(newProj)
    return filename

def printNewFolderMessage(newFolderName: str) -> None:
    print("Warning! - New dataset folder (" + newFolderName + ") added! You must do the following manually.")
    print("\t1. Set the imageWidth and imageHeight values in " + TOP_LEVEL_STRUCTURE_FILENAME)
    print("\t2. Add and imageLookup.json file to " + newFolderName +".")
    print('\t3. Add a new tiledImg.png file to ' + newFolderName + '.')
    return

def csvToJson(csvFile, numRows: int, outFilename: str) -> None:
    # x,y,attr1,attr2,...,attrN
    labels = csvFile.readline().rstrip()
    labels = labels.split(',')

    maxNameLength = len(str(numRows))

    jsonList: List[dict] = []

    index = 0
    line = csvFile.readline()
    while line:
        line = line.rstrip()
        line = line.split(',')
        line = [float(x) for x in line]

        thisDict = {}
        thisDict['x'] = line[0]
        thisDict['y'] = line[1]
        imgName = str(index)
        while len(imgName) < maxNameLength:
            imgName = '0' + imgName

        thisDict['image'] = imgName + '.png'

        attributeDict = {}
        for i in range(2, len(line)):
            name = labels[i]
            attributeDict[name] = {'displayName': name, 'value': line[i]}
        thisDict['attributes'] = attributeDict
        jsonList.append(thisDict)

        index += 1
        line = csvFile.readline()

    outFile = open(outFilename, 'w')
    outFile.write(json.dumps(jsonList))
    return

if __name__ == "__main__":
    main()