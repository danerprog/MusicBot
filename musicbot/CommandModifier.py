from .aliases import Aliases
from .gacha import Gacha

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

