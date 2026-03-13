# Industrial Helmet Detection System

## Overview
The **Industrial Helmet Detection System** is a computer vision–based safety solution designed to monitor the use of Personal Protective Equipment (PPE) in industrial environments. The system analyzes live video streams to detect whether workers are wearing safety helmets.

If the system identifies the **absence of a helmet**, it triggers a signal to a **PLC (Programmable Logic Controller)**. This signal can be used to interrupt or prevent the proper operation of a machine, ensuring that equipment cannot run when safety protocols are not being followed.

This approach helps increase workplace safety by automatically enforcing PPE compliance in real time.

## How It Works
1. A camera captures a live video stream from the monitored environment.
2. The system processes each frame using computer vision and object detection models.
3. A trained model detects the presence or absence of **safety helmets**.
4. If a helmet is **not detected**, a signal is sent to the PLC through a communication protocol.
5. The PLC can then stop or restrict machine operation until the safety condition is met.

## Technologies Used

- **Python** – Core programming language for the system.
- **OpenCV** – Video capture and image processing.
- **YOLO** – Real-time object detection model.
- **PyTorch** – Deep learning framework used to run the detection model.
- **PyModbus** – Communication with the PLC via the Modbus protocol.
- **TTK Bootstrap** – GUI framework for the monitoring interface.

## Project Goals
- Improve industrial safety using computer vision.
- Automatically detect PPE compliance.
- Integrate AI systems with industrial automation equipment.
- Provide a real-time monitoring interface.

## Possible Future Improvements
- Detection of additional PPE (gloves, vests, goggles).
- Event logging and safety reports.
- Alarm and notification systems.
- Multi-camera monitoring support.
