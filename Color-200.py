# import cv2
# import numpy as np
# import streamlit as st
# from PIL import Image as PILImage
# import tempfile
# import os
# from io import BytesIO
# import glob
# import zipfile

# # Define paths to model files
# prototxt = 'model/colorization_deploy_v2.prototxt'
# model = 'model/colorization_release_v2.caffemodel'
# points = 'model/pts_in_hull.npy'

# # Load model files
# net = cv2.dnn.readNetFromCaffe(prototxt, model)
# pts = np.load(points)
# class8 = net.getLayerId("class8_ab")
# conv8 = net.getLayerId("conv8_313_rh")
# pts = pts.transpose().reshape(2, 313, 1, 1)
# net.getLayer(class8).blobs = [pts.astype("float32")]
# net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]

# def colorize_image(image):
#     st.subheader("Step 1: Original Image")
#     st.image(image, use_column_width=True)

#     # Convert image to float and LAB color space
#     scaled = image.astype("float32") / 255.0
#     lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)
#     L, A, B = cv2.split(lab)

#     # Normalize L channel to [0, 1] range for display
#     L_normalized = L / 255.0

#     st.subheader("Step 2: Grayscale Image (L Channel)")
#     st.image(L_normalized, channels="GRAY", use_column_width=True)

#     # Display A and B channels
#     st.subheader("Step 3: A and B Channels")
#     st.image(A, channels="GRAY", use_column_width=True, caption="A Channel")
#     st.image(B, channels="GRAY", use_column_width=True, caption="B Channel")

#     resized_L = cv2.resize(L, (224, 224))
#     L_resized = resized_L - 50

#     st.subheader("Step 4: Resized L Channel for Model Input")
#     st.image(resized_L / 255.0, channels="GRAY", use_column_width=True)

#     net.setInput(cv2.dnn.blobFromImage(L_resized))
#     ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
#     ab_resized = cv2.resize(ab, (image.shape[1], image.shape[0]))

#     st.subheader("Step 5: Predicted AB Channels")
#     ab_image = cv2.cvtColor(np.zeros_like(image), cv2.COLOR_BGR2LAB)
#     ab_image[:, :, 1:] = ab_resized
#     st.image(ab_image, channels="LAB", use_column_width=True)

#     colorized = np.concatenate((L[:, :, np.newaxis], ab_resized), axis=2)
#     colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
#     colorized = np.clip(colorized, 0, 1)
#     colorized = (255 * colorized).astype("uint8")

#     st.subheader("Step 6: Final Colorized Image")
#     st.image(colorized, use_column_width=True)

#     return colorized

# def adjust_image(image, brightness=1.0, contrast=1.0, saturation=1.0, gamma=1.0):
#     img = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
#     hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#     hsv_img[..., 1] = hsv_img[..., 1] * saturation
#     img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
#     img = np.power(img / 255.0, gamma)
#     img = np.clip(img * 255, 0, 255).astype(np.uint8)
#     return img

# def apply_filter(image, filter_type):
#     if filter_type == 'Blur':
#         return cv2.GaussianBlur(image, (15, 15), 0)
#     elif filter_type == 'Sharpen':
#         kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
#         return cv2.filter2D(image, -1, kernel)
#     elif filter_type == 'Edge Detection':
#         return cv2.Canny(image, 100, 200)
#     elif filter_type == 'Sepia':
#         sepia_filter = np.array([[0.272, 0.534, 0.131],
#                                  [0.349, 0.686, 0.168],
#                                  [0.393, 0.769, 0.189]])
#         return cv2.transform(image, sepia_filter)
#     elif filter_type == 'Vignette':
#         rows, cols = image.shape[:2]
#         X_resultant_kernel = cv2.getGaussianKernel(cols, 200)
#         Y_resultant_kernel = cv2.getGaussianKernel(rows, 200)
#         resultant_kernel = Y_resultant_kernel * X_resultant_kernel.T
#         mask = 255 * resultant_kernel / np.linalg.norm(resultant_kernel)
#         return cv2.filter2D(image, -1, mask)
#     return image

# def process_video(video_file, brightness, contrast, saturation, gamma, filter_type):
#     video_file.seek(0)  # Reset file pointer to start
#     temp_video_path = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name

#     cap = cv2.VideoCapture(video_file.name)
#     if not cap.isOpened():
#         st.error("Error: Could not open the video file.")
#         return None

#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fps = cap.get(cv2.CAP_PROP_FPS)
    
#     out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         colorized_frame = colorize_image(frame)
#         adjusted_frame = adjust_image(colorized_frame, brightness, contrast, saturation, gamma)
#         final_frame = apply_filter(adjusted_frame, filter_type)
#         out.write(final_frame)

#     cap.release()
#     out.release()
#     return temp_video_path

# def download_colorized_images(colorized_images, filenames):
#     zip_buffer = BytesIO()
#     with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
#         for image, filename in zip(colorized_images, filenames):
#             img_bytes = cv2.imencode('.png', image)[1].tobytes()
#             zip_file.writestr(filename, img_bytes)
#     zip_buffer.seek(0)
#     return zip_buffer

# st.title("High-End Photo & Video Colorizer")

# uploaded_files = st.file_uploader("Upload images or video", type=["jpg", "jpeg", "png", "mp4", "avi"], accept_multiple_files=True)
# folder_path = st.text_input("Enter folder path for images", "")

# if uploaded_files or folder_path:
#     images = []
#     videos = []
#     filenames = []

#     # Process uploaded files
#     for uploaded_file in uploaded_files:
#         if uploaded_file.type.startswith('image'):
#             image = np.array(PILImage.open(uploaded_file))
#             images.append(image)
#             filenames.append(uploaded_file.name)
#         elif uploaded_file.type.startswith('video'):
#             videos.append(uploaded_file)

#     # Process images from a folder
#     if folder_path:
#         for file_path in glob.glob(os.path.join(folder_path, "*.jpg")):
#             image = cv2.imread(file_path)
#             images.append(image)
#             filenames.append(os.path.basename(file_path))

#     # Parameters
#     st.sidebar.header("Adjustments")
#     brightness = st.sidebar.slider("Brightness", -100.0, 100.0, 0.0, 0.1)
#     contrast = st.sidebar.slider("Contrast", 0.0, 3.0, 1.0, 0.01)
#     saturation = st.sidebar.slider("Saturation", 0.0, 3.0, 1.0, 0.01)
#     gamma = st.sidebar.slider("Gamma", 0.1, 2.0, 1.0, 0.01)

#     st.sidebar.header("Filters")
#     filter_type = st.sidebar.selectbox("Filter", ["None", "Blur", "Sharpen", "Edge Detection", "Sepia", "Vignette"])

#     colorized_images = []

#     # Process each image
#     for image in images:
#         colorized = colorize_image(image)
#         adjusted = adjust_image(colorized, brightness, contrast, saturation, gamma)
#         final_image = apply_filter(adjusted, filter_type)
#         st.image(final_image, use_column_width=True)
#         colorized_images.append(final_image)

#     # Download option for images
#     if colorized_images:
#         st.markdown("## Download Colorized Images")
#         zip_buffer = download_colorized_images(colorized_images, filenames)
#         st.download_button("Download All Images as ZIP", data=zip_buffer, file_name="colorized_images.zip")

#     # Process each video
#     for video in videos:
#         processed_video_path = process_video(video, brightness, contrast, saturation, gamma, filter_type)
#         if processed_video_path:
#             st.markdown("## Download Processed Video")
#             with open(processed_video_path, "rb") as file:
#                 st.download_button("Download Video", data=file, file_name=os.path.basename(processed_video_path))

#     st.success("Processing complete!")

# else:
#     st.info("Please upload images or video files or specify a folder path to process.")


# Import the necessary packages
import numpy as np
import cv2
import streamlit as st
from PIL import Image
import os
from streamlit import *
import base64

# Set page configuration to expand sidebar by default
st.set_page_config(layout="wide", initial_sidebar_state="expanded")


# Function to create a navigation bar with padding
def render_navbar():
    navbar_style = """
    <style>
        .navbar {
            background-color: #0078D7;
            padding: 15px 10px;
            color: white;
            font-size: 18px;
            font-weight: bold;
        }
        .navbar a {
            color: white;
            text-decoration: none;
            margin-right: 20px;
        }
        .navbar a:hover {
            text-decoration: underline;
        }
    </style>
    <div class="navbar">
        <a href="#Colorize Your Black and White Image">Home</a>
        <a href="#About">About</a>
        <a href="#Contact">Contact</a>
    </div>
    """
    st.markdown(navbar_style, unsafe_allow_html=True)



def set_background_image(image_path):
    # Open the image file and encode it into base64
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    
    # Construct the background style using the base64-encoded image
    background_style = f"""
    <style>
        .stApp {{
            background-image: url('data:image/jpg;base64,{encoded_image}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
    </style>
    """
    st.markdown(background_style, unsafe_allow_html=True)

# Set background image (local path)
set_background_image("D:/FY_TEST/templates/color-back.jpg")  # Make sure the path is correct


# Render the navigation bar
render_navbar()


def colorizer(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    
    # Use relative paths based on the current script directory
    script_dir = os.path.dirname(__file__)
    prototxt = os.path.join(script_dir, "model/colorization_deploy_v2.prototxt")
    model = os.path.join(script_dir, "model/colorization_release_v2.caffemodel")
    points = os.path.join(script_dir, "model/pts_in_hull.npy")
    
    net = cv2.dnn.readNetFromCaffe(prototxt, model)
    pts = np.load(points)
    
    # Add the cluster centers as 1x1 convolutions to the model
    class8 = net.getLayerId("class8_ab")
    conv8 = net.getLayerId("conv8_313_rh")
    pts = pts.transpose().reshape(2, 313, 1, 1)
    net.getLayer(class8).blobs = [pts.astype("float32")]
    net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]
    
    # Scale the pixel intensities to the range [0, 1], and convert the image from BGR to Lab color space
    scaled = img.astype("float32") / 255.0
    lab = cv2.cvtColor(scaled, cv2.COLOR_RGB2LAB)
    
    # Display the L channel
    L = cv2.split(lab)[0]
    st.image(L, caption="L Channel (Lightness)", width=600, clamp=True, channels="gray")
    
    # Resize the Lab image to 224x224 (the dimensions the colorization network accepts), extract the 'L' channel, and perform mean centering
    resized = cv2.resize(lab, (224, 224))
    L_resized = cv2.split(resized)[0]
    L_resized -= 50
    
    # Pass the L channel through the network which will predict the 'a' and 'b' channel values
    net.setInput(cv2.dnn.blobFromImage(L_resized))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
    
    # Resize the predicted 'ab' volume to the same dimensions as the input image
    ab = cv2.resize(ab, (img.shape[1], img.shape[0]))
    
    # Display the 'a' and 'b' channels separately as grayscale images
    st.image(ab[:, :, 0], caption="'a' Channel", width=600, clamp=True, channels="gray")
    st.image(ab[:, :, 1], caption="'b' Channel", width=600, clamp=True, channels="gray")
    
    # Combine 'ab' channels into a dummy 3-channel image for visualization
    ab_combined = np.zeros((ab.shape[0], ab.shape[1], 3))
    ab_combined[:, :, 0] = ab[:, :, 0]  # Map 'a' to the red channel
    ab_combined[:, :, 1] = ab[:, :, 1]  # Map 'b' to the green channel
    st.image(ab_combined, caption="Combined 'ab' Channels (Visualization)", width=600, clamp=True)
    
    # Grab the 'L' channel from the original input image and concatenate it with the predicted 'ab' channels
    L = cv2.split(lab)[0]
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
    
    # Convert the output image from Lab color space to RGB, and clip values to [0, 1]
    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2RGB)
    colorized = np.clip(colorized, 0, 1)
    
    # Convert to unsigned 8-bit integer representation in the range [0, 255]
    colorized = (255 * colorized).astype("uint8")
    
    return colorized

##########################################################################################################

# Streamlit App UI
st.title("Colorize Your Black and White Image")
st.write("This app colorizes your B&W images and displays intermediate phases like 'L', 'a', 'b', and 'ab' channels.")

# Load sample images
input_images_dir = "C:/Users/mahes/Desktop/New folder/"
input_images = [f for f in os.listdir(input_images_dir) if f.endswith(('.jpg', '.png'))]
selected_image = st.sidebar.selectbox("Choose a sample image", ["None"] + input_images)

file = st.sidebar.file_uploader("Or upload an image file", type=["jpg", "png"])

if file is None:
    if selected_image != "None":
        image_path = os.path.join(input_images_dir, selected_image)
        image = Image.open(image_path)
        img = np.array(image)
    else:
        image = None
else:
    image = Image.open(file)
    img = np.array(image)

if image:
    st.text("Your Original Image")
    st.image(image, width=600)
    
    st.text("Processing...")
    color = colorizer(img)
    
    st.text("Your Colorized Image")
    st.image(color, width=600)
else:
    st.text("Select an image to display its colorized version.")
