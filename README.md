
# OCR Text Extraction App

This project is an OCR (Optical Character Recognition) application that can extract text from images or PDF files using the FastAPI framework. The application can be run locally or within a Docker container.

## Project Structure

- **[`local-app.py`](#)**: Script to run the application locally, using environment variables from a `.env` file to configure API keys and other settings. [Download here](#).
- **[`app.py`](#)**: Script that will be executed within the Docker container. [Download here](#).
- **[`Dockerfile`](#)**: Docker configuration file used to build the image for the application. [Download here](#).
- **[`requirements.txt`](#)**: Contains the list of dependencies required for the application. [Download here](#).

## Features

- Extracts text from images and PDF files using the Azure Form Recognizer service.
- Supports local execution or Docker-based execution.
- Accepts input as a file upload or a URL for the file location.
- Outputs extracted text in JSON format.

---

## Local Execution Instructions

### 1. Prerequisites

Make sure you have the following installed:

- Python 3.9 or higher
- [pip](https://pip.pypa.io/en/stable/)

### 2. Install Dependencies

Before running the application locally, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root of your project with the following content. You can find the required Azure credentials from your Azure portal:

```bash
AZURE_FORM_RECOGNIZER_ENDPOINT=<your-azure-endpoint>
AZURE_FORM_RECOGNIZER_KEY=<your-azure-api-key>
```

### 4. Running Locally

To run the application locally using the `local-app.py` file:

```bash
python local-app.py
```

### 5. Usage Instructions

You can use Postman or any other REST client to interact with the application. The application supports two ways to input files for OCR:

1. **File Upload**: Upload a local image or PDF file.
2. **URL**: Provide a URL to the file.

#### Example Request (Postman)

- **URL**: `http://localhost:8000/extract-text`
- **Method**: `POST`
- **Body**:
  - Select "form-data".
  - Add two keys:
    1. **file**: Choose the image or PDF file to upload.
    2. **url**: (Optional) Provide a URL of the file to extract text from.

#### Optional Parameters
- **extract_format**: Specify whether to extract text in a specific format (like `json`, `plain_text`). Default is `json`.
  
  Example:
  ```json
  {
    "extract_format": "plain_text"
  }
  ```

#### Example Response

```json
{
  "extracted_text": "Your extracted text will be here..."
}
```

---

## Docker Execution Instructions

### 1. Build the Docker Image

To build the Docker image using the provided `Dockerfile`, navigate to the project root and run:

```bash
docker build -t test-ocr-app .
```

### 2. Run the Docker Container

To run the container and expose the application on port 8000:

```bash
docker run -d -p 8000:8000 --name test-ocr-app test-ocr-app
```

### 3. Usage Instructions

Once the Docker container is running, you can use Postman to interact with the application.

- **URL**: `http://localhost:8000/extract-text`
- **Method**: `POST`
- **Body**:
  - Use the same structure as the local usage example:
    - **file**: Choose the file to upload (image or PDF).
    - **url**: Provide a URL if the file is hosted remotely.

#### Optional Parameters
- **extract_format**: Specify the format (`json`, `plain_text`) in which the text should be extracted. Default is `json`.

Example request:
- **file**: Your local file to extract.
- **url**: Optional file URL if hosted online.
- **extract_format**: (Optional) `plain_text` or `json`.

---

## Cleaning Up Docker Resources

To remove any unused Docker containers, networks, and images, run the following command:

```bash
docker system prune -f
```

---

## Conclusion

This project allows you to extract text from image and PDF files either locally or within a Docker container. It provides flexibility by supporting both file uploads and URLs as inputs, and the extracted text can be retrieved in either JSON or plain text format.
