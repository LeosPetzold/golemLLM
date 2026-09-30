# Shot archive access & caching

import time
import urllib.request
import urllib.error
#import argparse

HTTP_SHOTSURL_DEFAULT = "http://golem.fjfi.cvut.cz/shots"
HTTP_TIMEOUT  = 10  # seconds
HTTP_ATTEMPTS = 5   # retries for file requests

LOCAL_SHOTSPATH_DEFAULT = "/home/tG/shots/" # Sample
LOCAL_ATTEMPTS = 5  # retries for file access

class GolemCLIENThttp:
    def __init__(self, shotsURL=HTTP_SHOTSURL_DEFAULT, cache=True, verbose=False):
        self.shotsURL = shotsURL
        self.cache = cache
        self.verbose = verbose
        self._cache = {}

    # General shot functionality

    def shotProbeHEAD(self, shotID):
        """Checks the shot database to find whether a shot with the ID is already registered *on the database*."""
        if self.verbose:
            print(f"[DEBUG] Checking existence of shot {'LATEST' if shotID == 0 else shotID} at {self.shotsURL}")
        try:
            req = urllib.request.Request(f"{self.shotsURL}/{shotID}", method='HEAD')
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as response:
                return response.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            else:
                raise e

    # Helper functions

    def getShotFile(self, shotID, fileName):
        """Downloads a specific file from the shot archive."""
        if self.verbose:
            print(f"[DEBUG] Downloading file '{fileName}' for shot {'LATEST' if shotID == 0 else shotID} from {self.shotsURL}")
        for attempt in range(HTTP_ATTEMPTS):
            try:
                req = urllib.request.Request(f"{self.shotsURL}/{shotID}/{fileName}", method='GET')
                with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as response:
                    return response.read()
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    raise e
                if attempt < HTTP_ATTEMPTS - 1:
                    if self.verbose:
                        print(f"[DEBUG] Attempt {attempt + 1} failed for file '{fileName}' of shot {shotID}. Retrying...")
                    time.sleep(1)  # Wait a bit before retrying
                    continue
                #if e.code == 404:
                raise FileNotFoundError(f"File '{fileName}' not found for shot {shotID}.")

    def getShotFileCached(self, shotID, fileName):
        """Downloads a specific file from the shot archive and caches it locally."""

        #if (shotID == 0):
        #            result = self.getShotFile(shotID, "shot_no")
        #            shotID = int(result.decode('utf-8').strip())

        path_parts = [p for p in str(fileName).replace("\\", "/").split("/") if p not in ("", ".", "..")]
        fileName = "/".join(path_parts)
        
        if not self.cache:
            data = self.getShotFile(shotID, fileName)
            if self.verbose: print(f"[DEBUG] Caching disabled. Returning file '{fileName}' for shot {shotID} without caching.")
            return data
        #else:

        cache_key = (shotID, fileName)
        if cache_key in self._cache:
            if self.verbose: print(f"[DEBUG] Returning cached file '{fileName}' for shot {shotID}")
            return self._cache[cache_key]

        data = self.getShotFile(shotID, fileName)
        self._cache[cache_key] = data
        print(f"[DEBUG] Cached file '{fileName}' for shot {shotID}")
        return data
        
    def clearCache(self):
        """Clears the local cache of downloaded shot files."""
        self._cache.clear()

class GolemCLIENTlocal:
    def __init__(self, shotsURL=HTTP_SHOTSURL_DEFAULT, verbose=False):
            self.shotsURL = shotsURL
            self.verbose = verbose
            self._cache = {}