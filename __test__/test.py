#########################################################
#               Import libs
#########################################################
import sys, os, json

os.chdir(os.path.realpath(os.path.dirname(sys.argv[0])))
sys.path.append("..")

import cv2 as cv
from src.LSBer import LSBer
from src.Coder import Coder
from src.Hasher import Hasher
from src.Helper import Helper

os.chdir(os.path.realpath(os.path.join("..")))



#########################################################
#               Clean working directory
#########################################################

Helper.cleanDirectory(Helper.OUTPUT_PATH)


#########################################################
#               Insertion data
#########################################################
image_name = os.path.join("X-RayImages", "jpg", "0.jpg")
# data = { "name": "devloker", "date": "07-21-1990" }
# data = [ "devloker", "30", "seatle" ]
data = [ "devdevdevd0123456789", "lokerloker0123456789", "130", "m", "clinic01CL0123456789", f'{Hasher.hash("AE4569")}' ]
key = '#My_SickRat_Key#'

insertion_results = LSBer.insert(image_name, data, key)


#########################################################
#               Extraction data
#########################################################
if insertion_results["issues"]!=None:
    exit(0)
watermarked_image_name = os.path.join(Helper.OUTPUT_PATH, insertion_results["watermarked_image_name"])
extraction_results = LSBer.extract(watermarked_image_name, key)
print("Extracted data = {}".format(extraction_results["str"]))

Helper.deff_importantFeaturePoints(insertion_results["important_feature_points"], extraction_results["important_feature_points"])


#########################################################
#               Applying filters
#########################################################
# 1: blurFilter      2: averagingFilter     3: identityFilter   4: sharpeningFilter
# 5: gaussianFilter  6: medianFilter        7: bilateralFilter  8: sobelFilter
attacked_image, attacked_image_name = LSBer.attack(watermarked_image_name, attackType=1, val=1)

# Helper.deff_importantFeaturePoints(insertion_results["important_feature_points"], extraction_results["important_feature_points"])


#########################################################
#               Extraction data after applying filters
#########################################################

attacked_image_name2 = os.path.join(Helper.OUTPUT_PATH, attacked_image_name)
extraction_results2 = LSBer.extract(attacked_image_name2, key)
print("Extracted data = {}".format(extraction_results2["str"]))

"""
"""


"""
image_name = os.path.join("X-RayImages", "8-bits", "6.jpg")

metadata = Helper.getMetadata(image_name)
print(metadata)
# for key, value in metadata.items():
#     print(f"{key}: {value}")


jsonData = { "thresh": 0.045, "blockSize": 2, "ksize": 5, "k": 0.07 }
Helper.setMetadata(image_name, jsonData)
"""



"""




#########################################################
#               Show image
#########################################################
cv.imshow('Image Source: {}'.format(image_name), image)
cv.imshow('Harris Corner Detection', harris_image)
cv.imshow('watermarked Image {}'.format(watermarked_image_name), watermarked_image)
cv.imshow('Attacked Image: {}'.format(attacked_image_name), attacked_image)
if cv.waitKey(0) & 0xff == 27:
    cv.destroyAllWindows()
"""


