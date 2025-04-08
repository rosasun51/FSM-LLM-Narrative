<<<<<<< HEAD
import os
import requests
import zipfile
import shutil

def download_model():
    """
    Download the sentence-transformers model manually.
    """
    # Create cache directory
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    # Model URL (using a direct download link)
    model_url = "https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/paraphrase-MiniLM-L3-v2.zip"
    model_path = os.path.join(cache_dir, "paraphrase-MiniLM-L3-v2.zip")
    
    print("Downloading model...")
    # Download the model
    response = requests.get(model_url, stream=True)
    with open(model_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    print("Extracting model...")
    # Extract the model
    with zipfile.ZipFile(model_path, 'r') as zip_ref:
        zip_ref.extractall(cache_dir)
    
    # Clean up
    os.remove(model_path)
    print("Model downloaded and extracted successfully!")

if __name__ == "__main__":
    download_model() 
||||||| 73f7c15e6
=======
import os
import requests
import zipfile
import shutil

def download_model():
    """
    Download the sentence-transformers model manually.
    """
    # Create cache directory
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    # Model URL (using a direct download link)
    model_url = "https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/paraphrase-MiniLM-L3-v2.zip"
    model_path = os.path.join(cache_dir, "paraphrase-MiniLM-L3-v2.zip")
    
    print("Downloading model...")
    # Download the model
    response = requests.get(model_url, stream=True)
    with open(model_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    print("Extracting model...")
    # Extract the model
    with zipfile.ZipFile(model_path, 'r') as zip_ref:
        zip_ref.extractall(cache_dir)
    
    # Clean up
    os.remove(model_path)
    print("Model downloaded and extracted successfully!")

if __name__ == "__main__":
    download_model() 
>>>>>>> fe5206a7596bb44889a38717f23363f9e0fbf95e
