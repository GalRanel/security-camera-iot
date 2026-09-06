# IoT Security Camera with Face Recognition

An IoT-based security camera system that detects faces, identifies authorized individuals, and sends email alerts when an unauthorized person is detected.

The project was designed to run on a Raspberry Pi with a camera module and uses AWS S3 to store images of authorized individuals.

## How It Works

1. Authorized face images are downloaded from an AWS S3 bucket.
2. The Raspberry Pi camera continuously captures images.
3. OpenCV detects whether a face is present in the captured image.
4. DeepFace generates facial embeddings using FaceNet.
5. Cosine distance is used to compare the captured face with authorized faces.
6. If a match is found, the person is recognized as authorized.
7. If no match is found, an email security alert is sent with the captured image.
8. A cooldown mechanism prevents repeated email alerts within a short period.

## Technologies

- Python
- Raspberry Pi
- Picamera2
- OpenCV
- DeepFace / FaceNet
- NumPy
- SciPy
- AWS S3
- Boto3
- SMTP

## Project Flow

```text
AWS S3
   |
   | Authorized face images
   v
Raspberry Pi Camera
   |
   v
Face Detection (OpenCV)
   |
   v
Face Embedding (DeepFace / FaceNet)
   |
   v
Cosine Distance Comparison
   |
   +---- Match ----> Authorized Access
   |
   +---- No Match -> Email Security Alert
```

## Configuration

Sensitive configuration is stored in environment variables and is not committed to the repository.

Create a `.env` file based on `.env.example`:

```env
EMAIL_ADDRESS=
EMAIL_PASSWORD=
TARGET_EMAIL=

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET_NAME=
AWS_REGION=
```

Never commit the `.env` file or AWS/email credentials.

## Installation

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Picamera2 must also be available on the Raspberry Pi environment.

## Running

Once the Raspberry Pi camera, AWS credentials, S3 bucket, and email configuration are available:

```bash
python security_camera_iot.py
```

## Security

- Credentials are loaded from environment variables.
- `.env` is excluded from Git.
- Captured and downloaded face images are excluded from the repository.
- Email alerts use SMTP with TLS.# IoT Security Camera with Face Recognition

An IoT-based security camera system that detects faces, identifies authorized individuals, and sends email alerts when an unauthorized person is detected.

The project was designed to run on a Raspberry Pi with a camera module and uses AWS S3 to store images of authorized individuals.

## How It Works

1. Authorized face images are downloaded from an AWS S3 bucket.
2. The Raspberry Pi camera continuously captures images.
3. OpenCV detects whether a face is present in the captured image.
4. DeepFace generates facial embeddings using FaceNet.
5. Cosine distance is used to compare the captured face with authorized faces.
6. If a match is found, the person is recognized as authorized.
7. If no match is found, an email security alert is sent with the captured image.
8. A cooldown mechanism prevents repeated email alerts within a short period.

## Technologies

- Python
- Raspberry Pi
- Picamera2
- OpenCV
- DeepFace / FaceNet
- NumPy
- SciPy
- AWS S3
- Boto3
- SMTP

## Project Flow

```text
AWS S3
   |
   | Authorized face images
   v
Raspberry Pi Camera
   |
   v
Face Detection (OpenCV)
   |
   v
Face Embedding (DeepFace / FaceNet)
   |
   v
Cosine Distance Comparison
   |
   +---- Match ----> Authorized Access
   |
   +---- No Match -> Email Security Alert
```

## Configuration

Sensitive configuration is stored in environment variables and is not committed to the repository.

Create a `.env` file based on `.env.example`:

```env
EMAIL_ADDRESS=
EMAIL_PASSWORD=
TARGET_EMAIL=

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET_NAME=
AWS_REGION=
```

Never commit the `.env` file or AWS/email credentials.

## Installation

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Picamera2 must also be available on the Raspberry Pi environment.

## Running

Once the Raspberry Pi camera, AWS credentials, S3 bucket, and email configuration are available:

```bash
python security_camera_iot.py
```

## Security

- Credentials are loaded from environment variables.
- `.env` is excluded from Git.
- Captured and downloaded face images are excluded from the repository.
- Email alerts use SMTP with TLS.
