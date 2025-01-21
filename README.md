# AI Meeting Scheduler for Telegram

## Overview

This project is an AI-powered meeting scheduler designed to work seamlessly with Telegram and Google Calendar. It uses Telegram as the primary platform for scheduling meetings and extracts your schedule from Google Calendar to ensure no conflicts arise. The application allows you to manage your time efficiently by analyzing your calendar and coordinating meetings via Telegram.

---

## Features

- **Telegram Integration**: Communicate with the AI directly through Telegram for scheduling meetings.
- **Google Calendar Analysis**: Extracts your schedule from Google Calendar to find available slots for meetings.
- **AI-Powered Assistance**: Uses natural language understanding to schedule meetings intuitively.
- **Desktop-Based Telegram**: Requires Telegram to be installed on your desktop for smooth integration.

---

## Setup Guide

Follow these steps to set up the AI Meeting Scheduler:

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/desktop-app.git
cd desktop-app
```

### 2. Install Dependencies

Ensure you have Python 3.9 or higher installed. Install the required dependencies:

```bash
pip install -r requirements.txt
```

#### Integrating Ollama for Llama Models

Ollama facilitates running large language models like Llama 3.2 locally.

##### 1. Install Ollama

- **Windows**:
  - Download the installer from the [official Ollama website](https://ollama.com/download/windows).
  - Run the installer and follow the on-screen instructions.

- **macOS**:
  - Download the installer from the [official Ollama website](https://ollama.com/download/macos).
  - Open the `.dmg` file and follow the installation prompts.

- **Linux**:
  - Open a terminal and execute:

    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```

##### 2. Pull Llama Models

After installing Ollama, download the desired Llama models:

- **Llama 3.2 3B Model**:

  ```bash
  ollama pull llama3.2:3b
  ```

- **Llama 3.1 8B Model**:

  ```bash
  ollama pull llama3.1:8b
  ```

These commands will download the specified models to your local machine.


#### Integrating PyTesseract for OCR

PyTesseract is a Python wrapper for Google's Tesseract-OCR Engine, enabling text extraction from images.

##### 1. Install Tesseract-OCR

- **Windows**:
  - Download the installer from the [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) page.
  - Run the installer and follow the instructions.

- **macOS**:
  - Use Homebrew to install Tesseract:

    ```bash
    brew install tesseract
    ```

- **Linux (Ubuntu)**:
  - Update your package list and install Tesseract:

    ```bash
    sudo apt update
    sudo apt install tesseract-ocr
    ```

##### 2. Install PyTesseract and Pillow

Install the necessary Python packages:

```bash
pip install pytesseract pillow
```

##### 3. Configure Environment Variables (Windows Only)

Add Tesseract-OCR to your system's PATH:

1. Locate the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`).
2. Add this path to the system environment variables.




### 3. Obtain Configuration Files



### Telegram Configuration

To configure Telegram, you need to set up access using the Telegram API for clients, which allows the application to interact with your personal Telegram account (not as a bot). Follow these steps:

1. **Obtain Telegram API Credentials**:
   - Go to the [Telegram API development portal](https://my.telegram.org/).
   - Log in using your Telegram account.
   - Create a new application under the "API Development Tools" section.
   - Save the `api_id` and `api_hash` provided for your application.

2. **Set Up Configuration**:
   Save your details in `config.yaml` file in the `config/` folder with the following structure:

   ```yaml
   telegram:
     api_id: YOUR_API_ID
     api_hash: YOUR_API_HASH
     phone_number: YOUR_PHONE_NUMBER
     session_name: YOUR_SESSION_NAME
   ```

   Replace `YOUR_API_ID`, `YOUR_API_HASH`, `YOUR_PHONE_NUMBER`, and `YOUR_SESSION_NAME` with your respective details:
   - `api_id` and `api_hash`: Obtained from the Telegram API portal.
   - `phone_number`: Your registered Telegram phone number.
   - `session_name`: A unique name to identify your session 



#### Google Calendar API JSON File

To enable Google Calendar schedule extraction:

1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or use an existing one.
3. Enable the Google Calendar API for your project.
4. Create service account credentials and download the JSON key file.
5. Save the JSON file as `config.json` in the `config/` folder

---

## How to Run

After completing the setup, run the application using the following command:

```bash
python -m src.main
```

This will start the AI Meeting Scheduler, and the AI will interact with it through your Telegram bot. The application will extract your current schedule from Google Calendar to identify suitable time slots for new meetings, and the AI will schedule meetings with your interlocutors if needed.

