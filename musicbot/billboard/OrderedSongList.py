import logging


log = logging.getLogger(__name__)

class OrderedSongList:
    def __init__(self):
        log.debug("OrderedSongList created.")
        self._ordered_song_list = []
        
    def _putInOrderedSongList(self, song_to_place):
        log.debug("_putInOrderedSongList called. song_to_place: {}".format(str(song_to_place)))
        number_of_songs_in_ordered_song_list = len(self._ordered_song_list)

        for index in range(0, number_of_songs_in_ordered_song_list + 1):
            try:
                song_to_check = self._ordered_song_list[index]
                log.debug("index: {}, song_to_check: {}".format(str(index), str(song_to_check)))
                
                if song_to_place.isQueuedMoreThan(song_to_check):
                    self._ordered_song_list.insert(index, song_to_place)
                    break
            except IndexError:
                self._ordered_song_list.append(song_to_place)
                
        log.debug("Song placed. self._ordered_song_list: {}".format(
            str(self._ordered_song_list)
        ))

    def __getitem__(self, key):
        return self._ordered_song_list[key]
        
    def add(self, song):
        self._putInOrderedSongList(song);

    def getTopQueuedSongs(self, number_of_songs):
        top_songs_list = self._ordered_song_list[:number_of_songs]
        log.debug("getTopQueuedSongs called. number_of_songs: {}, top_songs_list: {}, ordered_song_list: {}".format(
            str(number_of_songs),
            str(top_songs_list),
            str(self._ordered_song_list)
        ))
        return top_songs_list
            
    def dumpSongInfoToLogs(self):
        log.debug("ordered_song_array: {}".format(str(self._ordered_song_list)))
