import os
from threading import Lock

import yaml
from fastapi import Depends


def get_config():
    return BaseApplicationConfig()


class SingletonMeta(type):
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class BaseApplicationConfig(metaclass=SingletonMeta):
    value: str = None

    def __init__(self) -> None:
        self.config_path = (
            os.environ["CFG_FILE"]
            if "CFG" in os.environ
            else "./config/local/config.yaml"
        )
        self.cfg = yaml.safe_load(open(self.config_path, "r"))


class ApplicationConfig:
    def __init__(self, appcfg: BaseApplicationConfig = None):
        self.cfg = appcfg.cfg if appcfg is not None else {}

    def __call__(self, appcfg: BaseApplicationConfig = Depends(get_config)):
        self.cfg = appcfg.cfg
        return self

    def __getitem__(self, item):
        return self.cfg[item]
