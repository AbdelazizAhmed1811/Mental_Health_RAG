---
title: Mental Health RAG Chatbot
emoji: 🌿
colorFrom: green
colorTo: blue
sdk: docker
app_file: Dockerfile
pinned: false
---

# 🧠 Mental Health Companion Chatbot

<div align="center">
  <p><strong>Empathetic, Context-Aware, and Intelligent Support at Your Fingertips</strong></p>
  <p>An advanced AI-driven conversational agent built utilizing state-of-the-art NLP, Retrieval-Augmented Generation (RAG), and Emotion Classification to assist users with their mental well-being securely and responsibly.</p>
</div>

---

## 📖 Table of Contents

1. [Project Overview](#-project-overview)
2. [Core Architecture & Technologies](#-core-architecture--technologies)
3. [Key Features & Capabilities](#-key-features--capabilities)
4. [Project Structure in Detail](#-project-structure-in-detail)
5. [Model Weights & Datasets](#-model-weights--datasets)
6. [Emotion API Integration (Google Colab)](#-emotion-api-integration-google-colab)
7. [Comprehensive Setup Guide](#-comprehensive-setup-guide)
   - [Prerequisites](#prerequisites)
   - [Local Environment Setup](#local-environment-setup)
   - [Running the Application](#running-the-application)
8. [Development Roadmap & Future Enhancements](#-development-roadmap--future-enhancements)
9. [Contributing](#-contributing)
10. [License](#-license)

---

## 🌟 Project Overview

Mental health is a critical pillar of overall well-being. However, immediate and context-aware conversational support is not always accessible. The **Mental Health Companion App** aims to bridge this gap by offering a sophisticated, responsive, and deeply empathetic AI chatbot. 

By leveraging **Retrieval-Augmented Generation (RAG)**, the chatbot doesn't just "guess" its responses; it securely queries a rich vector database of clinical guidelines, grounding its therapeutic answers in verified knowledge. Moreover, this system implements multi-stage NLP processing—from language detection to nuanced emotion and intent classification—to tailor its conversational approach dynamically.

Whether a user is experiencing joy, fear, or distress, the Companion adjusts its tone and retrieves the most helpful context to assist the user effectively.

---

## 🏗 Core Architecture & Technologies

This project is highly modularized to ensure scalability, ease of development, and maintainability. It employs a modern web application stack divided into several micro-components:

### The Artificial Intelligence & NLP Layer
- **Language Detection**: Automatically infers the language of the user prompt to handle internationalization seamlessly.
- **Emotion Classification**: Uses a specialized neural network to classify the user's emotional state in real-time based on their text input.
- **RAG Pipeline (DSPy)**: We utilize DSPy to seamlessly combine Large Language Models with powerful retrieval systems.
- **Vector Database (Qdrant)**: Embeddings of mental health texts are stored and queried using Qdrant. We utilize both **Keyword-based Search** and **Hybrid Search** for optimal context retrieval.
- **Intent Classification**: Predicts the true purpose of the user's input before forming the final response.

### The Backend Application
- **Python 3.13 & FastAPI**: Provides a lightning-fast, asynchronous API interface for the frontend to consume.
- **UV**: For rapid package installation and reliable dependency management.
- **Microservices Approach**: The NLP pipeline interacts heavily with externally hosted models via HTTP APIs.

### The Frontend Application
- **Vanilla HTML5, CSS3, JavaScript**: A sleek, lightweight, and modern UI built without heavy frameworks to ensure maximum performance and responsiveness.
- **Real-Time Asynchronous UI**: Ensures a seamless chat experience without page reloads or latency spikes.

---

## 🚀 Key Features & Capabilities

- 🎭 **Real-Time Emotion Recognition**: Every message sent by the user is routed through our custom Emotion API to determine their current mental state (e.g., joy, sadness, fear, anger).
- 🧠 **Context-Aware Responses**: By incorporating the user's detected emotion and intent, the core LLM shifts its persona to be as supportive and relevant as possible.
- 📚 **Knowledge Grounding via RAG**: Halting LLM hallucinations by enforcing strict retrieval of psychological facts and guidelines before replying to the user.
- ⚡ **Streamlined Execution**: A beautifully automated `start.sh` script spins up the entire local infrastructure with a single command, making developer onboarding frictionless.

---

## 📁 Project Structure in Detail

Understanding the repository layout is crucial for extending the application. Here is a high-level overview of our codebase:

```text
final_project/
├── backend/                  # The Python/FastAPI Backend Service
│   ├── src/                  # Core source code, routing, and Pydantic schemas
│   ├── scripts/              # Helper scripts for backend management
│   ├── tests/                # Automated Pytest suite
│   ├── run.py                # Main application entry point
│   └── requirements.txt      # Backend-specific dependencies
├── frontend/                 # The User Interface
│   ├── index.html            # Main markup and application skeleton
│   ├── style.css             # Styling rules, animations, and responsive design
│   └── app.js                # Frontend logic, DOM manipulation, and API fetching
├── notebooks/                # Experimental & Data Engineering Notebooks
│   ├── Emotion_API.ipynb         # Crucial: Hosts the Emotion Classification Model
│   ├── Language_classifier.ipynb # Language detection model training & validation
│   ├── Emotions_classifier.ipynb # Emotion model training sandbox
│   ├── Embeddings.ipynb          # Generates vector embeddings for our datasets
│   └── Qdrant_Ingestion.ipynb    # Code to push embeddings into Qdrant vector DB
├── models/                   # Directory to hold downloaded `.pt` or `.bin` weights
├── docs/                     # Additional architectural or operational documentation
├── todo.txt                  # The team's active task list and sprint goals
└── start.sh                  # The master script to launch all local services
```

---

## 💾 Model Weights & Datasets

To ensure the repository remains lightweight and cloneable, we host our large pre-trained machine learning weights and compiled datasets externally on Google Drive. 

> **CRITICAL REQUIREMENT:** The system cannot function without these model files! Before running the application, you must procure these assets.

👉 **[Click Here to Download the Models Folder](https://drive.google.com/drive/u/0/folders/1DWRlLCzMf8znqAwRMZ4C5VcIz1LsUS5K)**

**Instructions:**
1. Download the contents of the Google Drive link.
2. Extract the downloaded files if they are compressed.
3. Place the required model files directly into the `/models/` directory in the root of this project.

---

## 🌐 Emotion API Integration (Google Colab)

Due to hardware constraints and the heavy computational requirements of our Emotion Classification deep learning model, **the Emotion classifier does not run locally by default.** Instead, we leverage Google Colab's free GPU resources to host this segment of the pipeline.

### How It Works:
1. The `notebooks/Emotion_API.ipynb` file contains the logic to load the emotion model, instantiate a Flask/FastAPI server, and expose it to the internet utilizing tools like Ngrok or Localtunnel.
2. Your local backend application will make HTTP `POST` requests to this Colab endpoint every time a user sends a message.

### Instructions to Start the Emotion API:
1. Open the hosted Colab Notebook directly here: 👉 **[Emotion API Colab Notebook](https://colab.research.google.com/drive/1qrAmR5AnISbW6LmsZJjqpFQ9H3YeQyYx?usp=sharing)**.
2. (Optional) Alternatively, you can manually upload the `notebooks/Emotion_API.ipynb` file from this repository into your own Colab environment.
3. Change the runtime type to **T4 GPU** (or better) via the runtime menu.
4. **Run All Cells**.
5. The final cell will output a public URL (e.g., `https://xxxx-xx-xx.ngrok-free.app`).
6. Copy this URL. You must inject this URL into your backend `.env` file (or hardcode it if testing) so the backend knows exactly where to route its emotion classification requests.

---

## 🛠 Comprehensive Setup Guide

Follow these steps carefully to launch the complete application stack on your local machine. Ensure you do not skip steps, especially regarding model downloads.

### Prerequisites
Before you begin, ensure you have the following installed on your system:
- **Python 3.13** (The project adheres strictly to Python 3.13 standards)
- **uv** (An extremely fast Python package installer and resolver)
- **Git** (For version control)
- A Modern Web Browser (Chrome, Firefox, Edge, Safari)

### Local Environment Setup

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd final_project
   ```

2. **Set up the Virtual Environment (Optional but Recommended)**
   While `uv` handles a lot, it's safe to use a virtual environment.
   ```bash
   python3.13 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Backend Dependencies**
   Navigate to the backend and use `uv` to install everything cleanly.
   ```bash
   cd backend
   uv pip install -r requirements.txt
   cd ..
   ```

4. **Populate Models**
   Ensure you have downloaded the models from the provided Google Drive link and placed them in the `/models/` folder as explained earlier.

5. **Configure Environment Variables**
   Create a `.env` file in the `/backend/` directory. Be sure to add the Colab Emotion API URL as discussed in the section above.

### Running the Application

To make life exceptionally easy, we have provided an automated startup script. This bash script will initialize both the backend API and the frontend server as background processes and bind them together.

1. **Make the Script Executable**
   ```bash
   chmod +x start.sh
   ```

2. **Execute the Start Script**
   ```bash
   ./start.sh
   ```

   **What happens when you run this?**
   - Any stale processes lingering on ports `8000` or `8080` are gracefully killed.
   - The FastAPI backend starts on **Port 8000** in the background.
   - A local Python HTTP server serves the frontend on **Port 8080** in the background.
   - Your terminal will display a clear success message.

3. **Access the Chatbot**
   Open your browser and navigate to: `http://localhost:8080`

4. **Stopping the Services**
   When you are done testing, return to the terminal running `start.sh` and hit `Ctrl+C`. The script has a built-in trap that will cleanly shut down both servers safely.

---

## 📈 Development Roadmap & Future Enhancements

The project is continually evolving. Below is an exhaustive overview of our current priorities (as defined in our `todo.txt`):

### Currently Completed milestones:
- ✅ **Language Detection Pipeline** (Lead: Abdelaziz)
- ✅ **Emotion Classification Integration** (Lead: Sokary)

### Active Development (Mandatory Sprint Goals):
- 🔄 **DSPy Integration**: Refactoring the RAG layer using DSPy to program our language models effectively and reproducibly (Lead: Abdelaziz).
- 🔄 **Advanced Retrieval Mechanisms**: Researching and implementing the absolute best retrieval methodologies, heavily focusing on combining **Keyword-based Search** and dense **Hybrid Search** algorithms (Lead: Sokary).
- 🔄 **UI/UX Enhancements**: Dramatically improving the aesthetic and interactivity of the frontend user interface to provide a truly premium and calming experience.
- 🔄 **Prompt Engineering Mastery**: Reassessing, refining, and rigorously testing the intent classification prompts and final response generation prompts to guarantee a high degree of clinical empathy and safety guardrails.
- 🔄 **Deployment & DevOps Architecture**:
  - Fully Dockerizing the project for seamless containerized deployments (Lead: Reda).
  - Configuring CI/CD pipelines to publish the web application directly onto the Render hosting platform (Lead: Reda).

### Future Pipeline (Optional / Phase 2 Objectives):
- 🔮 **Persistent User Database**: Integrating a robust relational (PostgreSQL) or NoSQL database to persistently store ongoing user chats, transcripts, and emotional trends over time.
- 🔮 **Historical Context Integration**: Allowing the chatbot to actively remember past sessions and utilize previous emotional states to provide deep, long-term therapeutic continuity rather than just stateless one-off interactions.
- 🔮 **Langsmith Observability Framework**: Integrating Langsmith to trace, evaluate, and monitor the LLM applications in real time, giving us unparalleled insight into latency, token usage, and answer quality.

