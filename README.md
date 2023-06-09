# Watermarking-Medical-Image
A Python application implement an approach for watermarking of medical images 
based on the least significant bits (LSBs) that presented on this [Article](https://www.researchgate.net/publication/236166546_A_Watermarking_of_Medical_Image_Method_Based_LSB), 
it is intended to insert a encrypted set of data in a medical image, 
while the data specific to the patient and his diagnostic.


| Data Insertion  | Data Extraction |
| ------------- | ------------- |
| ![](https://github.com/DEVLOKER/Watermarking-Medical-Image/blob/main/screenshots/INSERT.jpg)  | ![](https://github.com/DEVLOKER/Watermarking-Medical-Image/blob/main/screenshots/EXTRACT.jpg)  |


## Used Modules

developed using:
- **opencv**: for detecting the important feature points using Harris corner detector
- **Crypto**: for encrypting and decrypting patient data using a secret key.
- **reedmuller**: algorithm used to verify the conformity of the obtained message and correct the possible alterations if they exist
- **Flask**: provide a micro web services.
- **Bootstrap and Jquery**: to code the frontend side of the project

install required by typing:
`pip install opencv-python opencv-python-contrib numpy flask crypto reedmuller`

<!--
[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)]()
[![FLASK](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)]()
[![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)]()
[![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)]()
[![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)]()
[![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)]()
[![Jquery](https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white)]()
-->

## Run it
- In the project directory, type: `flask --app app run`
- In browser navigate to: `http://127.0.0.1:5000`

## Results

#### Data Insertion
![](https://github.com/DEVLOKER/Watermarking-Medical-Image/blob/main/screenshots/insertion.gif)

#### Data Extraction
![](https://github.com/DEVLOKER/Watermarking-Medical-Image/blob/main/screenshots/extraction.gif)

#### Watermarked Image Attacks
![](https://github.com/DEVLOKER/Watermarking-Medical-Image/blob/main/screenshots/attack.gif)

