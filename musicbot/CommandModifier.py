import logging

from .aliases import Aliases
from .gacha import Gacha


log = logging.getLogger(__name__)

class CommandModifier:

    class NoAliases:
        def get(self, arg):
            return ""
            
    class NoGacha:
        def roll(self, arg):
            return ""
            

    def __init__(self, aliases_file, gacha_file):
        self._initializeAliasesFile(aliases_file)
        self._initializeGachaFile(gacha_file)
 
    def _initializeAliasesFile(self, aliases_file):
        if aliases_file is None:
            self._aliases = NoAliases()
        else:
            self._aliases = Aliases(aliases_file)
            
    def _initializeGachaFile(self, gacha_file):
        if gacha_file is None:
            self._gacha = NoGacha()
        else:
            self._gacha = Gacha(gacha_file)
            
    def modifyUsingAlias(self, command):
        return self._aliases.get(command)
        
    def modifyUsingGacha(self, command):
        return self._gacha.roll(command)
        
    def get(self, original_command, original_args):
        modified_command = self.modifyUsingAlias(original_command)
        modified_command, *modified_args = modified_command.split(" ")

        if modified_command == "gacha":
            modified_command = self.modifyUsingGacha(" ".join(modified_args))
            modified_command, *modified_args = modified_command.split(" ")
        elif modified_command == "" and original_command == "gacha":
            modified_command = self.modifyUsingGacha(" ".join(args))
            modified_command, *modified_args = modified_command.split(" ")
 
        for modified_arg in modified_args:
            original_args.append(modified_arg)

        return modified_command, original_args
        
