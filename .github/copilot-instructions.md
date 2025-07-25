# general instructions
- this repository is a proof of concept for a webapp that uses a chatbot to help medical doctors and healthcare professionals to read and annotate information from journal articles in pdf format.
- it uses streamlit as the web framework and is designed to be run locally.
- the chatbot is powered by OpenRouter and can use various models
- the webapp will run locally using a docker container

# development instructions
- the app will be written mostly in Python, with some HTML and CSS for the frontend.
- keep in mind that the app is designed to be user-friendly for medical professionals, so the interface should be intuitive and easy to navigate.
- always consider that the app will run as a Docker container, so ensure that all dependencies, variables, volumes and necessary files are included in the Dockerfile.
- the main file is `app.py`, which contains the Streamlit app logic.
- the Dockerfile is used to build the Docker image for the app.
- the `requirements.txt` file lists the Python dependencies needed to run the app.

