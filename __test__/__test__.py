import sys, os, json

os.chdir(os.path.realpath(os.path.dirname(sys.argv[0])))
sys.path.append("..")

from src.LSBer import LSBer
from src.Coder import Coder
from src.Hasher import Hasher
from src.Helper import Helper

os.chdir(os.path.realpath(os.path.join("..")))

import cv2
import numpy as np



def detect_featured_pixels(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    positions = []
    max_corners = 2000

    # # Create SIFT detector
    # # sift = cv2.FastFeatureDetector_create()
    # sift = cv2.SIFT_create(nfeatures=max_corners)
    # keypoints, descriptors = sift.detectAndCompute(gray, None)
    # positions = [tuple(map(int, kp.pt)) for kp in keypoints]

    # # Create SIFT detector
    # sift = cv2.FastFeatureDetector_create(nonmaxSuppression=True)# threshold = 50000, 
    # # Detect keypoints and compute descriptors
    # keypoints = sift.detect(gray, None)
    # # Convert keypoints to positions
    # positions = [tuple(map(int, kp.pt)) for kp in keypoints]


    # orb = cv2.ORB_create(nfeatures=max_corners)
    # keypoints, descriptors = orb.detectAndCompute(gray, None)
    # positions = [tuple(map(int, kp.pt)) for kp in keypoints]

    # corners = cv2.goodFeaturesToTrack(gray, maxCorners=max_corners, qualityLevel=0.01, minDistance=10)
    # # corners = np.int64(corners)
    # keypoints = [cv2.KeyPoint(x, y, 10) for [[x, y]] in corners]
    # positions = [tuple(map(int, kp.pt)) for kp in keypoints]
    # # positions = [tuple(corner[0]) for corner in corners]


    # Detect corners using the Harris corner detector
    corners = cv2.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)
    
    # Normalize the corner response
    # cv2.normalize(corners, corners, 0, 255, cv2.NORM_MINMAX)
    # corners = np.uint8(corners)
    thresh = 0.01 * cv2.dilate(corners, None).max()
    
    # Find the local maxima of the corners
    # _, corners = cv2.threshold(corners, 0.01 * corners.max(), 255, cv2.THRESH_BINARY)
    # cv2.imshow('corners', corners)

    # Convert corners to keypoints
    keypoints = []
    for x in range(corners.shape[0]):
        for y in range(corners.shape[1]):
            # if corners[x, y] == 255:
            if corners[x,y] > thresh:
                keypoints.append(cv2.KeyPoint(y, x, 1))
    
    # Sort keypoints based on the corner response
    keypoints.sort(key=lambda kp: kp.response, reverse=True)
    
    # Select the top max_corners keypoints
    keypoints = keypoints[:max_corners]

    # Convert keypoints to positions
    positions = [tuple(map(int, kp.pt)) for kp in keypoints]
    """    """

    drawn_image = image.copy()
    drawn_image = cv2.drawKeypoints(gray, keypoints, drawn_image)
    cv2.imshow('drawn_image', drawn_image)
    # print(len(positions))
    return positions

def modify_LSBer(image, positions):
    modified_image = image.copy()

    # Iterate over each pixel in the image
    # for i in range(modified_image.shape[0]):
    #     for j in range(modified_image.shape[1]):

    # Iterate over each pixel in the position
    for position in positions:
        j, i = position
        # Get the pixel value
        pixel = modified_image[i, j]

        binary = "1" if (i+j)%2==0 else "0"
        # Modify the LSBer of each color channel
        for k in range(len(pixel)):  # Iterate over RGB channels
            if k==2:
                newPixel = pixel[k] | 0x01 if binary=="1" else pixel[k] & 0xFE
                pixel[k] = newPixel
                # pixel[k] = (pixel[k] & 0xFE) | (k % 2)  # Set LSBer to 0 or 1 based on channel index
            
        # Update the modified pixel value
        modified_image[i, j] = pixel

    return modified_image

def apply_filter(image):
    # Apply your desired filter to the image
    filtered_image = cv2.GaussianBlur(image, (5, 5), 0)
    return filtered_image

def compare_positions(positions1, positions2):
    positions_match = set(positions1) == set(positions2)
    # Print the result
    # if positions_match:
    #     print("The positions before and after filtering match.")
    # else:
    #     print("The positions before and after filtering do not match.")
    deff = 0
    l = min(len(positions1),len(positions2))
    for i in range(l):
        x1, y1 = positions1[i]
        x2, y2 = positions2[i]
        # print(f'{(x1,y1)} <> {(x2, y2)}')
        if x1!=x2 or y1!=y2:
            deff+=1
    print(f'[{len(positions1)}/{len(positions2)}]: {deff}')
    return positions_match


def main():
    # Load the image
    image_name = os.path.join("X-RayImages", "24-bits", "jpg", "4.jpg")
    image = cv2.imread(image_name)

    # Detect featured pixels in the original image
    original_positions = detect_featured_pixels(image)


    # Apply LSBer modification to the image
    modified_image = modify_LSBer(image, original_positions)

    # Detect featured pixels in the modified image
    modified_positions = detect_featured_pixels(modified_image)

    # Compare the positions before and after filtering
    positions_match = compare_positions(original_positions, modified_positions)



    # Apply the filter to the image
    filtered_image = apply_filter(image)

    # Detect featured pixels in the filtered image
    filtered_positions = detect_featured_pixels(filtered_image)

    # Compare the positions before and after filtering
    positions_match = compare_positions(original_positions, filtered_positions)

    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()
    
# main()
pixel = 8

# v = pixel & 0x01
# print(v)

# binary = "1"
# newPixel = pixel | 0x01 if binary=="1" else pixel & 0xFE
# print(newPixel)

"""
"""