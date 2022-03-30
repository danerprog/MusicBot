import logging

from .aliases import Aliases
from .gacha import Gacha, NoGacha


log = logging.getLogger(__name__)

class CommandModifier:

    class NoAliases:
        def get(self, arg):
            return ""      

    def __init__(self, aliases_file, gacha_file):
        self._initializeAliasesFile(aliases_file)
        self._initializeGachaFile(gacha_file)
 
    def _initializeAliasesFile(self, aliases_file):
        if aliases_file is None:
            self._aliases = CommandModifier.NoAliases()
        else:
            self._aliases = Aliases(aliases_file)
            
    def _initializeGachaFile(self, gacha_file):
        if gacha_file is None:
            self._gacha = CommandModifier.NoGacha()
        else:
            self._gacha = Gacha(gacha_file)
            
    def modifyUsingAlias(self, command):
        return self._aliases.get(command)
        
    def modifyUsingGacha(self, command):
        return self._gacha.roll(command)
        
    def get(self, original_command, original_args):
        log.debug("get called. original_command: {}, original_args:{}".format(
            original_command,
            str(original_args)
        ))
        modified_command = self.modifyUsingAlias(original_command)
        modified_command, *modified_args = modified_command.split(" ")
        log.debug("modified_command: {}, modified_args: {}".format(
            modified_command,
            str(modified_args)
        ))

        if modified_command == "gacha":
            modified_command = self.modifyUsingGacha(" ".join(modified_args))
            modified_command, *modified_args = modified_command.split(" ")
        elif modified_command == "" and original_command == "gacha":
            if len(original_args) > 0 and original_args[0] == "rates":
                modified_command = "gacha_internal"
                modified_args = []
            else:
                modified_command = self.modifyUsingGacha(" ".join(original_args))
                modified_command, *modified_args = modified_command.split(" ")

            for original_arg in original_args:
                modified_args.append(original_arg)

        return modified_command, modified_args
        
    def rates(self, gacha_command):
        return self._gacha.rates(gacha_command)
        
    def generateDiscordEmbedForRates(self, gacha_command = None):
        embeds = []
        if gacha_command is None:
            commands = self._gacha.commands()
            for command in commands:
                embeds.append(self._gacha.generateDiscordEmbedForRates(command))
        else:
            embed = self._gacha.generateDiscordEmbedForRates(gacha_command)
            if embed is not None:
                embeds.append(embed)
        return embeds

        
