from flask import Flask, render_template, request, send_from_directory
import tensorflow as tf
import numpy as np
from werkzeug.utils import secure_filename
import datetime
import cv2
import os, base64
from pathlib import Path

app = Flask(__name__)
global capturedImagePath
global capturedFacePathForHTML
global cwd
cwd = Path(__file__).parent.resolve()
capturedImagePath = ""
capturedImageForHTML = ""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/mainpage")
def mainpage():
    htmlManipulationMap = {"predictedOutput": "", "imageSource": "", "inputFieldDisplay": 'flex', "imageDivDisplay": 'none', "imageHeadingDisplay": 'none'}
    return render_template("mainpage.html", htmlManipulationMap=htmlManipulationMap)

@app.route("/predict", methods=['GET', 'POST'])
def predict():
    global cwd
    model_path = cwd / 'predictor.h5'
    model_path = str(model_path)
    loaded_model = tf.keras.models.load_model(model_path, compile=False)
    loaded_model.compile(loss='categorical_crossentropy', optimizer=tf.keras.optimizers.Nadam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07, name='Nadam'), metrics=['accuracy'])
    class_mapping = {'0': 'Angry', '1': 'Disgust', '2': 'Fear', '3': 'Happy', '4': 'Sad', '5': 'Surprise', '6' : 'Neutral'}
    inputImage = request.files['input-face']
    # inputImage.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(inputImage.filename)).replace("\\", "/"))
    imagePath = cwd / "static/Uploads" / secure_filename(inputImage.filename)
    imagePathForHTML = "../static/Uploads/" + secure_filename(inputImage.filename)
    inputImage.save(imagePath)
    loadedImg = tf.keras.utils.load_img(imagePath, target_size=(48,48,1), color_mode = "grayscale")
    loadedImg = tf.keras.utils.img_to_array(loadedImg)/255
    finalImage = np.array([loadedImg])
    predictedOutput = class_mapping[str(loaded_model.predict(finalImage).argmax())]
    # os.remove("./static/Uploads/" + secure_filename(inputImage.filename))
    htmlManipulationMap = {"predictedOutput": predictedOutput, "imageSource": imagePathForHTML, "inputFieldDisplay": "none", "imageDivDisplay": 'flex', "imageHeadingDisplay": 'flex'}
    return render_template('mainpage.html', htmlManipulationMap=htmlManipulationMap)

@app.route('/webcampage')
def webcampage():
    htmlManipulationMap = {"predictedOutput": "",  "faceImageSource": "", "capturedFaceDisplay": "none", "startBtnDisplay": "block", "capturedImageHeading": "none"}
    return render_template("webcampage.html", htmlManipulationMap=htmlManipulationMap)

@app.route('/save-snapshot', methods=['POST'])
def save_snapshot():
    global capturedImagePath
    global cwd
    global capturedImageForHTML
    app.config['UPLOAD_FOLDER'] = cwd / "static/Uploads/"
    snapshot = request.form['snapshot']
    snapshot_data = snapshot.split(',')[1]
    now = datetime.datetime.now()
    capturedImageName = now.strftime("%Y") + now.strftime("%b") + now.strftime("%d") + now.strftime("%H") + now.strftime("%M") + now.strftime("%S") + now.strftime("%f") + ".png"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], capturedImageName).replace("\\", "/")
    capturedImageForHTML = capturedImageName
    with open(filepath, 'wb') as f:
        f.write(base64.b64decode(snapshot_data))
    capturedImagePath = str(filepath)
    return send_from_directory(app.config['UPLOAD_FOLDER'], capturedImageName)

@app.route("/predict-webcam", methods=['GET', 'POST'])
def predictWebcam():
    global cwd
    global capturedImagePath
    global capturedImageForHTML
    face_roi = np.array([None])
    htmlManipulationMap = {"predictedOutput": "No Face Found", "faceImageSource": "Null", "capturedFaceDisplay": "none"}
    trainedModelPath = cwd / 'predictor.h5'
    trainedModelPath = str(trainedModelPath)
    loaded_model = tf.keras.models.load_model(trainedModelPath, compile=False)
    loaded_model.compile(loss='categorical_crossentropy', optimizer=tf.keras.optimizers.Nadam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07, name='Nadam'), metrics=['accuracy'])
    class_mapping = {'0': 'Angry', '1': 'Disgust', '2': 'Fear', '3': 'Happy', '4': 'Sad', '5': 'Surprise', '6' : 'Neutral'}
    capturedImage = cv2.imread(capturedImagePath)
    capturedImageGray = cv2.cvtColor(capturedImage, cv2.COLOR_RGB2GRAY)
    haarCascadePath = cwd / 'static/haarcascade_frontalface_default.xml'
    haarCascadePath = str(haarCascadePath)
    faceCascade = cv2.CascadeClassifier(haarCascadePath)
    faces = faceCascade.detectMultiScale(capturedImage, 1.1,4)
    for x, y, w, h in faces:
        roi_gray = capturedImageGray[y:y+h, x:x+w]
        # roi_color = capturedImage[y:y+h, x:x+w]
        cv2.rectangle(capturedImage, (x,y), (x+w, y+h), (255, 0,0),2)
        faces = faceCascade.detectMultiScale(roi_gray)
        if len(faces) == 0:
            return render_template('webcampage.html', htmlManipulationMap=htmlManipulationMap)
        else:
            for (ex, ey, ew, eh) in faces:
                face_roi = roi_gray[ey: ey+eh, ex : ex+ew]
    if (face_roi.all() != None):
        capturedFace = cv2.cvtColor(face_roi,cv2.COLOR_BGR2RGB)
    else:
        return render_template('webcampage.html', htmlManipulationMap=htmlManipulationMap)
    capturedFacePath = capturedImagePath
    capturedFacePath = str(capturedFacePath)
    capturedFacePath = capturedFacePath.replace('Uploads/', 'Uploads/face')
    cv2.imwrite(capturedFacePath, capturedFace)
    capturedImageForHTML = "../static/Uploads/" + "face" + capturedImageForHTML
    loadedImg = tf.keras.utils.load_img(capturedFacePath, target_size=(48,48,1), color_mode = "grayscale")
    loadedImg = tf.keras.utils.img_to_array(loadedImg)/255
    finalImage = np.array([loadedImg])
    predictedOutput = class_mapping[str(loaded_model.predict(finalImage).argmax())]
    os.remove(capturedImagePath)
    htmlManipulationMap = {"predictedOutput": predictedOutput, "faceImageSource": capturedImageForHTML, "capturedFaceDisplay": "flex", "startBtnDisplay": "none", "capturedImageHeading": "block"}
    return render_template('webcampage.html', htmlManipulationMap=htmlManipulationMap)

if __name__ == "__main__":
    app.run(debug=True)