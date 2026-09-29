# HTTP shot archive access & caching

import urllib.request
import urllib.error
#import argparse

SHOTSURL_DEFAULT = "http://golem.fjfi.cvut.cz/shots"
TIMEOUT = 10  # seconds

class GolemCLIENThttp:
    def __init__(self, shotsURL=SHOTSURL_DEFAULT, verbose=False):
        self.shotsURL = shotsURL
        self.verbose = verbose
        self._cache = {}

    # General shot functionality

    def shotExists(self, shotID):
        """Checks the shot database to find whether a shot with the ID is already registered."""
        if self.verbose:
            print(f"[DEBUG] Checking existence of shot {'LATEST' if shotID == 0 else shotID} at {self.shotsURL}")
        try:
            with urllib.request.urlopen(f"{self.shotsURL}/{shotID}", method='HEAD', timeout=TIMEOUT) as response:
                if response.status == 200:
                    return True
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
        try:
            with urllib.request.urlopen(f"{self.shotsURL}/{shotID}/{fileName}", timeout=TIMEOUT) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"[ERROR] File '{fileName}' not found for shot {shotID}.")
                raise FileNotFoundError(f"File '{fileName}' not found for shot {shotID}.")
            else:
                raise e

    def getShotFileCached(self, shotID, fileName):
        """Downloads a specific file from the shot archive and caches it locally."""

        if (shotID == 0):
            result = self.getShotFile(shotID, "shot_no");
            assert result is not None, "[ERROR] Failed to retrieve shot number for (LATEST) shot."
            shotID = int(result.decode('utf-8').strip())

        path_parts = [p for p in str(fileName).replace("\\", "/").split("/") if p not in ("", ".")]
        fileName = path_parts.join("/");
        
    def clearCache(self):
        """Clears the local cache of downloaded shot files."""
        self._cache.clear()

        





from types import SimpleNamespace

class GolemSHOThttp:
    def __init__(self, shotID, client):
        self.shotID = shotID
        self.client = client
        self.verbose = client.verbose

    # Concrete shot functionality

