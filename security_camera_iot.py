import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

import boto3
import os
import time
import shutil
import cv2
import numpy as np

from deepface import DeepFace
from scipy.spatial.distance import cosine
from picamera2 import Picamera2
from dotenv import load_dotenv


load_dotenv()


# -------------------- Configuration --------------------

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TARGET_EMAIL = os.getenv("TARGET_EMAIL")

# AWS configuration
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

# Local paths
DOWNLOAD_FOLDER = "downloaded_images"
IMAGE_PATH = "Capture.JPG"

# Face recognition configuration
FACE_MATCH_THRESHOLD = 0.35

# Alert configuration
EMAIL_COOLDOWN_SECONDS = 30


# Load face detector once
FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


# -------------------- Email --------------------

def send_email(subject, body, attachment_path=None, inline_image_path=None):
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_ADDRESS
        message["To"] = TARGET_EMAIL
        message["Subject"] = subject

        # Add email body
        message.attach(MIMEText(body, "plain"))

        # Attach file if provided
        if attachment_path:
            attachment = MIMEBase("application", "octet-stream")

            with open(attachment_path, "rb") as file:
                attachment.set_payload(file.read())

            encoders.encode_base64(attachment)

            attachment.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(attachment_path)}"'
            )

            message.attach(attachment)

        # Add inline image if provided
        if inline_image_path:
            with open(inline_image_path, "rb") as image_file:
                image = MIMEImage(image_file.read())

            image.add_header("Content-ID", "<inline_image>")
            image.add_header(
                "Content-Disposition",
                "inline",
                filename=os.path.basename(inline_image_path)
            )

            message.attach(image)

        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(
                EMAIL_ADDRESS,
                TARGET_EMAIL,
                message.as_string()
            )

        print("Email sent successfully.")

    except Exception as error:
        print(f"Error sending email: {error}")


# -------------------- Local Storage --------------------

def clear_local_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path)


# -------------------- AWS S3 --------------------

def download_face_images():
    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION
    )

    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=BUCKET_NAME)

    folders = set()

    for page in pages:
        if "Contents" not in page:
            continue

        for obj in page["Contents"]:
            key = obj["Key"]

            if not key.lower().endswith(".jpg"):
                continue

            folder_name = os.path.dirname(key)
            file_name = os.path.basename(key)

            local_folder_path = os.path.join(
                DOWNLOAD_FOLDER,
                folder_name
            )

            os.makedirs(local_folder_path, exist_ok=True)
            folders.add(local_folder_path)

            local_file_path = os.path.join(
                local_folder_path,
                file_name
            )

            s3.download_file(
                BUCKET_NAME,
                key,
                local_file_path
            )

    return list(folders)


# -------------------- Face Recognition --------------------

def is_face_match(
    captured_image_path,
    authorized_image_path,
    threshold=FACE_MATCH_THRESHOLD
):
    try:
        # Extract embedding from captured image
        captured_embedding_result = DeepFace.represent(
            img_path=captured_image_path,
            model_name="Facenet",
            enforce_detection=False
        )

        if (
            not isinstance(captured_embedding_result, list)
            or len(captured_embedding_result) == 0
        ):
            print(
                f"Failed to extract embedding from captured image: "
                f"{captured_image_path}"
            )
            return False

        captured_embedding = np.array(
            captured_embedding_result[0]["embedding"]
        )

        # Extract embedding from authorized image
        authorized_embedding_result = DeepFace.represent(
            img_path=authorized_image_path,
            model_name="Facenet",
            enforce_detection=False
        )

        if (
            not isinstance(authorized_embedding_result, list)
            or len(authorized_embedding_result) == 0
        ):
            print(
                f"Failed to extract embedding from authorized image: "
                f"{authorized_image_path}"
            )
            return False

        authorized_embedding = np.array(
            authorized_embedding_result[0]["embedding"]
        )

        # Compute cosine distance between embeddings
        distance = cosine(
            captured_embedding,
            authorized_embedding
        )

        is_match = distance < threshold

        print(
            f"Distance: {distance:.4f}, "
            f"Match: {is_match}"
        )

        return is_match

    except Exception as error:
        print(f"Error processing images: {error}")
        return False


# -------------------- Face Detection --------------------

def detect_face_in_video(frame):
    if frame is None:
        print("Image is empty.")
        return False

    if FACE_CASCADE.empty():
        print("Failed to load face detection model.")
        return False

    gray_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = FACE_CASCADE.detectMultiScale(
        gray_frame,
        scaleFactor=1.1,
        minNeighbors=4
    )

    return len(faces) > 0


def face_detection(folders):
    print("Comparing with authorized photos...")

    for folder in folders:
        person_name = os.path.basename(folder)

        print(f"Processing authorized person: {person_name}")

        for file_name in os.listdir(folder):
            if not file_name.lower().endswith(".jpg"):
                continue

            authorized_image_path = os.path.join(
                folder,
                file_name
            )

            print(
                f"Comparing with: {authorized_image_path}"
            )

            if is_face_match(
                IMAGE_PATH,
                authorized_image_path
            ):
                print(
                    f"Authorized entrance: {person_name}"
                )
                return True

    print("Unauthorized entrance was detected.")
    return False


# -------------------- Main --------------------

def main():
    # Remove previously downloaded authorized images
    clear_local_directory(DOWNLOAD_FOLDER)

    # Download current authorized images from S3
    folders = download_face_images()

    if not folders:
        print("No authorized face images were found in S3.")
        return

    print(
        f"Finished downloading authorized images "
        f"for {len(folders)} people."
    )

    # Initialize camera
    os.environ["LIBCAMERA_LOG_LEVELS"] = "*:ERROR"

    picam2 = Picamera2()

    video_config = picam2.create_video_configuration()
    picam2.configure(video_config)

    picam2.start()

    last_email_time = 0

    try:
        print("Starting face detection...")

        while True:
            # Remove previous captured image
            if os.path.exists(IMAGE_PATH):
                os.remove(IMAGE_PATH)

            # Capture new image
            picam2.capture_file(IMAGE_PATH)

            frame = cv2.imread(IMAGE_PATH)

            # Check if the image contains a face
            if detect_face_in_video(frame):
                print("Face detected!")

                # Compare face with authorized people
                is_authorized = face_detection(folders)

                if not is_authorized:
                    current_time = time.time()

                    # Prevent repeated email alerts
                    if (
                        current_time - last_email_time
                        >= EMAIL_COOLDOWN_SECONDS
                    ):
                        subject = "Unauthorized access"

                        message = (
                            "An unauthorized entrance attempt was detected. "
                            "An image of the person is attached."
                        )

                        send_email(
                            subject,
                            message,
                            inline_image_path=IMAGE_PATH
                        )

                        last_email_time = current_time

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopping camera...")

    finally:
        picam2.stop()
        picam2.close()

        if os.path.exists(IMAGE_PATH):
            os.remove(IMAGE_PATH)


if __name__ == "__main__":
    main()