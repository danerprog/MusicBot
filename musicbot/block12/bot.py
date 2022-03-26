import logging

from .config import Block12ConfigDecorator

from musicbot.aliases import AliasesDefault
from musicbot.billboard.Manager import Manager as BillboardManager
from musicbot.bot import MusicBot
from musicbot.constructs import Response
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

    @overrides(MusicBot)
    async def on_ready(self):
        await super().on_ready()
        
        if self.config.is_billboard_feature_enabled:
            for guild in self.guilds:
                guild_id = guild.id
                log.info("Registering Overall billboard for guild_id: {}".format(
                    str(guild_id)
                ))
                BillboardManager.registerCumulative(guild_id)
            BillboardManager.activate()
            
    async def cmd_billboard(self, channel, guild, leftover_args):
        log.info("cmd_billboard called. leftover_args: {}".format(str(leftover_args)))
        
        if not self.config.is_billboard_feature_enabled:
            response = "Billboard feature is disabled."
        elif not self.config.embeds:
            response = "Embeds are disabled. Unable to display top songs."  
        elif len(leftover_args) > 1 and leftover_args[0] == "dump":
            response = "Dumping track info to logs."
            billboard = BillboardManager.get(guild.id, leftover_args[1])
            if billboard is None:
                response = "No billboard found with name: {}".format(leftover_args[1])
            else:
                billboard.dumpTrackInfoToLogs()
        elif len(leftover_args) > 0 :
            response = None
            billboard = BillboardManager.get(guild.id, leftover_args[0])
            if billboard is None:
                response = "No billboard found with name: {}".format(leftover_args[0])
            else:
                embeds = billboard.generateDiscordEmbedsForTopSongs()
                for embed in embeds:
                    await self.safe_send_message(channel, embed)
        else:
            response = "Invalid arguments provided. args: {}".format(str(leftover_args))
                
        return None if response is None else Response(response)

    @overrides(MusicBot)
    def _postSuccessfulQueue(self, args):
        info = args["info"]
        BillboardManager.queue(args["guild_id"], "Cumulative", {
            "video_id" : info["id"],
            "title" : info["title"]
        })

    def _initializeCommandModifier(self, aliases_file, gacha_file):
        aliases_file = aliases_file if aliases_file is not None else AliasesDefault.aliases_file
        gacha_file = gacha_file if gacha_file is not None else GachaDefault.gacha_file
        self.command_modifier = CommandModifier(
            aliases_file if self.config.usealias else None,
            gacha_file if self.config.usegacha else None)
        self.should_command_modifier_be_used = self.config.usealias or self.config.usegacha


