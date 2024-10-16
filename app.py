# app.py
import os
import json
import logging
import requests
from urllib.parse import urlparse
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

# Azure credentials from environment variables
endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

# Initialize FastAPI app
app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    """Check if the provided string is a valid and accessible URL."""
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            logger.error("Invalid URL structure: %s", url)
            return False
        
        if result.scheme not in ["http", "https"]:
            logger.error("Unsupported URL scheme: %s. Only http and https are allowed.", result.scheme)
            return False

        logger.info("URL format looks valid: %s", url)
        
        # Make a HEAD request to check if the URL is accessible and if it's a PDF
        response = requests.head(url, timeout=10, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '')
        
        if response.status_code == 200 and ('application/pdf' in content_type.lower() or content_type == ''):
            logger.info("URL is accessible and likely points to a PDF file.")
            return True
        else:
            logger.error("URL is either not accessible or does not point to a PDF. Status Code: %d, Content-Type: %s", 
                         response.status_code, content_type)
            return False

    except requests.exceptions.RequestException as e:
        logger.error("Error during URL validation request: %s", str(e))
        return False
    except Exception as e:
        logger.error("Unexpected error validating URL: %s", str(e))
        return False

def analyze_document_from_url(document_analysis_client, url):
    """Analyze document content from a URL."""
    try:
        logger.info("Initiating document analysis from URL: %s", url)
        poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-read", url, locale="th"
        )
        logger.info("Polling for the result from URL analysis...")
        result = poller.result()
        logger.info("Document analysis from URL completed successfully.")
        log_api_result(result)
        return extract_content(result)
    except Exception as e:
        logger.error("Error analyzing document from URL: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error analyzing document from URL: {str(e)}")

def analyze_document_from_file(document_analysis_client, file):
    """Analyze document content from an uploaded file."""
    try:
        logger.info("Initiating document analysis from uploaded file.")
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-read", document=file, locale="th"
        )
        logger.info("Polling for the result from file analysis...")
        result = poller.result()
        logger.info("Document analysis from file completed successfully.")
        log_api_result(result)
        return extract_content(result)
    except Exception as e:
        logger.error("Error analyzing document from file: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error analyzing document from file: {str(e)}")

def log_api_result(result):
    """Log the full API result for detailed analysis."""
    try:
        result_dict = result.to_dict()
        logger.info("Full API result: %s", json.dumps(result_dict, ensure_ascii=False, indent=2))
    except Exception as e:
        logger.error("Error logging API result: %s", str(e))

def extract_content(result):
    """Extract text content from the document result."""
    try:
        logger.info("Extracting content from the analysis result.")
        full_content = ""
        for page_number, page in enumerate(result.pages, start=1):
            logger.info("Processing page %d", page_number)
            page_text = "\n".join([line.content for line in page.lines])
            
            # Decode the text to handle UTF-8-SIG (Byte Order Mark)
            page_text = page_text.encode("utf-8-sig").decode("utf-8-sig")
            
            logger.debug("Extracted content from page %d: %s", page_number, page_text.encode("utf-8-sig"))
            full_content += page_text + "\n"
        
        logger.info("Content extraction completed.")
        return {"Content": full_content}
    except Exception as e:
        logger.error("Error extracting content: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error extracting content: {str(e)}")

@app.post("/ocr")
async def ocr_document(file: UploadFile = File(None), url: str = Form(None)):
    """API endpoint for OCR document analysis."""
    logger.info("Received OCR request.")
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    # Log the inputs explicitly
    logger.info("File: %s, URL: %s", file.filename if file else "None", url)

    try:
        # Check if neither file nor URL is provided
        if file is None and url is None:
            logger.error("No file or URL received in the request.")
            raise HTTPException(status_code=400, detail="No file or URL received in the request.")

        if file and url:
            logger.warning("Both file and URL provided. Please provide only one input.")
            raise HTTPException(status_code=400, detail="Provide either a file or a valid URL, not both.")

        if file:
            logger.info("File detected in the request, processing it.")
            content = await file.read()
            if not content:
                logger.error("Uploaded file is empty.")
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")
            logger.debug("File read successfully, size: %d bytes", len(content))
            response = analyze_document_from_file(document_analysis_client, content)

        elif url:
            logger.info("URL detected in the request: %s", url)
            if not is_valid_url(url):
                logger.error("Invalid or inaccessible URL: %s", url)
                raise HTTPException(status_code=400, detail="Invalid or inaccessible URL. Provide a valid PDF URL.")
            response = analyze_document_from_url(document_analysis_client, url)

        logger.info("Returning extracted content as JSON response.")
        return JSONResponse(content=response, media_type="application/json; charset=utf-8-sig")

    except HTTPException as http_exc:
        logger.error("HTTPException occurred: %s", http_exc.detail)
        raise http_exc
    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    import uvicorn
    # Run the app locally
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
