import configparser


class Block12PermissionsDecorator:

    def __init__(self, musicbot_permissions):
        config = configparser.ConfigParser(interpolation=None)
        config.read(musicbot_permissions.config_file, encoding="utf-8")
        for group in musicbot_permissions.groups:
            section = config[group.name]
            group.allow_billboard_log_dumps = section.get(
                "AllowBillboardLogDumps",
                fallback = True if group.name == "Owner (auto)" else False)
 
