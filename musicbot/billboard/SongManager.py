import logging


log = logging.getLogger(__name__)

class SongManager:
    def __init__(self):
        log.debug("SongManager created.")
        self._song_dictionary = {}
        self._ordered_song_array = []
        
    def _putInOrderedSongArray(self, song_to_place):
        log.debug("_putInOrderedSongArray called. song_to_place: {}".format(str(song_to_place)))
        number_of_songs_in_ordered_song_array = len(self._ordered_song_array)
        index_where_song_should_be_placed = 0
        
        for index in range(0, number_of_songs_in_ordered_song_array):
            song_to_check = self._ordered_song_array[index]
            log.debug("index: {}, song_to_check: {}".format(str(index), str(song_to_check)))
            index_where_song_should_be_placed = index
            
            if song_to_place.isQueuedMoreThan(song_to_check):
                log.debug("Found index. Breaking loop. index_where_song_should_be_placed: {}".format(str(index_where_song_should_be_placed)))
                break

        self._ordered_song_array.insert(index_where_song_should_be_placed, song_to_place)    
        log.debug("Song placed. self._ordered_song_array: {}".format(str(self._ordered_song_array)))
        
    def get(self, video_id):
        return None if video_id not in self._song_dictionary else self.song_dictionary[video_id]
        
    def manage(self, song):
        log.debug("manage called. song: {}".format(str(song)))
        video_id = song.getVideoId()
        
        if video_id not in self._song_dictionary:
            log.debug("Placing song.")
            self._song_dictionary[video_id] = song
        
    def queue(self, song):
        log.debug("queue called. song: {}".format(str(song)))
        self.manage(song)

        log.debug("Incrementing number of times song is queued.")
        self._song_dictionary[song.getVideoId()].incrementTimesQueued()
        song.save()
            
    def getTopQueuedSongs(self, number_of_songs):
        self._ordered_song_array = []
        for video_id, song in self._song_dictionary.items():
            self._putInOrderedSongArray(song)
    
        top_songs_array = self._ordered_song_array[:number_of_songs]
    
        log.debug("getTopQueuedSongs called. number_of_songs: {}, top_songs_array: {}".format(
            str(number_of_songs),
            str(top_songs_array)
        ))
        return top_songs_array
            
    def dumpSongInfoToLogs(self):
        log.debug("song_dictionary: {}\nordered_song_array: {}".format(str(self._song_dictionary), str(self._ordered_song_array)))
