import logging

from .config import Block12ConfigDecorator
from musicbot.aliases import AliasesDefault
from musicbot.bot import MusicBot
from musicbot.CommandModifier import CommandModifier
from musicbot.constructs import Response
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
        
    async def cmd_gacha_internal(self, channel, leftover_args):
        log.info("cmd_gacha called. leftover_args: {}".format(
            str(leftover_args)
        ))
        response = None
        subcommand = None if len(leftover_args) < 1 else leftover_args[0]
        
        if subcommand == "rates":
            gacha_command = None if len(leftover_args) < 2 else leftover_args[1]
            log.debug("displaying rates. gacha_command: {}".format(str(gacha_command)))
            
            if self.config.embeds:
                embeds = self.command_modifier.generateDiscordEmbedForRates(gacha_command)
                if len(embeds) <= 0:
                    response = "No rates found{}.".format("" if gacha_command is None else " for " + gacha_command)
                else:
                    for embed in embeds:
                        await self.safe_send_message(channel, embed)
            else:
                response = "Embeds are disabled. Unable to display gacha rates."
        elif subcommand == None:
            response = "No arguments provided."
        else:
            log.debug("subcommand not recognized: {}".format(subcommand))
            response = "Invalid arguments provided. args: {}".format(str(leftover_args))
            
        return None if response is None else Response(response)
        
    def _initializeCommandModifier(self, aliases_file, gacha_file):
        aliases_file = aliases_file if aliases_file is not None else AliasesDefault.aliases_file
        gacha_file = gacha_file if gacha_file is not None else GachaDefault.gacha_file
        self.command_modifier = CommandModifier(
            aliases_file if self.config.usealias else None,
            gacha_file if self.config.usegacha else None)
        self.should_command_modifier_be_used = self.config.usealias or self.config.usegacha
        
    
