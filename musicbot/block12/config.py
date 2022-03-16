import configparser

class Block12ConfigInjector:

    def __init__(self, musicbot_config):
        config = configparser.ConfigParser(interpolation=None)
        config.read(musicbot_config.config_file, encoding="utf-8")

        musicbot_config.is_billboard_feature_enabled = config.getboolean(
            "MusicBot", "EnableBillboardFeature", fallback = False
        )
