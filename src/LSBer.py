
import sys, os, time, math, json, uuid
import numpy as np
import cv2 as cv
from src.Coder import Coder
from src.Crypter import Crypter
from src.Detector import Detector
from src.Helper import Helper



class LSBer(object):

    #########################################################
    #               static variables
    #########################################################
    END = 16*"0"


    # def __init__(self, imageName=None):
    #     pass

    @staticmethod
    def insert(imageName, data, key):
        source_image = Helper.loadImage(imageName)
        name, extension = Helper.fileNameExtension(imageName)
        Helper.saveImage(source_image, "original_image", extension, gray=Helper.isGrayScale(source_image))
        points_results = LSBer.importantFeaturePoints(source_image, "insertion", extension)
        bin = LSBer.encodeData(source_image, data, key)
        watermarked_image, watermarked_image_name, issues = LSBer.embedDataIntoImage(source_image, extension, points_results["list"], bin)
        if issues==None and extension!="bmp":
            Helper.setMetadata(os.path.join(Helper.OUTPUT_PATH, watermarked_image_name), points_results["metadata"])
        return {
            "source_image" : source_image,
            "important_feature_points": points_results["list"],
            "metadata": points_results["metadata"],
            "harris_image": points_results["harris_image"],
            "bin": bin,
            "watermarked_image": watermarked_image,
            "watermarked_image_name": watermarked_image_name,
            "issues": issues
        }

    @staticmethod
    def extract(imageName, key):
        watermarked_image = Helper.loadImage(imageName)
        name, extension = Helper.fileNameExtension(imageName)
        metadata = Helper.getMetadata(imageName)
        points_results = LSBer.importantFeaturePoints(watermarked_image, "extraction", extension, metadata)
        bin = LSBer.extractDataFromImage(watermarked_image, points_results["list"])
        str = LSBer.decodeWatermarkedData(bin, key)
        return {
            "str": str,
            "bin": bin,
            "important_feature_points": points_results["list"],
            "harris_image": points_results["harris_image"],
            "harris_image_name": points_results["harris_image_name"]
        }

    @staticmethod
    def attack(imageName, attackType=1, val=None):
        watermarked_image = Helper.loadImage(imageName)
        name, extension = Helper.fileNameExtension(imageName)
        # metadata = Helper.getMetadata(os.path.join(Helper.INPUT_PATH, imageName))
        match attackType:
            case 1:
                attacked_image, image_name = Helper.blurFilter(watermarked_image, val, extension)
            case 2:
                attacked_image, image_name = Helper.averagingFilter(watermarked_image, val, extension)
            case 3:
                attacked_image, image_name = Helper.identityFilter(watermarked_image, val, extension)
            case 4:
                attacked_image, image_name = Helper.sharpeningFilter(watermarked_image, val, extension)
            case 5:
                attacked_image, image_name = Helper.gaussianFilter(watermarked_image, val, extension)
            case 6:
                attacked_image, image_name = Helper.medianFilter(watermarked_image, val, extension)
            case 7:
                attacked_image, image_name = Helper.bilateralFilter(watermarked_image, val, extension)
            case 8:
                attacked_image, image_name = Helper.sobelFilter(watermarked_image, val, extension)
            case _:
                attacked_image, image_name = Helper.blurFilter(watermarked_image, val, extension)

        # Helper.setMetadata(os.path.join(Helper.OUTPUT_PATH, image_name), metadata)
        return attacked_image, image_name


    #########################################################
    #               Features
    #########################################################
    #________________________________________________________
    #                   Insertion
    #________________________________________________________
    @staticmethod
    def watermarkedColor(pixel, binary):
        new_pixel_value = pixel | 0x01 if binary=="1" else pixel & 0xFE
        return new_pixel_value

    @staticmethod
    def watermarkedPixel(img, x, y, data):
        if(Helper.isGrayScale(img)):
            color = LSBer.watermarkedColor(img[x][y], data)
            return color
        else:
            # r_data, g_data, b_data = data
            r, g, b = img[x][y]
            r = LSBer.watermarkedColor(r, data)
            # g = LSBer.watermarkedColor(g, g_data)
            # b = LSBer.watermarkedColor(b, b_data)
            return [r, g, b]

    @staticmethod
    def embedDataIntoImage(img, extension, important_feature_points_list, bin):
        if(len(important_feature_points_list)<=len(bin)):
            print("can't watermarked in image![{} , {}]".format(len(important_feature_points_list), len(bin)))
            return None, None, (len(bin), len(important_feature_points_list))

        watermarked_image = img.copy()
        for i in range(len(bin)):
            point = important_feature_points_list[i]
            x, y, val = [point[k] for k in point.keys()]
            watermarked_image[x][y] = LSBer.watermarkedPixel(watermarked_image, x, y, bin[i])
        
        watermarked_image_name = Helper.saveImage(watermarked_image, "watermarked_image", extension, gray=Helper.isGrayScale(img))
        return watermarked_image, watermarked_image_name, None

    @staticmethod
    def encodeData(img, data, key):
        data_type = type(data).__name__
        if(data_type=="dict"):
            text = json.dumps(data, indent=0)
        if(data_type=="list"):
            text = ','.join(data)

        encrypted_message = Crypter(key=key).encrypt(text)
        bin = Coder.encode(encrypted_message)

        return bin

    #________________________________________________________
    #                   Extraction
    #________________________________________________________
    @staticmethod
    def extractColor(pixel):
        binary = pixel & 0x01
        return str(binary)

    @staticmethod
    def extractPixel(img, x, y):
        if(Helper.isGrayScale(img)):
            data = LSBer.extractColor(img[x][y])
            return data
        else:
            data = ""
            r, g, b = img[x][y]
            data+= LSBer.extractColor(r)
            # data+= LSBer.extractColor(g)
            # data+= LSBer.extractColor(b)
            return data

    @staticmethod
    def extractDataFromImage(watermarked_image, important_feature_points_list):
        bin = ""
        for i in range(len(important_feature_points_list)):
            point = important_feature_points_list[i]
            x, y, val = [point[k] for k in point.keys()] # , val
            bin += LSBer.extractPixel(watermarked_image, x, y)

        bits = len(LSBer.END)#8
        # bin = bin.split(LSBer.END)[0]
        # tmp = [bin[i:i+bits] for i in range(0, len(bin), bits)]
        for i in range(0, len(bin), bits):
            byte = bin[i:i+bits]
            if byte==LSBer.END:
                return bin[:i+bits]
            else:
                pass
        return bin

    @staticmethod
    def decodeWatermarkedData(bin, key):
        bits = 8
        str = ""
        bin = Coder.decode(bin)
        bin = [bin[i:i+bits] for i in range(0, len(bin), bits)]
        for byte in bin:
            if len(byte)==bits:
                try:
                    str+= Helper.BinaryToString(byte)
                except Exception as e:
                    pass
        extracted_data = ""
        str = Crypter(key=key).decrypt(str)
        try:
            extracted_data = json.loads(str)
        except:
            try:
                extracted_data = str.split(",")
            except:
                extracted_data = ""
        return extracted_data
    


    #########################################################
    #               Helper
    #########################################################
    #________________________________________________________
    #                   Tools
    #________________________________________________________
    @staticmethod
    def importantFeaturePoints(img, name, extension, metadata=None):
        if type(img).__name__=="str":
            name_, extension = Helper.fileNameExtension(img)
            img = cv.imread(img, cv.IMREAD_ANYDEPTH | cv.IMREAD_UNCHANGED)

        detector = Detector(img)

        list, edges, harris_image = detector.harris_corner_detection()

        harris_image_name = Helper.saveImage(harris_image, f'harris_{name}_image', extension, gray=False)
        Helper.saveJsonFile(os.path.join(Helper.OUTPUT_PATH, f'harris_{name}_points.json'), list)
        return {
            "list": list,
            "harris_image": harris_image,
            "harris_image_name": harris_image_name,
            "metadata": metadata
        }