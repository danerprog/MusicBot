import json
import os
from pathlib import Path
import logging

from .exceptions import HelpfulError


log = logging.getLogger(__name__)


class Billboard:

    class Track:
        def __init__(self, video_information_dictionary, working_directory):
            log.debug("Creating Track. video_information_dictionary: {}, working_directory: {}".format(str(video_information_dictionary), str(working_directory)))
            self._base_working_directory = working_directory
            self._video_id = video_information_dictionary["video_id"]
            self._working_directory = self._base_working_directory + self._video_id + "\\"
            self._info_json_path = self._working_directory + "\\info.json"

            Path(self._working_directory).mkdir(exist_ok=True)
            self._initializeInfoJson(video_information_dictionary)
            
        def _createInfoJson(self, content):
            log.debug("_createInfoJson called")
            with open(self._info_json_path, "w") as json_file:
                json_file.write(json.dumps(content, indent = 4))
                
        def _initializeTitle(self, loaded_info_json, default_title):
            key = "title"
            title = "null" if key not in loaded_info_json else loaded_info_json[key]
            self._info_json[key] = title if title != "null" else default_title
                
        def _initializeTimesQueued(self, loaded_info_json):
            key = "times_queued"
            self._info_json[key] = 0 if key not in loaded_info_json else loaded_info_json[key]
            
        def _initializeInfoJson(self, video_information_dictionary):
            log.debug("_initializeInfoJson called. video_information_dictionary: {}".format(str(video_information_dictionary)))
            self._info_json = {
                "title" : "null",   
                "times_queued" : 0
            }
            
            if not Path(self._info_json_path).exists():
                self._createInfoJson(self._info_json)

            with open(self._info_json_path, "r") as json_file:
                loaded_info_json = json.loads(json_file.read())
                log.debug("Opened json.file. loaded_info_json: {}".format(str(loaded_info_json)))
                self._initializeTitle(loaded_info_json, video_information_dictionary["title"])
                self._initializeTimesQueued(loaded_info_json)
            
        def incrementTimesQueued(self):
            self._info_json["times_queued"] += 1
            self._createInfoJson(self._info_json)
            log.debug("incrementTimesQueued called. self._info_json: {}".format(str(self._info_json)))
            
        def getNumberOfTimesQueued(self):
            return self._info_json["times_queued"]
            
        def getTitle(self):
            return self._info_json["title"]
            
        def getVideoId(self):
            return self._video_id
            
        def isQueuedMoreThan(self, other_track):
            return self.getNumberOfTimesQueued() > other_track.getNumberOfTimesQueued()
            
        def __str__(self):
            return str("video_id: {}, info_json: {}".format(
                str(self._video_id), 
                str(self._info_json)))
                    
                    
    class TrackManager:
        def __init__(self):
            log.debug("TrackManager created.")
            self._track_dictionary = {}
            self._ordered_track_array = []
            
        def _putInOrderedTrackArray(self, track_to_place):
            log.debug("_putInOrderedTrackArray called. track_to_place: {}".format(str(track_to_place)))
            number_of_tracks_in_ordered_track_array = len(self._ordered_track_array)
            index_where_track_should_be_placed = 0
            
            for index in range(0, number_of_tracks_in_ordered_track_array):
                track_to_check = self._ordered_track_array[index]
                log.debug("index: {}, track_to_check: {}".format(str(index), str(track_to_check)))
                index_where_track_should_be_placed = index
                
                if track_to_place.isQueuedMoreThan(track_to_check):
                    log.debug("Found index. Breaking loop. index_where_track_should_be_placed: {}".format(str(index_where_track_should_be_placed)))
                    break

            self._ordered_track_array.insert(index_where_track_should_be_placed, track_to_place)    
            log.debug("Track placed. self._ordered_track_array: {}".format(str(self._ordered_track_array)))
            
        def get(self, video_id):
            return None if video_id not in self._track_dictionary else self.track_dictionary[video_id]
            
        def manage(self, track):
            log.debug("manage called. track: {}".format(str(track)))
            video_id = track.getVideoId()
            
            if video_id not in self._track_dictionary:
                log.debug("Placing track.")
                self._track_dictionary[video_id] = track
            
        def queue(self, track):
            log.debug("queue called. track: {}".format(str(track)))
            self.manage(track)

            log.debug("Incrementing number of times track is queued.")
            self._track_dictionary[track.getVideoId()].incrementTimesQueued()
                
        def getTopQueuedSongs(self, number_of_songs):
            self._ordered_track_array = []
            for video_id, track in self._track_dictionary.items():
                self._putInOrderedTrackArray(track)
        
            top_songs_array = self._ordered_track_array[:number_of_songs]
        
            log.debug("getTopQueuedSongs called. number_of_songs: {}, top_songs_array: {}".format(
                str(number_of_songs),
                str(top_songs_array)
            ))
            return top_songs_array
                
        def dumpTrackInfoToLogs(self):
            log.debug("track_dictionary: {}\nordered_track_array: {}".format(str(self._track_dictionary), str(self._ordered_track_array)))


    class Chart:
        def __init__(self, column_widths):
            log.debug("Creating Chart. column_widths: {}".format(str(column_widths)))
            self._column_widths = column_widths
            self._chart_segments = []

            self._initializeSegmentFormats()
            self._addHeadersToChart()
            
        def _initializeSegmentFormats(self):
            self._header_segment_format = "{:-^" + str(self._column_widths["title"]) + "}|{:-^" + str(self._column_widths["times_queued"]) + "}"
            self._row_segment_format = "{:<" + str(self._column_widths["title"]) + "}|{:^" + str(self._column_widths["times_queued"]) + "}"
            log.debug("_initializeSegmentFormats called. header_segment_format: {}, row_segment_format: {}".format(
                self._header_segment_format,
                self._row_segment_format
            ))
            
        def _getTitleHeader(self):
            title_header_long = "Video Title"
            title_header_short = "Title"
            title_header_letter = "t"
            column_width = self._column_widths["title"]
            
            header_to_return = title_header_long if len(title_header_long) < column_width else title_header_short if len(title_header_short) else title_header_letter
            log.debug("_getTitleHeader called. header_to_return: {}".format(header_to_return))
            
            return header_to_return
  
        def _getTimesQueuedHeader(self):
            times_queued_header_long = "Times Queued"
            times_queued_header_short = "Queue"
            times_queued_header_letter = "q"
            column_width = self._column_widths["times_queued"]
            
            header_to_return = times_queued_header_long if len(times_queued_header_long) < column_width else times_queued_header_short if len(times_queued_header_short) else times_queued_header_letter
            log.debug("_getTimesQueuedHeader called. header_to_return: {}".format(header_to_return))
            
            return header_to_return
            
        def _addHeadersToChart(self):
            title_header = self._getTitleHeader()
            times_queued_header = self._getTimesQueuedHeader()
            
            segment = self._header_segment_format.format(title_header, times_queued_header)
            
            log.debug("_addHeadersToChart called. segment: {}".format(segment))
            self._chart_segments.append(segment)
        
        def _cutTitleIfNeeded(self, title):
            max_column_width = self._column_widths["title"]
            title_length = len(title)
            title_to_return = title if title_length < max_column_width else title[:max_column_width - 3] + "..."
            
            log.debug("_cutTitleIfNeeded called. title: {}, title_length: {}, title_to_return: {}".format(
                title,
                str(title_length),
                title_to_return
            ))
            
            return title_to_return

        def _addRowToChart(self, data):
            log.debug("_addRowToChart called.")
            segment = self._row_segment_format.format(self._cutTitleIfNeeded(data["title"]), data["times_queued"])
            self._chart_segments.append(segment)
            
        def addTrack(self, track):
            log.debug("addTrack called. track: {}".format(str(track)))
            self._addRowToChart({
                "title" : track.getTitle(),
                "times_queued" : str(track.getNumberOfTimesQueued())
            })
            
        def addTracks(self, track_array):
            log.debug("addTracks called.")
            for track in track_array:
                self.addTrack(track)
                
        def generateString(self):
            log.debug("generateString called.")
            string_to_return = ""
            
            for segment in self._chart_segments:
                string_to_return += segment + "\n"
                
            return string_to_return
            

    BILLBOARDS = {}

    def __init__(self, guild_id):
        log.debug("Creating Billboard. guild_id: {}".format(str(guild_id)))
        self._base_working_directory = guild_id
        self._track_manager = Billboard.TrackManager()
        
        self._throwHelpfulErrorIfWorkingDirectoryDoesNotExist()
        self._initializeWorkingDirectory()
        self._loadTracks()
        
    def _throwHelpfulErrorIfWorkingDirectoryDoesNotExist(self):
        if not Path(self._base_working_directory).exists():
            raise HelpfulError("Unable to proceed. Cannot find directory: {} ".format(str(self._base_working_directory)))
        
    def _initializeWorkingDirectory(self):
        self._working_directory = self._base_working_directory + "billboard\\"
        Path(self._working_directory).mkdir(exist_ok=True)
        
    def _loadTracks(self):
        log.debug("_loadTracks called.")
        for video_id in next(os.walk(self._working_directory))[1]:
            log.debug("video_id: {}".format(video_id))
            self._track_manager.manage(
                Billboard.Track({
                    "video_id": video_id,
                    "title" : "null"
                }, 
                self._working_directory))
  
    def queue(self, video_information_dictionary):
        self._track_manager.queue(Billboard.Track(video_information_dictionary, self._working_directory))
        
    def generateTopSongsChart(self, number_of_songs):
        top_songs_list = self._track_manager.getTopQueuedSongs(number_of_songs)
        column_widths = {
            "title" : 30,
            "times_queued" : 10
        }
        
        chart = Billboard.Chart(column_widths)
        chart.addTracks(top_songs_list)
        return chart.generateString()
        
    def dumpTrackInfoToLogs(self):
        self._track_manager.dumpTrackInfoToLogs()
        
    def getBillboard(guild_id):
        guild_id = str(guild_id)
        if guild_id not in Billboard.BILLBOARDS:
            Billboard.BILLBOARDS[guild_id] = Billboard("data\\" + guild_id + "\\")
        return Billboard.BILLBOARDS[guild_id]
        
        
        
        
        
        
        
        