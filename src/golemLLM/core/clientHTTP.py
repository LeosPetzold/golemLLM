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

    def shotProbeHEAD(self, shotID):
        """Checks the shot database to find whether a shot with the ID is already registered."""
        if self.verbose:
            print(f"[DEBUG] Checking existence of shot {'LATEST' if shotID == 0 else shotID} at {self.shotsURL}")
        try:
            req = urllib.request.Request(f"{self.shotsURL}/{shotID}", method='HEAD')
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
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
        try:
            req = urllib.request.Request(f"{self.shotsURL}/{shotID}/{fileName}", method='GET')
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise FileNotFoundError(f"File '{fileName}' not found for shot {shotID}.")
            else:
                raise e

    def getShotFileCached(self, shotID, fileName):
        """Downloads a specific file from the shot archive and caches it locally."""

        #if (shotID == 0):
        #            result = self.getShotFile(shotID, "shot_no")
        #            shotID = int(result.decode('utf-8').strip())

        path_parts = [p for p in str(fileName).replace("\\", "/").split("/") if p not in ("", ".", "..")]
        fileName = "/".join(path_parts)

        cache_key = (shotID, fileName)
        if cache_key in self._cache:
            if (self.verbose):
                print(f"[DEBUG] Returning cached file '{fileName}' for shot {shotID}")
            return self._cache[cache_key]

        data = self.getShotFile(shotID, fileName)
        self._cache[cache_key] = data
        print(f"[DEBUG] Cached file '{fileName}' for shot {shotID}")
        return data
        
    def clearCache(self):
        """Clears the local cache of downloaded shot files."""
        self._cache.clear()


from types import SimpleNamespace

class GolemSHOThttp:
    def __init__(self, shotID, client):
        if (shotID == 0):
                    result = client.getShotFile(shotID, "shot_no")
                    shotID = int(result.decode('utf-8').strip())
        elif (not client.shotProbeHEAD(shotID)):
            raise ValueError(f"Shot ID {shotID} does not exist in the shot database.")
        self._shotID = shotID

        self.client = client
        self.verbose = client.verbose

    # Concrete shot functionality

    ## Helpers
    def simUTF8(self, path): # Simple UTF-8 file value processing
        return self.client.getShotFileCached(self._shotID, path).decode('utf-8').strip()

    ## Basic information
    @property
    def ID(self):
        return self._shotID
    @property
    def timestamp(self):
        """Returns the timestamp of the shot."""
        return self.simUTF8("shot_date") + " " + self.simUTF8("shot_time")
    @property
    def comment(self):
        """Returns the comment associated with the shot."""
        return self.simUTF8("comment")


# Testing
client = GolemCLIENThttp(verbose=True)
shot = GolemSHOThttp(0, client)
