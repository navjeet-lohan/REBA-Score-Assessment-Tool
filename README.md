# REBA Score Assessment Tool

This project aims to provide a tool for calculating REBA scores using computer vision, helping in ergonomic risk assessment based on body posture. It uses a pose detection model to calculate angles for key body parts such as the neck, trunk, upper arm, and lower arm, which are then used to calculate the REBA score.

## Features

- **Pose Detection**: Utilizes the `mediapipe` library for pose landmark detection.
- **REBA Score Calculation**: Automatically computes the REBA score based on detected body posture angles.
- **Live Video Processing**: The tool captures video feed and processes it frame by frame.
- **Graphical User Interface (GUI)**: Provides a real-time visual interface for viewing body landmarks, angles, and REBA scores.
- **Ergonomic Risk Evaluation**: Helps users assess ergonomic risks related to body posture during work or other activities.
