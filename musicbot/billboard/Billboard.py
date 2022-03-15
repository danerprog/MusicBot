import asyncio
from datetime import datetime, date
import discord
import logging
import os
from pathlib import Path


from .Chart import Chart
from musicbot.exceptions import HelpfulError
from musicbot.lib.JsonFile import JsonFile
from .Song import Song
from .SongManager import SongManager


log = logging.getLogger(__name__)

class Billboard:

    def __init__(self, args):
        self._guild_id = str(args["guild_id"])
        self._billboard_name = args["name"]
        self._number_of_songs_to_display = args["number_of_songs_to_display"]
        self._number_of_days_before_recalculation_should_be_performed = args["number_of_days_before_recalculation_should_be_performed"]
        
        log.debug("Creating Billboard. args: {}".format(
            str(args)
        ))

        self._base_working_directory = "data\\" + self._guild_id + "\\"
        self._song_manager = SongManager()
        self._billboard_content = {}
        self._top_songs_cache = []
        
        self._throwHelpfulErrorIfWorkingDirectoryDoesNotExist()
        self._initializeWorkingDirectories()
        self._loadBillboardFile()

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
        
        Path(self._working_directory).mkdir(exist_ok=True)
        Path(self._song_working_directory).mkdir(exist_ok=True)
        
    def _loadBillboardFile(self):
        billboard_json_file_path = self._working_directory + "info.json"
        self._billboard_content = {
            "date_last_calculated" : "1970-01-01",
            "song_ids_ordered_by_most_to_least_queued" : []
        }
        log.debug("_loadBillboardFile called. billboard_json_file_path: {}".format(billboard_json_file_path))
        self._json_file = JsonFile(self._working_directory + "info.json", default_content = self._billboard_content)
        json_content = self._json_file.json()

        for key, value in self._billboard_content.items():
            self._billboard_content[key] = value if key not in json_content else json_content[key]


    def _calculateBillboardTopSongs(self):
        log.debug("_calculateBillboardTopSongs called.")
        self._top_songs_cache = []
        song_manager = SongManager()

        for video_id in next(os.walk(self._song_working_directory))[1]:
            log.debug("video_id: {}".format(video_id))
            song_manager.manage(
                Song({
                    "video_id": video_id,
                    "title" : "null"
                }, 
                self._song_working_directory))

        self._billboard_content["song_ids_ordered_by_most_to_least_queued"] = []
        top_queued_songs = song_manager.getTopQueuedSongs(self._number_of_songs_to_display)
        for song in top_queued_songs:
            log.debug("song: {}".format(str(song)))

            song.incrementNumberOfWeeksInChart()
            song.updatePositionOnChart(len(self._top_songs_cache))
            song.save()
            
            self._billboard_content["song_ids_ordered_by_most_to_least_queued"].append(song.getVideoId()) 
            
    def _loadTopSongsToCacheIfNeeded(self):
        log.debug("_loadTopSongsToCacheIfNeeded called.")
    
        if len(self._top_songs_cache) == 0:
            song_manager = SongManager()
            
            for video_id in self._billboard_content["song_ids_ordered_by_most_to_least_queued"]:
                song_manager.manage(
                    Song({
                        "video_id": video_id,
                        "title" : "null"
                    }, 
                    self._song_working_directory))
                    
            self._top_songs_cache = song_manager.getTopQueuedSongs(self._number_of_songs_to_display)
            
            log.debug("Cache loaded. top_songs_cache: {}".format(self._top_songs_cache))

    def queue(self, video_information_dictionary):
        song = Song(video_information_dictionary, self._song_working_directory)
        song.incrementTimesQueued()
        song.save()
        
    def generateTopSongsChart(self, number_of_songs = None):
        number_of_songs = self._number_of_songs_to_display if number_of_songs is None else number_of_songs
        column_widths = {
            "title" : 30,
            "times_queued" : 10
        }
        
        chart = Chart(column_widths)
        chart.addSongs(self._top_songs_cache[:number_of_songs])
        return chart.generateString()
        
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
                embed.colour = discord.Colour.green() if position_this_week > position_last_week else discord.Colour.red() if position_this_week < position_last_week else discord.Colour.darker_gray()

            place += 1  
            embeds.append(embed)
            
        return embeds
        
    def dumpSongInfoToLogs(self):
        log.debug("top_songs_cache: {}".format(str(self._top_songs_cache)))
        
    def calculateBillboardTopSongsIfNeeded(self):
        date_last_calculated = date.fromisoformat(self._billboard_content["date_last_calculated"])
        date_now = datetime.now().date()
        delta_in_days = (date_now - date_last_calculated).days
        
        log.debug("calculateBillboardTopSongsIfNeeded called. date_last_calculated: {}, date_now: {}, delta_in_days: {}".format(
            str(date_last_calculated),
            str(date_now),
            str(delta_in_days)
        ))
        
        if delta_in_days >= self._number_of_days_before_recalculation_should_be_performed:
            self._calculateBillboardTopSongs()
            self._billboard_content["date_last_calculated"] =  str(date_now)
            self._json_file.save(self._billboard_content)
        
    def getGuildId(self):
        return self._guild_id
        
    def getName(self):
        return self._billboard_name
        
    def getNumberOfSongsToDisplay(self):
        return self._number_of_songs_to_display
        
    def getNumberOfDaysBeforeRecalculationShouldBePerformed(self):
        return self._number_of_days_before_recalculation_should_be_performed

        