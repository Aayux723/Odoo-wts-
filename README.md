# ERP-Flow: WhatsApp-to-ERP Automation Platform

![Tech Stack](https://img.shields.io/badge/Tech_Stack-Python_|_FastAPI_|_Odoo_|_Gemini_|_Docker-blue)

ERP-Flow is an automated, multimodal order processing pipeline that connects WhatsApp directly to Odoo ERP. It leverages the Meta WhatsApp Cloud API for receiving customer messages, Google's Gemini Vision API for intelligent data extraction, and FastAPI for webhook orchestration.

By converting free-form texts, photos of handwritten notes, and screenshots into structured Odoo Sales Orders automatically, this platform eliminates manual data entry and streamlines sales workflows.

## 🚀 Key Features

*   **Webhook-Driven Pipeline**: Real-time integration with the Meta WhatsApp Cloud API via a robust FastAPI backend.
*   **Multimodal AI Order Extraction**: Utilizes Google Gemini Vision to accurately extract products and quantities from:
    *   Free-form text messages
    *   Screenshots and printed product lists
    *   Handwritten order sheets
*   **Automated ERP Transactions**: Creates structured Odoo Quotations/Sales Orders dynamically using Odoo XML-RPC APIs.
*   **Robust Error Handling**: Includes duplicate webhook protection, graceful AI fallback mechanisms, and lazy Odoo authentication to ensure system stability.
*   **Docker Ready**: Designed to work seamlessly with containerized Odoo and PostgreSQL environments.

## 🛠️ Technology Stack

*   **Backend**: Python, FastAPI, Uvicorn
*   **AI/ML**: Google Gemini API (`gemini-2.5-flash`, `gemini-2.0-flash`), Gemini Vision
*   **ERP/Database**: Odoo ERP, PostgreSQL (Dockerized)
*   **Integrations**: Meta WhatsApp Cloud API, Odoo XML-RPC

## 📁 Project Structure

*   `webhook.py`: Main FastAPI application handling incoming WhatsApp webhook events and routing messages.
*   `ai_parser.py`: Interfaces with the Google Gemini SDK to parse text and image-based orders into structured JSON.
*   `whatsapp_media.py`: Handles secure downloading of image attachments from Meta's Graph API.
*   `process_order.py`: Orchestrates the flow from AI extraction to ERP creation.
*   `customer.py` / `product.py` / `sales.py`: Handlers for searching/creating Odoo records (Customers, Products, Sales Orders) via XML-RPC.
*   `odoo_client.py`: Manages the XML-RPC connection and authentication with the Odoo server.

## ⚙️ Setup Instructions

### 1. Prerequisites
*   Python 3.9+
*   A running instance of Odoo (e.g., via Docker)
*   Meta Developer Account (WhatsApp Business API App)
*   Google AI Studio API Key (Gemini)

### 2. Installation
Clone the repository and install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory and configure the following variables:

```env
# Odoo ERP Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=your_database_name
ODOO_USERNAME=admin
ODOO_PASSWORD=your_admin_password

# Google Gemini
GEMINI_API_KEY=your_google_gemini_api_key

# WhatsApp Cloud API
WHATSAPP_VERIFY_TOKEN=your_custom_verify_token
WHATSAPP_ACCESS_TOKEN=your_meta_system_user_token
```

### 4. Running the Application
Start the FastAPI server using Uvicorn:
```bash
uvicorn webhook:app --reload --host 0.0.0.0 --port 8000
```
*(Note: You will need to expose your local port via a tool like Ngrok or deploy to a public server for Meta to send webhook events successfully).*

## 🛡️ Robustness Features
*   **Duplicate Message Protection**: Maintains a sliding window cache to ignore redundant webhook retries from Meta.
*   **Graceful Failures**: If AI parsing yields low confidence or a product isn't mapped in Odoo, the system skips the item or flags the order without crashing the server.
*   **Audit Logging**: Built-in Python logging to track incoming payloads, parsed JSON results, and Odoo transaction IDs.
