import discord
import logging

from .Billboard import Billboard


log = logging.getLogger(__name__)

def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

class Specialized:
    
    OVERALL = {}
    
    def overall(guild_id):
        guild_id = str(guild_id)
        if guild_id not in Specialized.OVERALL:
            Specialized.OVERALL[guild_id] = Specialized._Overall(guild_id)
        return Specialized.OVERALL[guild_id]
    
    class _Overall(Billboard):
        def __init__(self, guild_id):
            super().__init__(guild_id, "Overall", 20)
            
        @overrides(Billboard)
        def generateDiscordEmbedsForTopSongs(self, number_of_songs = None):
            self._loadTopSongsToCacheIfNeeded()
        
            number_of_songs = self._number_of_songs_to_display if number_of_songs is None else number_of_songs
            log.info("generateDiscordEmbedsForTopSongs called. number_of_songs: {}".format(str(number_of_songs)))
            
            embed_author_name = self.getName() + " #"
            embeds = []
            place = 1

            for song in self._top_songs_cache[:number_of_songs]:
                embed = song.generateDiscordEmbed()
                embed.set_author(name = embed_author_name + str(place))
                
                if place == 1:
                    embed.set_thumbnail(url = "")
                    embed.colour = discord.Colour.gold()
                else:
                    embed.set_image(url = "")
                    position_last_week = song.getPositionLastWeek()
                    position_this_week = song.getPositionThisWeek()
                    embed.colour = discord.Colour.green() if position_this_week > position_last_week else discord.Colour.red() if position_this_week < position_last_week else discord.Colour.darker_gray()

                place += 1  
                embeds.append(embed)
                
            return embeds