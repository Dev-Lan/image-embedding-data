from PIL import Image, ImageDraw
import os, math

imageDir = "./tmp/" # todo -it would be nice to get this from the command line
(smallW, smallH) = (256, 64) # todo - get image size


imageLookup = open("./imageLookup.json", "w")
imageLookup.write("{\n")
outName = "./tiledImg.png"

imageFiles = os.listdir(imageDir)
# print(imageFiles)
imageFiles = [file for file in imageFiles if file[-4:] == ".png"]
# imageFiles.sort()
# print(imageFiles)
numImages = len(imageFiles)
numImageW = round(numImages**0.5)
numImageH = math.ceil(numImages / float(numImageW))
(bigWidth, bigHeight) = (numImageW * smallW, numImageH * smallH)
bigImg = Image.new('RGB', (bigWidth, bigHeight))

for i in range(len(imageFiles)):
	x = i % numImageW
	y = math.floor(i / numImageW)

	imageFilename = imageFiles[i]
	smallImg = Image.open(imageDir + imageFilename)
	top = y * smallH
	left = x * smallW
	bigImg.paste(smallImg, (left, top))

	lookupObj = '"' + imageFilename + '": {"top":' + str(top) + ', "left":' + str(left) + ', "width":' + str(smallW) + ', "height":' + str(smallH) + '}'
	if i < len(imageFiles) - 1:
		lookupObj += ","
	imageLookup.write(lookupObj + '\n')

bigImg.save(outName)

imageLookup.write("}")
