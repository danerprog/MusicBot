import json
from pathlib import Path
import logging

from .exceptions import HelpfulError


log = logging.getLogger(__name__)


class Billboard:

    class Track:
        def __init__(self, youtube_video_link, working_directory):
            log.debug("Creating Track. youtube_video_link: {}, working_directory: {}".format(str(youtube_video_link), str(working_directory)))
            self._base_working_directory = working_directory
            self._video_id = youtube_video_link.split("watch?v=")[-1]
            self._working_directory = self._base_working_directory + self._video_id + "\\"
            self._info_json_path = self._working_directory + "\\info.json"
            
            Path(self._working_directory).mkdir(exist_ok=True)
            self._initializeInfoJson()
            
        def _createInfoJson(self, content):
            log.debug("_createInfoJson called")
            with open(self._info_json_path, "w") as json_file:
                json_file.write(json.dumps(content, indent = 4))
            
        def _initializeInfoJson(self):
            log.debug("_initializeInfoJson called")
            self._info_json = {
                "times_queued" : 0
            }
            
            if not Path(self._info_json_path).exists():
                self._createInfoJson(self._info_json)
            else:
                with open(self._info_json_path, "r") as json_file:
                    loaded_info_json = json.loads(json_file.read())
                    log.debug("Opened json.file. loaded_info_json: {}".format(str(loaded_info_json)))
                    for key, default_value in self._info_json.items():
                        log.debug("key: {}, default_value: {}".format(str(key), str(default_value)))
                        self._info_json[key] = default_value if key not in loaded_info_json else loaded_info_json[key]
            
        def incrementTimesQueued(self):
            self._info_json["times_queued"] += 1
            self._createInfoJson(self._info_json)
            log.debug("incrementTimesQueued called. self._info_json: {}".format(str(self._info_json)))
            
        def getNumberOfTimesQueued(self):
            return self._info_json["times_queued"]
            
        def getVideoId(self):
            return self._video_id
            
        def isQueuedMoreThan(self, other_track):
            return self.getNumberOfTimesQueued() > other_track.getNumberOfTimesQueued()
            
        def __str__(self):
            return str("video_id: {}, info_json: {}".format(str(self._video_id), str(self._info_json)))
                    
    class TrackManager:
        
        def __init__(self):
            log.debug("TrackManager created.")
            self._track_dictionary = {}
            self._ordered_track_array = []
            
        def _putInOrderedTrackArray(self, track_to_place):
            log.debug("_putInOrderedTrackArray called. track_to_place: {}".format(str(track_to_place)))
            for index in range(0, len(self._ordered_track_array)):
                track_to_check = self._ordered_track_array[index]
                log.debug("index: {}, track_to_check: {}".format(str(index), str(track_to_check)))
                
                if track_to_place.isQueuedMoreThan(track_to_check):
                    self._ordered_track_array.insert(track_to_place, index)
                    log.debug("Track placed. self._ordered_track_array: {}".format(str(self._ordered_track_array)))
                    break     
            
        def get(self, video_id):
            return None if video_id not in self._track_dictionary else self.track_dictionary[video_id]
            
        def queue(self, track):
            log.debug("queue called. track: {}".format(str(track)))
            video_id = track.getVideoId()
            
            if video_id not in self._track_dictionary:
                log.debug("Placing track.")
                self._track_dictionary[video_id] = track
                self._putInOrderedTrackArray(self._track_dictionary[video_id])

            log.debug("Incrementing number of times track is queued.")
            self._track_dictionary[video_id].incrementTimesQueued()
                
        def getTopQueuedSongs(self, number_of_songs):
            return self._ordered_track_array[:number_of_songs]
                
        def dumpTrackInfoToLogs(self):
            log.debug("track_dictionary: {}\nordered_track_array: {}".format(str(self._track_dictionary), str(self._ordered_track_array)))

    BILLBOARDS = {}

    def __init__(self, guild_id):
        log.debug("Creating Billboard. guild_id: {}".format(str(guild_id)))
        self._base_working_directory = guild_id
        self._track_manager = Billboard.TrackManager()
        
        self._throwHelpfulErrorIfWorkingDirectoryDoesNotExist()
        self._initializeWorkingDirectory()
        
    def _throwHelpfulErrorIfWorkingDirectoryDoesNotExist(self):
        if not Path(self._base_working_directory).exists():
            raise HelpfulError("Unable to proceed. Cannot find directory: {} ".format(str(self._base_working_directory)))
        
    def _initializeWorkingDirectory(self):
        self._working_directory = self._base_working_directory + "billboard\\"
        Path(self._working_directory).mkdir(exist_ok=True)
  
    def queue(self, youtube_video_link):
        self._track_manager.queue(Billboard.Track(youtube_video_link, self._working_directory))
        
    def dumpTrackInfoToLogs(self):
        self._track_manager.dumpTrackInfoToLogs()
        
    def getBillboard(guild_id):
        guild_id = str(guild_id)
        if guild_id not in Billboard.BILLBOARDS:
            Billboard.BILLBOARDS[guild_id] = Billboard("data\\" + guild_id + "\\")
        return Billboard.BILLBOARDS[guild_id]
        
        
        
        
        
        
        
        