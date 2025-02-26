import toml

class Config(object):
    
    http: dict
    server: dict
    authorization: dict

    def __init__(cls, path: str = None):
        if path is not None:
            for section, options in toml.load(path).items():
                setattr(Config, section, options)