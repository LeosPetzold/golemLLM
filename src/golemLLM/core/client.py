# Shot archive access & caching

from urllib import response
import urllib.request
import urllib.error
#import argparse

class GolemCLIENThttp:
    def __init__(self, shotsURL="http://golem.fjfi.cvut.cz/shots", verbose=False):
        self.shotsURL = shotsURL
        self.verbose = verbose


    def shotExists(self, shotID):
        """Checks the shot database to find whether a shot with the ID is already registered."""
        if self.verbose:
            print(f"[DEBUG] Checking existence of shot {'LATEST' if shotID == 0 else shotID} at {self.shotsURL}")
        try:
            req = urllib.request.Request(f"{self.shotsURL}/{shotID}", method='HEAD')
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            else:
                raise e


    def getShotFile(self, shotID, fileName):
        """Downloads a specific file from the shot archive."""
        if self.verbose:
            print(f"[DEBUG] Downloading file '{fileName}' for shot {'LATEST' if shotID == 0 else shotID} from {self.shotsURL}")
        try:
            with urllib.request.urlopen(f"{self.shotsURL}/{shotID}/{fileName}") as response:
                return response.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"[ERROR] File '{fileName}' not found for shot {shotID}.")
                return None
            else:
                raise e