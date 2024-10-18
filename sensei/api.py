import requests
from tqdm import tqdm
import os
import math

class Api:
    def __init__(self, api_key, destination=None):
        self.api_key = api_key
        self.api_root = "http://127.0.0.1:8000/datasets/"
        self.destination = destination

    def make_request(self, url):
        response = requests.get(f"{self.api_root}{url}", headers={"Authorization": f"ApiKey {self.api_key}"})
        if response.status_code == 403:
            raise RuntimeError("Authentication failed. Check your API key.")
        return response.json()
    
    def _iter_results(self, url):
        """
        Iterates over a paginated API response
        """
        response = self.make_request(url)
        yield from response["results"]
        if response["next"]:
            yield from self._iter_results(response["next"])

    def iter_files(self, path="/"):
        """
        Iterates over files in given directory (defaults to root directory)
        """
        return self._iter_results(f"files/?parent={path}")

    def iter_dirs(self, path="/"):
        """
        Iterates over directories in given directory (defaults to root directory)
        """
        return self._iter_results(f"paths/?parent={path}")
    
    def get_file(self, path):
        """
        Gets API info of file at given path
        """
        path_parts = path.split("/")
        filename = path_parts[-1]
        filepath = "/".join(path_parts[:-1])
        response = self.make_request(f"files/?parent={filepath}&filename={filename}")
        if response["count"] == 0:
            raise FileNotFoundError()
        assert response["count"] == 1
        return response["results"][0]
    
    def _download_file(self, file, overwrite=False):
        """
        Downloads the file
        """
        if not self.destination:
            raise RuntimeError("To download files, pass in a destination to the Api class constructor")
        
        dest_filepath = os.path.join(self.destination, file['path'], file["filename"])
        
        print("Downloading to", dest_filepath)
        os.makedirs(os.path.dirname(dest_filepath), exist_ok=True)
        if os.path.isfile(dest_filepath):
            if overwrite:
                print("Overwriting")
            else:
                print("WARNING: File already exists. Skipping download. Set overwrite=True to overwrite")
                return
            
        response = requests.get(file["url"], stream=True)
        CHUNK_SIZE = 10240
        num_chunks = math.ceil(int(response.headers['Content-Length'])/CHUNK_SIZE)
        with open(dest_filepath, "wb") as handle:
            for data in tqdm(response.iter_content(chunk_size=10*1024), unit='kB', total=num_chunks):
                handle.write(data)

    def download_file_from_path(self, path, overwrite=False):
        file = self.get_file(path)
        return self._download_file(file, overwrite=overwrite)

    def recursive_download(self, path="/", overwrite=False):
        """
        Recursively download all files in given folder
        """
        
        print(f"Downloading from {path}...")
        file_found = False
        for file in self.iter_files(path):
            self._download_file(file, overwrite=overwrite)
            file_found = True

        for folder in self.iter_dirs(path):
            self.recursive_download(path=folder["path"], overwrite=overwrite)
            file_found = True
            
        return file_found


