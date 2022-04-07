import asyncio
from datetime import datetime
import discord
import logging
import os
from pathlib import Path

from musicbot.exceptions import HelpfulError
from musicbot.lib.JsonFile import JsonFile
from .Song import Song
from .OrderedSongList import OrderedSongList


log = logging.getLogger(__name__)

class Billboard:

    DATE_FORMAT = "%Y%m%d%H%M%S"
    FILENAME = "info.json"

    def __init__(self, args):
        self._guild_id = str(args["guild_id"])
        self._billboard_name = args["name"]
        self._number_of_songs_to_display = args["number_of_songs_to_display"]
        self._number_of_days_before_recalculation_should_be_performed = args["number_of_days_before_recalculation_should_be_performed"]
        
        log.debug("Creating Billboard. args: {}".format(
            str(args)
        ))

        self._base_working_directory = "data\\" + self._guild_id + "\\"
        self._billboard_content = {
            "date_last_calculated" : datetime(1970, 1, 1).strftime(Billboard.DATE_FORMAT),
            "song_ids_ordered_by_most_to_least_queued" : []
        }
        self._top_songs_cache = []
        
        self._throwHelpfulErrorIfWorkingDirectoryDoesNotExist()
        self._initializeWorkingDirectories()
        self._loadBillboardFile()
        
    def __json__(self):
        return self._billboard_content

    def _throwHelpfulErrorIfWorkingDirectoryDoesNotExist(self):
        if not Path(self._base_working_directory).exists():
            raise HelpfulError("Unable to proceed. Cannot find directory: {} ".format(str(self._base_working_directory)))
        
    def _initializeWorkingDirectories(self):
        self._working_directory = self._base_working_directory + "billboard\\" + self._billboard_name + "\\"
        self._song_working_directory = self._working_directory + "songs\\"

        log.debug("_initializeWorkingDirectories called. working_directory: {}, song_working_dictionary: {}".format(
            self._working_directory,
            self._song_working_directory
        ))
        
        os.makedirs(self._working_directory, exist_ok=True)
        Path(self._song_working_directory).mkdir(exist_ok=True)
        
    def _loadBillboardFile(self):
        billboard_json_file_path = self._working_directory + Billboard.FILENAME
        log.debug("_loadBillboardFile called. billboard_json_file_path: {}".format(billboard_json_file_path))
        self._json_file = JsonFile(self._working_directory + "info.json", default_content = self._billboard_content)
        json_content = self._json_file.json()

        for key, value in self._billboard_content.items():
            self._billboard_content[key] = value if key not in json_content else json_content[key]


    def _calculateBillboardTopSongs(self):
        log.debug("_calculateBillboardTopSongs called.")
        self._clearTopSongsCache()
        ordered_song_list = OrderedSongList()

        for video_id in next(os.walk(self._song_working_directory))[1]:
            log.debug("video_id: {}".format(video_id))
            ordered_song_list.add(
                Song({
                    "video_id": video_id,
                    "title" : "null"
                }, 
                self._song_working_directory))

        self._billboard_content["song_ids_ordered_by_most_to_least_queued"] = []
        top_queued_songs = ordered_song_list[:self._number_of_songs_to_display]
        for song in top_queued_songs:
            self._top_songs_cache.append(song)
            
            song.incrementNumberOfWeeksInChart()
            song.updatePositionOnChart(len(self._top_songs_cache))
            song.save()
            log.debug("song: {}".format(str(song)))
            
            self._billboard_content["song_ids_ordered_by_most_to_least_queued"].append(song.getVideoId()) 
            
    def _loadTopSongsToCacheIfNeeded(self):
        log.debug("_loadTopSongsToCacheIfNeeded called.")
    
        if len(self._top_songs_cache) == 0:
            for video_id in self._billboard_content["song_ids_ordered_by_most_to_least_queued"][:self._number_of_songs_to_display]:
                self._top_songs_cache.append(
                    Song({
                        "video_id": video_id,
                        "title" : "null"
                    }, 
                    self._song_working_directory))

            log.debug("Cache loaded. top_songs_cache: {}".format(self._top_songs_cache))
            
    def _clearTopSongsCache(self):
        self._top_songs_cache = []

    def queue(self, video_information_dictionary):
        log.debug("queue called. video_information_dictionary: {}".format(video_information_dictionary))
        song = Song(video_information_dictionary, self._song_working_directory)
        song.incrementTimesQueued()
        song.save()
        self._clearTopSongsCache()
        
    def generateDiscordEmbedsForTopSongs(self, number_of_songs = None):
        self._loadTopSongsToCacheIfNeeded()
    
        number_of_songs = self._number_of_songs_to_display if number_of_songs is None else number_of_songs
        log.info("generateDiscordEmbedsForTopSongs called. number_of_songs: {}".format(str(number_of_songs)))
        
        embed_author_name = self.getName() + " #"
        embeds = []
        place = 1

        for song in self._top_songs_cache[:number_of_songs]:
            embed = song.generateDiscordEmbed()
            embed.set_author(name = embed_author_name + str(place))

            if place == 1:
                embed.set_thumbnail(url = "")
                embed.colour = discord.Colour.gold()
            else:
                embed.set_image(url = "")
                position_last_week = song.getPositionLastWeek()
                position_this_week = song.getPositionThisWeek()
                embed.colour = discord.Colour.green() if position_this_week < position_last_week else discord.Colour.red() if position_this_week > position_last_week else discord.Colour.darker_gray()

            place += 1  
            embeds.append(embed)
            
        return embeds
        
    def dumpSongInfoToLogs(self):
        log.debug("top_songs_cache: {}".format(str(self._top_songs_cache)))

    def calculateBillboardTopSongsIfNeeded(self):
        wasCalculationPerfomed = False
        date_last_calculated = datetime.strptime(self._billboard_content["date_last_calculated"], Billboard.DATE_FORMAT)
        date_now = datetime.now()
        date_delta = date_now - date_last_calculated
        delta_in_days = date_delta.days
        
        log.debug("calculateBillboardTopSongsIfNeeded called. date_last_calculated: {}, date_now: {}, date_delta: {}".format(
            str(date_last_calculated),
            str(date_now),
            str(date_delta)
        ))
        
        if delta_in_days >= self._number_of_days_before_recalculation_should_be_performed:
            self._calculateBillboardTopSongs()
            self._billboard_content["date_last_calculated"] = date_now.strftime(Billboard.DATE_FORMAT)
            self._json_file.save(self._billboard_content)
            wasCalculationPerfomed = True
        return wasCalculationPerfomed    
        
    def getGuildId(self):
        return self._guild_id
        
    def getName(self):
        return self._billboard_name
        
    def getNumberOfSongsToDisplay(self):
        return self._number_of_songs_to_display
        
    def getNumberOfDaysBeforeRecalculationShouldBePerformed(self):
        return self._number_of_days_before_recalculation_should_be_performed

