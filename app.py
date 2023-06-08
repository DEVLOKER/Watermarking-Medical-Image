
import json, uuid
import os, time
from flask import Flask, flash, jsonify, request, redirect, abort, url_for, render_template, send_file
# from werkzeug.datastructures import ImmutableMultiDict
from waitress import serve
from src.LSBer import LSBer
from src.Hasher import Hasher
from src.Helper import Helper


PORT = 5000
app = Flask(__name__, static_folder='static', static_url_path='/')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), Helper.INPUT_PATH)
PROCESSED_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), Helper.OUTPUT_PATH)
TMP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), Helper.TMP_PATH)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['TMP_FOLDER'] = TMP_FOLDER
app.config['SECRET_KEY'] = 'Sick Rat'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

JUST_UPLOAD, DETECT_POINTS, FILTER =  0, 1, 2

@app.route('/')
def index():
    Helper.cleanDirectory(UPLOAD_FOLDER)
    Helper.cleanDirectory(PROCESSED_FOLDER)

    return render_template('index.html')




@app.route('/get/<name>', methods=['GET'])
def get(name):
    files1 = Helper.getFilesInDirectory(UPLOAD_FOLDER)
    files2 = Helper.getFilesInDirectory(PROCESSED_FOLDER)
    files = files1 + files2
    for file in files:
        if file["name"] == name:
            path = os.path.join(UPLOAD_FOLDER, name)
            if os.path.exists(path):
                # return { "b64": Helper.tifToBase64JPG(path) }
                return send_file(path)
            path = os.path.join(PROCESSED_FOLDER, name)
            if os.path.exists(path):
                # return { "b64": Helper.tifToBase64JPG(path) }
                return send_file(path)
    abort(404)


@app.route('/download/<name>', methods=['GET'])
def download(name):
    files = Helper.getFilesInDirectory(PROCESSED_FOLDER)
    for file in files:
        if file["name"] == name:
            path = os.path.join(PROCESSED_FOLDER, name)
            if os.path.exists(path):
                return send_file(path)
    abort(404)



@app.route("/upload" , methods=['POST'])
def upload():

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    upload_files = request.files.getlist('file')
    if not upload_files:
        flash('No selected file')
        return redirect(request.url)
    
    if len(upload_files)>1:
        flash('select only one file')
        return redirect(request.url)

    file = upload_files[0]
    original_filename = file.filename
    extension = original_filename.rsplit('.', 1)[1].lower()
    sourceImage = str(uuid.uuid1()) + '.' + extension
    file.save(os.path.join(UPLOAD_FOLDER, sourceImage))
    size = os.path.getsize(os.path.join(UPLOAD_FOLDER, sourceImage))

    action = json.loads(request.form.get('action'))
    
    if action["type"] == JUST_UPLOAD:
        return {
            "ImageName": sourceImage,
            "size": size,
        }
    
    if action["type"] == DETECT_POINTS:
        #important_feature_points_list, harris_image, harris_image_name, metadata
        points_results = LSBer.importantFeaturePoints(os.path.join(UPLOAD_FOLDER, sourceImage), "tmp", extension)
        return {
            "sourceImage": sourceImage,
            "size": size,
            "importantFeaturePoints": points_results["list"],
            "harrisImageName" : points_results["harris_image_name"]
        }



@app.route("/insertion" , methods=['POST'])
def insertion():
    jsonData = json.loads(request.data)
    source_image = os.path.join(UPLOAD_FOLDER, jsonData["src"])
    data = []
    for key, value in jsonData["data"].items():
        data.append(value)
    hospitalSignature = f'{Hasher.hash( jsonData["hospitalSignature"] )}'
    data.append(hospitalSignature)
    key = jsonData["key"]
    try:
        # image, important_feature_points_list_original, harris_image, bin, watermarked_image, watermarked_image_name, issues
        insertion_results = LSBer.insert(source_image, data, key)
        if insertion_results["watermarked_image"] is None or insertion_results["watermarked_image_name"] is None:
            return { 
                "binary": insertion_results["bin"], 
                "watermarkedImageName": None, 
                "size": None, 
                "issues": insertion_results["issues"], 
                "message": "can't watermarked in image! needs at minimum {} points, found only {}".format(insertion_results["issues"][0], insertion_results["issues"][1])
            }
        return {
            "binary": insertion_results["bin"],
            "watermarkedImageName": insertion_results["watermarked_image_name"],
            "size": os.path.getsize(source_image),
            "issues": None,
            "message": "Operation ends successfully!"
        }
    except Exception as error:
        app.logger.error(error)
        return {
            "error": error
        }


@app.route("/extraction" , methods=['POST'])
def extraction():

    jsonData = json.loads(request.data)
    watermarkedImage = jsonData["src"] # os.path.join(Helper.INPUT_PATH, jsonData["src"])
    key = jsonData["key"]
    size = os.path.getsize(os.path.join(UPLOAD_FOLDER, watermarkedImage))

    try:
        extraction_results = LSBer.extract(os.path.join(UPLOAD_FOLDER, watermarkedImage), key)
        return {
            "binary": extraction_results["bin"],
            "data": extraction_results["str"]
        }
    except Exception as error:
        app.logger.error(error)
        return {
            "error": "error"
        }


@app.route("/filter" , methods=['POST'])
def filter():
    jsonData = json.loads(request.data)
    watermarked_image_name, filter, value = jsonData["src"], jsonData["filter"], jsonData["value"]
    watermarked_image_name = os.path.join(UPLOAD_FOLDER, watermarked_image_name)
    attacked_image, attacked_image_name = LSBer.attack(watermarked_image_name, attackType=filter, val=value)
    size = os.path.getsize(os.path.join(PROCESSED_FOLDER, attacked_image_name))
    return {
        "attackedImageName": attacked_image_name,
        "size": size,
    }



# app.logger.debug("debug log info")
# app.logger.info("Info log information")
# app.logger.warning("Warning log info")
# app.logger.error("Error log info")
# app.logger.critical("Critical log info")









if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
    # serve(app, host="0.0.0.0", port=PORT)