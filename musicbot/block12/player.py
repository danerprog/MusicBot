from musicbot.player import MusicPlayer
import logging
import types


log = logging.getLogger(__name__)


class Block12MusicPlayerInjector:

    def __init__(self, music_player):
        log.debug("Using Block12 Music Player")
        
        log.debug("Injecting __json__ method.")
        music_player.__json__ = types.MethodType(Block12MusicPlayerInjector.__json__, music_player)

    def __json__(self):
        return self._enclose_json(
            {
                "current_entry": {
                    "entry": self.current_entry,
                    "progress": self.progress,
                },
                "entries": self.playlist,
            }
        )

