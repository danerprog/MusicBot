import json
import logging
from pathlib import Path


log = logging.getLogger(__name__)

class JsonFile:

    def __init__(self, json_file_path, default_content = None):
        log.debug("Creating JsonFile. json_file_path: {}, default_content: {}".format(
            json_file_path,
            str(default_content)
        ))
        self._json_file_path = json_file_path
        self._json = {}
        self._createJsonFileIfNeeded(default_content)
        self.load()

    def _createJsonFileIfNeeded(self, default_content):
        log.debug("_createJsonFileIfNeeded called.")       
        if not Path(self._json_file_path).exists() and default_content is not None:
            self.save(default_content)

    def _createJsonFile(self, content):
        log.debug("_createJsonFile called. content: {}".format(str(content)))
        with open(self._json_file_path, "w") as json_file:
            json_file.write(json.dumps(content, indent = 4))

    def json(self):
        return self._json
        
    def get(self):
        return self.json()
        
    def __getitem__(self, key):
        return self._json[key]

    def save(self, content):
        log.debug("save called. content: {}".format(
            str(content)
        ))
        self._createJsonFile(content)
        self._json = content

    def load(self):
        if Path(self._json_file_path).exists():
            with open(self._json_file_path, "r") as json_file:
                self._json = json.loads(json_file.read())
                log.debug("Opened json file. json: {}".format(
                    str(self._json)
                ))
