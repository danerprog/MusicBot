import logging

from .config import Block12ConfigDecorator
from .permissions import Block12PermissionsDecorator
from .player import Block12MusicPlayerInjector

from musicbot.aliases import AliasesDefault
from musicbot.billboard.Manager import Manager as BillboardManager
from musicbot.bot import MusicBot
from musicbot.constructs import Response
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
        Block12PermissionsDecorator(self.permissions)
        self._initializeCommandModifier(aliases_file, gacha_file)

    async def on_connect(self):
        log.info("\nMusicBot connected.")

    async def on_disconnect(self):
        log.info("MusicBot disconnected.")
        
    @overrides(MusicBot)
    async def on_ready(self):
        await super().on_ready()
        
        if self.config.is_billboard_feature_enabled:
            for guild in self.guilds:
                guild_id = guild.id
                log.info("Registering default billboards for guild_id: {}".format(
                    str(guild_id)
                ))
                BillboardManager.registerDefaultBillboards(guild_id)
            BillboardManager.activate()
            
    async def cmd_billboard(self, author, channel, guild, leftover_args):
        log.info("cmd_billboard called. leftover_args: {}".format(str(leftover_args)))
        
        if not self.config.is_billboard_feature_enabled:
            response = "Billboard feature is disabled."
        elif not self.config.embeds:
            response = "Embeds are disabled. Unable to display top songs."  
        elif self._isBillboardCommandForDumpingSongInfoToLogs(leftover_args):
            response = self._dumpSongInfoToLogsIfAllowed(guild.id, author)
        elif self._canDefaultBillboardCommandBeExecuted(leftover_args) :
            response = None
            billboard_name = " ".join(leftover_args[:])
            billboard = BillboardManager.get(guild.id, billboard_name)
            if billboard is None:
                response = "No billboard found with name: {}".format(billboard_name)
            else:
                embeds = billboard.generateDiscordEmbedsForTopSongs()
                for embed in embeds:
                    await self.safe_send_message(channel, embed)
        else:
            response = "Invalid arguments provided. args: {}".format(str(leftover_args))
                
        return None if response is None else Response(response)

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

    @overrides(MusicBot)
    def _init_player(self, player, *args, guild = None):
        Block12MusicPlayerInjector(player)
        player_to_return = super()._init_player(player, *args, guild = guild)
        BillboardManager.addEventEmitter(player_to_return)
        return player_to_return

    def _initializeCommandModifier(self, aliases_file, gacha_file):
        aliases_file = aliases_file if aliases_file is not None else AliasesDefault.aliases_file
        gacha_file = gacha_file if gacha_file is not None else GachaDefault.gacha_file
        self.command_modifier = CommandModifier(
            aliases_file if self.config.usealias else None,
            gacha_file if self.config.usegacha else None)
        self.should_command_modifier_be_used = self.config.usealias or self.config.usegacha

    def _dumpSongInfoToLogsIfAllowed(self, guild_id, author):
        log.debug("_dumpSongInfoToLogsIfAllowed called.")
        permissions = self.permissions.for_user(author)
        response = None
        if permissions.allow_billboard_log_dumps:
            billboard = BillboardManager.get(guild_id, leftover_args[1])
            if billboard is None:
                response = "No billboard found with name: {}".format(leftover_args[1])
            else:
                billboard.dumpSongInfoToLogs()
                response = "Dumping song info to logs."
        else:
            response = "You are not allowed to dump billboard logs."
        return response
        
    def _isBillboardCommandForDumpingSongInfoToLogs(self, leftover_args):
        leftover_args_length = len(leftover_args)
        first_leftover_args = leftover_args[0]
        
        log.debug("_isBillboardCommandForDumpingSongInfoToLogs called. leftover_args_length: {}, first_leftover_args: {}".format(
            str(leftover_args_length),
            first_leftover_args
        ))
        return leftover_args_length > 1 and first_leftover_args == "dump"
        
    def _canDefaultBillboardCommandBeExecuted(self, leftover_args):
        leftover_args_length = len(leftover_args)
        log.debug("_canDefaultBillboardCommandBeExecuted called. leftover_args_length: {}".format(
            str(leftover_args_length)
        ))
        return leftover_args_length > 0
        


