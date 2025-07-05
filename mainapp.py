from PIL import Image, ImageChops, ImageEnhance, UnidentifiedImageError
import imagehash
import numpy as np
from skimage import filters
import torch
import clip
from io import BytesIO
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, request
import socket

app = Flask(__name__)

def get_ip_from_url(image_url):
    try:
        domain = image_url.split('/')[2]
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except (socket.gaierror, IndexError):
        return "Could not resolve IP"

def send_email(user_name, image_link, description, ip_address, morph_status):
    sender_email = "navee20052005@gmail.com"
    sender_password = "hgzk benl edxx bvog"
    receiver_email = "charu172000@gmail.com"

    subject = "🚨 Morphed Image Detection Report"
    body = f"""
    **Morphed Image Report**
    
    Name: {user_name}
    Image Link: {image_link}
    Description: {description}
    Uploader IP: {ip_address}
    Morph Status: {morph_status}
    
    Please investigate and take the necessary actions.
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Report Sent Successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except (requests.exceptions.RequestException, UnidentifiedImageError) as e:
        print(f"Failed to fetch image: {e}")
        return None

def error_level_analysis(image, scale=10):
    ela_image = image.convert('RGB')
    temp = "temp.jpg"
    ela_image.save(temp, quality=90)
    ela_image = Image.open(temp)
    diff = ImageChops.difference(image, ela_image)
    diff = ImageEnhance.Brightness(diff).enhance(scale)
    return diff

def calculate_image_hash(image):
    return imagehash.phash(image)

def edge_intensity(image):
    gray_image = image.convert('L')
    edges = filters.sobel(np.array(gray_image))
    return np.mean(edges)

def color_histogram_difference(image1, image2):
    hist1 = np.array(image1.histogram())
    hist2 = np.array(image2.histogram())
    diff = np.linalg.norm(hist1 - hist2)
    return diff

def predict_image_morph(image):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    ela_image = error_level_analysis(image)
    image_input = preprocess(ela_image).unsqueeze(0).to(device)
    labels = ["Real Image", "Morphed Image"]
    text_inputs = torch.cat([clip.tokenize(label) for label in labels]).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image_input)
        text_features = model.encode_text(text_inputs)
        similarity = (image_features @ text_features.T).softmax(dim=-1).cpu().numpy()

        original_hash = calculate_image_hash(image)
        ela_hash = calculate_image_hash(ela_image)
        hash_diff = original_hash - ela_hash

        edge_score = edge_intensity(image)
        hist_diff = color_histogram_difference(image, ela_image)

        morph_votes = 0
        if hash_diff > 10:
            morph_votes += 1
        if edge_score > 0.2:
            morph_votes += 1
        if hist_diff > 5000:
            morph_votes += 1

        confidence_threshold = 0.7
        brightness_threshold = 100

        ela_gray = ela_image.convert('L')
        ela_brightness = sum(ela_gray.getdata()) / (ela_image.size[0] * ela_image.size[1])

        if similarity.max() < confidence_threshold and ela_brightness < brightness_threshold:
            prediction = "Uncertain (Low Confidence)"
        else:
            prediction = labels[similarity.argmax()]

        if morph_votes >= 2:
            prediction = "Morphed Image"

    return prediction

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/report', methods=['POST'])
def report():
    user_name = request.form['name']
    image_link = request.form['social_media']
    description = request.form['description']

    ip_address = get_ip_from_url(image_link)
    image = download_image(image_link)

    if image is None:
        return "Invalid image URL or unsupported format. Please upload a valid image."

    morph_status = predict_image_morph(image)
    send_email(user_name, image_link, description, ip_address, morph_status)

    return f"Report submitted successfully! Detected status: {morph_status}. Authorities have been notified."

if __name__ == '__main__':
    app.run(debug=True)