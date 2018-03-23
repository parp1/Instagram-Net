import os
import cv2
import base64

### JSON entry creation helper functions ###

def create_post_entry(caption, num_likes, num_comments, image_link, image_data, image_height, image_width, image_id):
    return {"caption":caption, 
            "num_likes":num_likes, 
            "num_comments":num_comments,
            "image_link":image_link,
            "image_data":image_data,
            "image_height":image_height,
            "image_width":image_width,
            "image_id":image_id}

def create_user_entry(username, bio, num_followers, num_following, num_posts, num_posts_scraped, post_data):
    return {"username":username,
            "bio":bio,
            "num_followers":num_followers,
            "num_following":num_following,
            "num_posts":num_posts,
            "num_posts_scraped":num_posts_scraped,
            "post_data":post_data}

### Image encoding/decoding functions (Base 64) ###

def encode_image_data(image):
    return base64.b64encode(image)

def decode_image_data(image_string):
    return base64.b64decode(image_string)

### Cropping functions ###

# Adds margin to bounding box found in the facecrop function
def add_margin(x, y, w, h, margin_scale_factor, original_width, original_height):

    h_margin = h * margin_scale_factor
    w_margin = w * margin_scale_factor

    x_post_margin = x - w_margin
    y_post_margin = y - h_margin

    if (x_post_margin < 0):
        x_post_margin = 0


    if (y_post_margin < 0):
        y_post_margin = 0

    w_scaled = w_margin + w + w_margin
    h_scaled = h_margin + h + h_margin

    if (w_scaled > original_width):
        w_scaled = original_width
        h_scaled = original_width

    if (h_scaled > original_height):
        h_scaled = original_height
        w_scaled = original_height

    return (x_post_margin, y_post_margin, w_scaled, h_scaled)

# Finds all faces in the given picture and crops them with a certain margin
def facecrop(image_name):
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    img = cv2.imread(image_name)

    minisize = (img.shape[1],img.shape[0])
    miniframe = cv2.resize(img, minisize)

    faces = face_cascade.detectMultiScale(miniframe)

    num_faces = 0
    for (x, y, w, h) in faces:
        cv2.rectangle

        (x_post_margin, y_post_margin, w_scaled, h_scaled) = add_margin(x, y, w, h, 0.25, img.shape[1], img.shape[0])

        sub_face = img[y:y+h, x:x+w]
        sub_face_with_margin = img[int(y_post_margin):int(y_post_margin + h_scaled), int(x_post_margin):int(x_post_margin + w_scaled)]

        eyes = eye_cascade.detectMultiScale(sub_face)
        if (len(eyes) == 0):
            continue

        fname, ext = os.path.splitext(image_name)
        num_faces += 1
        cv2.imwrite(fname + "_face_" + str(num_faces) + ext, sub_face_with_margin)

    os.remove(image_name)

    if (num_faces == 0):
        raise Exception("No faces found.")
    
    return num_faces