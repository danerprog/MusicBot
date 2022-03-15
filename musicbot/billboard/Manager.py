from .Billboard import Billboard

import logging


log = logging.getLogger(__name__)

class Manager:

    BILLBOARD = {}
    
    def register(billboard):
        if isinstance(billboard, Billboard):
            name = billboard.getName()
            guild_id = billboard.getGuildId()
            Manager.BILLBOARD[guild_id] = {} if guild_id not in Manager.BILLBOARD else Manager.BILLBOARD[guild_id]
            Manager.BILLBOARD[guild_id][name] = billboard
            
            log.debug("Registered billboard with guild_id: {}, name: {}".format(
                guild_id,
                name
            ))
            
    def get(guild_id, name):
        guild_id = str(guild_id)
        billboard = None
        try:
            billboard = Manager.BILLBOARD[guild_id][name]
        except KeyError:
            log.warning("No billboard registered with guild_id: {}, name: {}".format(
                guild_id,
                name
            ))
        return billboard
        
    def registerOverall(guild_id):
        guild_id = str(guild_id)
        Manager.register(Billboard(guild_id, "overall", 20))
        
    def getOverall(guild_id):
        return Manager.get(guild_id, "overall")