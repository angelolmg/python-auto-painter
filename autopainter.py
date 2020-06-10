import os, random, requests, glob, cv2, string
from PIL import Image
import numpy as np
import moviepy.editor as mpe
from myDrive.gdriveservice import drive
from datetime import datetime

################
# variable setup

lineNames = "lines_"
coloredName = "color_"
imagesPath = '\\Images\\'
linesPath = '\\Lines\\'
framesPath = '\\Frames\\'
audioPath = '\\Audio\\'
colorsPath = '\\colors.txt'
namesPath = '\\names.txt'
videoOptionsPath = '\\video_options.txt'
videoPath = 'test.avi';
projectName = '0 - yyy yyy'
videoExtension = '.mp4'
videoBitrate = "2500k"
driveDownloadFolder = 'bloob_buffer'
driveUploadFolder = 'Bloobs'
imgGlobExtension = ".jpg"

transparent = (0, 0, 0, 0)
black = (0, 0, 0, 255)
white = (255, 255, 255, 255)

baseWidth = 720
baseHeight = 1280
imgSize = (baseWidth, baseHeight)
normalizedSize = (864, 1152) # 0.75 ratio
imgBase = Image.new('RGBA', imgSize, color = transparent)
framePivot = (0, 280)
posOffset = 10
resizeOffset = 150
lightThreshold = 140
frameCounter = 0
FPS = 30
repeatFrames = 5
lineWidthThreshold = 100

################
# functions

#save a frame
def save(img):
    imgCopy = img.copy()
    SubstituteColor(imgCopy, transparent, white)
    global frameCounter
    imgCopy.save(framesPath + "frame_" + str(frameCounter) + ".png")
    frameCounter += 1

# make everything transparent except the lines
def CleanLineWork(img): 
    width, height = img.size
    pixelMatrix = img.load()
    for left in range(0, width):
        for top in range(0, height):
            r, g, b, a = pixelMatrix[left,top]
            if(r > lightThreshold):
                pixelMatrix[left,top] = transparent
            else:
                pixelMatrix[left,top] = black
                
# get any pixel that is not trasparent and turn it black
def FillLinesBlack(img):
    width, height = img.size
    pixelMatrix = img.load()
    
    for left in range(0, width):
        for top in range(0, height):
            if(pixelMatrix[left, top] != transparent):
                pixelMatrix[left, top] = black

# just substitute a color for another
def SubstituteColor(img, targetColor, fillColor):
    width, height = img.size
    pixelMatrix = img.load()
    
    for left in range(0, width):
        for top in range(0, height):
            if(pixelMatrix[left, top] == targetColor):
                pixelMatrix[left, top] = fillColor

# target a 'targetColor' on some edge and floodfill it with 'fillColor'
def FillFromEdges(img, targetColor, fillColor):
    width, height = img.size
    pixelMatrix = img.load()

    # check top
    for left in range(0, width-1):
        if(pixelMatrix[left, 0] == targetColor):
            FloodFill(pixelMatrix, left, 0, width, height, targetColor, fillColor)

    # check bottom
    for left in range(0, width-1):
        if(pixelMatrix[left, height-1] == targetColor):
            FloodFill(pixelMatrix, left, height-1, width, height, targetColor, fillColor)
            
    # check left
    for top in range(0, height-1):
        if(pixelMatrix[0, top] == targetColor):
            FloodFill(pixelMatrix, 0, top, width, height, targetColor, fillColor)
            
    # check rigth
    for top in range(0, height-1):
        if(pixelMatrix[width-1, top] == targetColor):
            FloodFill(pixelMatrix, width-1, top, width, height, targetColor, fillColor)   
    
# fill pixel and neighbors of the same color with the fill color
def FloodFill(pixelMatrix, x, y, width, height, targetColor, fillColor):
    toFill = set()
    toFill.add((x,y))
    
    while not len(toFill) == 0:
        (x,y) = toFill.pop()
        (r,g,b,a) = pixelMatrix[x,y]
        if not (r,g,b,a) == targetColor:
            continue
        pixelMatrix[x,y] = fillColor
        if(x > 0):
            toFill.add((x-1,y))
        if(x < width-1):
            toFill.add((x+1,y))
        if(y > 0):
            toFill.add((x,y-1))
        if(y < height-1):
            toFill.add((x,y+1))

# color the lines with different colors, crop, and save as different images
def IsolateImages(img):
    width, height = img.size
    pixelMatrix = img.load()

    # separate the pictures using colors for the lines
    for left in range(0, width):
        for top in range(0, height):
            if(pixelMatrix[left, top] == black):
                fillColor = GetRandomRGBA()
                FloodFill(pixelMatrix, left, top, width, height, black, fillColor)
                
    # find next color, then take the lines to another picture(s) 
    lineIndex = 0
    for left in range(0, width):
        for top in range(0, height):
            if(pixelMatrix[left, top] != transparent):
                #get lines from bounderies of selected color
                currentColor = pixelMatrix[left, top]
                (l,t,r,b) = GetBoxBoundaries(pixelMatrix, currentColor, left, top, width, height)
                
                # crop lines into another image, clean and save it
                croppedLines = img.crop((l,t,r,b))
                cropW, cropH = croppedLines.size
                FillLinesBlack(croppedLines)

                # only save lines if its width exceeds a given threshold
                if((r - l) > lineWidthThreshold):
                    # fill the bg white
                    FillFromEdges(croppedLines, transparent, white)
                    croppedLines.save(lineNames + str(lineIndex) + '.png')
                    lineIndex += 1

                # clear bounderies from original image and increase index
                FillBounderies(img, transparent, l, t, r, b)

# fill a closed boundery (square) with a color
def FillBounderies(imgCopy, fillColor, l, t, r, b):
    pixelMatrix = imgCopy.load()
    for left in range(l, r+1):
        for top in range(t, b+1):
            pixelMatrix[left,top] = fillColor

# get the bounderie coordinates from a given color
def GetBoxBoundaries(pixelMatrix, currentColor, x, y, width, height):
    leftSide = rightSide = x
    topSide = downSide = y
    
    for left in range(0, width):
        for top in range(0, height):
            if(pixelMatrix[left, top] == transparent):
                continue
            if(pixelMatrix[left, top] == currentColor):
                if(top < topSide):
                    topSide = top
                if(top > downSide):
                    downSide = top
                if(left > rightSide):
                    rightSide = left   
    return (leftSide, topSide, rightSide, downSide)

# return random rgba tuple
def GetRandomRGBA():
    return (random.choice(range(1, 255)),random.choice(range(1, 255)),random.choice(range(1, 255)),255)

# get set of colors from the net, then make a tuple rgba array
# if it fails just return a random rgba collection
def GetColorSet():
    colorArray = []
    try:
        url = 'http://colormind.io/api/'
        payload = '{"model":"default"}'

        results = requests.get(url, data = payload)
        colors = results.json()
        for tuples in colors['result']:
            colorArray.append((tuples[0], tuples[1], tuples[2], 255))

    except:
        readFile = open(colorsPath, "r")
        if(readFile):
            # get color array from text file
            colorArray = eval(random.choice(list(readFile)))
        else:
            # if there is no txt file, get random rgba
            colorArray = (GetRandomRGBA(), GetRandomRGBA(), GetRandomRGBA(), GetRandomRGBA(), GetRandomRGBA())

        readFile.close()

    return colorArray

def ColorImage(img, colorArray):
    save(img)
    width, height = img.size
    pixelMatrix = img.load()
    colorIndex = 0

    for left in range(0, width):
        for top in range(0, height):
            if(pixelMatrix[left, top] == transparent):
                FloodFill(pixelMatrix, left, top, width, height, transparent, colorArray[colorIndex])
                save(img)
                colorIndex += 1
                # save the last index to paint the lines
                if(colorIndex >= len(colorArray) - 1):
                    colorIndex = 0
    # paint the lines
    SubstituteColor(img, black, colorArray[len(colorArray) - 1])
    save(img)

# get the line images, copy, colors them and deletes line files
def ColorAllImages():
    imgList = []
    imgIndex = 0
    
    # load lines from folder
    while True:
        try:
            img = Image.open(lineNames + str(imgIndex) + ".png").convert('RGBA')
        except:
            break
        imgList.append(img)
        imgIndex += 1
        
    # get new color set from the net
    imgIndex = 0
    colorArray = GetColorSet()
    for picture in imgList:
        colorCopy = picture.copy()
        os.remove(lineNames + str(imgIndex) + ".png")
        ColorImage(colorCopy, colorArray)
        FillFromEdges(colorCopy, white, transparent)
        colorCopy.save(coloredName + str(imgIndex) + ".png")
        imgIndex += 1


def resizePositionImg(image, position):
    (x, y) = position
    (w, h) = image.size
    resizeAttempts = 0
    while True:
        resized = image.resize((w + resizeOffset, h + resizeOffset))        
        resizedW, resizedH = resized.size
        resizeAttempts += 1
        
        goodRightBound = (x + resizedW <= baseWidth)
        goodBottomBound = (y + resizedH <= baseHeight - 280)
        
        if(goodRightBound & goodBottomBound):
            break
        if(not goodRightBound):
            x -= posOffset
        if(not goodBottomBound):
            y -= posOffset
            
    return resized, (x,y)

def JoinAllImages():
    imgBase = Image.new('RGBA', imgSize, color = white)
    imgList = []
    imgIndex = 0

    # get all collored images
    while True:
        try:
            colorPath = coloredName + str(imgIndex) + ".png"
            image = Image.open(colorPath).convert('RGBA')
            os.remove(colorPath)
        except:
            break
        imgList.append(image)
        imgIndex += 1

    locations = [(posOffset, 280 + posOffset), (360 - posOffset, 280 + posOffset), (posOffset, 640 - posOffset), (360 - posOffset, 640 - posOffset)]
    imgIndex = random.choice(range(0, len(locations)))

    # place them into defined positions, with a resize
    for image in imgList:
        pos = locations[imgIndex]
        resized, newPos = resizePositionImg(image, pos)
        imgBase.paste(resized, newPos, resized)
        save(imgBase)
        imgIndex += 1
        if(imgIndex >= len(locations)):
            imgIndex = 0   

def getNextProjectName():
    wordSize = 9
    i = 0
    num = 0

    # get the project number
    readFile = open(videoOptionsPath, "r")
    num = int(readFile.readline())
    readFile.close()

    # get a new name to the project from random word api
    try:
        while True:
            i += 1
            url = 'https://random-word-api.herokuapp.com/word?number=2&swear=0'
            results = requests.get(url)
            words = results.json()
            x = words[0]
            y = words[1]

            if(len(x) <= wordSize & len(y) <= wordSize):
                break
    except:
        #x = y = randomString(4)
        # get the random names from file
        # if no file, just give a random string 
        readFile = open(namesPath, "r")
        if(readFile):
            fileList = list(readFile)
            x = random.choice(fileList).rstrip()
            y = random.choice(fileList).rstrip()
        else:
            x = randomString(4)
            y = randomString(4)
        readFile.close()

    writeFile = open(videoOptionsPath, "w")
    writeFile.write(str(num+1))
    writeFile.close()

    return (str(num) + " - " + x.capitalize() + " " + y.capitalize())

def clearFramesPath():
    filelist = glob.glob(os.path.join(framesPath, "*.png"))
    for f in filelist:
        os.remove(f)

# adjust the last frames for making the timelapse
def AdjustFrames():
    num = len(glob.glob(framesPath + "*.png"))
    # get array with the last pictures
    numberOfPictures = 4
    toRepeat = []
    for i in range(0,numberOfPictures):
        imagePath = framesPath + "frame_" + str(num - 1 - i) + ".png"
        framing = cv2.imread(imagePath)
        toRepeat.append(framing)
        os.remove(imagePath)

    # invert and repeat itens in array to repeat  e.g. if repeatFrames = 2: (1,2,3) -> (3,3,2,2,1,1)
    toRepeat = toRepeat[::-1]
    toRepeat = [item for item in toRepeat for i in range(repeatFrames)]

    # write the pictures in 'toRepeat' array
    i = 0
    for img in toRepeat:
        cv2.imwrite(framesPath + "frame_" + str(num - numberOfPictures + i) + ".png", img)
        i += 1

    # get the last frame 
    newNum = len(glob.glob(framesPath + "*.png"))
    lastFrame = cv2.imread(framesPath + "frame_" + str(newNum - 1) + ".png")

    # make a final frame into RGB (without the alpha channel)
    lastFrameW, lastFrameH, channels = lastFrame.shape
    blankImage = np.zeros((lastFrameW, lastFrameH, 3), np.uint8)
    blankImage[:,:] = (255, 255, 255)
    finalFrame = np.uint8(lastFrame + blankImage)

    # write the last fade in frames
    fadeIn (blankImage, finalFrame, newNum, len=FPS)

# does the frames for the fade in for the timelapse
# pass images here to fade between, last frame index and length of transition
def fadeIn (img1, img2, numFrames, len=10): 
    lastFrame = None
    i = 0
    if(len <= 0):
        len = 1
    for IN in range(0, len):
        fadein = IN / float(len)
        dst = cv2.addWeighted(img1, 1-fadein, img2, fadein, 0)
        lastFrame = dst
        cv2.imwrite(framesPath + "frame_" + str(numFrames + i) + ".png", dst)
        i += 1
    
    # get the name and save the result from the last frame 
    global projectName
    projectName = linesPath + getNextProjectName()
    cv2.imwrite(projectName + ".png", lastFrame)
    
def randomString(N):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=N))

# choose a random tune from the audio folder
def chooseTune():
    numberOfTunes = len(glob.glob(audioPath + '*.mp3'))
    return random.choice(range(0, numberOfTunes))

# makes the timelapse
def MakeTimelapse():
    img_array = []
    index = 0
    for filename in glob.glob(framesPath + "*.png"):
        print("making video: loading frame " + str(index))
        path = framesPath + 'frame_' + str(index) + ".png"
        img = cv2.imread(path)

        height, width, channels = img.shape
        blank_image = np.zeros((baseHeight,baseWidth,3), np.uint8)
        blank_image[:,:] = (255,255,255)
        
        if(width < 720):
            blank_image[280:1000, 0:720] = cv2.resize(img, (720,720))
        elif(width > 720):
            blank_image[:, :] = cv2.resize(img, (720,1280))
        else:
            blank_image[:, :] = img[0:height,0:width]
            
        img_array.append(blank_image)
        index += 1

    # releases the video without sound
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(videoPath, fourcc, float(FPS), imgSize)
    for i in range(len(img_array)):
        video.write(img_array[i])
    video.release()

    # add sound to video and then release
    my_clip = mpe.VideoFileClip(videoPath)
    audio_background = mpe.AudioFileClip(audioPath + 'tune_' + str(chooseTune()) + '.mp3')
    final_clip = my_clip.set_audio(audio_background)
    audioVideoPath  = projectName + videoExtension 
    final_clip.write_videofile(audioVideoPath,fps=FPS,codec='mpeg4',bitrate=videoBitrate)
    os.remove(videoPath)

def processImage(img):
    # before anything, clean the frames path from frames of previous executions
    clearFramesPath()

    width, height = img.size
    
    # sometimes Image.open() will rotate the image, this will rotate it back in place
    if(width > height):
        img = img.rotate(-90, expand=True)
    
    # reduce resolution of main image and make a copy of it
    os.chdir(linesPath)
    imgCopy = img.copy().resize(normalizedSize)
    width, height = imgCopy.size

    # clean linework and remove lines of no intrest
    CleanLineWork(imgCopy)
    
    FillFromEdges(imgCopy, black, transparent)

    # crop and isolate lines
    imageBox = imgCopy.getbbox()
    croppedImage = imgCopy.crop(imageBox)

    IsolateImages(croppedImage)
    
    # get new colors and fill pictures
    # also get frames to use in the timelapse
    ColorAllImages()

    # create new base and make a collage
    JoinAllImages()

    # adjust frames for the video
    AdjustFrames()

    # timelapse maker
    MakeTimelapse()

    #reset frame counter
    global frameCounter
    frameCounter = 0
    
def getImageListFromDrive():    
    # get the id of the folder by name
    # then get the ids of the files inside
    folderID = drive_service.getFolderIdByName(driveDownloadFolder)
    bufferedFiles = drive_service.getIdFilesFromFolder(folderID)

    # download everything to imagesPath
    # delete downloaded files
    for fileId in bufferedFiles:
        drive_service.downloadFileById(fileId, imagesPath)

    os.chdir(imagesPath)

    img_array = []
    for filename in glob.glob(imagesPath +'*.jpg'): 
        im = Image.open(filename).convert('RGBA')
        img_array.append(im)
        os.remove(filename)

    return img_array, bufferedFiles

def uploadFinalToDrive():
    # upload to Drive
    folderID = drive_service.getFolderIdByName(driveUploadFolder)
    for filePathToUpload in glob.glob(linesPath + '*'): 
        drive_service.uploadFile(filePathToUpload, folderID)
        os.remove(filePathToUpload)  

#################
# main():
# initiate and get the drive service object
drive_service = drive()

# get images from download folder in the drive, and buffered files id
image_list, bufferedFiles = getImageListFromDrive()
bufferedIndex = -1

# try to process every image in 'image_list'
# only delete lines from drive if the processing is successful 
if(image_list):
    print("Found " + str(len(image_list)) + " images as of", datetime.now())
    for img in image_list:
        bufferedIndex += 1
        try:
            processImage(img)
            drive_service.deleteFileById(bufferedFiles[bufferedIndex])
        except:
            print('Failed to process image.. moving to the next one')
            continue
    uploadFinalToDrive()
else:
    print("No images found as of", datetime.now())
################
