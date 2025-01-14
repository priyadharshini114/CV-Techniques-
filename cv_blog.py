# -*- coding: utf-8 -*-
"""CV_Blog.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IE9yPOQ7FcZni4KgGTn_CdjyB5drscRv
"""

!pip install Keras-Preprocessing

from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions

"""**Image Classification (TensorFlow/Keras)**"""

import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions

# Load the VGG16 model pre-trained on ImageNet
model = VGG16(weights='imagenet')

# Path to your image file in Google Colab environment
img_path = 'flower.jpg'  # Update with the correct path

# Load and preprocess the image using Keras preprocessing functions
img = image.load_img(img_path, target_size=(224, 224))
x = image.img_to_array(img)
x = preprocess_input(x)
x = tf.expand_dims(x, axis=0)

# Make predictions
preds = model.predict(x)

# Decode and print the top prediction
label = decode_predictions(preds, top=1)[0][0]
print('Predicted:', label)

# Display the image using matplotlib
plt.imshow(img)
plt.axis('off')
plt.title(f'Predicted: {label[1]} ({label[2]*100:.2f}%)')
plt.show()

"""**Semantic Segmentation (OpenCV + DeepLabV3)**"""

import torch
import torchvision
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# Load pre-trained DeepLabV3 model
model = torchvision.models.segmentation.deeplabv3_resnet101(pretrained=True)
model.eval()

# Define the transformation for input images
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Load and transform the image
image_path = "/content/dog_640.jpg"  # Replace with your image path
image = Image.open(image_path).convert("RGB")
input_tensor = transform(image).unsqueeze(0)

# Perform semantic segmentation
with torch.no_grad():
    output = model(input_tensor)['out'][0]
output = output.argmax(0)

# Define a color map for visualization
color_map = np.random.randint(0, 255, size=(21, 3), dtype=np.uint8)
color_map[0] = [0, 0, 0]  # Background color

# Create a color-coded segmentation map
segmentation_map = color_map[output.cpu().numpy()]

# Visualize the results
plt.figure(figsize=(15, 5))

plt.subplot(131)
plt.title("Original Image")
plt.imshow(image)
plt.axis('off')

plt.subplot(132)
plt.title("Segmentation Map")
plt.imshow(segmentation_map)
plt.axis('off')

plt.subplot(133)
plt.title("Overlay")
plt.imshow(image)
plt.imshow(segmentation_map, alpha=0.6)
plt.axis('off')

plt.tight_layout()
plt.show()

"""**Instance Segmentation (Mask R-CNN)**"""

!pip install norfair
!pip install "git+https://github.com/facebookresearch/detectron2.git@v0.5#egg=detectron2"
!pip uninstall -y detectron2
# !pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu111/torch1.9/index.html

import torch
import torchvision
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.transforms import transforms
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# Load pre-trained Mask R-CNN model
model = maskrcnn_resnet50_fpn(pretrained=True)
model.eval()

# Define the transformation for input images
transform = transforms.Compose([
    transforms.ToTensor(),
])

# Load and transform the image
image_path = "/content/dog_640.jpg"  # Replace with your image path
image = Image.open(image_path).convert("RGB")
image_tensor = transform(image)

# Convert image to numpy array
image_np = np.array(image)

# Perform instance segmentation
with torch.no_grad():
    prediction = model([image_tensor])

# Get the results
boxes = prediction[0]['boxes'].cpu().numpy()
labels = prediction[0]['labels'].cpu().numpy()
scores = prediction[0]['scores'].cpu().numpy()
masks = prediction[0]['masks'].cpu().numpy()

# Visualize the results
fig, axes = plt.subplots(1, 2, figsize=(5, 8))

# Original image
axes[0].imshow(image_np)
axes[0].set_title('Original Image')
axes[0].axis('off')

# Segmented image
axes[1].imshow(image_np)

for box, label, score, mask in zip(boxes, labels, scores, masks):
    if score > 0.5:  # Only show predictions with confidence > 50%
        x1, y1, x2, y2 = box.astype(int)
        axes[1].add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1,
                                          fill=False, color='r', linewidth=2))
        axes[1].text(x1, y1, f"{label}: {score:.2f}", color='r')

        mask = mask.squeeze()
        mask = np.expand_dims(mask, axis=-1)  # Add channel dimension
        masked_image = np.where(mask > 0.5, image_np * 0.7 + np.array([255, 0, 0]) * 0.3, image_np)
        axes[1].imshow(masked_image.astype(np.uint8), alpha=0.5)

axes[1].set_title('Instance Segmented Image')
axes[1].axis('off')

plt.tight_layout()
plt.show()

"""**Image Classification with Localization (VGG)**"""

!wget https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt

!pip install tensorflow numpy opencv-python matplotlib

!wget https://github.com/hfg-gmuend/openmoji/releases/latest/download/openmoji-72x72-color.zip
!mkdir emojis
!unzip -q openmoji-72x72-color.zip -d ./emojis

import tensorflow as tf
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
import cv2
from google.colab import files
from google.colab.patches import cv2_imshow
import matplotlib.pyplot as plt

# Load the VGG16 model
model = VGG16(weights='imagenet')

# Function to get image from user
def get_image():
    uploaded = files.upload()
    return next(iter(uploaded))

# Function to process image and make prediction
def process_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return img, x

# Function to generate and display heatmap
def generate_heatmap(img, x):
    preds = model.predict(x)
    print('Predicted:', decode_predictions(preds, top=1)[0])

    # Get the last convolutional layer
    last_conv_layer = model.get_layer("block5_conv3")

    # Create a model that goes from the input to the last conv layer
    heatmap_model = tf.keras.models.Model([model.inputs], [last_conv_layer.output, model.output])

    # Get the last conv layer output and model predictions
    with tf.GradientTape() as tape:
        conv_output, predictions = heatmap_model(x)
        class_idx = tf.argmax(predictions[0])
        loss = predictions[:, class_idx]

    # Compute gradients
    grads = tape.gradient(loss, conv_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Compute heatmap
    heatmap = tf.reduce_mean(tf.multiply(pooled_grads, conv_output), axis=-1)
    heatmap = np.maximum(heatmap, 0) / np.max(heatmap)
    heatmap = heatmap.reshape((14, 14))
    heatmap = cv2.resize(heatmap, (img.size[0], img.size[1]))
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    # Superimpose heatmap on original image
    superimposed_img = cv2.addWeighted(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR), 0.6, heatmap, 0.4, 0)

    # Display the result
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(superimposed_img, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.title('Image Classification with Localization')
    plt.show()

# Main execution
print("Please upload an image.")
img_path = get_image()

if img_path:
    img, x = process_image(img_path)
    generate_heatmap(img, x)
else:
    print("Failed to load image.")

"""**Object Recognition (OpenCV + ultralytics library, which includes YOLOv8)**"""

!pip install ultralytics

import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO

# Load a pretrained YOLOv8 model
model = YOLO('yolov8n.pt')

# Path to your image file
image_path = '/content/bear.jpg'  # Update this path

# Read the image
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Perform object detection
results = model(image)

# Plot the results
plt.figure(figsize=(12, 8))
plt.imshow(results[0].plot())
plt.axis('off')
plt.title('Object Recognition Results')
plt.show()

# Print detected objects and their confidences
for result in results:
    boxes = result.boxes
    for box in boxes:
        class_id = box.cls[0].item()
        conf = box.conf[0].item()
        class_name = model.names[int(class_id)]
        print(f"Detected {class_name} with confidence {conf:.2f}")

"""*** Object Detection (YOLO with OpenCV)***"""

# Install required libraries
!pip install torch torchvision
!pip install ultralytics

import cv2
import numpy as np

# Download the necessary files
!wget https://github.com/pjreddie/darknet/raw/master/cfg/yolov3.cfg -O /content/yolov3.cfg
!wget https://github.com/pjreddie/darknet/raw/master/data/coco.names -O /content/yolov3.txt
!wget https://pjreddie.com/media/files/yolov3.weights -O /content/yolov3.weights

# Define file paths
image_path = "/content/single_dog.jpg"
cfgfile_path = "/content/yolov3.cfg"
classfile_path = "/content/yolov3.txt"
weightfile_path = "/content/yolov3.weights"

def get_output_layers(net):
    layer_names = net.getLayerNames()
    try:
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    except:
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers

def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    color = COLORS[class_id]
    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
    cv2.putText(img, label, (x-10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 2)

# Read the image
image = cv2.imread(image_path)

Width = image.shape[1]
Height = image.shape[0]
scale = 0.00392

# Load class names
with open(classfile_path, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

# Generate colors for each class
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

# Load YOLO model
net = cv2.dnn.readNet(weightfile_path, cfgfile_path)

# Create a blob from the image
blob = cv2.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)
net.setInput(blob)

# Get the output layers from the YOLO model
outs = net.forward(get_output_layers(net))

class_ids = []
confidences = []
boxes = []
conf_threshold = 0.5
nms_threshold = 0.4

# Analyze the outputs
for out in outs:
    for detection in out:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > 0.5:
            center_x = int(detection[0] * Width)
            center_y = int(detection[1] * Height)
            w = int(detection[2] * Width)
            h = int(detection[3] * Height)
            x = center_x - w / 2
            y = center_y - h / 2
            class_ids.append(class_id)
            confidences.append(float(confidence))
            boxes.append([x, y, w, h])

indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

# Draw the bounding boxes on the image
for i in indices:
    try:
        box = boxes[i]
    except:
        i = i[0]
        box = boxes[i]

    x = box[0]
    y = box[1]
    w = box[2]
    h = box[3]
    draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))

# Save and display the output image
output_image_path = "/content/object-detection.jpg"
cv2.imwrite(output_image_path, image)

"""**Pattern Recognition( k-Nearest Neighbors classifier)**"""

# Consider running this code in an offline IDE like Visual Studio for potentially faster execution.

from sklearn import datasets, svm
import matplotlib.pyplot as plt

digits = datasets.load_digits()
clf = svm.SVC(gamma=0.001, C=100)
clf.fit(digits.data[:-1], digits.target[:-1])

print('Prediction:', clf.predict(digits.data[-1].reshape(1, -1)))
plt.imshow(digits.images[-1], cmap=plt.cm.gray_r, interpolation='nearest')
plt.show()

"""**Facial Recognition (DeepFace)**"""

!pip install face_recognition opencv-python-headless

!pip install opencv-python-headless
!pip install deepface matplotlib opencv-python-headless

import cv2
import numpy as np
from deepface import DeepFace
from google.colab import files
import matplotlib.pyplot as plt
import requests

# Function to download celebrity images
def download_celebrity_images():
    celebrities = {
        "Selena Gomez": "https://upload.wikimedia.org/wikipedia/commons/8/85/Selena_Gomez_-_Walmart_Soundcheck_Concert.jpg",
        "Brad Pitt": "https://upload.wikimedia.org/wikipedia/commons/4/4c/Brad_Pitt_2019_by_Glenn_Francis.jpg",
        "Emma Watson": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Emma_Watson_2013.jpg",
        "Samantha": "https://hnbgu.org/wp-content/uploads/2024/05/samantha.jpg",
        "Emilia Clarke": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Emilia_Clarke_%289347957209%29_%28cropped%29.jpg/986px-Emilia_Clarke_%289347957209%29_%28cropped%29.jpg"
    }

    celebrity_images = {}
    for name, url in celebrities.items():
        response = requests.get(url)
        img = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
        celebrity_images[name] = img
    return celebrity_images

# Download celebrity images
print("Downloading celebrity images...")
celebrity_images = download_celebrity_images()

# Function to upload image
def upload_image():
    uploaded = files.upload()
    file_name = next(iter(uploaded))
    return cv2.imdecode(np.frombuffer(uploaded[file_name], np.uint8), cv2.IMREAD_COLOR)

# Function to recognize face
def recognize_face(img, celebrity_images):
    for celebrity, celeb_img in celebrity_images.items():
        try:
            result = DeepFace.verify(img, celeb_img, enforce_detection=False, model_name="VGG-Face")
            if result["verified"]:
                return celebrity
        except:
            pass
    return "Unknown Person"

# Function to detect faces
def detect_faces(img):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    return faces

print("\nPlease upload an image for celebrity recognition:")
unknown_image = upload_image()

# Detect faces
faces = detect_faces(unknown_image)

# Perform face recognition
recognized_name = recognize_face(unknown_image, celebrity_images)

# Draw bounding boxes and display result
img_with_boxes = unknown_image.copy()
for (x, y, w, h) in faces:
    cv2.rectangle(img_with_boxes, (x, y), (x+w, y+h), (255, 0, 0), 2)

plt.figure(figsize=(10, 8))
plt.imshow(cv2.cvtColor(img_with_boxes, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.title(f'Recognized as: {recognized_name}')
plt.show()

"""**Edge Detection (OpenCV)**"""

# Consider running this code in an offline IDE like Visual Studio for potentially faster execution.

import cv2
import numpy as np

# Upload an image
img =cv2.imread("flower.jpg",0)
resized = cv2.resize(img, (300, 200 ), interpolation = cv2.INTER_LINEAR)

# Apply Canny Edge Detection
edges = cv2.Canny(img, 100, 200)
resize = cv2.resize(edges, (300, 200 ), interpolation = cv2.INTER_LINEAR)
cv2.imshow("edges", resize)
cv2.imshow("orginal", resized)
cv2.waitKey(0)
cv2.destroyAllWindows()

"""**Feature Matching (SIFT algorithm)**"""

# Consider running this code in an offline IDE like Visual Studio for potentially faster execution.

import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_image(path, size=(450, 400)):
    img = cv2.imread(path)  # Load the image in color
    img = cv2.resize(img, size)  # Resize the image to the specified size
    return img

# Load and resize two images from local paths
img1 = load_image("od/app.jpg")
img2 = load_image("od/apple.jpg")

# SIFT Feature Detection and Description
sift = cv2.SIFT_create()
kp1, des1 = sift.detectAndCompute(cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY), None)
kp2, des2 = sift.detectAndCompute(cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY), None)

# Feature Matching
bf = cv2.BFMatcher()
matches = bf.knnMatch(des1, des2, k=2)

# Apply ratio test
good_matches = []
for m, n in matches:
    if m.distance < 0.75 * n.distance:
        good_matches.append(m)

# Draw matches
img_matches = cv2.drawMatches(img1, kp1, img2, kp2, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

# Display the result
plt.figure(figsize=(12, 6))  # Adjust the window size here
plt.imshow(cv2.cvtColor(img_matches, cv2.COLOR_BGR2RGB))  # Convert BGR to RGB for correct color display
plt.title('Feature Matching')
plt.axis('off')
plt.show()

print(f"Number of good matches found: {len(good_matches)}")

