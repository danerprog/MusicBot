import logging

from .config import Block12ConfigDecorator
from musicbot.aliases import AliasesDefault
from musicbot.bot import MusicBot
from musicbot.CommandModifier import CommandModifier
from musicbot.gacha import GachaDefault


log = logging.getLogger(__name__)

def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider
    
class Block12MusicBot(MusicBot):
    
    def __init__(self, config_file=None, perms_file=None, aliases_file=None, gacha_file=None):
        log.info("Running Block12 version of MusicBot")
        super().__init__(config_file, perms_file, aliases_file)
        Block12ConfigDecorator(self.config)
        self._initializeCommandModifier(aliases_file, gacha_file)
        
    def _initializeCommandModifier(self, aliases_file, gacha_file):
        aliases_file = aliases_file if aliases_file is not None else AliasesDefault.aliases_file
        gacha_file = gacha_file if gacha_file is not None else GachaDefault.gacha_file
        self.command_modifier = CommandModifier(
            aliases_file if self.config.usealias else None,
            gacha_file if self.config.usegacha else None)
        self.should_command_modifier_be_used = self.config.usealias or self.config.usegacha
