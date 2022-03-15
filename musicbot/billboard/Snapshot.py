import os
from pathlib import Path
import logging
import shutil

from .Billboard import Billboard
from musicbot.lib.JsonFile import JsonFile


log = logging.getLogger(__name__)

def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

class Snapshot(Billboard):
    
    def __init__(self, billboard):
        self._original_billboard = billboard
        super().__init__({
            "guild_id" : billboard.getGuildId(),
            "name" : billboard.getName(),
            "number_of_songs_to_display" : billboard.getNumberOfSongsToDisplay(),
            "number_of_days_before_recalculation_should_be_performed" : billboard.getNumberOfDaysBeforeRecalculationShouldBePerformed()
        })
       
    @overrides(Billboard)
    def _initializeWorkingDirectories(self):
        self._working_directory = self._base_working_directory + "billboard\\" + self._billboard_name + "\\snapshots\\latest\\"
        self._song_working_directory = self._working_directory + "songs\\"

        log.debug("_initializeWorkingDirectories called. working_directory: {}, song_working_dictionary: {}".format(
            self._working_directory,
            self._song_working_directory
        ))
        
        os.makedirs(self._working_directory, exist_ok=True)
        Path(self._song_working_directory).mkdir(exist_ok=True)
    
    @overrides(Billboard)
    def _loadBillboardFile(self):
        billboard_json_file_path = self._working_directory + "info.json"
        log.debug("_loadBillboardFile called. billboard_json_file_path: {}".format(billboard_json_file_path))
        self._json_file = JsonFile(self._working_directory + "info.json", default_content = self._original_billboard._billboard_content)
        self._billboard_content = self._json_file.json()
        
    @overrides(Billboard)
    def queue(self, video_information_dictionary):
        log.warning("Attempted to queue on a billboard snapshot!")

    def archive(self):
        previous_working_directory = self._working_directory
        index_of_latest = previous_working_directory.rfind("latest")
        self._working_directory = previous_working_directory[:index_of_latest] + "\\" + self._billboard_content["date_last_calculated"]
        
        log.debug("archive called. previous_working_directory: {}, working_directory: {}".format(
            previous_working_directory,
            self._working_directory
        ))
        
        index = 1
        new_working_directory = self._working_directory
        while Path(new_working_directory + "\\").exists():
            new_working_directory = self._working_directory + "_" + str(index)
            index += 1
        self._working_directory = new_working_directory
        
        os.rename(previous_working_directory, self._working_directory)
        shutil.copytree(self._original_billboard._song_working_directory, self._song_working_directory)

        
        