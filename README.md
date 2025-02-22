# Bell ID: Facial Recognition System with Melody Playback

Bell ID is a system that allows access control through real-time facial recognition and the playback of personalized melodies. Utilizing [MediaPipe](https://mediapipe.dev/) for extracting facial landmarks and a JSON database to store user profiles, the system compares the captured face with the registered samples and plays the assigned melody if a match is found, or a default melody otherwise.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [How We Built It](#how-we-built-it)
- [Challenges We Ran Into](#challenges-we-ran-into)
- [Accomplishments We’re Proud Of](#accomplishments-were-proud-of)
- [What We Learned](#what-we-learned)
- [What’s Next for Bell ID](#whats-next-for-bell-id)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **User Registration:** Captures multiple facial samples to create a unique profile.
- **Facial Recognition:** Identifies users by comparing normalized facial landmarks.
- **Melody Playback:** Plays the selected melody for each user, or a default melody if the face is not recognized.
- **Visual Interface:** Displays the real-time registration and recognition process on-screen.
- **Database Management:** Utilizes a JSON file to store and update user profiles.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your_username/bell-id.git
   cd bell-id
Create a virtual environment (optional but recommended):

bash


python -m venv env
source env/bin/activate   # On Linux/macOS
env\Scripts\activate      # On Windows
Install the required dependencies:

bash


pip install -r requirements.txt
Ensure you have the following packages installed: opencv-python, mediapipe, numpy, sounddevice, and soundfile.

Usage
Run the main script:

bash
Cop

python main.py
Select an option from the menu:

Register a new user.
Perform facial recognition.
Reset the database.

Follow the on-screen instructions to capture facial samples and assign a personalized melody.

How We Built It
We developed the system by capturing real-time video from a camera, processing and normalizing facial landmarks using MediaPipe, integrating a JSON database for user profiles, and implementing a playback mechanism for personalized melodies based on facial recognition results.

Challenges We Ran Into
During development, we faced challenges such as:

Fine-tuning the recognition threshold.
Ensuring consistency in the normalization of facial landmarks.
Optimizing the flow to avoid false negatives and repeated sound playback.
Accomplishments We’re Proud Of
We successfully integrated real-time facial detection with personalized melody playback, creating a robust and adaptable access control system.

What We Learned
We deepened our understanding of image processing and the use of MediaPipe for landmark extraction.
We improved our skills in managing JSON databases.
We gained experience in synchronizing and playing audio in real time.
What’s Next for Bell ID
Our next steps include further optimizing the system, exploring new facial recognition techniques, and expanding functionalities to enhance security and user personalization.

Contributing
Contributions are welcome! If you'd like to help improve Bell ID, please open an issue or submit a pull request.

License
This project is distributed under the Apache License 2.0. See the LICENSE file for details.

Contact
For questions or suggestions, please reach out via pedro.rocha@udc.es
