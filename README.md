# Fake News Detector v0.3

A Python-based application equipped with an interactive Streamlit web interface designed to detect and analyze fake news articles.

## Features
* **Streamlit Web UI:** Clean, intuitive, and interactive browser-based dashboard.
* **Real-time Analysis:** Fast and accurate news text verification.
* **Environment Configuration:** Secure handling of configuration keys via a `.env` file.

## Prerequisites
Ensure you have Python installed on your system.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd fake-news-detector
   ```

2. **Set up a virtual environment:**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your environment variables:**
   Create a `.env` file in the root directory and populate it with your specific API credentials:
   ```env
   # Example configuration keys (Do not commit real keys!)
   API_KEY=your_secret_key_here
   ```

5. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

