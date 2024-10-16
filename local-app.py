import os
import json
from urllib.parse import urlparse
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure credentials from environment variables
endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

def is_valid_url(url):
    """Check if the provided string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def analyze_read(input_source):
    # Create DocumentAnalysisClient instance
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    # Determine if the input source is a URL or a local file
    if is_valid_url(input_source):
        print("Analyzing document from URL...")
        poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-read", input_source, locale="th"
        )
    elif os.path.isfile(input_source):
        print("Analyzing document from local file...")
        with open(input_source, "rb") as fd:
            poller = document_analysis_client.begin_analyze_document(
                "prebuilt-read", document=fd, locale="th"
            )
    else:
        print("Invalid input. Please provide a valid URL or a local PDF file path.")
        return

    result = poller.result()

    # Extract and concatenate the content of the document across all pages
    full_content = ""
    for page in result.pages:
        page_text = "\n".join([line.content for line in page.lines])
        full_content += page_text + "\n"

    # Ensure content is UTF-8 encoded for compatibility with Thai and other languages
    utf8_content = full_content.encode('utf-8').decode('utf-8')
    
    # Structure the output as JSON under the objective "Content"
    output = {
        "Content": utf8_content
    }

    # Print the output as a JSON string
    print(json.dumps(output, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    input_source = input("Enter the URL or path to your document (PDF): ")
    analyze_read(input_source)
