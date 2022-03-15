import logging


log = logging.getLogger(__name__)

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
        
    def addSong(self, song):
        log.debug("addSong called. song: {}".format(str(song)))
        self._addRowToChart({
            "title" : song.getTitle(),
            "times_queued" : str(song.getNumberOfTimesQueued())
        })
        
    def addSongs(self, song_array):
        log.debug("addSongs called.")
        for song in song_array:
            self.addSong(song)
            
    def generateString(self):
        log.debug("generateString called.")
        string_to_return = ""
        
        for segment in self._chart_segments:
            string_to_return += segment + "\n"
            
        return string_to_return
        
