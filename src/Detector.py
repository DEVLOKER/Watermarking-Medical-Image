# Laplacian 2nd order derivative
import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys, os, json
from src.Helper import Helper


class Detector(object):
    # First name: 20 bytes, Last name: 20 Bytes, Age: 03 Bytes, Sex: 01 Byte, Clinic name: 20 Bytes, Signature: 40 Bytes
    # Total: 20+20+3+1+20+40 = 104 Bytes
    # Separators: 04 Bytes => 109 bits
    # encrypting: (64~218) Bytes => 173 Bytes
    # EndOff: (1+2) Bytes => 176 Bytes = 1408 bits 
    # encoding: x2 => 2816 bits ~~ 3000 bits
    max_bits = 3000

    def __init__(self, img) -> None:
        self.image = cv2.imread(img) if type(img).__name__=="str" else img
        if(Helper.isGrayScale(img)):
            self.gray_image = img
        else:
            self.gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #########################################################
    #               Edge Detection
    #########################################################
        
    def laplacian_edge_detection(self):
        self.__noise_reduction(3)
        edges = cv2.Laplacian(self.gray_image, -1, ksize=5, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        # edges = cv2.Laplacian(self.blured_image, cv2.CV_64F, ksize=7)
        return self.__important_feature_points(edges)

    def canny_edge_detection(self, sigma=0.33):
        self.__noise_reduction(1)
        md = np.median(self.image)
        lower_value = int(max(0, (1.0-sigma) * md))
        upper_value = int(min(255, (1.0+sigma) * md))
        edges = cv2.Canny(image=self.blured_image, threshold1=lower_value, threshold2=upper_value)
        return self.__important_feature_points(edges)

    def sobel_edge_detection(self):
        self.__noise_reduction(3)
        edges = cv2.Sobel(self.blured_image, cv2.CV_8U, 1, 1, ksize=5, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        # edges = cv2.Sobel(src=self.blured_image, ddepth=cv2.CV_64F, dx=dx, dy=dy, ksize=ksize)
        return self.__important_feature_points(edges)
        
    #########################################################
    #               Corner Detection
    #########################################################

    def harris_corner_detection(self):
        self.__noise_reduction(3)
        gray = np.float32(self.blured_image)
        dest = cv2.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)
        dest = cv2.dilate(dest, None)
        thresh = 0.01 * dest.max()
        less_important_pixels, edges, drawn_image = self.__important_feature_points(dest, thresh)
        return less_important_pixels, edges, drawn_image

    def ShiTomasi_corner_detection(self):
        dest = cv2.goodFeaturesToTrack(self.gray_image, maxCorners=Detector.max_bits, qualityLevel=0.01, minDistance=10)
        dest = np.int0(dest)
        corners = []
        for i in dest:
            y, x = i.ravel().tolist()
            corners.append((x, y))
        return self.__important_feature_points(self.gray_image, thresh=None, points=corners)
    
    def SIFT_corner_detection(self):
        self.__noise_reduction(5)
        # sift = cv2.FastFeatureDetector_create()#threshold = 500000)#nonmaxSuppression=True
        # sift.setNonmaxSuppression(False)
        # sift = cv2.xfeatures2d.SIFT_create(nfeatures=Detector)
        sift = cv2.SIFT_create(nfeatures=Detector.max_bits)
        kp, descriptors = sift.detectAndCompute(self.blured_image, None)
        # kp = sift.detect(self.blured_image, None)
        
        
        pts = cv2.KeyPoint_convert(kp)
        pts = np.int0(pts)
        corners = []
        for i in pts:
            y, x = i.ravel().tolist()
            corners.append((x, y))
        return self.__important_feature_points(self.gray_image, thresh=None, points=corners)

    def ORB_corner_detection(self):
        orb = cv2.ORB_create(nfeatures=Detector.max_bits)
        kp, des = orb.detectAndCompute(self.gray_image, None)
        pts = cv2.KeyPoint_convert(kp)
        pts = np.int0(pts)
        corners = []
        for i in pts:
            y, x = i.ravel().tolist()
            corners.append((x, y))
        return self.__important_feature_points(self.gray_image, thresh=None, points=corners)


    #########################################################
    #               Helper
    #########################################################

    def __noise_reduction(self, noise=3):
        self.blured_image = cv2.GaussianBlur(self.gray_image, (noise, noise), 0)
    
    def __important_feature_points(self, edges, thresh=None, points=None):
        if(Helper.isGrayScale(self.image)):
            drawn_image = cv2.cvtColor(self.gray_image, cv2.COLOR_GRAY2RGB)
        else:
            drawn_image = self.image.copy()

        less_important_pixels = []
        color = 253, 110, 13 # 180, 80, 180 # BGR
        keypoints = []
        if points!=None:
            # points = points[:Detector.max_bits]
            for p in points:
                x, y = p
                if len(less_important_pixels) >= Detector.max_bits:
                    break
                less_important_pixels.append( {"x":x, "y":y, "val": int(self.gray_image[x, y]) } )
                # keypoints.append(cv2.KeyPoint(y, x, 1))
                Detector.__drawPoint(drawn_image, x, y, color)
        else:
            w, h = edges.shape[:2]
            for x in range(w):
                for y in range(h):
                    if len(less_important_pixels) >= Detector.max_bits:
                        break
                    if Detector.__is_important_pixel(edges, x, y, thresh):
                        less_important_pixels.append( {"x":x, "y":y, "val": int(self.gray_image[x, y])} )
                        # keypoints.append(cv2.KeyPoint(y, x, 1))
                        Detector.__drawPoint(drawn_image, x, y, color)

        # keypoints.sort(key=lambda kp: kp.response, reverse=True)
        # keypoints = keypoints[:Detector.max_bits]
        # # DRAW_MATCHES_FLAGS_DEFAULT  DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS  DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS
        # drawn_image = cv2.drawKeypoints(self.image, keypoints, 0)#, (color), flags=cv2.DRAW_MATCHES_FLAGS_DEFAULT)
        return less_important_pixels, edges, drawn_image

    @staticmethod
    def __is_important_pixel(img, x, y, thresh):
        try:
            if thresh!=None:
                return img[x, y] > thresh
            return img[x, y][0] == 255
        except Exception as e:
            return img[x, y] == 255
        
    @staticmethod
    def __drawPoint(img, x, y, color):
        _w = 2*int(img.shape[1]/256)
        _h = 2*int(img.shape[0]/256)
        # cv2.line(img,(y,x-_w),(y,x+_w),(color),1)
        # cv2.line(img,(y-_h,x),(y+_h,x),(color),1)
        cv2.circle(img, (y, x), 2, (color), -1)

"""
image_name = os.path.join("X-RayImages", "8-bits", "tmp", "_6.bmp")
detector1 = Detector(image_name)
less_important_pixels, edges, drawn_image = detector1.laplacian_edge_detection()
print(len(less_important_pixels))



filtered_image = cv2.GaussianBlur(detector1.image, (3, 3), 0)
# cv.imwrite(os.path.join(Helper.OUTPUT_PATH, name), img)


detector2 = Detector(filtered_image)
less_important_pixels, edges, drawn_image = detector2.laplacian_edge_detection()
print(len(less_important_pixels))


output = [detector1.image, detector2.image]
titles = ['Original', 'Passed through HPF']

for i in range(2):
    plt.subplot(1, 2, i + 1)
    plt.imshow(output[i], cmap='gray')
    plt.title(titles[i])
    plt.xticks([])
    plt.yticks([])
plt.show()
"""












"""
# Load the original image
image = cv2.imread('./1.bmp', 1)#cv2.IMREAD_ANYDEPTH | cv2.IMREAD_UNCHANGED)

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Compute pixel importance on the original image
less_important_mask = np.where(cv2.Laplacian(gray, cv2.CV_64F).var() < 100, 255, 0).astype(np.uint8)
print(less_important_mask)

# Store positions of less important pixels
less_important_pixels = []
for y in range(image.shape[0]):
    for x in range(image.shape[1]):
        if less_important_mask[y, x] == 255:
            less_important_pixels.append((y, x))

# Apply a filter to the image
filtered_image = cv2.GaussianBlur(image, (5, 5), 0)  # Example: Gaussian blur filter

# Convert the filtered image to grayscale
filtered_gray = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2GRAY)

# Compute pixel importance on the filtered image
filtered_less_important_mask = np.where(cv2.Laplacian(filtered_gray, cv2.CV_64F).var() < 100, 255, 0).astype(np.uint8)

# Reuse less important pixel positions on the filtered image
filtered_less_important_pixels = []
for (y, x) in less_important_pixels:
    if filtered_less_important_mask[y, x] == 255:
        filtered_less_important_pixels.append((y, x))

# Display the positions of less important pixels
print("Less Important Pixels (Original Image):")
for (y, x) in less_important_pixels:
    print(f"({y}, {x})")

print("\nLess Important Pixels (Filtered Image):")
for (y, x) in filtered_less_important_pixels:
    print(f"({y}, {x})")
"""