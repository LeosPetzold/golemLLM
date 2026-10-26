# Shot archive access & caching

import os
import time
import urllib.request
import urllib.error
import urllib.parse
from html.parser import HTMLParser
#import argparse

HTTP_SHOTSURL_DEFAULT = "http://golem.fjfi.cvut.cz/shots"
HTTP_TIMEOUT  = 10  # seconds
HTTP_ATTEMPTS = 5   # retries for file requests

LOCAL_SHOTSPATH_DEFAULT = "/home/tG/shots/" # Sample; shots shall be named by number
LOCAL_ATTEMPTS = 5  # retries for file access

_MISSING = object() # Sentinel for missing files


class _DirectoryListingParser(HTMLParser):
    """Parse files and directories from a standard HTML directory index."""
    def __init__(self):
        super().__init__()
        self.entries = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href", "")
        parsed = urllib.parse.urlparse(href)
        name = urllib.parse.unquote(parsed.path).rstrip("/").rsplit("/", 1)[-1]
        if name in ("", ".", ".."):
            return
        entry_type = "directory" if parsed.path.endswith("/") else "file"
        entry = {"name": name, "type": entry_type}
        if entry not in self.entries:
            self.entries.append(entry)

# Golem CLIENT base for shared processing functionality & caching features
class _GolemCLIENTbase:
    def _getShotFileCached(self, shotID, fileName):
        """BASE HAS NO DESCRIPTION FOR THIS."""

        if (shotID == 0):
            shotID = self.getLatestShotID()

        path_parts = [p for p in str(fileName).replace("\\", "/").split("/") if p not in ("", ".", "..")]
        fileName = "/".join(path_parts)
        
        if not self.cache:
            data = self.getShotFile(shotID, fileName)
            if self.verbose: print(f"[DEBUG] Caching disabled. Returning file '{fileName}' for shot {shotID} without caching.")
            return data
        #else:

        cache_key = (shotID, fileName)
        if cache_key in self._cache:
            data = self._cache[cache_key]
            if data is _MISSING:
                if self.verbose: print(f"[DEBUG] Returning cached MISSING for file '{fileName}' of shot {shotID}")
                raise FileNotFoundError(f"File '{fileName}' not found for shot {shotID}.")
            if self.verbose: print(f"[DEBUG] Returning cached file '{fileName}' for shot {shotID}")
            return data

        try:
            data = self.getShotFile(shotID, fileName)
        except FileNotFoundError:
            self._cache[cache_key] = _MISSING
            raise
        self._cache[cache_key] = data
        if self.verbose: print(f"[DEBUG] Cached file '{fileName}' for shot {shotID}")
        return data
        
    def _clearCache(self):
        """BASE HAS NO DESCRIPTION FOR THIS."""
        self._cache.clear()


# Golem CLIENT for HTTP access
class GolemCLIENThttp(_GolemCLIENTbase):
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
            # There is always a file named shot_no in the shot directory.
            req = urllib.request.Request(f"{self.shotsURL}/{shotID}/shot_no", method='GET')
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as response:
                return response.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            else:
                raise e

    # Helper functions

    def listDirectory(self, shotID, directory):
        """Lists files and directories in a shot directory exposed by the HTTP archive."""
        if shotID == 0:
            shotID = self.getLatestShotID()
        path_parts = [p for p in str(directory).replace("\\", "/").split("/") if p not in ("", ".", "..")]
        relative_directory = "/".join(path_parts)
        url = f"{self.shotsURL}/{shotID}/"
        if relative_directory:
            url += f"{urllib.parse.quote(relative_directory, safe='/')}/"
        try:
            with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as response:
                parser = _DirectoryListingParser()
                parser.feed(response.read().decode("utf-8", errors="replace"))
                return parser.entries
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise FileNotFoundError(f"Shot directory {shotID} not found.") from e
            raise

    def getLatestShotID(self):
        return int(self.getShotFile(0, "shot_no").decode('utf-8').strip())
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
                if e.code == 404:
                    raise FileNotFoundError(f"File '{fileName}' not found for shot {shotID}.") from e
                if e.code < 500:
                    raise e  # Client error (4xx), do not retry 
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                pass
            if attempt < HTTP_ATTEMPTS - 1:
                if self.verbose:
                    print(f"[DEBUG] Attempt {attempt + 1} failed for file '{fileName}' of shot {shotID}. Retrying...")
                time.sleep(0.5 * (2 ** attempt))  # Wait a bit before retrying
        raise ConnectionError(f"Failed to download file '{fileName}' of shot {shotID} after {HTTP_ATTEMPTS} attempts.")

    def getShotFileCached(self, shotID, fileName):
        """Downloads a specific file from the shot archive and caches it locally."""
        return self._getShotFileCached(shotID, fileName)
        
    def clearCache(self):
        """Clears the local cache of downloaded shot files."""
        self._clearCache()

# Golem CLIENT for filesystem access
class GolemCLIENTlocal(_GolemCLIENTbase):
    def __init__(self, basePath=LOCAL_SHOTSPATH_DEFAULT, cache=False, verbose=False):
        self.basePath = basePath
        self.cache = cache
        self.verbose = verbose
        self._cache = {}

    # General shot functionality

    def shotProbeHEAD(self, shotID):
        """Checks the shot directory to find whether the shot is already registered *on the filesystem*."""
        if self.verbose:
            print(f"[DEBUG] Checking existence of shot {shotID} at {self.basePath}")
        try:
            return os.path.exists(os.path.join(self.basePath, str(shotID)))
        except OSError as e:
            raise OSError(f"Failed to check existence of shot {shotID} at {self.basePath}: {e}") from e

    # Helper functions

    def listDirectory(self, shotID, directory):
        """Lists files and directories in a local shot directory."""
        if shotID == 0:
            shotID = self.getLatestShotID()
        path = os.path.join(self.basePath, str(shotID), directory)
        try:
            return [
                { "name": entry.name, "type": "directory" if entry.is_dir() else "file", }
                for entry in os.scandir(path)
            ]
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Shot directory {shotID} not found.") from e
        except OSError as e:
            raise OSError(f"Failed to list shot directory {shotID}: {e}") from e

    def getLatestShotID(self) -> int:
        ids = [int(dir) for dir in os.listdir(self.basePath)
            if dir.isdigit() and os.path.isdir(os.path.join(self.basePath, dir))]
        if not ids:
            raise FileNotFoundError(f"No labeled shots found at {self.basePath}.")
        return max(ids)
    def getShotFile(self, shotID, fileName):
        """Reads a specific file from the filesystem."""
        if self.verbose:
            print(f"[DEBUG] Reading file '{fileName}' for shot {shotID} from {self.basePath}")
        try:
            with open(os.path.join(self.basePath, str(shotID), fileName), 'rb') as f:
                return f.read()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File '{fileName}' not found for shot {shotID}.") from e
        except OSError as e:
            raise OSError(f"Failed to read file '{fileName}' for shot {shotID}: {e}") from e

    def getShotFileCached(self, shotID, fileName):
        """Reads a specific file from the filesystem and caches it locally."""
        return self._getShotFileCached(shotID, fileName)
        
    def clearCache(self):
        """Clears the local cache of read shot files."""
        self._clearCache()