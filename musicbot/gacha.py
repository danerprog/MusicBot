import discord
import json
import logging
import shutil
from pathlib import Path
import random

from .exceptions import HelpfulError


log = logging.getLogger(__name__)

class Gacha:

    class Command:
        def __init__(self, normal_command, minimum_value, maximum_value, weight):
            log.debug("Creating command. normal_command: {}, minimum_value: {}, maximum_value: {}, weight: {}".format(
                str(normal_command), 
                str(minimum_value), 
                str(maximum_value),
                str(weight)
            ))
            self._normal_command = normal_command
            self._minimum_value = minimum_value
            self._maximum_value = maximum_value
            self._weight = weight
            
        def isNumberWithinBounds(self, value):
            return value >= self._minimum_value and value <= self._maximum_value
            
        def getNormalCommand(self):
            return self._normal_command
          
        def getWeight(self):
            return self._weight

    class NoneCommand(Command):
        def __init__(self):
            super().__init__("", -1, -1, -1)


    def __init__(self, gacha_file):
        log.debug("__init__ called.")
        self._gacha_file = Path(gacha_file)
        self._gacha_seed = GachaDefault.gacha_seed
        self._gacha_commands = GachaDefault.gacha
        
        self._initializeGachaFile()
        self._parseGachaFile()
        self._constructGachaCommands()
        log.debug(str(self._gacha_commands))
        
    def _initializeGachaFile(self):
        log.debug("_initializeGachaFile called.")
        if not self._gacha_file.is_file():
            example_gacha = Path("config/example_gacha.json")
            if example_gacha.is_file():
                shutil.copy(str(example_gacha), str(self._gacha_file))
                log.warning("Gacha file not found, copying example_gacha.json")
            else:
                raise HelpfulError(
                    "Your gacha files are missing. Neither gacha.json nor example_gacha.json were found.",
                    "Grab the files back from the archive or remake them yourself and copy paste the content "
                    "from the repo. Stop removing important files!"
                )
                    
    def _parseGachaFile(self):
        log.debug("_parseGachaFile called.")
        with self._gacha_file.open() as file:
            try:
                self._gacha_seed = json.load(file)
            except json.JSONDecodeError:
                raise HelpfulError(
                    "Failed to parse gacha file.",
                    "Ensure your {} is a valid json file and restart the bot.".format(
                        str(self._gacha_file)
                    ),
                )
                
    def _constructGachaCommands(self):
        log.debug("_constructGachaCommands called.")
        for gacha_command, normal_command_to_rate_dictionary in self._gacha_seed.items():
            log.debug("gacha_command: {}, normal_command_to_rate_dictionary: {}".format(str(gacha_command), str(normal_command_to_rate_dictionary)))
            if not isinstance(gacha_command, str):
                log.warning("Unable to parse gacha_command: {}. Discarding.".format(str(gacha_command)))
            elif not isinstance(normal_command_to_rate_dictionary, dict):
                log.warning("Unable to parse dictionary: {}. Discarding.".format(str(normal_command_to_rate_dictionary)))
            else:
                self._addDictionaryToGachaCommands(gacha_command, normal_command_to_rate_dictionary)
                
    def _addDictionaryToGachaCommands(self, gacha_command, dictionary):
        log.debug("_addDictionaryToGachaCommands called. gacha_command: {}, dictionary: {}".format(str(gacha_command), str(dictionary)))
        self._gacha_commands[gacha_command] = {
            "maximum_value" : 0,
            "normal_commands" : []
        }
        current_maximum_value = 0
        
        for normal_command, weight in dictionary.items():
            log.debug("normal_command: {}, weight: {}".format(str(normal_command), str(weight)))
            if not isinstance(normal_command, str):
                log.warning("Unable to parse command: {}. Discarding.".format(str(normal_command)))
            else:
                parsed_weight = self._parseWeight(weight)
                self._gacha_commands[gacha_command]["normal_commands"].append(Gacha.Command(
                    normal_command, 
                    current_maximum_value, 
                    current_maximum_value + parsed_weight,
                    parsed_weight))
                current_maximum_value = current_maximum_value + parsed_weight

        self._gacha_commands[gacha_command]["maximum_value"] = current_maximum_value
        
    def _parseWeight(self, weight):
        log.debug("_parseWeight called")
        parsed_weight = 0
        try:
            parsed_weight = int(weight)
        except ValueError:
            log.warning("Unable to parse weight: {}. Setting to 0.".format(str(weight)))
        return parsed_weight
        
    def _rollNormalCommand(self, gacha_command):
        log.debug("_rollNormalCommand called. gacha_command: {}".format(str(gacha_command)))
        command = Gacha.NoneCommand()
        gacha = self._gacha_commands[gacha_command]
        rolled_number = random.randint(0, gacha["maximum_value"] - 1)
        log.debug("rolled_number: " + str(rolled_number))
        for normal_command in gacha["normal_commands"]:
            if normal_command.isNumberWithinBounds(rolled_number):
                command = normal_command
        return command.getNormalCommand()
        
    def roll(self, gacha_command):
        log.debug("roll called. gacha_command: {}".format(str(gacha_command)))
        normal_command = ""
        if gacha_command in self._gacha_commands:
            normal_command = self._rollNormalCommand(gacha_command)
        log.debug("normal_command: " + str(normal_command))
        return normal_command
        
    def rates(self, gacha_command):
        log.debug("rates called. gacha_command: {}".format(str(gacha_command)))
        rates = None
        if gacha_command in self._gacha_commands:
            rates = self._gacha_commands[gacha_command]
            log.debug("rates found for given command. rates: {}".format(str(rates)))
        else:
            log.debug("no rates found for given command. gacha_commands: {}".format(str(self._gacha_commands)))
        return rates
        
    def commands(self):
        keys = self._gacha_commands.keys()
        log.debug("commands called. keys: {}".format(str(keys)))
        return keys
        
    def generateDiscordEmbedForRates(self, gacha_command):
        log.debug("generateDiscordEmbedForRates called. gacha_command: {}".format(gacha_command))
        embed = None
        rates = self.rates(gacha_command)
        
        if rates is not None:
            embed = discord.Embed()
            embed.title = "Gacha Rate: {}".format(gacha_command)
            
            maximum_value = rates["maximum_value"]
            
            commands_string = ""
            weights_string = ""
            rates_string = ""
            
            for command in rates["normal_commands"]:
                weight = command.getWeight()
                commands_string += '\n' + command.getNormalCommand()
                weights_string += '\n' + str(weight)
                rates_string += "\n{0:.2f}%".format(round(weight / maximum_value, 4) * 100)
            
            embed.add_field(name = "Command", value = commands_string, inline = True)
            embed.add_field(name = "Weight", value = weights_string, inline = True)
            embed.add_field(name = "Rate", value = rates_string, inline = True)
            embed.add_field(name = "Maximum Weight", value = maximum_value, inline = False)
        
        return embed
                

class GachaDefault:

    gacha_file = "config/gacha.json"
    gacha_seed = {}
    gacha = {}


class NoGacha(Gacha):
    def roll(self, arg):
        return ""
        
    def rates(self, arg):
        return None
        
    def commands(self):
        return []
        
    def generateDiscordEmbedForRates(self, arg):
        return None


