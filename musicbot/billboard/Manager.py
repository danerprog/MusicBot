from .Billboard import Billboard
from .Snapshot import Snapshot

import asyncio
import logging


log = logging.getLogger(__name__)

class Manager:

    BILLBOARD = {}
    
    def register(billboard):
        if isinstance(billboard, Billboard):
            name = billboard.getName()
            guild_id = billboard.getGuildId()
            Manager.BILLBOARD[guild_id] = {} if guild_id not in Manager.BILLBOARD else Manager.BILLBOARD[guild_id]
            Manager.BILLBOARD[guild_id][name] = {
                "live" : billboard,
                "snapshot" : None
            }
            
            log.debug("Registered billboard with guild_id: {}, name: {}".format(
                guild_id,
                name
            ))
            
    def get(guild_id, name):
        guild_id = str(guild_id)
        billboard = None
        try:
            billboard = Manager.BILLBOARD[guild_id][name]["snapshot"]
        except KeyError:
            log.warning("No billboard registered with guild_id: {}, name: {}".format(
                guild_id,
                name
            ))
        return billboard

    def registerCumulative(guild_id):
        guild_id = str(guild_id)
        Manager.register(Billboard({
            "guild_id" : guild_id,
            "name" : "Cumulative",
            "number_of_songs_to_display" : 20,
            "number_of_days_before_recalculation_should_be_performed" : 7
        }))

    def activate():
        log.info("Creating infinite loop for _calculateTopSongsForAllBillboards")
        asyncio.create_task(Manager._calculateTopSongsForAllBillboards())
        
    def addEventEmitter(event_emitter):
        log.debug("addEventEmitter called. event_emitter: {}".format(str(event_emitter)))
        event_emitter.on("entry-added", Manager._onEntryAdded)

    async def _calculateTopSongsForAllBillboards():
        for guild_id in Manager.BILLBOARD:
            for name in Manager.BILLBOARD[guild_id]:
                log.info("Calculating Top Songs for billbords in guild_id: {}, name: {}".format(
                    guild_id,
                    name
                ))
                billboard = Manager.BILLBOARD[guild_id][name]["live"]
                wasCalculationPerformed = billboard.calculateBillboardTopSongsIfNeeded()
                old_snapshot = Manager.BILLBOARD[guild_id][name]["snapshot"]
                
                if wasCalculationPerformed and old_snapshot is not None:
                    old_snapshot.archive()
                    log.debug("Older snapshot archived. old_snapshot: {}".format(
                        str(old_snapshot)
                    ))

                Manager.BILLBOARD[guild_id][name]["snapshot"] = Snapshot(billboard)
                
        seconds_to_sleep = 3600
        log.info("Calculations done. Recalculating in {} seconds.".format(
            str(seconds_to_sleep)
        ))
        await asyncio.sleep(seconds_to_sleep)
        asyncio.create_task(Manager._calculateTopSongsForAllBillboards())
        
    async def _onEntryAdded(player, playlist, entry, **kwargs):
        log.debug("_onEntryAdded called.")
        guild_id = str(entry.meta.get("channel").guild.id)
        video_information_dictionary = {
            "video_id" : entry.url.split("=")[-1],
            "title" : entry.title
        }
        for name in Manager.BILLBOARD[guild_id].keys():
            Manager.BILLBOARD[guild_id][name]["live"].queue(video_information_dictionary)



