# from satorineuron import spoof
from satorineuron import config
from satorilib import logging
from satorineuron import init
from satorilib.api.wallet import Wallet
from satorilib.api.disk import Disk
Disk.setConfig(config)
logging.setup()
