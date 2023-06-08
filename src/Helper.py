import sys, os, time, math, json, uuid, base64
import cv2 as cv
import numpy as np
from pyexiv2 import Image
import PIL



class Helper(object):

    INPUT_PATH = os.path.join(__name__, "..", "uploaded")
    OUTPUT_PATH = os.path.join(__name__, "..", "processed")
    TMP_PATH = os.path.join(__name__, "..", "tmp")
    IMAGE_EXTENSION = "bmp"


    @staticmethod
    def isGrayScale(img):
        if(len(img.shape)==2):
            return True
        else:
            h, w, depth = img.shape
            if(depth==1):
                return True
            else:
                return False

    @staticmethod
    def saveImage(img, name, extension=IMAGE_EXTENSION, gray=True):
        if gray and not Helper.isGrayScale(img):
            img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # bits = '8 bits' if Helper.isGrayScale(img) else '24 bits'
        # print(f'{name} : {bits}')
        name = f'{name}_{str(uuid.uuid1())}.{extension}'
        params = []
        if extension=="jpg":
            params = [cv.IMWRITE_JPEG_QUALITY, 90]
        cv.imwrite(os.path.join(Helper.OUTPUT_PATH, name), img, params)
        return name

    #________________________________________________________
    #                   Filters
    #________________________________________________________
    @staticmethod
    def blurFilter (img, val=5, extension=IMAGE_EXTENSION):
        dst = cv.blur(img,(val, val))
        # dst = cv.boxFilter(img, -1, (2, 2), normalize=True)
        name = Helper.saveImage(dst, "blurFilter", extension, gray=Helper.isGrayScale(img))
        return dst, name

    @staticmethod
    def averagingFilter(img, val=5, extension=IMAGE_EXTENSION):
        kernel = np.ones((val, val),np.float32)/25
        dst = cv.filter2D(img,-1,kernel)
        name = Helper.saveImage(dst, "averagingFilter", extension, gray=Helper.isGrayScale(img))
        return dst, name
    
    @staticmethod
    def identityFilter(img, val=1, extension=IMAGE_EXTENSION):
        kernel = np.array([[0, 0, 0],
                    [0, 1, 0],
                    [0, 0, 0]])
        dst = cv.filter2D(img,-1,kernel)
        name = Helper.saveImage(dst, "identityFilter", extension, gray=Helper.isGrayScale(img))
        return dst, name
    
    @staticmethod
    def sharpeningFilter(img, val=5, extension=IMAGE_EXTENSION):
        kernel = np.array([[0, -1,  0],
                    [-1,  val, -1],
                    [0, -1,  0]])
        dst = cv.filter2D(img,-1,kernel)
        name = Helper.saveImage(dst, "sharpeningFilter", extension, gray=Helper.isGrayScale(img))
        return dst, name

    @staticmethod
    def gaussianFilter(img, val=1, extension=IMAGE_EXTENSION):
        dst = cv.GaussianBlur(img,(val, val),cv.BORDER_DEFAULT)
        name = Helper.saveImage(dst, "gaussianFilter", extension, gray=Helper.isGrayScale(img))
        return dst, name

    @staticmethod
    def medianFilter(img, val=1, extension=IMAGE_EXTENSION):
        dst = cv.medianBlur(img, val)
        name = Helper.saveImage(dst, "medianFilter", extension, gray=Helper.isGrayScale(img))
        return dst, name

    @staticmethod
    def bilateralFilter(img, val=9, extension=IMAGE_EXTENSION):
        # dst = cv.bilateralFilter(img, -1, 5, 5)
        dst = cv.bilateralFilter(src=img, d=val, sigmaColor=75, sigmaSpace=75)
        name = Helper.saveImage(dst, "bilateralFilter", extension, gray=Helper.isGrayScale(img))
        return dst, name

    @staticmethod
    def sobelFilter(img, val=5, extension=IMAGE_EXTENSION):
        if(not Helper.isGrayScale(img)):
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        else:
            gray = img
        dst = cv.Sobel(gray, cv.CV_16S, 1, 1, ksize=val, scale=1, delta=0, borderType=cv.BORDER_DEFAULT)
        name = Helper.saveImage(dst, "SobelFilter", extension, gray=Helper.isGrayScale(img))
        return img, name



    @staticmethod
    def tifToBase64JPG(tif_path):
        tmp = os.path.join(Helper.TMP_PATH, 'tmp.jpg')
        im = PIL.Image.open(tif_path)
        im.save(tmp)
        b64 = ''
        with open(tmp, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode('utf-8')
        os.remove(tmp)
        return f'data:image/jpeg;base64,{b64}'


    @staticmethod
    def DecimalToBinary(dic):
        return str(format(dic,'08b'))

    @staticmethod
    def BinaryToDecimal(bin):
        return int(bin,2)

    @staticmethod
    def StringToBinary(str):
        bin = ''.join(format(ord(i), '08b') for i in str)
        return bin

    @staticmethod
    def BinaryToString(bin):
        n=int(bin, 2)
        str = n.to_bytes((n.bit_length() + 7) // 8, 'big')
        str = str.decode('unicode_escape')#  'utf-8'     'unicode_escape'    'ascii'    'cp1252'     
        return str
    
    @staticmethod
    def deff_pixels(img, otherImg):
        deff = 0
        w, h = img.shape[:2]
        for x in range(w):
            for y in range(h):
                if img[x][y] != otherImg[x][y]:
                    deff+=1
        print(f'{deff}')

    @staticmethod
    def deff_importantFeaturePoints(list, otherList):
        deff = 0
        l = min(len(list),len(otherList))
        for i in range(l):
            point_original = list[i]
            point_watermarked = otherList[i]
            if(point_original["x"]!=point_watermarked["x"] or point_original["y"]!=point_watermarked["y"]):
                deff+=1
        print(f'[{len(list)}/{len(otherList)}]: {deff}')

    
    @staticmethod
    def deff_binary(str, otherStr):
        deff = 0
        for i in range(len(str)):
            if(str[i]!=otherStr[i]):
                deff+=1
        print(deff)


    @staticmethod
    def loadImage(img):
        image = cv.imread(img, cv.IMREAD_ANYDEPTH | cv.IMREAD_UNCHANGED) if type(img).__name__=="str" else img
        # image = cv.imread(img, cv.IMREAD_GRAYSCALE) if type(img).__name__=="str" else img
        return image

    @staticmethod
    def fileNameExtension(path):
        # extension = imageName.rsplit('.', 1)[1].lower()
        name, extension = os.path.basename(path).split('.')
        return name, extension


    @staticmethod
    def saveJsonFile(fileName, data):
        with open(fileName, "w") as outfile:
            outfile.write(json.dumps(data, indent=4))

    @staticmethod
    def loadJsonFile(fileName):
        with open(fileName, "r") as outfile:
            data = json.load(outfile)
        return data


    @staticmethod
    def getMetadata(image_path):
        name, extension = Helper.fileNameExtension(image_path)
        if extension=="bmp":
            return None
        img = Image(image_path)
        if img.read_exif().get("Exif.Image.Make") is None:
            return {}
        metadata = img.read_exif()["Exif.Image.Make"]
        metadata = json.loads(str(metadata))
        img.close()
        return metadata if metadata!={} else None

    @staticmethod
    def setMetadata(image_path, new_metadata={}):
        img = Image(image_path)
        img.clear_exif()
        img.modify_exif({ "Exif.Image.Make": json.dumps(new_metadata) })
        img.close()


    @staticmethod
    def cleanDirectory(dir):
        now = time.time()
        timer = 0# 730 * 86400 # 60 minutes : 60 * 60      30 days : 30 * 86400
        for filename in os.listdir(dir):
            path = os.path.join(dir, filename)
            if os.path.getmtime(path) < now - timer:
                if os.path.isfile(path):
                    os.remove(path)

    @staticmethod
    def getFilesInDirectory(dir):
        files = []
        name_list = os.listdir(dir)
        full_list = [os.path.join(dir,i) for i in name_list]
        time_sorted_list = sorted(full_list, key=os.path.getmtime)
        sorted_filename_list = [ os.path.basename(i) for i in time_sorted_list]
        sorted_filename_list.reverse()
        
        for filename in sorted_filename_list:
            sz = os.path.getsize(os.path.join(dir, filename))
            files.append({"name":filename, "size": sz, "path": os.path.join(dir) })
        
        return files