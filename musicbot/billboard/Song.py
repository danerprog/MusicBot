import copy
import discord
import json
import logging
import os
from pathlib import Path

from musicbot.lib.JsonFile import JsonFile


log = logging.getLogger(__name__)

class Song:
    DEFAULT_JSON_CONTENT = {
        "title" : "null",   
        "times_queued" : 0,
        "number_of_weeks_on_chart" : -1,
        "position_this_week" : -1,
        "position_last_week" : -1,
        "peak_position" : -1 
    }

    def __init__(self, video_information_dictionary, working_directory):
        log.debug("Creating Song. video_information_dictionary: {}, working_directory: {}".format(str(video_information_dictionary), str(working_directory)))
        self._base_working_directory = working_directory
        self._video_id = video_information_dictionary["video_id"]
        self._working_directory = self._base_working_directory + self._video_id + "\\"
        self._info_json_path = self._working_directory + "info.json"

        Path(self._working_directory).mkdir(exist_ok=True)
        self._initializeInfoJson(video_information_dictionary)
      
    def _initializeTitle(self, loaded_info_json, default_title):
        key = "title"
        title = "null" if key not in loaded_info_json else loaded_info_json[key]
        self._info_json[key] = title if title != "null" else default_title
        
    def _initializeKeyWithDefaultValue(self, key, loaded_info_json):
        self._info_json[key] = self._info_json[key] if key not in loaded_info_json else loaded_info_json[key]
         
    def _initializeInfoJson(self, video_information_dictionary):
        log.debug("_initializeInfoJson called. video_information_dictionary: {}".format(str(video_information_dictionary)))
        self._info_json = copy.deepcopy(Song.DEFAULT_JSON_CONTENT)
        self._json_file = JsonFile(self._info_json_path, default_content = self._info_json)
        
        loaded_info_json = self._json_file.json()
        self._initializeTitle(loaded_info_json, video_information_dictionary["title"])
        self._initializeKeyWithDefaultValue("times_queued", loaded_info_json)
        self._initializeKeyWithDefaultValue("number_of_weeks_on_chart", loaded_info_json)
        self._initializeKeyWithDefaultValue("position_this_week", loaded_info_json)
        self._initializeKeyWithDefaultValue("position_last_week", loaded_info_json)
        self._initializeKeyWithDefaultValue("peak_position", loaded_info_json)
        
    def incrementTimesQueued(self):
        self._info_json["times_queued"] += 1
        log.debug("incrementTimesQueued called. self._info_json: {}".format(str(self._info_json)))
        
    def incrementNumberOfWeeksInChart(self):
        self._info_json["number_of_weeks_on_chart"] += 1
        
    def updatePositionOnChart(self, new_position):
        self._info_json["position_last_week"] = self._info_json["position_this_week"]
        self._info_json["position_this_week"] = new_position
        self._info_json["peak_position"] = self._info_json["peak_position"] if self._info_json["peak_position"] >= new_position else new_position

    def save(self):
        self._json_file.save(self._info_json)
        
    def getNumberOfTimesQueued(self):
        return self._info_json["times_queued"]
        
    def getTitle(self):
        return self._info_json["title"]
        
    def getVideoId(self):
        return self._video_id
        
    def getPositionThisWeek(self):
        return self._info_json["position_this_week"]
        
    def getPositionLastWeek(self):
        return self._info_json["position_last_week"]
        
    def isQueuedMoreThan(self, other_song):
        return self.getNumberOfTimesQueued() > other_song.getNumberOfTimesQueued()

    def generateDiscordEmbed(self):
        embed = discord.Embed()
        embed.title = self._info_json["title"]
        embed.url = "https://www.youtube.com/watch?v=" + self._video_id
        embed.add_field(name = "Times Queued", value = self._info_json["times_queued"], inline = False)

        number_of_weeks_on_chart = self._info_json["number_of_weeks_on_chart"]
        weeks_on_chart_value = "New!" if number_of_weeks_on_chart <= 0 else number_of_weeks_on_chart
        embed.add_field(name = "Weeks on Chart", value = weeks_on_chart_value, inline = True)

        position_last_week_value = "-" if self._info_json["position_last_week"] <= 0 else self._info_json["position_last_week"]
        embed.add_field(name = "Position Last Week", value = position_last_week_value, inline = True)

        thumbnail_url = "https://i.ytimg.com/vi/" + self._video_id + "/hq720.jpg"
        embed.set_thumbnail(url = thumbnail_url)
        embed.set_image(url = thumbnail_url)
        return embed

    def __str__(self):
        return str("video_id: {}, info_json: {}".format(
            str(self._video_id), 
            str(self._info_json)))
