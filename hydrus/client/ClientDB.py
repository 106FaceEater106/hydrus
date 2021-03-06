import collections
import gc
import hashlib
import itertools    
import json
import os
import psutil
import random
import re
import sqlite3
import stat
import time
import traceback
import typing

from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from hydrus.client import ClientAPI
from hydrus.client import ClientConstants as CC
from hydrus.client import ClientData
from hydrus.client import ClientDefaults
from hydrus.client import ClientFiles
from hydrus.client import ClientOptions
from hydrus.client import ClientRatings
from hydrus.client import ClientSearch
from hydrus.client import ClientServices
from hydrus.client import ClientTags
from hydrus.client import ClientThreading
from hydrus.client.gui import QtPorting as QP
from hydrus.client.media import ClientMedia
from hydrus.client.media import ClientMediaManagers
from hydrus.client.media import ClientMediaResult
from hydrus.client.media import ClientMediaResultCache
from hydrus.client.networking import ClientNetworkingBandwidth
from hydrus.client.networking import ClientNetworkingContexts
from hydrus.client.networking import ClientNetworkingDomain
from hydrus.client.networking import ClientNetworkingLogin
from hydrus.client.networking import ClientNetworkingSessions
from hydrus.core import HydrusConstants as HC
from hydrus.core import HydrusData
from hydrus.core import HydrusDB
from hydrus.core import HydrusExceptions
from hydrus.core import HydrusGlobals as HG
from hydrus.core import HydrusNetwork
from hydrus.core import HydrusNetworking
from hydrus.core import HydrusPaths
from hydrus.core import HydrusSerialisable
from hydrus.core import HydrusTags

#
#                                𝓑𝓵𝓮𝓼𝓼𝓲𝓷𝓰𝓼 𝓸𝓯 𝓽𝓱𝓮 𝓢𝓱𝓻𝓲𝓷𝓮 𝓸𝓷 𝓽𝓱𝓲𝓼 𝓗𝓮𝓵𝓵 𝓒𝓸𝓭𝓮
#                                              ＲＥＳＯＬＶＥ ＩＮＣＩＤＥＮＴ
#
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▒█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▓▓▓▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██ █▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░▒▓▓▓░  █▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▓▒  ░▓▓▓ ▒█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▓▒  ▓▓▓▓ ▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▓▓▒▒▒▒▒▓  ▓▓▓▓  ▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▒█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ░▓░  ▓▓▓▓▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▓▓▓█▒ ▓▓▓█  ▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░ ▓░  ▓▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▒▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▓▓▓░   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▒▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▒▒▒▓▓▓▓▒▒▒▒▒▒▒▒▒▒▓  ▓▓▓   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█  ▒█▓░▒▓▒▒▒▒▓▓▓█▓████████████▓▓▓▓▓▒▒▒▓  ▒▓▓▓  ▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ░█▓ ░▓▓█████████▓███▓█▓███████▓▓▓▓▓ ░▓▓█  █▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓█▓▓▓▓▓▓▓▓▓▓▓▓▓█▒▒█▓▓▓▓▓▓▓▓▓▓  ▓▓ ░██████▓███▓█████▓▓▓▓▓█████▓▓▓▒ ▓▓▓▒ ▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒███▓▓▓▓▓▓▓▓▓▓▓████▓█▓▓▓▓▓▓▓▓▓▓█░▓▓███▓▓▓█▓█▓▓▓█▓█▓███▓▓▓▓▓▓██████▓ ▓▓▓   ▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▒▓▓▓█▒▓▓▒▓▓▓██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒██████▓▓▓▓▓████▓▓█▓▓██▓▓▓▓▓▓██▓███ ▓█   ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓ ▒███▒█▒▓█▓▓███▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓█▓▓██▓▓▓▓▓▓▓▓██▓▓▓▓█▓░▒▒▒▓▓█████ ▒█  ▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓░▓██▓▒█▓████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓███▓▓▓█▓▓██▓▓▓▓▓▓▓▓▓█▓▓▓▓█░ ▓▓▓▓█████▓▓▓░   █▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▒▓██▓▒█▓▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓▓▓▓▓▓▓▓██▓▓▓▓▓▒▒▒▓▒ ▒▓▓░▓▓▓▓▓█████▓▓▒  ▓▓▓▒▓▓  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓███▓███▓▓▓▒█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▓█▓█▓▓█▓▓▓▓███▓▒▒▒▒░░▓▓▓▓█▓▓▓▓▓███████▓▓░██▓▓▓▓▒ ▒▓ ▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▒▓█▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▓▓▓▓▓▓█▓▓▓▓▒▒▓██▓▓▒▓▓▓▓████▓▓▓▓▓██▓▓███▒ ▒█▓▒░░ ▓▓ ▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒██▒▓▓█▓█▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓█▓█▓▒▓█▓▓▓▓▓▓▓▓██████▓▓███▓▓▓▓█████▓█▓  ▓  ░▒▓▓▒ ▒█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▓▓█▓▓█▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓█▓▓█▓▓▓▓▓▓██▓██████████████▓▓▓███▓▓▓█░░█░▒▓▓░▒▒ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▒▓██▓█▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒██▓▓█▓▓▓██▓▓▓▓░▓█▓▒▓███████████▓▓▓███▓▓▓█▓▒▒▓▒   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓█▒▓██▓▓█▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▓███ ▓███░▒▒  ▓▓▒     ░░▒░░▓█▓▓██▓▓▓▓█▓▓▒  ▒█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▓██▓▓███▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓██▓███   ███  ▒   ▒▒░░▓▓▒██   ██████▓▓▓█░▒▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓██▓█▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓█▒   ░██▓  ░▒▒▓█████▓    █▓█▓██▓▓▓█▓██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒██▓▓██▓▒█▒█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▒▓  ░   ▒▒   ▒ ░█▓▒      ▒ ░░▒█▓▓█████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓███▓███▒█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓██▒  ▒▓▓▒                  ░▓▒▒██▓▓███▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓░▓▓█░▓█▒▓█▓███▓▓▒▓▓▓▓▓▓▓▒▓██▒▓████                  ▒▓░▒█▓▓█▓██▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓██▓░█▓█▓▒▒▒▓▓██▓▓▒▓▓▓▓▓▒▓██▒  ▓░                  ▒▓▒▓█▓███▓▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓▒▓▓█████▓▓▓██▒▓█▓█▓▓▓▓▒▒██▓▓▓▓▓▓▓▓▒▓█▓                      ▒▓▒▓█▓▓█▓█▓▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▒░▒▓▓███▓▓██▓▓▓▓█▓▓█▓██▓█▓▓▒▓█▓▓▓▓▓▓▓▓▓▓▓▓▒   ░                 ▓▓▒▓█▒██▓▓▓▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓▓█████▓▒▓▓▓█▓▓▓▓██▒█▓▓███▓▓▓▒██▓▓▓▓▓▓▓▓▓▓▓▓░                   ▓█▒░▒▒▓██▓█▓▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█████▓▓  ▓▓██▓▓▓██▒▓█▓█▓▒▓▓▓▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓░    ░░          ░▒█▒▒▒░▒▓█▓▓▓▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▓█▓▓▓   ▒██▓▓▓▓█▓▒██▓▓▒▓▓▓▓▒██▓▓▓▓▓▓▓▓▓▓▓▓█▓             ░▓░░ ░███▓██▓▓▓▓▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒██▓▓▓░▓██▓▓▓▓██░▓█▓▓▓▓▓▓▓▒▓██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒        ░▓▒  ░ ▓███▓██▓█▓▓▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓█▓█▓▒▓██▓▓▓██▓▒█▓▓▓▓▓▓▓▓▒██▓▒▓▓▓▓▓▓▓▓▓▓█▓▓▓▓▓░   ▓█▓      █▓▓█▓█▓▓█▓▓▓██▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██   ░██▓▓▓▓█▓▒▓█▓▓▒▓▓▓▓▒▓█▓▓▓▓▓▓▓▓▓▒███▓▒▓▓▓▓███▓░       █▓▓█▓█▓▓█▓▓▓██▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓  █▓░  ░█▓▓▓▓██▓▓██▓▓▒▓▓▓▓▒██▓▓▓▓▓▓▓▓▒▓█▓▓▓▒▓▓▓▓▓░        ░█▒▓█▓█▓▓▓█▓▓▓▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█░ ░   ███  ██▓▓▓██▓▒██▓▓▒▓▓▓▓▒▓██▓▓▓▓▓▓▓▒▓█▓▓▓▒▒▓▓█▓          █▓██▒█▓▓▓▓█▓▓▓█▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒    ░  ███  ▓█▓▓▓▓██▒▓█▓▓▓▓▓▓▓▓▒██▓▒▓▓▓▓▓▓▓██▓█▒▓▓█▓░          █▓██▒▓██████▓▓▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█      ▓ ▓█   ░█▓▓▓▓██▓▓██▓▓▒▓▓▓▓▒▓█▓▓▒▓▓▓▓▓░▓███▓▓█░            █▓█▓▓▓▓▓█▓░███▓▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▓█  ▓▒ ██▒    ▒████▓███▒▓█▓▓▓▒▓▓▓▒▓██▓▓▓▓▓▓▓▒▒███▓▓▒     ▒      ▓███▓▓▓▓▓ ░░▓▓██▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓█▓██     ▓█▓▓▓▓▓██▓▓██▓▓▒▒▓▒▒▒▓██▓▒      ▓█▓██   ░        ▓▒▓██▓▓▓▒  ░    ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓██▓█████▓      ▓██▓█████▓▓▓█▓▓▓▓▓▓▓▓█▒██     █░▒▓▓▓█           ▓▒▓██▓▒░  ▒▒      █▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓████▓         ▓█████████▓▓██▓▓▓▓▓█▓▓▓██▒   █▓  ▓▒▓▒          ▓▓▓█▓   ▒▓         ▒█▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒██▓▒▓░        ▒███▓█████▓▓███▓▓▓▓▓█████▓  ▓▓▓░ ▓▒▓▒        ▒▓▓▓▒  ▓▓▓█▒          ▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▓▓▓▒        ███▓▓█████▓▓████▓▓▓███▓░   ▓▓▓█▓ ▓▓▓       ▓█▒░  ▒▒▓▓▓█            ██▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▓▒▓▒▓▓▓▓▓▓▓▓▓▓█▓       ▒███▓█████▓▓▓█▓▓▓███▓     ▓▓▓▓▓  ▒▓▓     ▓▓▒  ▒▓▒█▓▓▒▓▓            ▓█▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▓▒▒█▓▒▓▒▓▓▓▓▓▓▓▓█▒       ███▓▓█▒██▓▓█▓███▓▓▓░    ▓▓▒▓▒▓▓█  ▓▒ ░▓▓░   ▒█▓▓▓▒▒▓▓▓            ▒█▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▓▒▒▓▓▓▓▓▒▓▓▒▒▒▓▓▓▓▓       ▒██▓█▒▒▓██▒████▓▒▒▓    ▓▓▒▓▒▒▒▓▓▓ ▒▒ ▒▓░▓▒█▓▓▒▒▒▒▒▒▒▓▒             █▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▓▓▓▓▓▒▒▓█▓▓▓▓▓▓▓▓▓▓▒▓▒▒▓▒       ▓███▓▓▓██░▓▓██▓▒▓▒   ▓▓▒▒▒▒▒▒▓▓▓█▓░ ▒█▓▓▓▓▓▒▒▒▒▒▒▒▒▓▒  ░░         ▓▓▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▓▒▓▒▓▒▒▓█▓██▓▓▓▓▓▓▓▓▓▓▓▓▓▓░      ▒█▓▓█▓▒██░░ ▒██▒▓  ░▓▒▒▒▒▒▒▒▒▓▓▓▓▓█▓▓█▓▓▒▒▒▒▒▒▒▒▒▒▒▓░ ░▒▓▓         █▓▓▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓
#▒▓▓▓▒▒▓█▓▓▓█▓▓▓▓▓▓▒▓▓▓▓▓▓▓██████████▓██▒▓█▓▓  ██▓▓  ▓▒▒▒▒▒▒▒▒▒▒▓▓▓░▒▓▒▓▓▒▒▒▒▒▒▒▒▒▒▒▒▓░░▒▒░▒▓        ▒███▒▓▓▓▒▓▓▓▓▓▓▓▒▓▓▓
#▓▓▓▒▒▓█▓▓████▓▓▓▓▓▓▓▓▓▓▓▓█▓▓███████▓▒▓█▓▓██▒▒ ▓██  ▒▓▒▒▒▒▒▒▒▒▒▒▓▓░ ▒▒░▓▓▒▒▒▒▒▒▒▒▒▒▒▒▓▒ ░░░░█▓        ▓█▒▒▓▓▓▓▒▓▓▓▓▓▓▓▓▓▓
#▒▓▒▒▓███████████▓▓▓▓▓▓▓▓▓▓▓█▓▓▓▓▓▓██▒▓█▓▒██▒▓░▒██  ▓▓▒▒▒▒▒▒▒▒▒▒▓▒  ▒▒░▓▓▒▒▒▒▒▒▒▒▒▒▒▒▓▓  ░░▒▓▓░    ▒░▒   ▒▓▒▓▒▓▒▓▒▓▒▓▒▓▒▓
#▓▒▓▒▓▓▓▓███████▓█▓██▓▓█▓▓▓▓▓▓▓▓▓█▓██▓▓██▒▓█▓▒▓▓██░ ▒▓▒▓▒▓▓▓▒▒▓▓▓ ░░▒░ ▒▓▒▒▒▒▒▒▒▒▒▒▒▒▓▓  ░ ▓▓▓▓  ▒ ▒     ▒▓▓▒▓▒▓▒▓▓▓▒▓▒▓▒
#▒▓▒▓▒▒▒▒▒▓▓██████████▓▓▓▓▓▓█▓█▓█▓███▓▓▓█▓▒██▒▓█▒██ ░█▓▓▓▓▓▓▓▓▓▓  ▒▒▒░ ▒▓▒▒▒▒▒▒▒▒▒▒▒▓▓▓ ░░▒▓▒▓█▒ ░       ██▒▓▒▓▒▓▒▓▒▓▒▓▒▓
#▓▒▓▒▓▒▓▒▒▒▒▒▒▒▓▓█████████▓▓██████████▓▓█▓▒▓██▓█▒▓█░ ▓▓▓▓▓▓▓▓▓█▒ ▒▒▓░▒ ░█▓▓▓▒▓▓▓▓▓▓▓▒▓▓▒ ▒▓▓▒▓▒░    ░▒█▒ ▓▒▓▓▓▒▓▒▓▒▓▒▓▒▓▒
#▒▓▒▓▒▓▒▓▒▓▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓███████▓▓██▓▓▓█▒▒██▓▓▓▓█▓ ░█▓▓▓▓▓▓▓▓  ▒▒▒ ▒  █▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ▒▓▒▓▒▓▓▓▓▓░▓█▓▒   ▒▓▒▓▒▓▒▓▒▓▒▓▒▓
#▓▒▓▒▓▒▓▒▓▒▒▒▓▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▓    ░▓▒██▓▓▓▓▒▓█▓▓█▓▓█ ░▓▓▓▓▓▓▓█░ ░▒▒▒ ▒  █▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▒▒▓▒▒▒▒▓▓▓▒░ ░      ▓▓▒▓▒▓▒▓▒▓▒▒▒
#▒▓▒▓▒▒▒▒▒▒▒▒▒▒▒▓▒▒▒▒▒▒▒▒▒▒▒▒▓▒   ▒░  ██▓██▒▓██▓█▓▒█▒░▓▓▓▓▓▓▓▓  ░▓▓▒ ▒  ▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▓▒          ▓▓▒▒▒▓▒▒▒▓▒▒
#▓▒▓▒▓▒▓▒▒▒▒▒▒▒▓▒▒▒▒▒▓▒▒▒▓▒▒▒▓▓░░░    ▓██▓█▓▓██▓▓█▒█▓▒▓▓▓▓▓▓▓░  ░▓▒░ ▒  ▒▒▒█▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▒▒▒▒▒▒▓▓▒         ░▓▓▒▒▒▒▒▒▒▓▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒ ░     ██▓▓█▒▓█▓▒█▓▓█▓▓▓▓▓▓▓▓░  ░▓▓  ▒░ ▒▒ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▓▒▓▒▓▓▒     ░░░ ░▓▓▒▒▒▓▒▒▒▒
#▓▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒▒▒▓▒▒▒▒▒▒▒▒▒▒▒▓ ░░    ▓██▓█▒▓██▓▓▓▓█▓▓▓▓▓▓▓▓██▒░▒▒  ▓▒ ░▓ ░█▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▓▒▒▒▓▒▓▓     ░░░░ ▒▓▓▒▒▒▒▒▓▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓ ░░   ░██▓▓▓▒██▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▒  ▒▒  ▓░ ▓▓▓▓▓▓▓▓▓▓▓█▒▒▒▒▒▒▒▒▒▒▒▒▓▓▒       ░ ▒▓▓▒▒▒▒▒▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒▒▒▒▓▓ ░░   ██▓▓█▒▓██▓██▓▓▓▓▓▓▓▓▓▓▓▓▓█▒  ▒▓  ░▒  ▓▓▓▓▓▓▓▓▓█▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓ ░ ░░░     ▒▓▒▒▒▒▒▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓░    ▓██▓▓▓▒██▓▓▓▓▓▓▓▓▒▒▒▓▓▓▓▓▓░  ░▓▒▓▓▓░▒▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒     ░░ ░░  ▒▓▒▒▒▒▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▒  ▓█▓█▓▓█▒███▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▓▓▓▒▒▓█▓█▓▓█▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓      ░░░ ░░  ▓▒▒▒▒▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▒▓█▓█▓▓██▓▒▓▓▓▓▓▓▓▓▓▓▓▒▒▒▓▓▓▓▓▓▒▒▒▒▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▓▓     ░  ░░░░░  ▓▓▒▒▒▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓██▒▒▓▓█▓▓▒▓██▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▓▒  ▒░   ░ ░░░░░  ▓▒▒▒▒▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▓▒▓▓▓▒▓▓▓█▓▒▒▓▓▓▒▓▒▒▒▓▒▒▒▒▓▓▒▒▒▓▓▓▓▓▓▓▒▒▒▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▓░  ██▓   ░  ░░░░ ▒▓▒▒▒▒▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░▓██▒▓▓▓█▓▓██▓▒▓▓▓▓▓▒▒▒▒▒▒▒▒▒▓▒▓▓▓▓▓▒▓▒▓▓▒▓▓▓▓▓▒▓▓▒▒▒▒▒▒▒▒▒▓░▓█▒▒░▒    ░ ░░░░ ▒▓▒▒▒▒▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▓▓▓▓▓███▓▒▓▒▓▒▓▒▓▒▒▒▒▒▒▒▒▓▓▒▓▒▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▓▓██▒   ▒░      ░░░ ▓▒▒▒▒▒▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒███▓▒▓██▓█▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒█░    ▒       ░░ ░▓▒▒▒▒▒▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓██▓▓▓▒▒▓▓▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▓▓        ▒░▓░  ░░ ▒▓▒▒▒▒▒▒
#▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░▒▒░░▓▓▒▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓  ░▒▒▒▒       ▓████▒     ▒▒▒▒▒▒▒▒

YAML_DUMP_ID_SINGLE = 0
YAML_DUMP_ID_REMOTE_BOORU = 1
YAML_DUMP_ID_FAVOURITE_CUSTOM_FILTER_ACTIONS = 2
YAML_DUMP_ID_GUI_SESSION = 3
YAML_DUMP_ID_IMAGEBOARD = 4
YAML_DUMP_ID_IMPORT_FOLDER = 5
YAML_DUMP_ID_EXPORT_FOLDER = 6
YAML_DUMP_ID_SUBSCRIPTION = 7
YAML_DUMP_ID_LOCAL_BOORU = 8

# Sqlite can handle -( 2 ** 63 ) -> ( 2 ** 63 ) - 1, but the user won't be searching that distance, so np
MIN_CACHED_INTEGER = -99999999
MAX_CACHED_INTEGER = 99999999

def BlockingSafeShowMessage( message ):
    
    HG.client_controller.CallBlockingToQt( HG.client_controller.app, QW.QMessageBox.warning, None, 'Warning', message )
    
def CanCacheInteger( num ):
    
    return MIN_CACHED_INTEGER <= num and num <= MAX_CACHED_INTEGER
    
def ConvertWildcardToSQLiteLikeParameter( wildcard ):
    
    like_param = wildcard.replace( '*', '%' )
    
    return like_param
    
def DealWithBrokenJSONDump( db_dir, dump, dump_descriptor ):
    
    timestamp_string = time.strftime( '%Y-%m-%d %H-%M-%S' )
    hex_chars = os.urandom( 4 ).hex()
    
    filename = '({}) at {} {}.json'.format( dump_descriptor, timestamp_string, hex_chars )
    
    path = os.path.join( db_dir, filename )
    
    with open( path, 'wb' ) as f:
        
        if isinstance( dump, str ):
            
            dump = bytes( dump, 'utf-8', errors = 'replace' )
            
        
        f.write( dump )
        
    
    message = 'A serialised object failed to load! Its description is "{}".'.format( dump_descriptor )
    message += os.linesep * 2
    message += 'This error could be due to several factors, but is most likely a hard drive fault (perhaps your computer recently had a bad power cut?).'
    message += os.linesep * 2
    message += 'The database has attempted to delete the broken object, errors have been written to the log, and the object\'s dump written to {}. Depending on the object, your client may no longer be able to boot, or it may have lost something like a session or a subscription.'.format( path )
    message += os.linesep * 2
    message += 'Please review the \'help my db is broke.txt\' file in your install_dir/db directory as background reading, and if the situation or fix here is not obvious, please contact hydrus dev.'
    
    HydrusData.ShowText( message )
    
    raise HydrusExceptions.SerialisationException( message )
    
def GenerateCombinedFilesMappingsCacheTableName( service_id ):
    
    return 'external_caches.combined_files_ac_cache_{}'.format( service_id )
    
def GenerateMappingsTableNames( service_id ):
    
    suffix = str( service_id )
    
    current_mappings_table_name = 'external_mappings.current_mappings_{}'.format( suffix )
    
    deleted_mappings_table_name = 'external_mappings.deleted_mappings_{}'.format( suffix )
    
    pending_mappings_table_name = 'external_mappings.pending_mappings_{}'.format( suffix )
    
    petitioned_mappings_table_name = 'external_mappings.petitioned_mappings_{}'.format( suffix )
    
    return ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name )
    
def GenerateRepositoryMasterCacheTableNames( service_id ):
    
    suffix = str( service_id )
    
    hash_id_map_table_name = 'external_master.repository_hash_id_map_{}'.format( suffix )
    tag_id_map_table_name = 'external_master.repository_tag_id_map_{}'.format( suffix )
    
    return ( hash_id_map_table_name, tag_id_map_table_name )
    
def GenerateRepositoryRepositoryUpdatesTableName( service_id ):
    
    repository_updates_table_name = 'repository_updates_{}'.format( service_id )
    
    return repository_updates_table_name
    
def GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id ):
    
    suffix = str( file_service_id ) + '_' + str( tag_service_id )
    
    cache_files_table_name = 'external_caches.specific_files_cache_{}'.format( suffix )
    
    cache_current_mappings_table_name = 'external_caches.specific_current_mappings_cache_{}'.format( suffix )
    
    cache_deleted_mappings_table_name = 'external_caches.specific_deleted_mappings_cache_{}'.format( suffix )
    
    cache_pending_mappings_table_name = 'external_caches.specific_pending_mappings_cache_{}'.format( suffix )
    
    ac_cache_table_name = 'external_caches.specific_ac_cache_{}'.format( suffix )
    
    return ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name )
    
def GenerateTagSiblingsLookupCacheTableName( service_id ):
    
    return 'external_caches.tag_siblings_lookup_cache_{}'.format( service_id )
    
def report_content_speed_to_job_key( job_key, rows_done, total_rows, precise_timestamp, num_rows, row_name ):
    
    it_took = HydrusData.GetNowPrecise() - precise_timestamp
    
    rows_s = HydrusData.ToHumanInt( int( num_rows / it_took ) )
    
    popup_message = 'content row ' + HydrusData.ConvertValueRangeToPrettyString( rows_done, total_rows ) + ': processing ' + row_name + ' at ' + rows_s + ' rows/s'
    
    HG.client_controller.pub( 'splash_set_status_text', popup_message, print_to_log = False )
    job_key.SetVariable( 'popup_text_2', popup_message )
    
def report_speed_to_job_key( job_key, precise_timestamp, num_rows, row_name ):
    
    it_took = HydrusData.GetNowPrecise() - precise_timestamp
    
    rows_s = HydrusData.ToHumanInt( int( num_rows / it_took ) )
    
    popup_message = 'processing ' + row_name + ' at ' + rows_s + ' rows/s'
    
    HG.client_controller.pub( 'splash_set_status_text', popup_message, print_to_log = False )
    job_key.SetVariable( 'popup_text_2', popup_message )
    
def report_speed_to_log( precise_timestamp, num_rows, row_name ):
    
    if num_rows == 0:
        
        return
        
    
    it_took = HydrusData.GetNowPrecise() - precise_timestamp
    
    rows_s = HydrusData.ToHumanInt( int( num_rows / it_took ) )
    
    summary = 'processed ' + HydrusData.ToHumanInt( num_rows ) + ' ' + row_name + ' at ' + rows_s + ' rows/s'
    
    HydrusData.Print( summary )
    
class JobDatabaseClient( HydrusData.JobDatabase ):
    
    def _DoDelayedResultRelief( self ):
        
        if HG.db_ui_hang_relief_mode:
            
            if QC.QThread.currentThread() == HG.client_controller.main_qt_thread:
                
                HydrusData.Print( 'ui-hang event processing: begin' )
                QW.QApplication.instance().processEvents()
                HydrusData.Print( 'ui-hang event processing: end' )
                
            
        
    
class DB( HydrusDB.HydrusDB ):
    
    READ_WRITE_ACTIONS = [ 'service_info', 'system_predicates', 'missing_thumbnail_hashes' ]
    
    def __init__( self, controller, db_dir, db_name ):
        
        self._initial_messages = []
        
        self._have_printed_a_cannot_vacuum_message = False
        
        HydrusDB.HydrusDB.__init__( self, controller, db_dir, db_name )
        
    
    def _AddFilesInfo( self, rows, overwrite = False ):
        
        if overwrite:
            
            insert_phrase = 'REPLACE INTO'
            
        else:
            
            insert_phrase = 'INSERT OR IGNORE INTO'
            
        
        # hash_id, size, mime, width, height, duration, num_frames, has_audio, num_words
        self._c.executemany( insert_phrase + ' files_info VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ? );', rows )
        
    
    def _AddFiles( self, service_id, rows ):
        
        hash_ids = { row[0] for row in rows }
        
        existing_hash_ids = self._STS( self._ExecuteManySelect( 'SELECT hash_id FROM current_files WHERE service_id = ? AND hash_id = ?;', ( ( service_id, hash_id ) for hash_id in hash_ids ) ) )
        
        valid_hash_ids = hash_ids.difference( existing_hash_ids )
        
        if len( valid_hash_ids ) > 0:
            
            valid_rows = [ ( hash_id, timestamp ) for ( hash_id, timestamp ) in rows if hash_id in valid_hash_ids ]
            
            # insert the files
            
            self._c.executemany( 'INSERT OR IGNORE INTO current_files VALUES ( ?, ?, ? );', ( ( service_id, hash_id, timestamp ) for ( hash_id, timestamp ) in valid_rows ) )
            
            self._c.executemany( 'DELETE FROM file_transfers WHERE service_id = ? AND hash_id = ?;', ( ( service_id, hash_id ) for hash_id in valid_hash_ids ) )
            
            info = list( self._ExecuteManySelectSingleParam( 'SELECT hash_id, size, mime FROM files_info WHERE hash_id = ?;', valid_hash_ids ) )
            
            num_files = len( valid_hash_ids )
            delta_size = sum( ( size for ( hash_id, size, mime ) in info ) )
            num_inbox = len( valid_hash_ids.intersection( self._inbox_hash_ids ) )
            
            service_info_updates = []
            
            service_info_updates.append( ( delta_size, service_id, HC.SERVICE_INFO_TOTAL_SIZE ) )
            service_info_updates.append( ( num_files, service_id, HC.SERVICE_INFO_NUM_FILES ) )
            service_info_updates.append( ( num_inbox, service_id, HC.SERVICE_INFO_NUM_INBOX ) )
            
            select_statement = 'SELECT 1 FROM files_info WHERE mime IN ' + HydrusData.SplayListForDB( HC.SEARCHABLE_MIMES ) + ' AND hash_id = ?;'
            
            num_viewable_files = sum( self._STI( self._ExecuteManySelectSingleParam( select_statement, valid_hash_ids ) ) )
            
            service_info_updates.append( ( num_viewable_files, service_id, HC.SERVICE_INFO_NUM_VIEWABLE_FILES ) )
            
            # now do special stuff
            
            service = self._GetService( service_id )
            
            service_type = service.GetServiceType()
            
            # remove any records of previous deletion
            
            if service_id == self._combined_local_file_service_id or service_type == HC.FILE_REPOSITORY:
                
                self._c.executemany( 'DELETE FROM deleted_files WHERE service_id = ? AND hash_id = ?;', ( ( service_id, hash_id ) for hash_id in valid_hash_ids ) )
                
                num_deleted = self._GetRowCount()
                
                service_info_updates.append( ( -num_deleted, service_id, HC.SERVICE_INFO_NUM_DELETED_FILES ) )
                
            
            # if we are adding to a local file domain, remove any from the trash and add to combined local file service if needed
            
            if service_type == HC.LOCAL_FILE_DOMAIN:
                
                self._DeleteFiles( self._trash_service_id, valid_hash_ids )
                
                self._AddFiles( self._combined_local_file_service_id, valid_rows )
                
            
            # if we track tags for this service, update the a/c cache
            
            if service_type in HC.AUTOCOMPLETE_CACHE_SPECIFIC_FILE_SERVICES:
                
                tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
                
                for tag_service_id in tag_service_ids:
                    
                    self._CacheSpecificMappingsAddFiles( service_id, tag_service_id, valid_hash_ids )
                    
                
            
            # push the service updates, done
            
            self._c.executemany( 'UPDATE service_info SET info = info + ? WHERE service_id = ? AND info_type = ?;', service_info_updates )
            
        
    
    def _AddService( self, service_key, service_type, name, dictionary ):
        
        result = self._c.execute( 'SELECT 1 FROM services WHERE name = ?;', ( name, ) ).fetchone()
        
        while result is not None:
            
            name += str( random.randint( 0, 9 ) )
            
            result = self._c.execute( 'SELECT 1 FROM services WHERE name = ?;', ( name, ) ).fetchone()
            
        
        dictionary_string = dictionary.DumpToString()
        
        self._c.execute( 'INSERT INTO services ( service_key, service_type, name, dictionary_string ) VALUES ( ?, ?, ?, ? );', ( sqlite3.Binary( service_key ), service_type, name, dictionary_string ) )
        
        service_id = self._c.lastrowid
        
        if service_type == HC.COMBINED_TAG:
            
            self._combined_tag_service_id = service_id
            
            self._CacheTagSiblingsLookupGenerate( service_id )
            
        
        if service_type in HC.REPOSITORIES:
            
            repository_updates_table_name = GenerateRepositoryRepositoryUpdatesTableName( service_id )
            
            self._c.execute( 'CREATE TABLE ' + repository_updates_table_name + ' ( update_index INTEGER, hash_id INTEGER, processed INTEGER_BOOLEAN, PRIMARY KEY ( update_index, hash_id ) );' )
            self._CreateIndex( repository_updates_table_name, [ 'hash_id' ] )
            
            ( hash_id_map_table_name, tag_id_map_table_name ) = GenerateRepositoryMasterCacheTableNames( service_id )
            
            self._c.execute( 'CREATE TABLE ' + hash_id_map_table_name + ' ( service_hash_id INTEGER PRIMARY KEY, hash_id INTEGER );' )
            self._c.execute( 'CREATE TABLE ' + tag_id_map_table_name + ' ( service_tag_id INTEGER PRIMARY KEY, tag_id INTEGER );' )
            
        
        if service_type in HC.REAL_TAG_SERVICES:
            
            self._GenerateMappingsTables( service_id )
            
            #
            
            self._CacheTagSiblingsLookupGenerate( service_id )
            
            self._CacheCombinedFilesMappingsGenerate( service_id )
            
            file_service_ids = self._GetServiceIds( HC.AUTOCOMPLETE_CACHE_SPECIFIC_FILE_SERVICES )
            
            for file_service_id in file_service_ids:
                
                self._CacheSpecificMappingsGenerate( file_service_id, service_id )
                
            
        
        if service_type in HC.AUTOCOMPLETE_CACHE_SPECIFIC_FILE_SERVICES:
            
            tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
            for tag_service_id in tag_service_ids:
                
                self._CacheSpecificMappingsGenerate( service_id, tag_service_id )
                
            
        
    
    def _AddTagParents( self, service_id, pairs, make_content_updates = False ):
        
        self._c.executemany( 'DELETE FROM tag_parents WHERE service_id = ? AND child_tag_id = ? AND parent_tag_id = ?;', ( ( service_id, child_tag_id, parent_tag_id ) for ( child_tag_id, parent_tag_id ) in pairs ) )
        self._c.executemany( 'DELETE FROM tag_parent_petitions WHERE service_id = ? AND child_tag_id = ? AND parent_tag_id = ? AND status = ?;', ( ( service_id, child_tag_id, parent_tag_id, HC.CONTENT_STATUS_PENDING ) for ( child_tag_id, parent_tag_id ) in pairs )  )
        
        self._c.executemany( 'INSERT OR IGNORE INTO tag_parents ( service_id, child_tag_id, parent_tag_id, status ) VALUES ( ?, ?, ?, ? );', ( ( service_id, child_tag_id, parent_tag_id, HC.CONTENT_STATUS_CURRENT ) for ( child_tag_id, parent_tag_id ) in pairs ) )
        
        tag_ids = set()
        
        for ( child_tag_id, parent_tag_id ) in pairs:
            
            tag_ids.add( child_tag_id )
            
        
        for tag_id in tag_ids:
            
            self._FillInParents( service_id, tag_id, make_content_updates = make_content_updates )
            
        
    
    def _AddTagSiblings( self, service_id, pairs, make_content_updates = False ):
        
        self._c.executemany( 'DELETE FROM tag_siblings WHERE service_id = ? AND bad_tag_id = ?;', ( ( service_id, bad_tag_id ) for ( bad_tag_id, good_tag_id ) in pairs ) )
        self._c.executemany( 'DELETE FROM tag_sibling_petitions WHERE service_id = ? AND bad_tag_id = ? AND status = ?;', ( ( service_id, bad_tag_id, HC.CONTENT_STATUS_PENDING ) for ( bad_tag_id, good_tag_id ) in pairs ) )
        
        self._c.executemany( 'INSERT OR IGNORE INTO tag_siblings ( service_id, bad_tag_id, good_tag_id, status ) VALUES ( ?, ?, ?, ? );', ( ( service_id, bad_tag_id, good_tag_id, HC.CONTENT_STATUS_CURRENT ) for ( bad_tag_id, good_tag_id ) in pairs ) )
        
        tag_ids = set()
        
        for ( bad_tag_id, good_tag_id ) in pairs:
            
            tag_ids.add( bad_tag_id )
            tag_ids.add( good_tag_id )
            
        
        self._CacheTagSiblingsUpdateChains( service_id, tag_ids )
        
        for tag_id in tag_ids:
            
            self._FillInParents( service_id, tag_id, make_content_updates = make_content_updates )
            
        
    
    def _AnalyzeDueTables( self, maintenance_mode = HC.MAINTENANCE_FORCED, stop_time = None, force_reanalyze = False ):
        
        names_to_analyze = self._GetTableNamesDueAnalysis( force_reanalyze = force_reanalyze )
        
        if len( names_to_analyze ) > 0:
            
            job_key = ClientThreading.JobKey( cancellable = True )
            
            try:
                
                job_key.SetVariable( 'popup_title', 'database maintenance - analyzing' )
                
                self._controller.pub( 'modal_message', job_key )
                
                random.shuffle( names_to_analyze )
                
                for name in names_to_analyze:
                    
                    self._controller.pub( 'splash_set_status_text', 'analyzing ' + name )
                    job_key.SetVariable( 'popup_text_1', 'analyzing ' + name )
                    
                    time.sleep( 0.1 )
                    
                    started = HydrusData.GetNowPrecise()
                    
                    self._AnalyzeTable( name )
                    
                    time_took = HydrusData.GetNowPrecise() - started
                    
                    if time_took > 1:
                        
                        HydrusData.Print( 'Analyzed ' + name + ' in ' + HydrusData.TimeDeltaToPrettyTimeDelta( time_took ) )
                        
                    
                    p1 = HG.client_controller.ShouldStopThisWork( maintenance_mode, stop_time = stop_time )
                    p2 = job_key.IsCancelled()
                    
                    if p1 or p2:
                        
                        break
                        
                    
                
                self._c.execute( 'ANALYZE sqlite_master;' ) # this reloads the current stats into the query planner
                
                job_key.SetVariable( 'popup_text_1', 'done!' )
                
                HydrusData.Print( job_key.ToString() )
                
            finally:
                
                job_key.Finish()
                
                job_key.Delete( 10 )
                
            
        
    
    def _AnalyzeTable( self, name ):
        
        do_it = True
        
        result = self._c.execute( 'SELECT num_rows FROM analyze_timestamps WHERE name = ?;', ( name, ) ).fetchone()
        
        if result is not None:
            
            ( num_rows, ) = result
            
            # if we have previously analyzed a table with some data but the table is now empty, we do not want a new analyze
            
            if num_rows > 0 and self._TableIsEmpty( name ):
                
                do_it = False
                
            
        
        if do_it:
            
            self._c.execute( 'ANALYZE ' + name + ';' )
            
            ( num_rows, ) = self._c.execute( 'SELECT COUNT( * ) FROM ' + name + ';' ).fetchone()
            
        
        self._c.execute( 'DELETE FROM analyze_timestamps WHERE name = ?;', ( name, ) )
        
        self._c.execute( 'INSERT OR IGNORE INTO analyze_timestamps ( name, num_rows, timestamp ) VALUES ( ?, ?, ? );', ( name, num_rows, HydrusData.GetNow() ) )
        
    
    def _ArchiveFiles( self, hash_ids ):
        
        hash_ids = set( hash_ids )
        
        valid_hash_ids = hash_ids.intersection( self._inbox_hash_ids )
        
        if len( valid_hash_ids ) > 0:
            
            self._c.executemany( 'DELETE FROM file_inbox WHERE hash_id = ?;', ( ( hash_id, ) for hash_id in valid_hash_ids ) )
            
            with HydrusDB.TemporaryIntegerTable( self._c, valid_hash_ids, 'hash_id' ) as temp_table_name:
                
                self._AnalyzeTempTable( temp_table_name )
                
                updates = self._c.execute( 'SELECT service_id, COUNT( * ) FROM current_files NATURAL JOIN {} GROUP BY service_id;'.format( temp_table_name ) ).fetchall()
                
                self._c.executemany( 'UPDATE service_info SET info = info - ? WHERE service_id = ? AND info_type = ?;', [ ( count, service_id, HC.SERVICE_INFO_NUM_INBOX ) for ( service_id, count ) in updates ] )
                
            
            self._inbox_hash_ids.difference_update( valid_hash_ids )
            
        
    
    def _AssociateRepositoryUpdateHashes( self, service_key, metadata_slice ):
        
        service_id = self._GetServiceId( service_key )
        
        processed = False
        
        inserts = []
        
        for ( update_index, update_hashes ) in metadata_slice.GetUpdateIndicesAndHashes():
            
            for update_hash in update_hashes:
                
                hash_id = self._GetHashId( update_hash )
                
                inserts.append( ( update_index, hash_id, processed ) )
                
            
        
        repository_updates_table_name = GenerateRepositoryRepositoryUpdatesTableName( service_id )
        
        self._c.executemany( 'INSERT OR IGNORE INTO ' + repository_updates_table_name + ' ( update_index, hash_id, processed ) VALUES ( ?, ?, ? );', inserts )
        
    
    def _Backup( self, path ):
        
        self._CloseDBCursor()
        
        try:
            
            job_key = ClientThreading.JobKey( cancellable = True )
            
            job_key.SetVariable( 'popup_title', 'backing up db' )
            
            self._controller.pub( 'modal_message', job_key )
            
            job_key.SetVariable( 'popup_text_1', 'closing db' )
            
            HydrusPaths.MakeSureDirectoryExists( path )
            
            for filename in self._db_filenames.values():
                
                if job_key.IsCancelled():
                    
                    break
                    
                
                job_key.SetVariable( 'popup_text_1', 'copying ' + filename )
                
                source = os.path.join( self._db_dir, filename )
                dest = os.path.join( path, filename )
                
                HydrusPaths.MirrorFile( source, dest )
                
            
            conf_files = [ 'mpv.conf' ]
            
            for conf_file in conf_files:
                
                source = os.path.join( self._db_dir, conf_file )
                dest = os.path.join( path, conf_file )
                
                if os.path.exists( source ):
                    
                    HydrusPaths.MirrorFile( source, dest )
                    
                
            
            def is_cancelled_hook():
                
                return job_key.IsCancelled()
                
            
            def text_update_hook( text ):
                
                job_key.SetVariable( 'popup_text_1', text )
                
            
            client_files_default = os.path.join( self._db_dir, 'client_files' )
            
            if os.path.exists( client_files_default ):
                
                HydrusPaths.MirrorTree( client_files_default, os.path.join( path, 'client_files' ), text_update_hook = text_update_hook, is_cancelled_hook = is_cancelled_hook )
                
            
        finally:
            
            self._InitDBCursor()
            
            job_key.SetVariable( 'popup_text_1', 'backup complete!' )
            
            job_key.Finish()
            
        
    
    def _CacheCombinedFilesMappingsDrop( self, service_id ):
        
        ac_cache_table_name = GenerateCombinedFilesMappingsCacheTableName( service_id )
        
        self._c.execute( 'DROP TABLE IF EXISTS ' + ac_cache_table_name + ';' )
        
    
    def _CacheCombinedFilesMappingsGenerate( self, service_id ):
        
        ac_cache_table_name = GenerateCombinedFilesMappingsCacheTableName( service_id )
        
        self._c.execute( 'CREATE TABLE ' + ac_cache_table_name + ' ( tag_id INTEGER PRIMARY KEY, current_count INTEGER, pending_count INTEGER );' )
        
        #
        
        ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( service_id )
        
        current_mappings_exist = self._c.execute( 'SELECT 1 FROM ' + current_mappings_table_name + ' LIMIT 1;' ).fetchone() is not None
        pending_mappings_exist = self._c.execute( 'SELECT 1 FROM ' + pending_mappings_table_name + ' LIMIT 1;' ).fetchone() is not None
        
        if current_mappings_exist or pending_mappings_exist:
            
            for group_of_ids in HydrusDB.ReadLargeIdQueryInSeparateChunks( self._c, 'SELECT tag_id FROM tags;', 10000 ):
                
                current_counter = collections.Counter()
                
                if current_mappings_exist:
                    
                    select_statement = 'SELECT tag_id, COUNT( * ) FROM ' + current_mappings_table_name + ' WHERE tag_id = ?;'
                    
                    for ( tag_id, count ) in self._ExecuteManySelectSingleParam( select_statement, group_of_ids ):
                        
                        if count > 0:
                            
                            current_counter[ tag_id ] = count
                            
                        
                    
                
                #
                
                pending_counter = collections.Counter()
                
                if pending_mappings_exist:
                    
                    select_statement = 'SELECT tag_id, COUNT( * ) FROM ' + pending_mappings_table_name + ' WHERE tag_id = ?;'
                    
                    for ( tag_id, count ) in self._ExecuteManySelectSingleParam( select_statement, group_of_ids ):
                        
                        if count > 0:
                            
                            pending_counter[ tag_id ] = count
                            
                        
                    
                
                all_ids_seen = set( current_counter.keys() )
                all_ids_seen.update( pending_counter.keys() )
                
                count_ids = [ ( tag_id, current_counter[ tag_id ], pending_counter[ tag_id ] ) for tag_id in all_ids_seen ]
                
                if len( count_ids ) > 0:
                    
                    self._CacheCombinedFilesMappingsUpdate( service_id, count_ids )
                    
                
            
        
        self._AnalyzeTable( ac_cache_table_name )
        
    
    def _CacheCombinedFilesMappingsGetAutocompleteCounts( self, service_id, tag_ids ):
        
        ac_cache_table_name = GenerateCombinedFilesMappingsCacheTableName( service_id )
        
        select_statement = 'SELECT tag_id, current_count, pending_count FROM ' + ac_cache_table_name + ' WHERE tag_id = ?;'
        
        return list( self._ExecuteManySelectSingleParam( select_statement, tag_ids ) )
        
    
    def _CacheCombinedFilesMappingsUpdate( self, service_id, count_ids ):
        
        ac_cache_table_name = GenerateCombinedFilesMappingsCacheTableName( service_id )
        
        self._c.executemany( 'INSERT OR IGNORE INTO ' + ac_cache_table_name + ' ( tag_id, current_count, pending_count ) VALUES ( ?, ?, ? );', ( ( tag_id, 0, 0 ) for ( tag_id, current_delta, pending_delta ) in count_ids ) )
        
        self._c.executemany( 'UPDATE ' + ac_cache_table_name + ' SET current_count = current_count + ?, pending_count = pending_count + ? WHERE tag_id = ?;', ( ( current_delta, pending_delta, tag_id ) for ( tag_id, current_delta, pending_delta ) in count_ids ) )
        
        self._c.executemany( 'DELETE FROM ' + ac_cache_table_name + ' WHERE tag_id = ? AND current_count = ? AND pending_count = ?;', ( ( tag_id, 0, 0 ) for ( tag_id, current_delta, pending_delta ) in count_ids ) )
        
    
    def _CacheLocalTagIdsGenerate( self ):
        
        self._c.execute( 'DROP TABLE IF EXISTS local_tags_cache;' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.local_tags_cache ( tag_id INTEGER PRIMARY KEY, tag TEXT UNIQUE );' )
        
        tag_ids = set()
        
        tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
        
        for tag_service_id in tag_service_ids:
            
            ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( self._combined_local_file_service_id, tag_service_id )
            
            service_tag_ids = self._STL( self._c.execute( 'SELECT tag_id FROM ' + ac_cache_table_name + ' WHERE current_count > 0;' ) )
            
            tag_ids.update( service_tag_ids )
            
        
        for block_of_tag_ids in HydrusData.SplitListIntoChunks( tag_ids, 1000 ):
            
            self._CacheLocalTagIdsPotentialAdd( block_of_tag_ids )
            
        
        self._AnalyzeTable( 'external_caches.local_tags_cache' )
        
    
    def _CacheLocalTagIdsPotentialAdd( self, tag_ids ):
        
        self._PopulateTagIdsToTagsCache( tag_ids )
        
        self._c.executemany( 'INSERT OR IGNORE INTO local_tags_cache ( tag_id, tag ) VALUES ( ?, ? );', ( ( tag_id, self._tag_ids_to_tags_cache[ tag_id ] ) for tag_id in tag_ids ) )
        
    
    def _CacheLocalTagIdsPotentialDelete( self, tag_ids ):
        
        include_current = True
        include_pending = False
        
        ids_to_count = self._GetAutocompleteCounts( self._combined_tag_service_id, self._combined_local_file_service_id, tag_ids, include_current, include_pending )
        
        useful_tag_ids = [ tag_id for ( tag_id, ( current_min, current_max, pending_min, pending_max ) ) in ids_to_count.items() if current_min > 0 ]
        
        bad_tag_ids = set( tag_ids ).difference( useful_tag_ids )
        
        self._c.executemany( 'DELETE FROM local_tags_cache WHERE tag_id = ?;', ( ( tag_id, ) for tag_id in bad_tag_ids ) )
        
    
    def _CacheRepositoryNormaliseServiceHashId( self, service_id, service_hash_id ):
        
        ( hash_id_map_table_name, tag_id_map_table_name ) = GenerateRepositoryMasterCacheTableNames( service_id )
        
        result = self._c.execute( 'SELECT hash_id FROM ' + hash_id_map_table_name + ' WHERE service_hash_id = ?;', ( service_hash_id, ) ).fetchone()
        
        if result is None:
            
            self._HandleCriticalRepositoryDefinitionError( service_id )
            
        
        ( hash_id, ) = result
        
        return hash_id
        
    
    def _CacheRepositoryNormaliseServiceHashIds( self, service_id, service_hash_ids ):
        
        ( hash_id_map_table_name, tag_id_map_table_name ) = GenerateRepositoryMasterCacheTableNames( service_id )
        
        select_statement = 'SELECT hash_id FROM ' + hash_id_map_table_name + ' WHERE service_hash_id = ?;'
        
        hash_ids = self._STL( self._ExecuteManySelectSingleParam( select_statement, service_hash_ids ) )
        
        if len( hash_ids ) != len( service_hash_ids ):
            
            self._HandleCriticalRepositoryDefinitionError( service_id )
            
        
        return hash_ids
        
    
    def _CacheRepositoryNormaliseServiceTagId( self, service_id, service_tag_id ):
        
        ( hash_id_map_table_name, tag_id_map_table_name ) = GenerateRepositoryMasterCacheTableNames( service_id )
        
        result = self._c.execute( 'SELECT tag_id FROM ' + tag_id_map_table_name + ' WHERE service_tag_id = ?;', ( service_tag_id, ) ).fetchone()
        
        if result is None:
            
            self._HandleCriticalRepositoryDefinitionError( service_id )
            
        
        ( tag_id, ) = result
        
        return tag_id
        
    
    def _CacheRepositoryDrop( self, service_id ):
        
        ( hash_id_map_table_name, tag_id_map_table_name ) = GenerateRepositoryMasterCacheTableNames( service_id )
        
        self._c.execute( 'DROP ' + hash_id_map_table_name )
        self._c.execute( 'DROP ' + tag_id_map_table_name )
        
    
    def _CacheRepositoryGenerate( self, service_id ):
        
        ( hash_id_map_table_name, tag_id_map_table_name ) = GenerateRepositoryMasterCacheTableNames( service_id )
        
        self._c.execute( 'CREATE TABLE ' + hash_id_map_table_name + ' ( service_hash_id INTEGER PRIMARY KEY, hash_id INTEGER );' )
        self._c.execute( 'CREATE TABLE ' + tag_id_map_table_name + ' ( service_tag_id INTEGER PRIMARY KEY, tag_id INTEGER );' )
        
        self._AnalyzeTable( hash_id_map_table_name )
        self._AnalyzeTable( tag_id_map_table_name )
        
    
    def _CacheSpecificMappingsAddFiles( self, file_service_id, tag_service_id, hash_ids ):
        
        ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
        
        self._c.executemany( 'INSERT OR IGNORE INTO ' + cache_files_table_name + ' VALUES ( ? );', ( ( hash_id, ) for hash_id in hash_ids ) )
        
        ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( tag_service_id )
        
        ac_cache_changes = []
        
        for group_of_hash_ids in HydrusData.SplitListIntoChunks( hash_ids, 100 ):
            
            splayed_group_of_hash_ids = HydrusData.SplayListForDB( group_of_hash_ids )
            
            current_mapping_ids_raw = self._c.execute( 'SELECT tag_id, hash_id FROM ' + current_mappings_table_name + ' WHERE hash_id IN ' + splayed_group_of_hash_ids + ';' ).fetchall()
            
            current_mapping_ids_dict = HydrusData.BuildKeyToSetDict( current_mapping_ids_raw )
            
            deleted_mapping_ids_raw = self._c.execute( 'SELECT tag_id, hash_id FROM ' + deleted_mappings_table_name + ' WHERE hash_id IN ' + splayed_group_of_hash_ids + ';' ).fetchall()
            
            deleted_mapping_ids_dict = HydrusData.BuildKeyToSetDict( deleted_mapping_ids_raw )
            
            pending_mapping_ids_raw = self._c.execute( 'SELECT tag_id, hash_id FROM ' + pending_mappings_table_name + ' WHERE hash_id IN ' + splayed_group_of_hash_ids + ';' ).fetchall()
            
            pending_mapping_ids_dict = HydrusData.BuildKeyToSetDict( pending_mapping_ids_raw )
            
            all_ids_seen = set( current_mapping_ids_dict.keys() )
            all_ids_seen.update( deleted_mapping_ids_dict.keys() )
            all_ids_seen.update( pending_mapping_ids_dict.keys() )
            
            for tag_id in all_ids_seen:
                
                current_hash_ids = current_mapping_ids_dict[ tag_id ]
                
                num_current = len( current_hash_ids )
                
                if num_current > 0:
                    
                    self._c.executemany( 'INSERT OR IGNORE INTO ' + cache_current_mappings_table_name + ' ( hash_id, tag_id ) VALUES ( ?, ? );', ( ( hash_id, tag_id ) for hash_id in current_hash_ids ) )
                    
                
                #
                
                deleted_hash_ids = deleted_mapping_ids_dict[ tag_id ]
                
                num_deleted = len( deleted_hash_ids )
                
                if num_deleted > 0:
                    
                    self._c.executemany( 'INSERT OR IGNORE INTO ' + cache_deleted_mappings_table_name + ' ( hash_id, tag_id ) VALUES ( ?, ? );', ( ( hash_id, tag_id ) for hash_id in deleted_hash_ids ) )
                    
                
                #
                
                pending_hash_ids = pending_mapping_ids_dict[ tag_id ]
                
                num_pending = len( pending_hash_ids )
                
                if num_pending > 0:
                    
                    self._c.executemany( 'INSERT OR IGNORE INTO ' + cache_pending_mappings_table_name + ' ( hash_id, tag_id ) VALUES ( ?, ? );', ( ( hash_id, tag_id ) for hash_id in pending_hash_ids ) )
                    
                
                if num_current > 0 or num_pending > 0:
                    
                    ac_cache_changes.append( ( tag_id, num_current, num_pending ) )
                    
                
            
        
        if len( ac_cache_changes ) > 0:
            
            self._c.executemany( 'INSERT OR IGNORE INTO ' + ac_cache_table_name + ' ( tag_id, current_count, pending_count ) VALUES ( ?, ?, ? );', ( ( tag_id, 0, 0 ) for ( tag_id, num_current, num_pending ) in ac_cache_changes ) )
            
            self._c.executemany( 'UPDATE ' + ac_cache_table_name + ' SET current_count = current_count + ?, pending_count = pending_count + ? WHERE tag_id = ?;', ( ( num_current, num_pending, tag_id ) for ( tag_id, num_current, num_pending ) in ac_cache_changes ) )
            
            if file_service_id == self._combined_local_file_service_id:
                
                potential_new_tag_ids = [ tag_id for ( tag_id, num_current, num_pending ) in ac_cache_changes if num_current > 0 ]
                
                self._CacheLocalTagIdsPotentialAdd( potential_new_tag_ids )
                
            
        
    
    def _CacheSpecificMappingsAddMappings( self, file_service_id, tag_service_id, mappings_ids ):
        
        potential_new_tag_ids = []
        
        ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
        
        for ( tag_id, hash_ids ) in mappings_ids:
            
            hash_ids = self._CacheSpecificMappingsFilterHashIds( file_service_id, tag_service_id, hash_ids )
            
            if len( hash_ids ) > 0:
                
                self._c.executemany( 'DELETE FROM ' + cache_pending_mappings_table_name + ' WHERE hash_id = ? AND tag_id = ?;', ( ( hash_id, tag_id ) for hash_id in hash_ids ) )
                
                num_pending_rescinded = self._GetRowCount()
                
                #
                
                self._c.executemany( 'INSERT OR IGNORE INTO ' + cache_current_mappings_table_name + ' ( hash_id, tag_id ) VALUES ( ?, ? );', ( ( hash_id, tag_id ) for hash_id in hash_ids ) )
                
                num_added = self._GetRowCount()
                
                if num_pending_rescinded > 0:
                    
                    potential_new_tag_ids.append( tag_id )
                    
                    self._c.execute( 'UPDATE ' + ac_cache_table_name + ' SET current_count = current_count + ?, pending_count = pending_count - ? WHERE tag_id = ?;', ( num_added, num_pending_rescinded, tag_id ) )
                    
                elif num_added > 0:
                    
                    self._c.execute( 'INSERT OR IGNORE INTO ' + ac_cache_table_name + ' ( tag_id, current_count, pending_count ) VALUES ( ?, ?, ? );', ( tag_id, 0, 0 ) )
                    
                    if self._GetRowCount() > 0:
                        
                        potential_new_tag_ids.append( tag_id )
                        
                    
                    self._c.execute( 'UPDATE ' + ac_cache_table_name + ' SET current_count = current_count + ? WHERE tag_id = ?;', ( num_added, tag_id ) )
                    
                
                #
                
                self._c.executemany( 'DELETE FROM ' + cache_deleted_mappings_table_name + ' WHERE hash_id = ? AND tag_id = ?;', ( ( hash_id, tag_id ) for hash_id in hash_ids ) )
                
            
        
        if file_service_id == self._combined_local_file_service_id and len( potential_new_tag_ids ) > 0:
            
            self._CacheLocalTagIdsPotentialAdd( potential_new_tag_ids )
            
        
    
    def _CacheSpecificMappingsDrop( self, file_service_id, tag_service_id ):
        
        ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
        
        self._c.execute( 'DROP TABLE IF EXISTS ' + cache_files_table_name + ';' )
        
        self._c.execute( 'DROP TABLE IF EXISTS ' + cache_current_mappings_table_name + ';' )
        
        self._c.execute( 'DROP TABLE IF EXISTS ' + cache_deleted_mappings_table_name + ';' )
        
        self._c.execute( 'DROP TABLE IF EXISTS ' + cache_pending_mappings_table_name + ';' )
        
        self._c.execute( 'DROP TABLE IF EXISTS ' + ac_cache_table_name + ';' )
        
    
    def _CacheSpecificMappingsDeleteFiles( self, file_service_id, tag_service_id, hash_ids ):
        
        ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
        
        self._c.executemany( 'DELETE FROM ' + cache_files_table_name + ' WHERE hash_id = ?;', ( ( hash_id, ) for hash_id in hash_ids ) )
        
        ac_cache_changes = []
        
        for group_of_hash_ids in HydrusData.SplitListIntoChunks( hash_ids, 100 ):
            
            splayed_group_of_hash_ids = HydrusData.SplayListForDB( group_of_hash_ids )
            
            current_mapping_ids_raw = self._c.execute( 'SELECT tag_id, hash_id FROM ' + cache_current_mappings_table_name + ' WHERE hash_id IN ' + splayed_group_of_hash_ids + ';' ).fetchall()
            
            current_mapping_ids_dict = HydrusData.BuildKeyToSetDict( current_mapping_ids_raw )
            
            deleted_mapping_ids_raw = self._c.execute( 'SELECT tag_id, hash_id FROM ' + cache_deleted_mappings_table_name + ' WHERE hash_id IN ' + splayed_group_of_hash_ids + ';' ).fetchall()
            
            deleted_mapping_ids_dict = HydrusData.BuildKeyToSetDict( deleted_mapping_ids_raw )
            
            pending_mapping_ids_raw = self._c.execute( 'SELECT tag_id, hash_id FROM ' + cache_pending_mappings_table_name + ' WHERE hash_id IN ' + splayed_group_of_hash_ids + ';' ).fetchall()
            
            pending_mapping_ids_dict = HydrusData.BuildKeyToSetDict( pending_mapping_ids_raw )
            
            all_ids_seen = set( current_mapping_ids_dict.keys() )
            all_ids_seen.update( deleted_mapping_ids_dict.keys() )
            all_ids_seen.update( pending_mapping_ids_dict.keys() )
            
            for tag_id in all_ids_seen:
                
                current_hash_ids = current_mapping_ids_dict[ tag_id ]
                
                num_current = len( current_hash_ids )
                
                if num_current > 0:
                    
                    self._c.executemany( 'DELETE FROM ' + cache_current_mappings_table_name + ' WHERE tag_id = ? AND hash_id = ?;', ( ( tag_id, hash_id ) for hash_id in current_hash_ids ) )
                    
                
                #
                
                deleted_hash_ids = deleted_mapping_ids_dict[ tag_id ]
                
                num_deleted = len( deleted_hash_ids )
                
                if num_deleted > 0:
                    
                    self._c.executemany( 'DELETE FROM ' + cache_deleted_mappings_table_name + ' WHERE tag_id = ? AND hash_id = ?;', ( ( tag_id, hash_id ) for hash_id in deleted_hash_ids ) )
                    
                
                #
                
                pending_hash_ids = pending_mapping_ids_dict[ tag_id ]
                
                num_pending = len( pending_hash_ids )
                
                if num_pending > 0:
                    
                    self._c.executemany( 'DELETE FROM ' + cache_pending_mappings_table_name + ' WHERE tag_id = ? AND hash_id = ?;', ( ( tag_id, hash_id ) for hash_id in pending_hash_ids ) )
                    
                
                ac_cache_changes.append( ( tag_id, num_current, num_pending ) )
                
            
        
        if len( ac_cache_changes ) > 0:
            
            self._c.executemany( 'UPDATE ' + ac_cache_table_name + ' SET current_count = current_count - ?, pending_count = pending_count - ? WHERE tag_id = ?;', ( ( num_current, num_pending, tag_id ) for ( tag_id, num_current, num_pending ) in ac_cache_changes ) )
            
            self._c.executemany( 'DELETE FROM ' + ac_cache_table_name + ' WHERE tag_id = ? AND current_count = ? AND pending_count = ?;', ( ( tag_id, 0, 0 ) for ( tag_id, num_current, num_pending ) in ac_cache_changes ) )
            
            if file_service_id == self._combined_local_file_service_id:
                
                potential_deleted_tag_ids = [ tag_id for ( tag_id, num_current, num_pending ) in ac_cache_changes if num_current > 0 ]
                
                self._CacheLocalTagIdsPotentialDelete( potential_deleted_tag_ids )
                
            
        
    
    def _CacheSpecificMappingsDeleteMappings( self, file_service_id, tag_service_id, mappings_ids ):
        
        deleted_tag_ids = []
        
        ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
        
        for ( tag_id, hash_ids ) in mappings_ids:
            
            hash_ids = self._CacheSpecificMappingsFilterHashIds( file_service_id, tag_service_id, hash_ids )
            
            if len( hash_ids ) > 0:
                
                self._c.executemany( 'DELETE FROM ' + cache_current_mappings_table_name + ' WHERE hash_id = ? AND tag_id = ?;', ( ( hash_id, tag_id ) for hash_id in hash_ids ) )
                
                num_deleted = self._GetRowCount()
                
                if num_deleted > 0:
                    
                    self._c.execute( 'UPDATE ' + ac_cache_table_name + ' SET current_count = current_count - ? WHERE tag_id = ?;', ( num_deleted, tag_id ) )
                    
                    self._c.execute( 'DELETE FROM ' + ac_cache_table_name + ' WHERE tag_id = ? AND current_count = ? AND pending_count = ?;', ( tag_id, 0, 0 ) )
                    
                    if self._GetRowCount() > 0:
                        
                        deleted_tag_ids.append( tag_id )
                        
                    
                
                #
                
                self._c.executemany( 'INSERT OR IGNORE INTO ' + cache_deleted_mappings_table_name + ' ( hash_id, tag_id ) VALUES ( ?, ? );', ( ( hash_id, tag_id ) for hash_id in hash_ids ) )
                
            
        
        if file_service_id == self._combined_local_file_service_id and len( deleted_tag_ids ) > 0:
            
            self._CacheLocalTagIdsPotentialDelete( deleted_tag_ids )
            
        
    
    def _CacheSpecificMappingsFilterHashIds( self, file_service_id, tag_service_id, hash_ids ):
        
        ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
        
        select_statement = 'SELECT hash_id FROM ' + cache_files_table_name + ' WHERE hash_id = ?;'
        
        return self._STL( self._ExecuteManySelectSingleParam( select_statement, hash_ids ) )
        
    
    def _CacheSpecificMappingsGenerate( self, file_service_id, tag_service_id ):
        
        ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
        
        self._c.execute( 'CREATE TABLE ' + cache_files_table_name + ' ( hash_id INTEGER PRIMARY KEY );' )
        
        self._c.execute( 'CREATE TABLE ' + cache_current_mappings_table_name + ' ( hash_id INTEGER, tag_id INTEGER, PRIMARY KEY ( hash_id, tag_id ) ) WITHOUT ROWID;' )
        
        self._c.execute( 'CREATE TABLE ' + cache_deleted_mappings_table_name + ' ( hash_id INTEGER, tag_id INTEGER, PRIMARY KEY ( hash_id, tag_id ) ) WITHOUT ROWID;' )
        
        self._c.execute( 'CREATE TABLE ' + cache_pending_mappings_table_name + ' ( hash_id INTEGER, tag_id INTEGER, PRIMARY KEY ( hash_id, tag_id ) ) WITHOUT ROWID;' )
        
        self._c.execute( 'CREATE TABLE ' + ac_cache_table_name + ' ( tag_id INTEGER PRIMARY KEY, current_count INTEGER, pending_count INTEGER );' )
        
        #
        
        select_statement = 'SELECT hash_id FROM current_files WHERE service_id = {};'.format( file_service_id )
        
        for group_of_hash_ids in HydrusDB.ReadLargeIdQueryInSeparateChunks( self._c, select_statement, 10000 ):
            
            self._CacheSpecificMappingsAddFiles( file_service_id, tag_service_id, group_of_hash_ids )
            
        
        self._CreateIndex( cache_current_mappings_table_name, [ 'tag_id', 'hash_id' ], unique = True )
        self._CreateIndex( cache_deleted_mappings_table_name, [ 'tag_id', 'hash_id' ], unique = True )
        self._CreateIndex( cache_pending_mappings_table_name, [ 'tag_id', 'hash_id' ], unique = True )
        
        self._AnalyzeTable( cache_files_table_name )
        self._AnalyzeTable( cache_current_mappings_table_name )
        self._AnalyzeTable( cache_deleted_mappings_table_name )
        self._AnalyzeTable( cache_pending_mappings_table_name )
        self._AnalyzeTable( ac_cache_table_name )
        
    
    def _CacheSpecificMappingsGetAutocompleteCounts( self, file_service_id, tag_service_id, tag_ids ):
        
        ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
        
        select_statement = 'SELECT tag_id, current_count, pending_count FROM ' + ac_cache_table_name + ' WHERE tag_id = ?;'
        
        return list( self._ExecuteManySelectSingleParam( select_statement, tag_ids ) )
        
    
    def _CacheSpecificMappingsPendMappings( self, file_service_id, tag_service_id, mappings_ids ):
        
        ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
        
        for ( tag_id, hash_ids ) in mappings_ids:
            
            hash_ids = self._CacheSpecificMappingsFilterHashIds( file_service_id, tag_service_id, hash_ids )
            
            if len( hash_ids ) > 0:
                
                self._c.executemany( 'INSERT OR IGNORE INTO ' + cache_pending_mappings_table_name + ' ( hash_id, tag_id ) VALUES ( ?, ? );', ( ( hash_id, tag_id ) for hash_id in hash_ids ) )
                
                num_added = self._GetRowCount()
                
                if num_added > 0:
                    
                    self._c.execute( 'INSERT OR IGNORE INTO ' + ac_cache_table_name + ' ( tag_id, current_count, pending_count ) VALUES ( ?, ?, ? );', ( tag_id, 0, 0 ) )
                    
                    self._c.execute( 'UPDATE ' + ac_cache_table_name + ' SET pending_count = pending_count + ? WHERE tag_id = ?;', ( num_added, tag_id ) )
                    
                
                
            
        
    
    def _CacheSpecificMappingsRescindPendingMappings( self, file_service_id, tag_service_id, mappings_ids ):
        
        ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
        
        for ( tag_id, hash_ids ) in mappings_ids:
            
            hash_ids = self._CacheSpecificMappingsFilterHashIds( file_service_id, tag_service_id, hash_ids )
            
            if len( hash_ids ) > 0:
                
                self._c.executemany( 'DELETE FROM ' + cache_pending_mappings_table_name + ' WHERE hash_id = ? AND tag_id = ?;', ( ( hash_id, tag_id ) for hash_id in hash_ids ) )
                
                num_deleted = self._GetRowCount()
                
                if num_deleted > 0:
                    
                    self._c.execute( 'UPDATE ' + ac_cache_table_name + ' SET pending_count = pending_count - ? WHERE tag_id = ?;', ( num_deleted, tag_id ) )
                    
                    self._c.execute( 'DELETE FROM ' + ac_cache_table_name + ' WHERE tag_id = ? AND current_count = ? AND pending_count = ?;', ( tag_id, 0, 0 ) )
                    
                
            
        
    
    def _CacheTagSiblingsLookupDrop( self, tag_service_id ):
        
        cache_tag_siblings_lookup_table_name = GenerateTagSiblingsLookupCacheTableName( tag_service_id )
        
        self._c.execute( 'DROP TABLE IF EXISTS {};'.format( cache_tag_siblings_lookup_table_name ) )
        
    
    def _CacheTagSiblingsLookupGenerate( self, tag_service_id ):
        
        cache_tag_siblings_lookup_table_name = GenerateTagSiblingsLookupCacheTableName( tag_service_id )
        
        self._c.execute( 'CREATE TABLE {} ( bad_tag_id INTEGER PRIMARY KEY, ideal_tag_id INTEGER );'.format( cache_tag_siblings_lookup_table_name ) )
        
        #
        
        if tag_service_id == self._combined_tag_service_id:
            
            # until we have the nice system here, we'll do the old-fashioned local, then remote precedence
            
            search_tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
        else:
            
            search_tag_service_ids = [ tag_service_id ]
            
        
        tss = ClientTags.TagSiblingsStructure()
        
        for search_tag_service_id in search_tag_service_ids:
            
            for ( bad_tag_id, good_tag_id ) in self._c.execute( 'SELECT bad_tag_id, good_tag_id FROM tag_siblings WHERE service_id = ? AND status = ?;', ( search_tag_service_id, HC.CONTENT_STATUS_CURRENT ) ):
                
                tss.AddPair( bad_tag_id, good_tag_id )
                
            
        
        for search_tag_service_id in search_tag_service_ids:
            
            for ( bad_tag_id, good_tag_id ) in self._c.execute( 'SELECT bad_tag_id, good_tag_id FROM tag_sibling_petitions WHERE service_id = ? AND status = ?;', ( search_tag_service_id, HC.CONTENT_STATUS_PENDING ) ):
                
                tss.AddPair( bad_tag_id, good_tag_id )
                
            
        
        self._c.executemany( 'INSERT OR IGNORE INTO {} ( bad_tag_id, ideal_tag_id ) VALUES ( ?, ? );'.format( cache_tag_siblings_lookup_table_name ), tss.GetBadTagsToIdealTags().items() )
        
        self._CreateIndex( cache_tag_siblings_lookup_table_name, [ 'ideal_tag_id' ] )
        
        self._AnalyzeTable( cache_tag_siblings_lookup_table_name )
        
    
    def _CacheTagSiblingsLookupGetAdditionalSiblings( self, tag_service_id, tag_ids ):
        
        cache_tag_siblings_lookup_table_name = GenerateTagSiblingsLookupCacheTableName( tag_service_id )
        
        sibling_tag_ids = set()
        
        with HydrusDB.TemporaryIntegerTable( self._c, tag_ids, 'tag_id' ) as temp_table_name:
            
            self._AnalyzeTempTable( temp_table_name )
            
            sibling_tag_ids.update( self._STI( self._c.execute( 'SELECT bad_tag_id FROM {}, {} ON ( ideal_tag_id = tag_id );'.format( cache_tag_siblings_lookup_table_name, temp_table_name ) ) ) )
            sibling_tag_ids.update( self._STI( self._c.execute( 'SELECT ideal_tag_id FROM {}, {} ON ( bad_tag_id = tag_id );'.format( cache_tag_siblings_lookup_table_name, temp_table_name ) ) ) )
            
        
        sibling_tag_ids.difference_update( tag_ids )
        
        return sibling_tag_ids
        
    
    def _CacheTagSiblingsUpdateChains( self, tag_service_id, tag_ids, regenerate_existing_entry = True ):
        
        cache_tag_siblings_lookup_table_name = GenerateTagSiblingsLookupCacheTableName( tag_service_id )
        
        tag_ids = set( tag_ids )
        
        tag_ids.update( self._CacheTagSiblingsLookupGetAdditionalSiblings( tag_service_id, tag_ids ) )
        
        if regenerate_existing_entry:
            
            tag_ids_to_do = tag_ids
            
        else:
            
            tag_ids_to_do = set()
            
            for tag_id in tag_ids:
                
                result = self._c.execute( 'SELECT 1 FROM {} WHERE bad_tag_id = ? OR ideal_tag_id = ?;'.format( cache_tag_siblings_lookup_table_name ), ( tag_id, tag_id ) ).fetchone()
                
                no_entry_yet = result is None
                
                if no_entry_yet:
                    
                    tag_ids_to_do.add( tag_id )
                    
                
            
            if len( tag_ids_to_do ) == 0:
                
                return
                
            
        
        self._c.executemany( 'DELETE FROM {} WHERE bad_tag_id = ? OR ideal_tag_id = ?;'.format( cache_tag_siblings_lookup_table_name ), ( ( tag_id, tag_id ) for tag_id in tag_ids_to_do ) )
        
        if tag_service_id == self._combined_tag_service_id:
            
            # until we have the nice system here, we'll do the old-fashioned local, then remote precedence
            
            search_tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
        else:
            
            search_tag_service_ids = [ tag_service_id ]
            
        
        tss = ClientTags.TagSiblingsStructure()
        
        for search_tag_service_id in search_tag_service_ids:
            
            for tag_id in tag_ids_to_do:
                
                some_pairs = self._c.execute( 'SELECT bad_tag_id, good_tag_id FROM tag_siblings WHERE service_id = ? AND ( bad_tag_id = ? OR good_tag_id = ? ) AND status = ?;', ( search_tag_service_id, tag_id, tag_id, HC.CONTENT_STATUS_CURRENT ) ).fetchall()
                
                for ( bad_tag_id, good_tag_id ) in some_pairs:
                    
                    tss.AddPair( bad_tag_id, good_tag_id )
                    
                
            
        
        for search_tag_service_id in search_tag_service_ids:
            
            for tag_id in tag_ids_to_do:
                
                some_pairs = self._c.execute( 'SELECT bad_tag_id, good_tag_id FROM tag_sibling_petitions WHERE service_id = ? AND ( bad_tag_id = ? OR good_tag_id = ? ) AND status = ?;', ( search_tag_service_id, tag_id, tag_id, HC.CONTENT_STATUS_PENDING ) ).fetchall()
                
                for ( bad_tag_id, good_tag_id ) in some_pairs:
                    
                    tss.AddPair( bad_tag_id, good_tag_id )
                    
                
            
        
        self._c.executemany( 'INSERT OR IGNORE INTO {} ( bad_tag_id, ideal_tag_id ) VALUES ( ?, ? );'.format( cache_tag_siblings_lookup_table_name ), tss.GetBadTagsToIdealTags().items() )
        
        if tag_service_id != self._combined_tag_service_id:
            
            self._CacheTagSiblingsUpdateChains( self._combined_tag_service_id, tag_ids, regenerate_existing_entry = regenerate_existing_entry )
            
        
    
    def _CheckDBIntegrity( self ):
        
        prefix_string = 'checking db integrity: '
        
        job_key = ClientThreading.JobKey( cancellable = True )
        
        try:
            
            job_key.SetVariable( 'popup_title', prefix_string + 'preparing' )
            
            self._controller.pub( 'modal_message', job_key )
            
            num_errors = 0
            
            job_key.SetVariable( 'popup_title', prefix_string + 'running' )
            job_key.SetVariable( 'popup_text_1', 'errors found so far: ' + HydrusData.ToHumanInt( num_errors ) )
            
            db_names = [ name for ( index, name, path ) in self._c.execute( 'PRAGMA database_list;' ) if name not in ( 'mem', 'temp', 'durable_temp' ) ]
            
            for db_name in db_names:
                
                for ( text, ) in self._c.execute( 'PRAGMA ' + db_name + '.integrity_check;' ):
                    
                    ( i_paused, should_quit ) = job_key.WaitIfNeeded()
                    
                    if should_quit:
                        
                        job_key.SetVariable( 'popup_title', prefix_string + 'cancelled' )
                        job_key.SetVariable( 'popup_text_1', 'errors found: ' + HydrusData.ToHumanInt( num_errors ) )
                        
                        return
                        
                    
                    if text != 'ok':
                        
                        if num_errors == 0:
                            
                            HydrusData.Print( 'During a db integrity check, these errors were discovered:' )
                            
                        
                        HydrusData.Print( text )
                        
                        num_errors += 1
                        
                    
                    job_key.SetVariable( 'popup_text_1', 'errors found so far: ' + HydrusData.ToHumanInt( num_errors ) )
                    
                
            
        finally:
            
            job_key.SetVariable( 'popup_title', prefix_string + 'completed' )
            job_key.SetVariable( 'popup_text_1', 'errors found: ' + HydrusData.ToHumanInt( num_errors ) )
            
            HydrusData.Print( job_key.ToString() )
            
            job_key.Finish()
            
        
    
    def _CleanUpCaches( self ):
        
        self._subscriptions_cache = {}
        self._service_cache = {}
        
    
    def _ClearOrphanFileRecords( self ):
        
        job_key = ClientThreading.JobKey( cancellable = True )
        
        job_key.SetVariable( 'popup_title', 'clear orphan file records' )
        
        self._controller.pub( 'modal_message', job_key )
        
        try:
            
            job_key.SetVariable( 'popup_text_1', 'looking for orphans' )
            
            local_file_service_ids = self._GetServiceIds( ( HC.LOCAL_FILE_DOMAIN, HC.LOCAL_FILE_TRASH_DOMAIN ) )
            
            local_hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM current_files WHERE service_id IN ' + HydrusData.SplayListForDB( local_file_service_ids ) + ';' ) )
            
            combined_local_file_service_id = self._GetServiceId( CC.COMBINED_LOCAL_FILE_SERVICE_KEY )
            
            combined_local_hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM current_files WHERE service_id = ?;', ( combined_local_file_service_id, ) ) )
            
            in_local_not_in_combined = local_hash_ids.difference( combined_local_hash_ids )
            in_combined_not_in_local = combined_local_hash_ids.difference( local_hash_ids )
            
            if job_key.IsCancelled():
                
                return
                
            
            job_key.SetVariable( 'popup_text_1', 'deleting orphans' )
            
            if len( in_local_not_in_combined ) > 0:
                
                # these files were deleted from the umbrella service without being cleared from a specific file domain
                # they are most likely deleted from disk
                # pushing the 'delete combined' call will flush from the local services as well
                
                self._DeleteFiles( self._combined_local_file_service_id, in_local_not_in_combined )
                
                for hash_id in in_local_not_in_combined:
                    
                    self._PHashesDeleteFile( hash_id )
                    
                
                HydrusData.ShowText( 'Found and deleted ' + HydrusData.ToHumanInt( len( in_local_not_in_combined ) ) + ' local domain orphan file records.' )
                
            
            if job_key.IsCancelled():
                
                return
                
            
            if len( in_combined_not_in_local ) > 0:
                
                # these files were deleted from all specific services but not from the combined service
                # I have only ever seen one example of this and am not sure how it happened
                # in any case, the same 'delete combined' call will do the job
                
                self._DeleteFiles( self._combined_local_file_service_id, in_combined_not_in_local )
                
                for hash_id in in_combined_not_in_local:
                    
                    self._PHashesDeleteFile( hash_id )
                    
                
                HydrusData.ShowText( 'Found and deleted ' + HydrusData.ToHumanInt( len( in_combined_not_in_local ) ) + ' combined domain orphan file records.' )
                
            
            if len( in_local_not_in_combined ) == 0 and len( in_combined_not_in_local ) == 0:
                
                HydrusData.ShowText( 'No orphan file records found!' )
                
            
        finally:
            
            job_key.SetVariable( 'popup_text_1', 'done!' )
            
            job_key.Finish()
            
        
    
    def _ClearOrphanTables( self ):
        
        service_ids = self._STL( self._c.execute( 'SELECT service_id FROM services;' ) )
        
        table_prefixes = []
        
        table_prefixes.append( 'repository_hash_id_map_' )
        table_prefixes.append( 'repository_tag_id_map_' )
        table_prefixes.append( 'repository_updates_' )
        
        good_table_names = set()
        
        for service_id in service_ids:
            
            suffix = str( service_id )
            
            for table_prefix in table_prefixes:
                
                good_table_names.add( table_prefix + suffix )
                
            
        
        existing_table_names = set()
        
        existing_table_names.update( self._STS( self._c.execute( 'SELECT name FROM sqlite_master WHERE type = ?;', ( 'table', ) ) ) )
        existing_table_names.update( self._STS( self._c.execute( 'SELECT name FROM external_master.sqlite_master WHERE type = ?;', ( 'table', ) ) ) )
        
        existing_table_names = { name for name in existing_table_names if True in ( name.startswith( table_prefix ) for table_prefix in table_prefixes ) }
        
        surplus_table_names = sorted( existing_table_names.difference( good_table_names ) )
        
        for table_name in surplus_table_names:
            
            HydrusData.ShowText( 'Dropping ' + table_name )
            
            self._c.execute( 'DROP table ' + table_name + ';' )
            
        
    
    def _CreateDB( self ):
        
        client_files_default = os.path.join( self._db_dir, 'client_files' )
        
        HydrusPaths.MakeSureDirectoryExists( client_files_default )
        
        self._c.execute( 'CREATE TABLE services ( service_id INTEGER PRIMARY KEY AUTOINCREMENT, service_key BLOB_BYTES UNIQUE, service_type INTEGER, name TEXT, dictionary_string TEXT );' )
        
        # main
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS alternate_file_groups ( alternates_group_id INTEGER PRIMARY KEY );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS alternate_file_group_members ( alternates_group_id INTEGER, media_id INTEGER UNIQUE, PRIMARY KEY ( alternates_group_id, media_id ) );' )
        
        self._c.execute( 'CREATE TABLE analyze_timestamps ( name TEXT, num_rows INTEGER, timestamp INTEGER );' )
        
        self._c.execute( 'CREATE TABLE client_files_locations ( prefix TEXT, location TEXT );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS ideal_client_files_locations ( location TEXT, weight INTEGER );' )
        self._c.execute( 'CREATE TABLE IF NOT EXISTS ideal_thumbnail_override_location ( location TEXT );' )
        
        self._c.execute( 'CREATE TABLE current_files ( service_id INTEGER REFERENCES services ON DELETE CASCADE, hash_id INTEGER, timestamp INTEGER, PRIMARY KEY ( service_id, hash_id ) );' )
        self._CreateIndex( 'current_files', [ 'timestamp' ] )
        
        self._c.execute( 'CREATE TABLE deleted_files ( service_id INTEGER REFERENCES services ON DELETE CASCADE, hash_id INTEGER, PRIMARY KEY ( service_id, hash_id ) );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS duplicate_files ( media_id INTEGER PRIMARY KEY, king_hash_id INTEGER UNIQUE );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS duplicate_file_members ( media_id INTEGER, hash_id INTEGER UNIQUE, PRIMARY KEY ( media_id, hash_id ) );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS duplicate_false_positives ( smaller_alternates_group_id INTEGER, larger_alternates_group_id INTEGER, PRIMARY KEY ( smaller_alternates_group_id, larger_alternates_group_id ) );' )
        self._CreateIndex( 'duplicate_false_positives', [ 'larger_alternates_group_id', 'smaller_alternates_group_id' ], unique = True )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS potential_duplicate_pairs ( smaller_media_id INTEGER, larger_media_id INTEGER, distance INTEGER, PRIMARY KEY ( smaller_media_id, larger_media_id ) );' )
        self._CreateIndex( 'potential_duplicate_pairs', [ 'larger_media_id', 'smaller_media_id' ], unique = True )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS confirmed_alternate_pairs ( smaller_media_id INTEGER, larger_media_id INTEGER, PRIMARY KEY ( smaller_media_id, larger_media_id ) );' )
        self._CreateIndex( 'confirmed_alternate_pairs', [ 'larger_media_id', 'smaller_media_id' ], unique = True )
        
        self._c.execute( 'CREATE TABLE local_file_deletion_reasons ( hash_id INTEGER PRIMARY KEY, reason_id INTEGER );' )
        
        self._c.execute( 'CREATE TABLE file_inbox ( hash_id INTEGER PRIMARY KEY );' )
        
        self._c.execute( 'CREATE TABLE files_info ( hash_id INTEGER PRIMARY KEY, size INTEGER, mime INTEGER, width INTEGER, height INTEGER, duration INTEGER, num_frames INTEGER, has_audio INTEGER_BOOLEAN, num_words INTEGER );' )
        self._CreateIndex( 'files_info', [ 'size' ] )
        self._CreateIndex( 'files_info', [ 'mime' ] )
        self._CreateIndex( 'files_info', [ 'width' ] )
        self._CreateIndex( 'files_info', [ 'height' ] )
        self._CreateIndex( 'files_info', [ 'duration' ] )
        self._CreateIndex( 'files_info', [ 'num_frames' ] )
        
        self._c.execute( 'CREATE TABLE file_notes ( hash_id INTEGER, name_id INTEGER, note_id INTEGER, PRIMARY KEY ( hash_id, name_id ) );' )
        self._CreateIndex( 'file_notes', [ 'note_id' ] )
        
        self._c.execute( 'CREATE TABLE file_transfers ( service_id INTEGER REFERENCES services ON DELETE CASCADE, hash_id INTEGER, PRIMARY KEY ( service_id, hash_id ) );' )
        self._CreateIndex( 'file_transfers', [ 'hash_id' ] )
        
        self._c.execute( 'CREATE TABLE file_petitions ( service_id INTEGER REFERENCES services ON DELETE CASCADE, hash_id INTEGER, reason_id INTEGER, PRIMARY KEY ( service_id, hash_id, reason_id ) );' )
        self._CreateIndex( 'file_petitions', [ 'hash_id' ] )
        
        self._c.execute( 'CREATE TABLE json_dict ( name TEXT PRIMARY KEY, dump BLOB_BYTES );' )
        self._c.execute( 'CREATE TABLE json_dumps ( dump_type INTEGER PRIMARY KEY, version INTEGER, dump BLOB_BYTES );' )
        self._c.execute( 'CREATE TABLE json_dumps_named ( dump_type INTEGER, dump_name TEXT, version INTEGER, timestamp INTEGER, dump BLOB_BYTES, PRIMARY KEY ( dump_type, dump_name, timestamp ) );' )
        
        self._c.execute( 'CREATE TABLE last_shutdown_work_time ( last_shutdown_work_time INTEGER );' )
        
        self._c.execute( 'CREATE TABLE local_ratings ( service_id INTEGER REFERENCES services ON DELETE CASCADE, hash_id INTEGER, rating REAL, PRIMARY KEY ( service_id, hash_id ) );' )
        self._CreateIndex( 'local_ratings', [ 'hash_id' ] )
        self._CreateIndex( 'local_ratings', [ 'rating' ] )
        
        self._c.execute( 'CREATE TABLE file_modified_timestamps ( hash_id INTEGER PRIMARY KEY, file_modified_timestamp INTEGER );' )
        self._CreateIndex( 'file_modified_timestamps', [ 'file_modified_timestamp' ] )
        
        self._c.execute( 'CREATE TABLE options ( options TEXT_YAML );', )
        
        self._c.execute( 'CREATE TABLE recent_tags ( service_id INTEGER REFERENCES services ON DELETE CASCADE, tag_id INTEGER, timestamp INTEGER, PRIMARY KEY ( service_id, tag_id ) );' )
        
        self._c.execute( 'CREATE TABLE remote_ratings ( service_id INTEGER REFERENCES services ON DELETE CASCADE, hash_id INTEGER, count INTEGER, rating REAL, score REAL, PRIMARY KEY ( service_id, hash_id ) );' )
        self._CreateIndex( 'remote_ratings', [ 'hash_id' ] )
        self._CreateIndex( 'remote_ratings', [ 'rating' ] )
        self._CreateIndex( 'remote_ratings', [ 'score' ] )
        
        self._c.execute( 'CREATE TABLE remote_thumbnails ( service_id INTEGER, hash_id INTEGER, PRIMARY KEY( service_id, hash_id ) );' )
        
        self._c.execute( 'CREATE TABLE service_filenames ( service_id INTEGER REFERENCES services ON DELETE CASCADE, hash_id INTEGER, filename TEXT, PRIMARY KEY ( service_id, hash_id ) );' )
        self._c.execute( 'CREATE TABLE service_directories ( service_id INTEGER REFERENCES services ON DELETE CASCADE, directory_id INTEGER, num_files INTEGER, total_size INTEGER, note TEXT, PRIMARY KEY ( service_id, directory_id ) );' )
        self._c.execute( 'CREATE TABLE service_directory_file_map ( service_id INTEGER REFERENCES services ON DELETE CASCADE, directory_id INTEGER, hash_id INTEGER, PRIMARY KEY ( service_id, directory_id, hash_id ) );' )
        
        self._c.execute( 'CREATE TABLE service_info ( service_id INTEGER REFERENCES services ON DELETE CASCADE, info_type INTEGER, info INTEGER, PRIMARY KEY ( service_id, info_type ) );' )
        
        self._c.execute( 'CREATE TABLE statuses ( status_id INTEGER PRIMARY KEY, status TEXT UNIQUE );' )
        
        self._c.execute( 'CREATE TABLE tag_parents ( service_id INTEGER REFERENCES services ON DELETE CASCADE, child_tag_id INTEGER, parent_tag_id INTEGER, status INTEGER, PRIMARY KEY ( service_id, child_tag_id, parent_tag_id, status ) );' )
        
        self._c.execute( 'CREATE TABLE tag_parent_petitions ( service_id INTEGER REFERENCES services ON DELETE CASCADE, child_tag_id INTEGER, parent_tag_id INTEGER, status INTEGER, reason_id INTEGER, PRIMARY KEY ( service_id, child_tag_id, parent_tag_id, status ) );' )
        
        self._c.execute( 'CREATE TABLE tag_siblings ( service_id INTEGER REFERENCES services ON DELETE CASCADE, bad_tag_id INTEGER, good_tag_id INTEGER, status INTEGER, PRIMARY KEY ( service_id, bad_tag_id, status ) );' )
        
        self._c.execute( 'CREATE TABLE tag_sibling_petitions ( service_id INTEGER REFERENCES services ON DELETE CASCADE, bad_tag_id INTEGER, good_tag_id INTEGER, status INTEGER, reason_id INTEGER, PRIMARY KEY ( service_id, bad_tag_id, status ) );' )
        
        self._c.execute( 'CREATE TABLE url_map ( hash_id INTEGER, url_id INTEGER, PRIMARY KEY ( hash_id, url_id ) );' )
        self._CreateIndex( 'url_map', [ 'url_id' ] )
        
        self._c.execute( 'CREATE TABLE vacuum_timestamps ( name TEXT, timestamp INTEGER );' )
        
        self._c.execute( 'CREATE TABLE file_viewing_stats ( hash_id INTEGER PRIMARY KEY, preview_views INTEGER, preview_viewtime INTEGER, media_views INTEGER, media_viewtime INTEGER );' )
        self._CreateIndex( 'file_viewing_stats', [ 'preview_views' ] )
        self._CreateIndex( 'file_viewing_stats', [ 'preview_viewtime' ] )
        self._CreateIndex( 'file_viewing_stats', [ 'media_views' ] )
        self._CreateIndex( 'file_viewing_stats', [ 'media_viewtime' ] )
        
        self._c.execute( 'CREATE TABLE version ( version INTEGER );' )
        
        self._c.execute( 'CREATE TABLE yaml_dumps ( dump_type INTEGER, dump_name TEXT, dump TEXT_YAML, PRIMARY KEY ( dump_type, dump_name ) );' )
        
        # caches
        
        self._CreateDBCaches()
        
        # master
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.hashes ( hash_id INTEGER PRIMARY KEY, hash BLOB_BYTES UNIQUE );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.labels ( label_id INTEGER PRIMARY KEY, label TEXT UNIQUE );' )
        
        self._c.execute( 'CREATE TABLE external_master.local_hashes ( hash_id INTEGER PRIMARY KEY, md5 BLOB_BYTES, sha1 BLOB_BYTES, sha512 BLOB_BYTES );' )
        self._CreateIndex( 'external_master.local_hashes', [ 'md5' ] )
        self._CreateIndex( 'external_master.local_hashes', [ 'sha1' ] )
        self._CreateIndex( 'external_master.local_hashes', [ 'sha512' ] )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.namespaces ( namespace_id INTEGER PRIMARY KEY, namespace TEXT UNIQUE );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.notes ( note_id INTEGER PRIMARY KEY, note TEXT UNIQUE );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.subtags ( subtag_id INTEGER PRIMARY KEY, subtag TEXT UNIQUE );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.tags ( tag_id INTEGER PRIMARY KEY, namespace_id INTEGER, subtag_id INTEGER );' )
        self._CreateIndex( 'external_master.tags', [ 'subtag_id', 'namespace_id' ] )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.texts ( text_id INTEGER PRIMARY KEY, text TEXT UNIQUE );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.url_domains ( domain_id INTEGER PRIMARY KEY, domain TEXT UNIQUE );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.urls ( url_id INTEGER PRIMARY KEY, domain_id INTEGER, url TEXT UNIQUE );' )
        self._CreateIndex( 'external_master.urls', [ 'domain_id' ] )
        
        # inserts
        
        location = HydrusPaths.ConvertAbsPathToPortablePath( client_files_default )
        
        for prefix in HydrusData.IterateHexPrefixes():
            
            self._c.execute( 'INSERT INTO client_files_locations ( prefix, location ) VALUES ( ?, ? );', ( 'f' + prefix, location ) )
            self._c.execute( 'INSERT INTO client_files_locations ( prefix, location ) VALUES ( ?, ? );', ( 't' + prefix, location ) )
            
        
        self._c.execute( 'INSERT INTO ideal_client_files_locations ( location, weight ) VALUES ( ?, ? );', ( location, 1 ) )
        
        init_service_info = []
        
        init_service_info.append( ( CC.COMBINED_TAG_SERVICE_KEY, HC.COMBINED_TAG, 'all known tags' ) )
        init_service_info.append( ( CC.COMBINED_FILE_SERVICE_KEY, HC.COMBINED_FILE, 'all known files' ) )
        init_service_info.append( ( CC.COMBINED_LOCAL_FILE_SERVICE_KEY, HC.COMBINED_LOCAL_FILE, 'all local files' ) )
        init_service_info.append( ( CC.LOCAL_FILE_SERVICE_KEY, HC.LOCAL_FILE_DOMAIN, 'my files' ) )
        init_service_info.append( ( CC.TRASH_SERVICE_KEY, HC.LOCAL_FILE_TRASH_DOMAIN, 'trash' ) )
        init_service_info.append( ( CC.LOCAL_UPDATE_SERVICE_KEY, HC.LOCAL_FILE_DOMAIN, 'repository updates' ) )
        init_service_info.append( ( CC.DEFAULT_LOCAL_TAG_SERVICE_KEY, HC.LOCAL_TAG, 'my tags' ) )
        init_service_info.append( ( CC.LOCAL_BOORU_SERVICE_KEY, HC.LOCAL_BOORU, 'local booru' ) )
        init_service_info.append( ( CC.LOCAL_NOTES_SERVICE_KEY, HC.LOCAL_NOTES, 'local notes' ) )
        init_service_info.append( ( CC.CLIENT_API_SERVICE_KEY, HC.CLIENT_API_SERVICE, 'client api' ) )
        
        for ( service_key, service_type, name ) in init_service_info:
            
            dictionary = ClientServices.GenerateDefaultServiceDictionary( service_type )
            
            self._AddService( service_key, service_type, name, dictionary )
            
        
        self._c.executemany( 'INSERT INTO yaml_dumps VALUES ( ?, ?, ? );', ( ( YAML_DUMP_ID_IMAGEBOARD, name, imageboards ) for ( name, imageboards ) in ClientDefaults.GetDefaultImageboards() ) )
        
        new_options = ClientOptions.ClientOptions()
        
        new_options.SetSimpleDownloaderFormulae( ClientDefaults.GetDefaultSimpleDownloaderFormulae() )
        
        names_to_tag_filters = {}
        
        tag_filter = ClientTags.TagFilter()
        
        tag_filter.SetRule( 'diaper', CC.FILTER_BLACKLIST )
        tag_filter.SetRule( 'gore', CC.FILTER_BLACKLIST )
        tag_filter.SetRule( 'guro', CC.FILTER_BLACKLIST )
        tag_filter.SetRule( 'scat', CC.FILTER_BLACKLIST )
        tag_filter.SetRule( 'vore', CC.FILTER_BLACKLIST )
        
        names_to_tag_filters[ 'example blacklist' ] = tag_filter
        
        tag_filter = ClientTags.TagFilter()
        
        tag_filter.SetRule( '', CC.FILTER_BLACKLIST )
        tag_filter.SetRule( ':', CC.FILTER_BLACKLIST )
        tag_filter.SetRule( 'series:', CC.FILTER_WHITELIST )
        tag_filter.SetRule( 'creator:', CC.FILTER_WHITELIST )
        tag_filter.SetRule( 'studio:', CC.FILTER_WHITELIST )
        tag_filter.SetRule( 'character:', CC.FILTER_WHITELIST )
        
        names_to_tag_filters[ 'basic namespaces only' ] = tag_filter
        
        tag_filter = ClientTags.TagFilter()
        
        tag_filter.SetRule( ':', CC.FILTER_BLACKLIST )
        tag_filter.SetRule( 'series:', CC.FILTER_WHITELIST )
        tag_filter.SetRule( 'creator:', CC.FILTER_WHITELIST )
        tag_filter.SetRule( 'studio:', CC.FILTER_WHITELIST )
        tag_filter.SetRule( 'character:', CC.FILTER_WHITELIST )
        
        names_to_tag_filters[ 'basic booru tags only' ] = tag_filter
        
        tag_filter = ClientTags.TagFilter()
        
        tag_filter.SetRule( 'title:', CC.FILTER_BLACKLIST )
        tag_filter.SetRule( 'filename:', CC.FILTER_BLACKLIST )
        tag_filter.SetRule( 'source:', CC.FILTER_BLACKLIST )
        tag_filter.SetRule( 'booru:', CC.FILTER_BLACKLIST )
        tag_filter.SetRule( 'url:', CC.FILTER_BLACKLIST )
        
        names_to_tag_filters[ 'exclude long/spammy namespaces' ] = tag_filter
        
        new_options.SetFavouriteTagFilters( names_to_tag_filters )
        
        self._SetJSONDump( new_options )
        
        list_of_shortcuts = ClientDefaults.GetDefaultShortcuts()
        
        for shortcuts in list_of_shortcuts:
            
            self._SetJSONDump( shortcuts )
            
        
        client_api_manager = ClientAPI.APIManager()
        
        self._SetJSONDump( client_api_manager )
        
        bandwidth_manager = ClientNetworkingBandwidth.NetworkBandwidthManager()
        
        ClientDefaults.SetDefaultBandwidthManagerRules( bandwidth_manager )
        
        self._SetJSONDump( bandwidth_manager )
        
        domain_manager = ClientNetworkingDomain.NetworkDomainManager()
        
        ClientDefaults.SetDefaultDomainManagerData( domain_manager )
        
        self._SetJSONDump( domain_manager )
        
        session_manager = ClientNetworkingSessions.NetworkSessionManager()
        
        self._SetJSONDump( session_manager )
        
        login_manager = ClientNetworkingLogin.NetworkLoginManager()
        
        ClientDefaults.SetDefaultLoginManagerScripts( login_manager )
        
        self._SetJSONDump( login_manager )
        
        favourite_search_manager = ClientSearch.FavouriteSearchManager()
        
        ClientDefaults.SetDefaultFavouriteSearchManagerData( favourite_search_manager )
        
        self._SetJSONDump( favourite_search_manager )
        
        tag_display_manager = ClientTags.TagDisplayManager()
        
        self._SetJSONDump( tag_display_manager )
        
        self._c.execute( 'INSERT INTO namespaces ( namespace_id, namespace ) VALUES ( ?, ? );', ( 1, '' ) )
        
        self._c.execute( 'INSERT INTO version ( version ) VALUES ( ? );', ( HC.SOFTWARE_VERSION, ) )
        
        self._c.executemany( 'INSERT INTO json_dumps_named VALUES ( ?, ?, ?, ?, ? );', ClientDefaults.GetDefaultScriptRows() )
        
    
    def _CreateDBCaches( self ):
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.file_maintenance_jobs ( hash_id INTEGER, job_type INTEGER, time_can_start INTEGER, PRIMARY KEY ( hash_id, job_type ) );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.shape_perceptual_hashes ( phash_id INTEGER PRIMARY KEY, phash BLOB_BYTES UNIQUE );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.shape_perceptual_hash_map ( phash_id INTEGER, hash_id INTEGER, PRIMARY KEY ( phash_id, hash_id ) );' )
        self._CreateIndex( 'external_caches.shape_perceptual_hash_map', [ 'hash_id' ] )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.shape_vptree ( phash_id INTEGER PRIMARY KEY, parent_id INTEGER, radius INTEGER, inner_id INTEGER, inner_population INTEGER, outer_id INTEGER, outer_population INTEGER );' )
        self._CreateIndex( 'external_caches.shape_vptree', [ 'parent_id' ] )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.shape_maintenance_branch_regen ( phash_id INTEGER PRIMARY KEY );' )
        
        self._c.execute( 'CREATE VIRTUAL TABLE IF NOT EXISTS external_caches.notes_fts4 USING fts4( note );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.shape_search_cache ( hash_id INTEGER PRIMARY KEY, searched_distance INTEGER );' )
        
        self._c.execute( 'CREATE VIRTUAL TABLE IF NOT EXISTS external_caches.subtags_fts4 USING fts4( subtag );' )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.subtags_searchable_map ( subtag_id INTEGER PRIMARY KEY, searchable_subtag_id INTEGER );' )
        self._CreateIndex( 'external_caches.subtags_searchable_map', [ 'searchable_subtag_id' ] )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.integer_subtags ( subtag_id INTEGER PRIMARY KEY, integer_subtag INTEGER );' )
        self._CreateIndex( 'external_caches.integer_subtags', [ 'integer_subtag' ] )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.local_tags_cache ( tag_id INTEGER PRIMARY KEY, tag TEXT UNIQUE );' )
        
    
    def _CullFileViewingStatistics( self ):
        
        media_min = self._controller.new_options.GetNoneableInteger( 'file_viewing_statistics_media_min_time' )
        media_max = self._controller.new_options.GetNoneableInteger( 'file_viewing_statistics_media_max_time' )
        preview_min = self._controller.new_options.GetNoneableInteger( 'file_viewing_statistics_preview_min_time' )
        preview_max = self._controller.new_options.GetNoneableInteger( 'file_viewing_statistics_preview_max_time' )
        
        if media_min is not None and media_max is not None and media_min > media_max:
            
            raise Exception( 'Media min was greater than media max! Abandoning cull now!' )
            
        
        if preview_min is not None and preview_max is not None and preview_min > preview_max:
            
            raise Exception( 'Preview min was greater than preview max! Abandoning cull now!' )
            
        
        if media_min is not None:
            
            self._c.execute( 'UPDATE file_viewing_stats SET media_views = CAST( media_viewtime / ? AS INTEGER ) WHERE media_views * ? > media_viewtime;', ( media_min, media_min ) )
            
        
        if media_max is not None:
            
            self._c.execute( 'UPDATE file_viewing_stats SET media_viewtime = media_views * ? WHERE media_viewtime > media_views * ?;', ( media_max, media_max ) )
            
        
        if preview_min is not None:
            
            self._c.execute( 'UPDATE file_viewing_stats SET preview_views = CAST( preview_viewtime / ? AS INTEGER ) WHERE preview_views * ? > preview_viewtime;', ( preview_min, preview_min ) )
            
        
        if preview_max is not None:
            
            self._c.execute( 'UPDATE file_viewing_stats SET preview_viewtime = preview_views * ? WHERE preview_viewtime > preview_views * ?;', ( preview_max, preview_max ) )
            
        
    
    def _DeleteFiles( self, service_id, hash_ids ):
        
        # the gui sometimes gets out of sync and sends a DELETE FROM TRASH call before the SEND TO TRASH call
        # in this case, let's make sure the local file domains are clear before deleting from the umbrella domain
        
        if service_id == self._combined_local_file_service_id:
            
            local_file_service_ids = self._GetServiceIds( ( HC.LOCAL_FILE_DOMAIN, ) )
            
            for local_file_service_id in local_file_service_ids:
                
                self._DeleteFiles( local_file_service_id, hash_ids )
                
            
            self._DeleteFiles( self._trash_service_id, hash_ids )
            
        
        service = self._GetService( service_id )
        
        service_type = service.GetServiceType()
        
        existing_hash_ids = self._STS( self._ExecuteManySelect( 'SELECT hash_id FROM current_files WHERE service_id = ? AND hash_id = ?;', ( ( service_id, hash_id ) for hash_id in hash_ids ) ) )
        
        service_info_updates = []
        
        if len( existing_hash_ids ) > 0:
            
            splayed_existing_hash_ids = HydrusData.SplayListForDB( existing_hash_ids )
            
            # remove them from the service
            
            self._c.executemany( 'DELETE FROM current_files WHERE service_id = ? AND hash_id = ?;', ( ( service_id, hash_id ) for hash_id in existing_hash_ids ) )
            
            self._c.executemany( 'DELETE FROM file_petitions WHERE service_id = ? AND hash_id = ?;', ( ( service_id, hash_id ) for hash_id in existing_hash_ids ) )
            
            info = list( self._ExecuteManySelectSingleParam( 'SELECT size, mime FROM files_info WHERE hash_id = ?;', existing_hash_ids ) )
            
            num_existing_files_removed = len( existing_hash_ids )
            delta_size = sum( ( size for ( size, mime ) in info ) )
            num_inbox = len( existing_hash_ids.intersection( self._inbox_hash_ids ) )
            
            service_info_updates.append( ( -delta_size, service_id, HC.SERVICE_INFO_TOTAL_SIZE ) )
            service_info_updates.append( ( -num_existing_files_removed, service_id, HC.SERVICE_INFO_NUM_FILES ) )
            service_info_updates.append( ( -num_inbox, service_id, HC.SERVICE_INFO_NUM_INBOX ) )
            
            select_statement = 'SELECT 1 FROM files_info WHERE mime IN ' + HydrusData.SplayListForDB( HC.SEARCHABLE_MIMES ) + ' AND hash_id = ?;'
            
            num_viewable_files = sum( self._STI( self._ExecuteManySelectSingleParam( select_statement, existing_hash_ids ) ) )
            
            service_info_updates.append( ( -num_viewable_files, service_id, HC.SERVICE_INFO_NUM_VIEWABLE_FILES ) )
            
            # now do special stuff
            
            # if we maintain tag counts for this service, update
            
            if service_type in HC.AUTOCOMPLETE_CACHE_SPECIFIC_FILE_SERVICES:
                
                tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
                
                for tag_service_id in tag_service_ids:
                    
                    self._CacheSpecificMappingsDeleteFiles( service_id, tag_service_id, existing_hash_ids )
                    
                
            
            # if the files are no longer in any local file services, send them to the trash
            
            local_file_service_ids = self._GetServiceIds( ( HC.LOCAL_FILE_DOMAIN, ) )
            
            if service_id in local_file_service_ids:
                
                splayed_local_file_service_ids = HydrusData.SplayListForDB( local_file_service_ids )
                
                non_orphan_hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM current_files WHERE hash_id IN ' + splayed_existing_hash_ids + ' AND service_id IN ' + splayed_local_file_service_ids + ';' ) )
                
                orphan_hash_ids = existing_hash_ids.difference( non_orphan_hash_ids )
                
                if len( orphan_hash_ids ) > 0:
                    
                    now = HydrusData.GetNow()
                    
                    delete_rows = [ ( hash_id, now ) for hash_id in orphan_hash_ids ]
                    
                    self._AddFiles( self._trash_service_id, delete_rows )
                    
                
            
            # if the files are being fully deleted, then physically delete them
            
            if service_id == self._combined_local_file_service_id:
                
                self._DeletePhysicalFiles( existing_hash_ids )
                
            
            self.pub_after_job( 'notify_new_pending' )
            
        
        # record the deleted row if appropriate
        # this happens outside of 'existing' and occurs on all files due to file repo stuff
        # file repos will sometimes report deleted files without having reported the initial file
        
        if service_id == self._combined_local_file_service_id or service_type == HC.FILE_REPOSITORY:
            
            self._c.executemany( 'INSERT OR IGNORE INTO deleted_files ( service_id, hash_id ) VALUES ( ?, ? );', [ ( service_id, hash_id ) for hash_id in hash_ids ] )
            
            num_new_deleted_files = self._GetRowCount()
            
            service_info_updates.append( ( num_new_deleted_files, service_id, HC.SERVICE_INFO_NUM_DELETED_FILES ) )
            
        
        # push the info updates, notify
        
        self._c.executemany( 'UPDATE service_info SET info = info + ? WHERE service_id = ? AND info_type = ?;', service_info_updates )
        
    
    def _DeleteJSONDump( self, dump_type ):
        
        self._c.execute( 'DELETE FROM json_dumps WHERE dump_type = ?;', ( dump_type, ) )
        
    
    def _DeleteJSONDumpNamed( self, dump_type, dump_name = None, timestamp = None ):
        
        if dump_name is None:
            
            self._c.execute( 'DELETE FROM json_dumps_named WHERE dump_type = ?;', ( dump_type, ) )
            
        elif timestamp is None:
            
            self._c.execute( 'DELETE FROM json_dumps_named WHERE dump_type = ? AND dump_name = ?;', ( dump_type, dump_name ) )
            
        else:
            
            self._c.execute( 'DELETE FROM json_dumps_named WHERE dump_type = ? AND dump_name = ? AND timestamp = ?;', ( dump_type, dump_name, timestamp ) )
            
        
    
    def _DeletePending( self, service_key ):
        
        service_id = self._GetServiceId( service_key )
        
        service = self._GetService( service_id )
        
        if service.GetServiceType() == HC.TAG_REPOSITORY:
            
            ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( service_id )
            
            pending_rescinded_mappings_ids = list( HydrusData.BuildKeyToListDict( self._c.execute( 'SELECT tag_id, hash_id FROM ' + pending_mappings_table_name + ';' ) ).items() )
            
            petitioned_rescinded_mappings_ids = list( HydrusData.BuildKeyToListDict( self._c.execute( 'SELECT tag_id, hash_id FROM ' + petitioned_mappings_table_name + ';' ) ).items() )
            
            self._UpdateMappings( service_id, pending_rescinded_mappings_ids = pending_rescinded_mappings_ids, petitioned_rescinded_mappings_ids = petitioned_rescinded_mappings_ids )
            
            self._c.execute( 'DELETE FROM tag_sibling_petitions WHERE service_id = ?;', ( service_id, ) )
            self._c.execute( 'DELETE FROM tag_parent_petitions WHERE service_id = ?;', ( service_id, ) )
            
        elif service.GetServiceType() in ( HC.FILE_REPOSITORY, HC.IPFS ):
            
            self._c.execute( 'DELETE FROM file_transfers WHERE service_id = ?;', ( service_id, ) )
            self._c.execute( 'DELETE FROM file_petitions WHERE service_id = ?;', ( service_id, ) )
            
        
        self.pub_after_job( 'notify_new_pending' )
        self.pub_after_job( 'notify_new_siblings_data' )
        self.pub_after_job( 'notify_new_parents' )
        
        self.pub_service_updates_after_commit( { service_key : [ HydrusData.ServiceUpdate( HC.SERVICE_UPDATE_DELETE_PENDING ) ] } )
        
    
    def _DeletePhysicalFiles( self, hash_ids ):
        
        hash_ids = set( hash_ids )
        
        self._ArchiveFiles( hash_ids )
        
        for hash_id in hash_ids:
            
            self._PHashesDeleteFile( hash_id )
            
        
        self._c.executemany( 'DELETE FROM file_maintenance_jobs WHERE hash_id = ?;', ( ( hash_id, ) for hash_id in hash_ids ) )
        
        potentially_pending_upload_hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM file_transfers;', ) )
        
        deletable_file_hash_ids = hash_ids.difference( potentially_pending_upload_hash_ids )
        
        client_files_manager = self._controller.client_files_manager
        
        if len( deletable_file_hash_ids ) > 0:
            
            file_hashes = self._GetHashes( deletable_file_hash_ids )
            
            self._controller.CallToThread( client_files_manager.DelayedDeleteFiles, file_hashes )
            
        
        useful_thumbnail_hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM current_files WHERE hash_id IN ' + HydrusData.SplayListForDB( hash_ids ) + ';' ) )
        
        deletable_thumbnail_hash_ids = hash_ids.difference( useful_thumbnail_hash_ids )
        
        if len( deletable_thumbnail_hash_ids ) > 0:
            
            thumbnail_hashes = self._GetHashes( deletable_thumbnail_hash_ids )
            
            self._controller.CallToThread( client_files_manager.DelayedDeleteThumbnails, thumbnail_hashes )
            
        
    
    def _DeleteService( self, service_id ):
        
        service = self._GetService( service_id )
        
        service_key = service.GetServiceKey()
        service_type = service.GetServiceType()
        
        self._c.execute( 'DELETE FROM services WHERE service_id = ?;', ( service_id, ) )
        
        self._c.execute( 'DELETE FROM remote_thumbnails WHERE service_id = ?;', ( service_id, ) )
        
        if service_type in HC.REPOSITORIES:
            
            repository_updates_table_name = GenerateRepositoryRepositoryUpdatesTableName( service_id )
            
            self._c.execute( 'DROP TABLE ' + repository_updates_table_name + ';' )
            
            ( hash_id_map_table_name, tag_id_map_table_name ) = GenerateRepositoryMasterCacheTableNames( service_id )
            
            self._c.execute( 'DROP TABLE ' + hash_id_map_table_name + ';' )
            self._c.execute( 'DROP TABLE ' + tag_id_map_table_name + ';' )
            
        
        if service_type in HC.REAL_TAG_SERVICES:
            
            ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( service_id )
            
            self._c.execute( 'DROP TABLE ' + current_mappings_table_name + ';' )
            self._c.execute( 'DROP TABLE ' + deleted_mappings_table_name + ';' )
            self._c.execute( 'DROP TABLE ' + pending_mappings_table_name + ';' )
            self._c.execute( 'DROP TABLE ' + petitioned_mappings_table_name + ';' )
            
            #
            
            self._c.execute( 'DELETE FROM tag_siblings WHERE service_id = ?;', ( service_id, ) )
            self._c.execute( 'DELETE FROM tag_sibling_petitions WHERE service_id = ?;', ( service_id, ) )
            self._c.execute( 'DELETE FROM tag_parents WHERE service_id = ?;', ( service_id, ) )
            self._c.execute( 'DELETE FROM tag_parent_petitions WHERE service_id = ?;', ( service_id, ) )
            
            self._CacheTagSiblingsLookupDrop( service_id )
            
            self._CacheTagSiblingsLookupDrop( self._combined_tag_service_id )
            
            self._CacheTagSiblingsLookupGenerate( self._combined_tag_service_id )
            
            self._CacheCombinedFilesMappingsDrop( service_id )
            
            file_service_ids = self._GetServiceIds( HC.AUTOCOMPLETE_CACHE_SPECIFIC_FILE_SERVICES )
            
            for file_service_id in file_service_ids:
                
                self._CacheSpecificMappingsDrop( file_service_id, service_id )
                
            
        
        if service_type in HC.AUTOCOMPLETE_CACHE_SPECIFIC_FILE_SERVICES:
            
            tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
            for tag_service_id in tag_service_ids:
                
                self._CacheSpecificMappingsDrop( service_id, tag_service_id )
                
            
        
        if service_id in self._service_cache:
            
            del self._service_cache[ service_id ]
            
        
        service_update = HydrusData.ServiceUpdate( HC.SERVICE_UPDATE_RESET )
        
        service_keys_to_service_updates = { service_key : [ service_update ] }
        
        self.pub_service_updates_after_commit( service_keys_to_service_updates )
        
    
    def _DeleteServiceDirectory( self, service_id, dirname ):
        
        directory_id = self._GetTextId( dirname )
        
        self._c.execute( 'DELETE FROM service_directories WHERE service_id = ? AND directory_id = ?;', ( service_id, directory_id ) )
        self._c.execute( 'DELETE FROM service_directory_file_map WHERE service_id = ? AND directory_id = ?;', ( service_id, directory_id ) )
        
    
    def _DeleteServiceInfo( self ):
        
        self._c.execute( 'DELETE FROM service_info;' )
        
        self.pub_after_job( 'notify_new_pending' )
        
    
    def _DeleteTagParents( self, service_id, pairs ):
        
        self._c.executemany( 'DELETE FROM tag_parents WHERE service_id = ? AND child_tag_id = ? AND parent_tag_id = ?;', ( ( service_id, child_tag_id, parent_tag_id ) for ( child_tag_id, parent_tag_id ) in pairs ) )
        self._c.executemany( 'DELETE FROM tag_parent_petitions WHERE service_id = ? AND child_tag_id = ? AND parent_tag_id = ? AND status = ?;', ( ( service_id, child_tag_id, parent_tag_id, HC.CONTENT_STATUS_PETITIONED ) for ( child_tag_id, parent_tag_id ) in pairs )  )
        
        self._c.executemany( 'INSERT OR IGNORE INTO tag_parents ( service_id, child_tag_id, parent_tag_id, status ) VALUES ( ?, ?, ?, ? );', ( ( service_id, child_tag_id, parent_tag_id, HC.CONTENT_STATUS_DELETED ) for ( child_tag_id, parent_tag_id ) in pairs ) )
        
    
    def _DeleteTagSiblings( self, service_id, pairs ):
        
        self._c.executemany( 'DELETE FROM tag_siblings WHERE service_id = ? AND bad_tag_id = ?;', ( ( service_id, bad_tag_id ) for ( bad_tag_id, good_tag_id ) in pairs ) )
        self._c.executemany( 'DELETE FROM tag_sibling_petitions WHERE service_id = ? AND bad_tag_id = ? AND status = ?;', ( ( service_id, bad_tag_id, HC.CONTENT_STATUS_PETITIONED ) for ( bad_tag_id, good_tag_id ) in pairs ) )
        
        self._c.executemany( 'INSERT OR IGNORE INTO tag_siblings ( service_id, bad_tag_id, good_tag_id, status ) VALUES ( ?, ?, ?, ? );', ( ( service_id, bad_tag_id, good_tag_id, HC.CONTENT_STATUS_DELETED ) for ( bad_tag_id, good_tag_id ) in pairs ) )
        
        tag_ids = set()
        
        for ( bad_tag_id, good_tag_id ) in pairs:
            
            tag_ids.add( bad_tag_id )
            tag_ids.add( good_tag_id )
            
        
        self._CacheTagSiblingsUpdateChains( service_id, tag_ids )
        
    
    def _DeleteYAMLDump( self, dump_type, dump_name = None ):
        
        if dump_name is None:
            
            self._c.execute( 'DELETE FROM yaml_dumps WHERE dump_type = ?;', ( dump_type, ) )
            
        else:
            
            if dump_type == YAML_DUMP_ID_LOCAL_BOORU: dump_name = dump_name.hex()
            
            self._c.execute( 'DELETE FROM yaml_dumps WHERE dump_type = ? AND dump_name = ?;', ( dump_type, dump_name ) )
            
        
        if dump_type == YAML_DUMP_ID_LOCAL_BOORU:
            
            service_id = self._GetServiceId( CC.LOCAL_BOORU_SERVICE_KEY )
            
            self._c.execute( 'DELETE FROM service_info WHERE service_id = ? AND info_type = ?;', ( service_id, HC.SERVICE_INFO_NUM_SHARES ) )
            
            self._controller.pub( 'refresh_local_booru_shares' )
            
        
    
    def _DisplayCatastrophicError( self, text ):
        
        message = 'The db encountered a serious error! This is going to be written to the log as well, but here it is for a screenshot:'
        message += os.linesep * 2
        message += text
        
        HydrusData.DebugPrint( message )
        
        self._controller.SafeShowCriticalMessage( 'hydrus db failed', message )
        
    
    def _DuplicatesAddPotentialDuplicates( self, media_id, potential_duplicate_media_ids_and_distances ):
        
        inserts = []
        
        for ( potential_duplicate_media_id, distance ) in potential_duplicate_media_ids_and_distances:
            
            if potential_duplicate_media_id == media_id: # already duplicates!
                
                continue
                
            
            if self._DuplicatesMediasAreFalsePositive( media_id, potential_duplicate_media_id ):
                
                continue
                
            
            if self._DuplicatesMediasAreConfirmedAlternates( media_id, potential_duplicate_media_id ):
                
                continue
                
            
            # if they are alternates with different alt label and index, do not add
            # however this _could_ be folded into areconfirmedalts on the setalt event--any other alt with diff label/index also gets added
            
            smaller_media_id = min( media_id, potential_duplicate_media_id )
            larger_media_id = max( media_id, potential_duplicate_media_id )
            
            inserts.append( ( smaller_media_id, larger_media_id, distance ) )
            
        
        if len( inserts ) > 0:
            
            self._c.executemany( 'INSERT OR IGNORE INTO potential_duplicate_pairs ( smaller_media_id, larger_media_id, distance ) VALUES ( ?, ?, ? );', inserts )
            
        
    
    def _DuplicatesAlternatesGroupsAreFalsePositive( self, alternates_group_id_a, alternates_group_id_b ):
        
        if alternates_group_id_a == alternates_group_id_b:
            
            return False
            
        
        smaller_alternates_group_id = min( alternates_group_id_a, alternates_group_id_b )
        larger_alternates_group_id = max( alternates_group_id_a, alternates_group_id_b )
        
        result = self._c.execute( 'SELECT 1 FROM duplicate_false_positives WHERE smaller_alternates_group_id = ? AND larger_alternates_group_id = ?;', ( smaller_alternates_group_id, larger_alternates_group_id ) ).fetchone()
        
        false_positive_pair_found = result is not None
        
        return false_positive_pair_found
        
    
    def _DuplicatesClearAllFalsePositiveRelations( self, alternates_group_id ):
        
        self._c.execute( 'DELETE FROM duplicate_false_positives WHERE smaller_alternates_group_id = ? OR larger_alternates_group_id = ?;', ( alternates_group_id, alternates_group_id ) )
        
        media_ids = self._DuplicatesGetAlternateMediaIds( alternates_group_id )
        
        for media_id in media_ids:
            
            hash_ids = self._DuplicatesGetDuplicateHashIds( media_id )
            
            self._PHashesResetSearch( hash_ids )
            
        
    
    def _DuplicatesClearAllFalsePositiveRelationsFromHashes( self, hashes ):
        
        hash_ids = self._GetHashIds( hashes )
        
        for hash_id in hash_ids:
            
            media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
            
            if media_id is not None:
                
                alternates_group_id = self._DuplicatesGetAlternatesGroupId( media_id, do_not_create = True )
                
                if alternates_group_id is not None:
                    
                    self._DuplicatesClearAllFalsePositiveRelations( alternates_group_id )
                    
                
            
        
    
    def _DuplicatesClearFalsePositiveRelationsBetweenGroups( self, alternates_group_ids ):
        
        pairs = list( itertools.combinations( alternates_group_ids, 2 ) )
        
        for ( alternates_group_id_a, alternates_group_id_b ) in pairs:
            
            smaller_alternates_group_id = min( alternates_group_id_a, alternates_group_id_b )
            larger_alternates_group_id = max( alternates_group_id_a, alternates_group_id_b )
            
            self._c.execute( 'DELETE FROM duplicate_false_positives WHERE smaller_alternates_group_id = ? AND larger_alternates_group_id = ?;', ( smaller_alternates_group_id, larger_alternates_group_id ) )
            
        
        for alternates_group_id in alternates_group_ids:
            
            media_ids = self._DuplicatesGetAlternateMediaIds( alternates_group_id )
            
            for media_id in media_ids:
                
                hash_ids = self._DuplicatesGetDuplicateHashIds( media_id )
                
                self._PHashesResetSearch( hash_ids )
                
            
        
    
    def _DuplicatesClearFalsePositiveRelationsBetweenGroupsFromHashes( self, hashes ):
        
        alternates_group_ids = set()
        
        hash_id = self._GetHashId( hash )
        
        media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
        
        if media_id is not None:
            
            alternates_group_id = self._DuplicatesGetAlternatesGroupId( media_id, do_not_create = True )
            
            if alternates_group_id is not None:
                
                alternates_group_ids.add( alternates_group_id )
                
            
        
        if len( alternates_group_ids ) > 1:
            
            self._DuplicatesClearFalsePositiveRelationsBetweenGroups( alternates_group_ids )
            
        
    
    def _DuplicatesClearPotentialsBetweenMedias( self, media_ids_a, media_ids_b ):
        
        # these two groups of medias now have a false positive or alternates relationship set between them, or they are about to be merged
        # therefore, potentials between them are no longer needed
        # note that we are not eliminating intra-potentials within A or B, only inter-potentials between A and B
        
        all_media_ids = set()
        
        all_media_ids.update( media_ids_a )
        all_media_ids.update( media_ids_b )
        
        potential_duplicate_pairs = set()
        
        potential_duplicate_pairs.update( self._ExecuteManySelectSingleParam( 'SELECT smaller_media_id, larger_media_id FROM potential_duplicate_pairs WHERE smaller_media_id = ?;', all_media_ids ) )
        potential_duplicate_pairs.update( self._ExecuteManySelectSingleParam( 'SELECT smaller_media_id, larger_media_id FROM potential_duplicate_pairs WHERE larger_media_id = ?;', all_media_ids ) )
        
        deletees = []
        
        for ( smaller_media_id, larger_media_id ) in potential_duplicate_pairs:
            
            if ( smaller_media_id in media_ids_a and larger_media_id in media_ids_b ) or ( smaller_media_id in media_ids_b and larger_media_id in media_ids_a ):
                
                deletees.append( ( smaller_media_id, larger_media_id ) )
                
            
        
        if len( deletees ) > 0:
            
            self._c.executemany( 'DELETE FROM potential_duplicate_pairs WHERE smaller_media_id = ? AND larger_media_id = ?;', deletees )
            
        
    
    def _DuplicatesClearPotentialsBetweenAlternatesGroups( self, alternates_group_id_a, alternates_group_id_b ):
        
        # these groups are being set as false positive. therefore, any potential between them no longer applies
        
        media_ids_a = self._DuplicatesGetAlternateMediaIds( alternates_group_id_a )
        media_ids_b = self._DuplicatesGetAlternateMediaIds( alternates_group_id_b )
        
        self._DuplicatesClearPotentialsBetweenMedias( media_ids_a, media_ids_b )
        
    
    def _DuplicatesDeleteAllPotentialDuplicatePairs( self ):
        
        media_ids = set()
        
        for ( smaller_media_id, larger_media_id ) in self._c.execute( 'SELECT smaller_media_id, larger_media_id FROM potential_duplicate_pairs;' ):
            
            media_ids.add( smaller_media_id )
            media_ids.add( larger_media_id )
            
        
        hash_ids = set()
        
        for media_id in media_ids:
            
            hash_ids.update( self._DuplicatesGetDuplicateHashIds( media_id ) )
            
        
        self._c.execute( 'DELETE FROM potential_duplicate_pairs;' )
        
        self._PHashesResetSearch( hash_ids )
        
    
    def _DuplicatesDissolveAlternatesGroupId( self, alternates_group_id ):
        
        media_ids = self._DuplicatesGetAlternateMediaIds( alternates_group_id )
        
        for media_id in media_ids:
            
            self._DuplicatesDissolveMediaId( media_id )
            
        
    
    def _DuplicatesDissolveAlternatesGroupIdFromHashes( self, hashes ):
        
        hash_ids = self._GetHashIds( hashes )
        
        for hash_id in hash_ids:
            
            media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
            
            if media_id is not None:
                
                alternates_group_id = self._DuplicatesGetAlternatesGroupId( media_id, do_not_create = True )
                
                if alternates_group_id is not None:
                    
                    self._DuplicatesDissolveAlternatesGroupId( alternates_group_id )
                    
                
            
        
    
    def _DuplicatesDissolveMediaId( self, media_id ):
        
        self._DuplicatesRemoveAlternateMember( media_id )
        
        self._c.execute( 'DELETE FROM potential_duplicate_pairs WHERE smaller_media_id = ? OR larger_media_id = ?;', ( media_id, media_id ) )
        
        hash_ids = self._DuplicatesGetDuplicateHashIds( media_id )
        
        self._c.execute( 'DELETE FROM duplicate_file_members WHERE media_id = ?;', ( media_id, ) )
        self._c.execute( 'DELETE FROM duplicate_files WHERE media_id = ?;', ( media_id, ) )
        
        self._PHashesResetSearch( hash_ids )
        
    
    def _DuplicatesDissolveMediaIdFromHashes( self, hashes ):
        
        hash_ids = self._GetHashIds( hashes )
        
        for hash_id in hash_ids:
            
            media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
            
            if media_id is not None:
                
                self._DuplicatesDissolveMediaId( media_id )
                
            
        
    
    def _DuplicatesFilterKingHashIds( self, allowed_hash_ids ):
        
        # can't just pull explicit king_hash_ids, since files not in the system are considered king of their group
        
        if not isinstance( allowed_hash_ids, set ):
            
            allowed_hash_ids = set( allowed_hash_ids )
            
        
        query = 'SELECT king_hash_id FROM duplicate_files WHERE king_hash_id = ?;'
        
        explicit_king_hash_ids = self._STS( self._ExecuteManySelectSingleParam( query, allowed_hash_ids ) )
        
        query = 'SELECT hash_id FROM duplicate_file_members WHERE hash_id = ?;'
        
        all_duplicate_member_hash_ids = self._STS( self._ExecuteManySelectSingleParam( query, allowed_hash_ids ) )
        
        all_non_king_hash_ids = all_duplicate_member_hash_ids.difference( explicit_king_hash_ids )
        
        return allowed_hash_ids.difference( all_non_king_hash_ids )
        
    
    def _DuplicatesGetAlternatesGroupId( self, media_id, do_not_create = False ):
        
        result = self._c.execute( 'SELECT alternates_group_id FROM alternate_file_group_members WHERE media_id = ?;', ( media_id, ) ).fetchone()
        
        if result is None:
            
            if do_not_create:
                
                return None
                
            
            self._c.execute( 'INSERT INTO alternate_file_groups DEFAULT VALUES;' )
            
            alternates_group_id = self._c.lastrowid
            
            self._c.execute( 'INSERT INTO alternate_file_group_members ( alternates_group_id, media_id ) VALUES ( ?, ? );', ( alternates_group_id, media_id ) )
            
        else:
            
            ( alternates_group_id, ) = result
            
        
        return alternates_group_id
        
    
    def _DuplicatesGetAlternateMediaIds( self, alternates_group_id ):
        
        media_ids = self._STS( self._c.execute( 'SELECT media_id FROM alternate_file_group_members WHERE alternates_group_id = ?;', ( alternates_group_id, ) ) )
        
        return media_ids
        
    
    def _DuplicatesGetBestKingId( self, media_id, file_service_id, allowed_hash_ids = None, preferred_hash_ids = None ):
        
        media_hash_ids = self._DuplicatesGetDuplicateHashIds( media_id, file_service_id = file_service_id )
        
        if allowed_hash_ids is not None:
            
            media_hash_ids.intersection_update( allowed_hash_ids )
            
        
        if len( media_hash_ids ) > 0:
            
            king_hash_id = self._DuplicatesGetKingHashId( media_id )
            
            if preferred_hash_ids is not None:
                
                preferred_hash_ids = media_hash_ids.intersection( preferred_hash_ids )
                
                if len( preferred_hash_ids ) > 0:
                    
                    if king_hash_id not in preferred_hash_ids:
                        
                        king_hash_id = random.sample( preferred_hash_ids, 1 )[0]
                        
                    
                    return king_hash_id
                    
                
            
            if king_hash_id not in media_hash_ids:
                
                king_hash_id = random.sample( media_hash_ids, 1 )[0]
                
            
            return king_hash_id
            
            
        
        return None
        
    
    def _DuplicatesGetDuplicateHashIds( self, media_id, file_service_id = None ):
        
        if file_service_id is None or file_service_id == self._combined_file_service_id:
            
            hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM duplicate_file_members WHERE media_id = ?;', ( media_id, ) ) )
            
        else:
            
            hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM duplicate_file_members NATURAL JOIN current_files WHERE media_id = ? AND service_id = ?;', ( media_id, file_service_id ) ) )
            
        
        return hash_ids
        
    
    def _DuplicatesGetFalsePositiveAlternatesGroupIds( self, alternates_group_id ):
        
        false_positive_alternates_group_ids = set()
        
        results = self._c.execute( 'SELECT smaller_alternates_group_id, larger_alternates_group_id FROM duplicate_false_positives WHERE smaller_alternates_group_id = ? OR larger_alternates_group_id = ?;', ( alternates_group_id, alternates_group_id ) ).fetchall()
        
        for ( smaller_alternates_group_id, larger_alternates_group_id ) in results:
            
            false_positive_alternates_group_ids.add( smaller_alternates_group_id )
            false_positive_alternates_group_ids.add( larger_alternates_group_id )
            
        
        return false_positive_alternates_group_ids
        
    
    def _DuplicatesGetFileDuplicateInfo( self, file_service_key, hash ):
        
        result_dict = {}
        
        result_dict[ 'is_king' ] = True
        
        hash_id = self._GetHashId( hash )
        
        counter = collections.Counter()
        
        media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
        
        if media_id is not None:
            
            ( table_join, predicate_string ) = self._DuplicatesGetPotentialDuplicatePairsTableJoinInfoOnFileService( file_service_key )
            
            ( num_potentials, ) = self._c.execute( 'SELECT COUNT( * ) FROM ( SELECT DISTINCT smaller_media_id, larger_media_id FROM ' + table_join + ' WHERE ' + predicate_string + ' AND ( smaller_media_id = ? OR larger_media_id = ? ) );', ( media_id, media_id, ) ).fetchone()
            
            if num_potentials > 0:
                
                counter[ HC.DUPLICATE_POTENTIAL ] = num_potentials
                
            
            king_hash_id = self._DuplicatesGetKingHashId( media_id )
            
            result_dict[ 'is_king' ] = king_hash_id == hash_id
            
            file_service_id = self._GetServiceId( file_service_key )
            
            media_hash_ids = self._DuplicatesGetDuplicateHashIds( media_id, file_service_id = file_service_id )
            
            num_other_dupe_members = len( media_hash_ids ) - 1
            
            if num_other_dupe_members > 0:
                
                counter[ HC.DUPLICATE_MEMBER ] = num_other_dupe_members
                
            
            alternates_group_id = self._DuplicatesGetAlternatesGroupId( media_id, do_not_create = True )
            
            if alternates_group_id is not None:
                
                alt_media_ids = self._DuplicatesGetAlternateMediaIds( alternates_group_id )
                
                alt_media_ids.discard( media_id )
                
                for alt_media_id in alt_media_ids:
                    
                    alt_hash_ids = self._DuplicatesGetDuplicateHashIds( alt_media_id, file_service_id = file_service_id )
                    
                    if len( alt_hash_ids ) > 0:
                        
                        counter[ HC.DUPLICATE_ALTERNATE ] += 1
                        
                        smaller_media_id = min( media_id, alt_media_id )
                        larger_media_id = max( media_id, alt_media_id )
                        
                        result = self._c.execute( 'SELECT 1 FROM confirmed_alternate_pairs WHERE smaller_media_id = ? AND larger_media_id = ?;', ( smaller_media_id, larger_media_id ) ).fetchone()
                        
                        if result is not None:
                            
                            counter[ HC.DUPLICATE_CONFIRMED_ALTERNATE ] += 1
                            
                        
                    
                
                false_positive_alternates_group_ids = self._DuplicatesGetFalsePositiveAlternatesGroupIds( alternates_group_id )
                
                false_positive_alternates_group_ids.discard( alternates_group_id )
                
                for false_positive_alternates_group_id in false_positive_alternates_group_ids:
                    
                    fp_media_ids = self._DuplicatesGetAlternateMediaIds( false_positive_alternates_group_id )
                    
                    for fp_media_id in fp_media_ids:
                        
                        fp_hash_ids = self._DuplicatesGetDuplicateHashIds( fp_media_id, file_service_id = file_service_id )
                        
                        if len( fp_hash_ids ) > 0:
                            
                            counter[ HC.DUPLICATE_FALSE_POSITIVE ] += 1
                            
                        
                    
                
            
        
        result_dict[ 'counts' ] = counter
        
        return result_dict
        
    
    def _DuplicatesGetFileHashesByDuplicateType( self, file_service_key, hash, duplicate_type, allowed_hash_ids = None, preferred_hash_ids = None ):
        
        hash_id = self._GetHashId( hash )
        
        file_service_id = self._GetServiceId( file_service_key )
        
        dupe_hash_ids = set()
        
        if duplicate_type == HC.DUPLICATE_FALSE_POSITIVE:
            
            media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
            
            if media_id is not None:
                
                alternates_group_id = self._DuplicatesGetAlternatesGroupId( media_id, do_not_create = True )
                
                if alternates_group_id is not None:
                    
                    false_positive_alternates_group_ids = self._DuplicatesGetFalsePositiveAlternatesGroupIds( alternates_group_id )
                    
                    false_positive_alternates_group_ids.discard( alternates_group_id )
                    
                    false_positive_media_ids = set()
                    
                    for false_positive_alternates_group_id in false_positive_alternates_group_ids:
                        
                        false_positive_media_ids.update( self._DuplicatesGetAlternateMediaIds( false_positive_alternates_group_id ) )
                        
                    
                    for false_positive_media_id in false_positive_media_ids:
                        
                        best_king_hash_id = self._DuplicatesGetBestKingId( false_positive_media_id, file_service_id, allowed_hash_ids = allowed_hash_ids, preferred_hash_ids = preferred_hash_ids )
                        
                        if best_king_hash_id is not None:
                            
                            dupe_hash_ids.add( best_king_hash_id )
                            
                        
                    
                
            
        elif duplicate_type == HC.DUPLICATE_ALTERNATE:
            
            media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
            
            if media_id is not None:
                
                alternates_group_id = self._DuplicatesGetAlternatesGroupId( media_id, do_not_create = True )
                
                if alternates_group_id is not None:
                    
                    alternates_media_ids = self._STS( self._c.execute( 'SELECT media_id FROM alternate_file_group_members WHERE alternates_group_id = ?;', ( alternates_group_id, ) ) )
                    
                    alternates_media_ids.discard( media_id )
                    
                    for alternates_media_id in alternates_media_ids:
                        
                        best_king_hash_id = self._DuplicatesGetBestKingId( alternates_media_id, file_service_id, allowed_hash_ids = allowed_hash_ids, preferred_hash_ids = preferred_hash_ids )
                        
                        if best_king_hash_id is not None:
                            
                            dupe_hash_ids.add( best_king_hash_id )
                            
                        
                    
                
            
        elif duplicate_type == HC.DUPLICATE_MEMBER:
            
            media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
            
            if media_id is not None:
                
                media_hash_ids = self._DuplicatesGetDuplicateHashIds( media_id, file_service_id = file_service_id )
                
                if allowed_hash_ids is not None:
                    
                    media_hash_ids.intersection_update( allowed_hash_ids )
                    
                
                dupe_hash_ids.update( media_hash_ids )
                
            
        elif duplicate_type == HC.DUPLICATE_KING:
            
            media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
            
            if media_id is not None:
                
                best_king_hash_id = self._DuplicatesGetBestKingId( media_id, file_service_id, allowed_hash_ids = allowed_hash_ids, preferred_hash_ids = preferred_hash_ids )
                
                if best_king_hash_id is not None:
                    
                    dupe_hash_ids.add( best_king_hash_id )
                    
                
            
        elif duplicate_type == HC.DUPLICATE_POTENTIAL:
            
            media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
            
            if media_id is not None:
                
                ( table_join, predicate_string ) = self._DuplicatesGetPotentialDuplicatePairsTableJoinInfoOnFileService( file_service_key )
                
                for ( smaller_media_id, larger_media_id ) in self._c.execute( 'SELECT smaller_media_id, larger_media_id FROM ' + table_join + ' WHERE ' + predicate_string + ' AND ( smaller_media_id = ? OR larger_media_id = ? );', ( media_id, media_id ) ).fetchall():
                    
                    if smaller_media_id != media_id:
                        
                        potential_media_id = smaller_media_id
                        
                    else:
                        
                        potential_media_id = larger_media_id
                        
                    
                    best_king_hash_id = self._DuplicatesGetBestKingId( potential_media_id, file_service_id, allowed_hash_ids = allowed_hash_ids, preferred_hash_ids = preferred_hash_ids )
                    
                    if best_king_hash_id is not None:
                        
                        dupe_hash_ids.add( best_king_hash_id )
                        
                    
                
            
        
        dupe_hash_ids.discard( hash_id )
        
        dupe_hash_ids = list( dupe_hash_ids )
        
        dupe_hash_ids.insert( 0, hash_id )
        
        dupe_hashes = self._GetHashes( dupe_hash_ids )
        
        return dupe_hashes
        
    
    def _DuplicatesGetHashIdsFromDuplicateCountPredicate( self, file_service_key, operator, num_relationships, dupe_type ):
        
        # doesn't work for '= 0' or '< 1'
        
        if operator == '\u2248':
            
            lower_bound = 0.8 * num_relationships
            upper_bound = 1.2 * num_relationships
            
            def filter_func( count ):
                
                return lower_bound < count and count < upper_bound
                
            
        elif operator == '<':
            
            def filter_func( count ):
                
                return count < num_relationships
                
            
        elif operator == '>':
            
            def filter_func( count ):
                
                return count > num_relationships
                
            
        elif operator == '=':
            
            def filter_func( count ):
                
                return count == num_relationships
                
            
        
        hash_ids = set()
        
        if dupe_type == HC.DUPLICATE_FALSE_POSITIVE:
            
            file_service_id = self._GetServiceId( file_service_key )
            
            alternates_group_ids_to_valid_for_file_domain = {}
            alternates_group_ids_to_false_positives = collections.defaultdict( list )
            
            query = 'SELECT smaller_alternates_group_id, larger_alternates_group_id FROM duplicate_false_positives;'
            
            for ( alternates_group_id_a, alternates_group_id_b ) in self._c.execute( query ):
                
                alternates_group_ids_to_false_positives[ alternates_group_id_a ].append( alternates_group_id_b )
                alternates_group_ids_to_false_positives[ alternates_group_id_b ].append( alternates_group_id_a )
                
            
            for ( alternates_group_id, false_positive_alternates_group_ids ) in alternates_group_ids_to_false_positives.items():
                
                count = 0
                
                for false_positive_alternates_group_id in false_positive_alternates_group_ids:
                    
                    if false_positive_alternates_group_id not in alternates_group_ids_to_valid_for_file_domain:
                        
                        valid = False
                        
                        fp_media_ids = self._DuplicatesGetAlternateMediaIds( false_positive_alternates_group_id )
                        
                        for fp_media_id in fp_media_ids:
                            
                            fp_hash_ids = self._DuplicatesGetDuplicateHashIds( fp_media_id, file_service_id = file_service_id )
                            
                            if len( fp_hash_ids ) > 0:
                                
                                valid = True
                                
                                break
                                
                            
                        
                        alternates_group_ids_to_valid_for_file_domain[ false_positive_alternates_group_id ] = valid
                        
                    
                    if alternates_group_ids_to_valid_for_file_domain[ false_positive_alternates_group_id ]:
                        
                        count += 1
                        
                    
                
                if filter_func( count ):
                    
                    media_ids = self._DuplicatesGetAlternateMediaIds( alternates_group_id )
                    
                    for media_id in media_ids:
                        
                        hash_ids.update( self._DuplicatesGetDuplicateHashIds( media_id, file_service_id = file_service_id ) )
                        
                    
                
            
        elif dupe_type == HC.DUPLICATE_ALTERNATE:
            
            file_service_id = self._GetServiceId( file_service_key )
            
            query = 'SELECT alternates_group_id, COUNT( * ) FROM alternate_file_group_members GROUP BY alternates_group_id;'
            
            results = self._c.execute( query ).fetchall()
            
            for ( alternates_group_id, count ) in results:
                
                count -= 1 # num relationships is number group members - 1
                
                media_ids = self._DuplicatesGetAlternateMediaIds( alternates_group_id )
                
                alternates_group_id_hash_ids = []
                
                for media_id in media_ids:
                    
                    media_id_hash_ids = self._DuplicatesGetDuplicateHashIds( media_id, file_service_id = file_service_id )
                    
                    if len( media_id_hash_ids ) == 0:
                        
                        # this alternate relation does not count for our current file domain, so it should not contribute to the count
                        count -= 1
                        
                    else:
                        
                        alternates_group_id_hash_ids.extend( media_id_hash_ids )
                        
                    
                
                if filter_func( count ):
                    
                    hash_ids.update( alternates_group_id_hash_ids )
                    
                
            
        elif dupe_type == HC.DUPLICATE_MEMBER:
            
            file_service_id = self._GetServiceId( file_service_key )
            
            if file_service_id == self._combined_file_service_id:
                
                table_join = 'duplicate_file_members'
                
                predicate_string = '1=1'
                
            else:
                
                table_join = 'duplicate_file_members NATURAL JOIN current_files'
                predicate_string = 'service_id = {}'.format( file_service_id )
                
            
            query = 'SELECT media_id, COUNT( * ) FROM {} WHERE {} GROUP BY media_id;'.format( table_join, predicate_string )
            
            media_ids = []
            
            for ( media_id, count ) in self._c.execute( query ):
                
                count -= 1
                
                if filter_func( count ):
                    
                    media_ids.append( media_id )
                    
                
            
            select_statement = 'SELECT hash_id FROM duplicate_file_members WHERE media_id = ?;'
            
            hash_ids = self._STS( self._ExecuteManySelectSingleParam( select_statement, media_ids ) )
            
        elif dupe_type == HC.DUPLICATE_POTENTIAL:
            
            ( table_join, predicate_string ) = self._DuplicatesGetPotentialDuplicatePairsTableJoinInfoOnFileService( file_service_key )
            
            smaller_query = 'SELECT smaller_media_id, COUNT( * ) FROM ( SELECT DISTINCT smaller_media_id, larger_media_id FROM ' + table_join + ' WHERE ' + predicate_string + ' ) GROUP BY smaller_media_id;'
            larger_query = 'SELECT larger_media_id, COUNT( * ) FROM ( SELECT DISTINCT smaller_media_id, larger_media_id FROM ' + table_join + ' WHERE ' + predicate_string + ' ) GROUP BY larger_media_id;'
            
            file_service_id = self._GetServiceId( file_service_key )
            
            media_ids_to_counts = collections.Counter()
            
            for ( media_id, count ) in self._c.execute( smaller_query ):
                
                media_ids_to_counts[ media_id ] += count
                
            
            for ( media_id, count ) in self._c.execute( larger_query ):
                
                media_ids_to_counts[ media_id ] += count
                
            
            media_ids = [ media_id for ( media_id, count ) in media_ids_to_counts.items() if filter_func( count ) ]
            
            hash_ids = set()
            
            for media_id in media_ids:
                
                hash_ids.update( self._DuplicatesGetDuplicateHashIds( media_id, file_service_id = file_service_id ) )
                
            
        
        return hash_ids
        
    
    def _DuplicatesGetKingHashId( self, media_id ):
        
        ( king_hash_id, ) = self._c.execute( 'SELECT king_hash_id FROM duplicate_files WHERE media_id = ?;', ( media_id, ) ).fetchone()
        
        return king_hash_id
        
    
    def _DuplicatesGetMediaId( self, hash_id, do_not_create = False ):
        
        result = self._c.execute( 'SELECT media_id FROM duplicate_file_members WHERE hash_id = ?;', ( hash_id, ) ).fetchone()
        
        if result is None:
            
            if do_not_create:
                
                return None
                
            
            self._c.execute( 'INSERT INTO duplicate_files ( king_hash_id ) VALUES ( ? );', ( hash_id, ) )
            
            media_id = self._c.lastrowid
            
            self._c.execute( 'INSERT INTO duplicate_file_members ( media_id, hash_id ) VALUES ( ?, ? );', ( media_id, hash_id ) )
            
        else:
            
            ( media_id, ) = result
            
        
        return media_id
        
    
    def _DuplicatesGetPotentialDuplicatePairsTableJoinInfoOnFileService( self, file_service_key ):
        
        if file_service_key == CC.COMBINED_FILE_SERVICE_KEY:
            
            table_join = 'potential_duplicate_pairs'
            predicate_string = '1=1'
            
        else:
            
            service_id = self._GetServiceId( file_service_key )
            
            table_join = 'potential_duplicate_pairs, duplicate_file_members AS duplicate_file_members_smaller, current_files AS current_files_smaller, duplicate_file_members AS duplicate_file_members_larger, current_files AS current_files_larger ON ( smaller_media_id = duplicate_file_members_smaller.media_id AND duplicate_file_members_smaller.hash_id = current_files_smaller.hash_id AND larger_media_id = duplicate_file_members_larger.media_id AND duplicate_file_members_larger.hash_id = current_files_larger.hash_id )'
            predicate_string = 'current_files_smaller.service_id = {} AND current_files_larger.service_id = {}'.format( service_id, service_id )
            
        
        return ( table_join, predicate_string )
        
    
    def _DuplicatesGetPotentialDuplicatePairsTableJoinInfoOnSearchResults( self, file_service_key, results_table_name, both_files_match ):
        
        if both_files_match:
            
            table_join = 'potential_duplicate_pairs, duplicate_file_members AS duplicate_file_members_smaller, {} AS results_smaller, duplicate_file_members AS duplicate_file_members_larger, {} AS results_larger ON ( smaller_media_id = duplicate_file_members_smaller.media_id AND duplicate_file_members_smaller.hash_id = results_smaller.hash_id AND larger_media_id = duplicate_file_members_larger.media_id AND duplicate_file_members_larger.hash_id = results_larger.hash_id )'.format( results_table_name, results_table_name )
            predicate_string = '1=1'
            
        else:
            
            service_id = self._GetServiceId( file_service_key )
            
            table_join = 'potential_duplicate_pairs, duplicate_file_members AS duplicate_file_members_smaller, duplicate_file_members AS duplicate_file_members_larger, {}, current_files ON ( ( smaller_media_id = duplicate_file_members_smaller.media_id AND duplicate_file_members_smaller.hash_id = {}.hash_id AND larger_media_id = duplicate_file_members_larger.media_id AND duplicate_file_members_larger.hash_id = current_files.hash_id ) OR ( smaller_media_id = duplicate_file_members_smaller.media_id AND duplicate_file_members_smaller.hash_id = current_files.hash_id AND larger_media_id = duplicate_file_members_larger.media_id AND duplicate_file_members_larger.hash_id = {}.hash_id ) )'.format( results_table_name, results_table_name, results_table_name )
            predicate_string = 'current_files.service_id = {}'.format( service_id )
            
        
        return ( table_join, predicate_string )
        
    
    def _DuplicatesGetRandomPotentialDuplicateHashes( self, file_search_context, both_files_match ):
        
        file_service_key = file_search_context.GetFileServiceKey()
        
        file_service_id = self._GetServiceId( file_service_key )
        
        is_complicated_search = False
        
        with HydrusDB.TemporaryIntegerTable( self._c, [], 'hash_id' ) as temp_table_name:
            
            # first we get a sample of current potential pairs in the db, given our limiting search context
            
            allowed_hash_ids = None
            preferred_hash_ids = None
            
            if file_search_context.IsJustSystemEverything() or file_search_context.HasNoPredicates():
                
                ( table_join, predicate_string ) = self._DuplicatesGetPotentialDuplicatePairsTableJoinInfoOnFileService( file_service_key )
                
            else:
                
                is_complicated_search = True
                
                query_hash_ids = self._GetHashIdsFromQuery( file_search_context, apply_implicit_limit = False )
                
                if both_files_match:
                    
                    allowed_hash_ids = query_hash_ids
                    
                else:
                    
                    preferred_hash_ids = query_hash_ids
                    
                
                self._c.executemany( 'INSERT OR IGNORE INTO {} ( hash_id ) VALUES ( ? );'.format( temp_table_name ), ( ( hash_id, ) for hash_id in query_hash_ids ) )
                
                self._AnalyzeTempTable( temp_table_name )
                
                ( table_join, predicate_string ) = self._DuplicatesGetPotentialDuplicatePairsTableJoinInfoOnSearchResults( file_service_key, temp_table_name, both_files_match )
                
            
            potential_media_ids = set()
            
            # distinct important here for the search results table join
            for ( smaller_media_id, larger_media_id ) in self._c.execute( 'SELECT DISTINCT smaller_media_id, larger_media_id FROM ' + table_join + ' WHERE ' + predicate_string + ';' ):
                
                potential_media_ids.add( smaller_media_id )
                potential_media_ids.add( larger_media_id )
                
                if len( potential_media_ids ) >= 1000:
                    
                    break
                    
                
            
            # now let's randomly select a file in these medias
            
            potential_media_ids = list( potential_media_ids )
            
            random.shuffle( potential_media_ids )
            
            chosen_hash_id = None
            
            for potential_media_id in potential_media_ids:
                
                best_king_hash_id = self._DuplicatesGetBestKingId( potential_media_id, file_service_id, allowed_hash_ids = allowed_hash_ids, preferred_hash_ids = preferred_hash_ids )
                
                if best_king_hash_id is not None:
                    
                    chosen_hash_id = best_king_hash_id
                    
                    break
                    
                
            
        
        if chosen_hash_id is None:
            
            return []
            
        
        hash = self._GetHash( chosen_hash_id )
        
        if is_complicated_search and both_files_match:
            
            allowed_hash_ids = query_hash_ids
            
        else:
            
            allowed_hash_ids = None
            
        
        return self._DuplicatesGetFileHashesByDuplicateType( file_service_key, hash, HC.DUPLICATE_POTENTIAL, allowed_hash_ids = allowed_hash_ids, preferred_hash_ids = preferred_hash_ids )
        
    
    def _DuplicatesGetPotentialDuplicatePairsForFiltering( self, file_search_context, both_files_match ):
        
        # we need to batch non-intersecting decisions here to keep it simple at the gui-level
        # we also want to maximise per-decision value
        
        # now we will fetch some unknown pairs
        
        file_service_key = file_search_context.GetFileServiceKey()
        
        file_service_id = self._GetServiceId( file_service_key )
        
        with HydrusDB.TemporaryIntegerTable( self._c, [], 'hash_id' ) as temp_table_name:
            
            allowed_hash_ids = None
            preferred_hash_ids = None
            
            if file_search_context.IsJustSystemEverything() or file_search_context.HasNoPredicates():
                
                ( table_join, predicate_string ) = self._DuplicatesGetPotentialDuplicatePairsTableJoinInfoOnFileService( file_service_key )
                
            else:
                
                query_hash_ids = self._GetHashIdsFromQuery( file_search_context, apply_implicit_limit = False )
                
                if both_files_match:
                    
                    allowed_hash_ids = query_hash_ids
                    
                else:
                    
                    preferred_hash_ids = query_hash_ids
                    
                
                self._c.executemany( 'INSERT OR IGNORE INTO {} ( hash_id ) VALUES ( ? );'.format( temp_table_name ), ( ( hash_id, ) for hash_id in query_hash_ids ) )
                
                self._AnalyzeTempTable( temp_table_name )
                
                ( table_join, predicate_string ) = self._DuplicatesGetPotentialDuplicatePairsTableJoinInfoOnSearchResults( file_service_key, temp_table_name, both_files_match )
                
            
            # distinct important here for the search results table join
            result = self._c.execute( 'SELECT DISTINCT smaller_media_id, larger_media_id, distance FROM ' + table_join + ' WHERE ' + predicate_string + ' LIMIT 2500;' ).fetchall()
            
        
        MAX_BATCH_SIZE = HG.client_controller.new_options.GetInteger( 'duplicate_filter_max_batch_size' )
        
        batch_of_pairs_of_media_ids = []
        seen_media_ids = set()
        
        distances_to_pairs = HydrusData.BuildKeyToListDict( ( ( distance, ( smaller_media_id, larger_media_id ) ) for ( smaller_media_id, larger_media_id, distance ) in result ) )
        
        distances = sorted( distances_to_pairs.keys() )
        
        # we want to preference pairs that have the smallest distance between them. deciding on more similar files first helps merge dupes before dealing with alts so reduces potentials more quickly
        for distance in distances:
            
            result_pairs_for_this_distance = distances_to_pairs[ distance ]
            
            # convert them into possible groups per each possible 'master hash_id', and value them
            
            master_media_ids_to_groups = collections.defaultdict( list )
            
            for pair in result_pairs_for_this_distance:
                
                ( smaller_media_id, larger_media_id ) = pair
                
                master_media_ids_to_groups[ smaller_media_id ].append( pair )
                master_media_ids_to_groups[ larger_media_id ].append( pair )
                
            
            master_hash_ids_to_values = collections.Counter()
            
            for ( media_id, pairs ) in master_media_ids_to_groups.items():
                
                # negative so we later serve up smallest groups first
                # we shall say for now that smaller groups are more useful to front-load because it lets us solve simple problems first
                master_hash_ids_to_values[ media_id ] = - len( pairs )
                
            
            # now let's add decision groups to our batch
            # we exclude hashes we have seen before in each batch so we aren't treading over ground that was implicitly solved by a previous decision in the batch
            
            for ( master_media_id, count ) in master_hash_ids_to_values.most_common():
                
                if master_media_id in seen_media_ids:
                    
                    continue
                    
                
                seen_media_ids_for_this_master_media_id = set()
                
                for pair in master_media_ids_to_groups[ master_media_id ]:
                    
                    ( smaller_media_id, larger_media_id ) = pair
                    
                    if smaller_media_id in seen_media_ids or larger_media_id in seen_media_ids:
                        
                        continue
                        
                    
                    seen_media_ids_for_this_master_media_id.add( smaller_media_id )
                    seen_media_ids_for_this_master_media_id.add( larger_media_id )
                    
                    batch_of_pairs_of_media_ids.append( pair )
                    
                    if len( batch_of_pairs_of_media_ids ) >= MAX_BATCH_SIZE:
                        
                        break
                        
                    
                
                seen_media_ids.update( seen_media_ids_for_this_master_media_id )
                
                if len( batch_of_pairs_of_media_ids ) >= MAX_BATCH_SIZE:
                    
                    break
                    
                
            
            if len( batch_of_pairs_of_media_ids ) >= MAX_BATCH_SIZE:
                
                break
                
            
        
        seen_hash_ids = set()
        
        media_ids_to_best_king_ids = {}
        
        for media_id in seen_media_ids:
            
            best_king_hash_id = self._DuplicatesGetBestKingId( media_id, file_service_id, allowed_hash_ids = allowed_hash_ids, preferred_hash_ids = preferred_hash_ids )
            
            if best_king_hash_id is not None:
                
                seen_hash_ids.add( best_king_hash_id )
                
                media_ids_to_best_king_ids[ media_id ] = best_king_hash_id
                
            
        
        batch_of_pairs_of_hash_ids = [ ( media_ids_to_best_king_ids[ smaller_media_id ], media_ids_to_best_king_ids[ larger_media_id ] ) for ( smaller_media_id, larger_media_id ) in batch_of_pairs_of_media_ids if smaller_media_id in media_ids_to_best_king_ids and larger_media_id in media_ids_to_best_king_ids ]
        
        self._PopulateHashIdsToHashesCache( seen_hash_ids )
        
        batch_of_pairs_of_hashes = [ ( self._hash_ids_to_hashes_cache[ hash_id_a ], self._hash_ids_to_hashes_cache[ hash_id_b ] ) for ( hash_id_a, hash_id_b ) in batch_of_pairs_of_hash_ids ]
        
        return batch_of_pairs_of_hashes
        
    
    def _DuplicatesGetPotentialDuplicatesCount( self, file_search_context, both_files_match ):
        
        file_service_key = file_search_context.GetFileServiceKey()
        
        with HydrusDB.TemporaryIntegerTable( self._c, [], 'hash_id' ) as temp_table_name:
            
            if file_search_context.IsJustSystemEverything() or file_search_context.HasNoPredicates():
                
                ( table_join, predicate_string ) = self._DuplicatesGetPotentialDuplicatePairsTableJoinInfoOnFileService( file_service_key )
                
            else:
                
                query_hash_ids = self._GetHashIdsFromQuery( file_search_context, apply_implicit_limit = False )
                
                self._c.executemany( 'INSERT OR IGNORE INTO {} ( hash_id ) VALUES ( ? );'.format( temp_table_name ), ( ( hash_id, ) for hash_id in query_hash_ids ) )
                
                self._AnalyzeTempTable( temp_table_name )
                
                ( table_join, predicate_string ) = self._DuplicatesGetPotentialDuplicatePairsTableJoinInfoOnSearchResults( file_service_key, temp_table_name, both_files_match )
                
            
            # distinct important here for the search results table join
            ( potential_duplicates_count, ) = self._c.execute( 'SELECT COUNT( * ) FROM ( SELECT DISTINCT smaller_media_id, larger_media_id FROM ' + table_join + ' WHERE ' + predicate_string + ' );', ).fetchone()
            
        
        return potential_duplicates_count
        
    
    def _DuplicatesMediasAreAlternates( self, media_id_a, media_id_b ):
        
        alternates_group_id_a = self._DuplicatesGetAlternatesGroupId( media_id_a, do_not_create = True )
        
        if alternates_group_id_a is None:
            
            return False
            
        
        alternates_group_id_b = self._DuplicatesGetAlternatesGroupId( media_id_b, do_not_create = True )
        
        if alternates_group_id_b is None:
            
            return False
            
        
        return alternates_group_id_a == alternates_group_id_b
        
    
    def _DuplicatesMediasAreConfirmedAlternates( self, media_id_a, media_id_b ):
        
        smaller_media_id = min( media_id_a, media_id_b )
        larger_media_id = max( media_id_a, media_id_b )
        
        result = self._c.execute( 'SELECT 1 FROM confirmed_alternate_pairs WHERE smaller_media_id = ? AND larger_media_id = ?;', ( smaller_media_id, larger_media_id ) ).fetchone()
        
        return result is not None
        
    
    def _DuplicatesMediasAreFalsePositive( self, media_id_a, media_id_b ):
        
        alternates_group_id_a = self._DuplicatesGetAlternatesGroupId( media_id_a, do_not_create = True )
        
        if alternates_group_id_a is None:
            
            return False
            
        
        alternates_group_id_b = self._DuplicatesGetAlternatesGroupId( media_id_b, do_not_create = True )
        
        if alternates_group_id_b is None:
            
            return False
            
        
        return self._DuplicatesAlternatesGroupsAreFalsePositive( alternates_group_id_a, alternates_group_id_b )
        
    
    def _DuplicatesMergeMedias( self, superior_media_id, mergee_media_id ):
        
        if superior_media_id == mergee_media_id:
            
            return
            
        
        self._DuplicatesClearPotentialsBetweenMedias( ( superior_media_id, ), ( mergee_media_id, ) )
        
        alternates_group_id = self._DuplicatesGetAlternatesGroupId( superior_media_id )
        mergee_alternates_group_id = self._DuplicatesGetAlternatesGroupId( mergee_media_id )
        
        if alternates_group_id != mergee_alternates_group_id:
            
            if self._DuplicatesAlternatesGroupsAreFalsePositive( alternates_group_id, mergee_alternates_group_id ):
                
                smaller_alternates_group_id = min( alternates_group_id, mergee_alternates_group_id )
                larger_alternates_group_id = max( alternates_group_id, mergee_alternates_group_id )
                
                self._c.execute( 'DELETE FROM duplicate_false_positives WHERE smaller_alternates_group_id = ? AND larger_alternates_group_id = ?;', ( smaller_alternates_group_id, larger_alternates_group_id ) )
                
            
            self._DuplicatesSetAlternates( superior_media_id, mergee_media_id )
            
        
        self._c.execute( 'UPDATE duplicate_file_members SET media_id = ? WHERE media_id = ?;', ( superior_media_id, mergee_media_id ) )
        
        smaller_media_id = min( superior_media_id, mergee_media_id )
        larger_media_id = max( superior_media_id, mergee_media_id )
        
        # ensure the potential merge pair is gone
        
        self._c.execute( 'DELETE FROM potential_duplicate_pairs WHERE smaller_media_id = ? AND larger_media_id = ?;', ( smaller_media_id, larger_media_id ) )
        
        # now merge potentials from the old to the new--however this has complicated tests to stop confirmed alts and so on, so can't just update ids
        
        existing_potential_info_of_mergee_media_id = self._c.execute( 'SELECT smaller_media_id, larger_media_id, distance FROM potential_duplicate_pairs WHERE smaller_media_id = ? OR larger_media_id = ?;', ( mergee_media_id, mergee_media_id ) ).fetchall()
        
        self._c.execute( 'DELETE FROM potential_duplicate_pairs WHERE smaller_media_id = ? OR larger_media_id = ?;', ( mergee_media_id, mergee_media_id ) )
        
        for ( smaller_media_id, larger_media_id, distance ) in existing_potential_info_of_mergee_media_id:
            
            if smaller_media_id == mergee_media_id:
                
                media_id_a = superior_media_id
                media_id_b = larger_media_id
                
            else:
                
                media_id_a = smaller_media_id
                media_id_b = superior_media_id
                
            
            potential_duplicate_media_ids_and_distances = [ ( media_id_b, distance ) ]
            
            self._DuplicatesAddPotentialDuplicates( media_id_a, potential_duplicate_media_ids_and_distances )
            
        
        # ensure any previous confirmed alt pair is gone
        
        self._c.execute( 'DELETE FROM confirmed_alternate_pairs WHERE smaller_media_id = ? AND larger_media_id = ?;', ( smaller_media_id, larger_media_id ) )
        
        # now merge confirmed alts from the old to the new
        
        self._c.execute( 'UPDATE OR IGNORE confirmed_alternate_pairs SET smaller_media_id = ? WHERE smaller_media_id = ?;', ( superior_media_id, mergee_media_id ) )
        self._c.execute( 'UPDATE OR IGNORE confirmed_alternate_pairs SET larger_media_id = ? WHERE larger_media_id = ?;', ( superior_media_id, mergee_media_id ) )
        
        # and clear out potentials that are now invalid
        
        confirmed_alternate_pairs = self._c.execute( 'SELECT smaller_media_id, larger_media_id FROM confirmed_alternate_pairs WHERE smaller_media_id = ? OR larger_media_id = ?;', ( superior_media_id, superior_media_id ) ).fetchall()
        
        self._c.executemany( 'DELETE FROM potential_duplicate_pairs WHERE smaller_media_id = ? AND larger_media_id = ?;', confirmed_alternate_pairs )
        
        # clear out empty records
        
        self._c.execute( 'DELETE FROM alternate_file_group_members WHERE media_id = ?;', ( mergee_media_id, ) )
        
        self._c.execute( 'DELETE FROM duplicate_files WHERE media_id = ?;', ( mergee_media_id, ) )
        
    
    def _DuplicatesRemoveAlternateMember( self, media_id ):
        
        alternates_group_id = self._DuplicatesGetAlternatesGroupId( media_id, do_not_create = True )
        
        if alternates_group_id is not None:
            
            alternates_media_ids = self._DuplicatesGetAlternateMediaIds( alternates_group_id )
            
            self._c.execute( 'DELETE FROM alternate_file_group_members WHERE media_id = ?;', ( media_id, ) )
            
            self._c.execute( 'DELETE FROM confirmed_alternate_pairs WHERE smaller_media_id = ? OR larger_media_id = ?;', ( media_id, media_id ) )
            
            if len( alternates_media_ids ) == 1: # i.e. what we just removed was the last of the group
                
                self._c.execute( 'DELETE FROM alternate_file_groups WHERE alternates_group_id = ?;', ( alternates_group_id, ) )
                
                self._c.execute( 'DELETE FROM duplicate_false_positives WHERE smaller_alternates_group_id = ? OR larger_alternates_group_id = ?;', ( alternates_group_id, alternates_group_id ) )
                
            
            hash_ids = self._DuplicatesGetDuplicateHashIds( media_id )
            
            self._PHashesResetSearch( hash_ids )
            
        
    
    def _DuplicatesRemoveAlternateMemberFromHashes( self, hashes ):
        
        hash_ids = self._GetHashIds( hashes )
        
        for hash_id in hash_ids:
            
            media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
            
            if media_id is not None:
                
                self._DuplicatesRemoveAlternateMember( media_id )
                
            
        
    
    def _DuplicatesRemoveMediaIdMember( self, hash_id ):
        
        media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
        
        if media_id is not None:
            
            king_hash_id = self._DuplicatesGetKingHashId( media_id )
            
            if hash_id == king_hash_id:
                
                self._DuplicatesDissolveMediaId( media_id )
                
            else:
                
                self._c.execute( 'DELETE FROM duplicate_file_members WHERE hash_id = ?;', ( hash_id, ) )
                
                self._PHashesResetSearch( ( hash_id, ) )
                
            
        
    
    def _DuplicatesRemoveMediaIdMemberFromHashes( self, hashes ):
        
        hash_ids = self._GetHashIds( hashes )
        
        for hash_id in hash_ids:
            
            self._DuplicatesRemoveMediaIdMember( hash_id )
            
        
    
    def _DuplicatesRemovePotentialPairs( self, hash_id ):
        
        media_id = self._DuplicatesGetMediaId( hash_id, do_not_create = True )
        
        if media_id is not None:
            
            self._c.execute( 'DELETE FROM potential_duplicate_pairs WHERE smaller_media_id = ? OR larger_media_id = ?;', ( media_id, media_id ) )
            
        
    
    def _DuplicatesRemovePotentialPairsFromHashes( self, hashes ):
        
        hash_ids = self._GetHashIds( hashes )
        
        for hash_id in hash_ids:
            
            self._DuplicatesRemovePotentialPairs( hash_id )
            
        
    
    def _DuplicatesSetAlternates( self, media_id_a, media_id_b ):
        
        # let's clear out any outstanding potentials. whether this is a valid or not connection, we don't want to see it again
        
        self._DuplicatesClearPotentialsBetweenMedias( ( media_id_a, ), ( media_id_b, ) )
        
        # now check if we should be making a new relationship
        
        alternates_group_id_a = self._DuplicatesGetAlternatesGroupId( media_id_a )
        alternates_group_id_b = self._DuplicatesGetAlternatesGroupId( media_id_b )
        
        if self._DuplicatesAlternatesGroupsAreFalsePositive( alternates_group_id_a, alternates_group_id_b ):
            
            return
            
        
        # write a confirmed result so this can't come up again due to subsequent re-searching etc...
        # in future, I can tune this to consider alternate labels and indices. alternates with different labels and indices are not appropriate for potentials, so we can add more rows here
        
        smaller_media_id = min( media_id_a, media_id_b )
        larger_media_id = max( media_id_a, media_id_b )
        
        self._c.execute( 'INSERT OR IGNORE INTO confirmed_alternate_pairs ( smaller_media_id, larger_media_id ) VALUES ( ?, ? );', ( smaller_media_id, larger_media_id ) )
        
        if alternates_group_id_a == alternates_group_id_b:
            
            return
            
        
        # ok, they are currently not alternates, so we need to merge B into A
        
        # first, for all false positive relationships that A already has, clear out potentials between B and those fps before it moves over
        
        false_positive_pairs = self._c.execute( 'SELECT smaller_alternates_group_id, larger_alternates_group_id FROM duplicate_false_positives WHERE smaller_alternates_group_id = ? OR larger_alternates_group_id = ?;', ( alternates_group_id_a, alternates_group_id_a ) )
        
        for ( smaller_false_positive_alternates_group_id, larger_false_positive_alternates_group_id ) in false_positive_pairs:
            
            if smaller_false_positive_alternates_group_id == alternates_group_id_a:
                
                self._DuplicatesClearPotentialsBetweenAlternatesGroups( alternates_group_id_b, larger_false_positive_alternates_group_id )
                
            else:
                
                self._DuplicatesClearPotentialsBetweenAlternatesGroups( smaller_false_positive_alternates_group_id, alternates_group_id_b )
                
            
        
        # first, update all B to A
        
        self._c.execute( 'UPDATE alternate_file_group_members SET alternates_group_id = ? WHERE alternates_group_id = ?;', ( alternates_group_id_a, alternates_group_id_b ) )
        
        # move false positive records for B to A
        
        false_positive_pairs = self._c.execute( 'SELECT smaller_alternates_group_id, larger_alternates_group_id FROM duplicate_false_positives WHERE smaller_alternates_group_id = ? OR larger_alternates_group_id = ?;', ( alternates_group_id_b, alternates_group_id_b ) )
        
        self._c.execute( 'DELETE FROM duplicate_false_positives WHERE smaller_alternates_group_id = ? OR larger_alternates_group_id = ?;', ( alternates_group_id_b, alternates_group_id_b ) )
        
        for ( smaller_false_positive_alternates_group_id, larger_false_positive_alternates_group_id ) in false_positive_pairs:
            
            if smaller_false_positive_alternates_group_id == alternates_group_id_b:
                
                self._DuplicatesSetFalsePositive( alternates_group_id_a, larger_false_positive_alternates_group_id )
                
            else:
                
                self._DuplicatesSetFalsePositive( smaller_false_positive_alternates_group_id, alternates_group_id_a )
                
            
        
        # remove master record
        
        self._c.execute( 'DELETE FROM alternate_file_groups WHERE alternates_group_id = ?;', ( alternates_group_id_b, ) )
        
        # pubsub to refresh alternates info for alternates_group_id_a and _b goes here
        
    
    def _DuplicatesSetDuplicatePairStatus( self, pair_info ):
        
        for ( duplicate_type, hash_a, hash_b, service_keys_to_content_updates ) in pair_info:
            
            if len( service_keys_to_content_updates ) > 0:
                
                self._ProcessContentUpdates( service_keys_to_content_updates )
                
            
            if duplicate_type == HC.DUPLICATE_WORSE:
                
                ( hash_a, hash_b ) = ( hash_b, hash_a )
                
                duplicate_type = HC.DUPLICATE_BETTER
                
            
            hash_id_a = self._GetHashId( hash_a )
            hash_id_b = self._GetHashId( hash_b )
            
            media_id_a = self._DuplicatesGetMediaId( hash_id_a )
            media_id_b = self._DuplicatesGetMediaId( hash_id_b )
            
            smaller_media_id = min( media_id_a, media_id_b )
            larger_media_id = max( media_id_a, media_id_b )
            
            # this shouldn't be strictly needed, but lets do it here anyway to catch unforeseen problems
            # it is ok to remove this even if we are just about to add it back in--this clears out invalid pairs and increases priority with distance 0
            self._c.execute( 'DELETE FROM potential_duplicate_pairs WHERE smaller_media_id = ? AND larger_media_id = ?;', ( smaller_media_id, larger_media_id ) )
            
            if hash_id_a == hash_id_b:
                
                continue
                
            
            if duplicate_type in ( HC.DUPLICATE_FALSE_POSITIVE, HC.DUPLICATE_ALTERNATE ):
                
                if duplicate_type == HC.DUPLICATE_FALSE_POSITIVE:
                    
                    alternates_group_id_a = self._DuplicatesGetAlternatesGroupId( media_id_a )
                    alternates_group_id_b = self._DuplicatesGetAlternatesGroupId( media_id_b )
                    
                    self._DuplicatesSetFalsePositive( alternates_group_id_a, alternates_group_id_b )
                    
                elif duplicate_type == HC.DUPLICATE_ALTERNATE:
                    
                    self._DuplicatesSetAlternates( media_id_a, media_id_b )
                    
                
            elif duplicate_type in ( HC.DUPLICATE_BETTER, HC.DUPLICATE_WORSE, HC.DUPLICATE_SAME_QUALITY ):
                
                if duplicate_type == HC.DUPLICATE_WORSE:
                    
                    ( hash_id_a, hash_id_b ) = ( hash_id_b, hash_id_a )
                    ( media_id_a, media_id_b ) = ( media_id_b, media_id_a )
                    
                    duplicate_type = HC.DUPLICATE_BETTER
                    
                
                king_hash_id_a = self._DuplicatesGetKingHashId( media_id_a )
                king_hash_id_b = self._DuplicatesGetKingHashId( media_id_b )
                
                if duplicate_type == HC.DUPLICATE_BETTER:
                    
                    if media_id_a == media_id_b:
                        
                        if hash_id_b == king_hash_id_b:
                            
                            # user manually set that a > King A, hence we are setting a new king within a group
                            
                            self._DuplicatesSetKing( hash_id_a, media_id_a )
                            
                        
                    else:
                        
                        if hash_id_b != king_hash_id_b:
                            
                            # user manually set that a member of A is better than a non-King of B. remove b from B and merge it into A
                            
                            self._DuplicatesRemoveMediaIdMember( hash_id_b )
                            
                            media_id_b = self._DuplicatesGetMediaId( hash_id_b )
                            
                            # b is now the King of its new group
                            
                        
                        # a member of A is better than King B, hence B can merge into A
                        
                        self._DuplicatesMergeMedias( media_id_a, media_id_b )
                        
                    
                elif duplicate_type == HC.DUPLICATE_SAME_QUALITY:
                    
                    if media_id_a != media_id_b:
                        
                        a_is_king = hash_id_a == king_hash_id_a
                        b_is_king = hash_id_b == king_hash_id_b
                        
                        if not ( a_is_king or b_is_king ):
                            
                            # if neither file is the king, remove B from B and merge it into A
                            
                            self._DuplicatesRemoveMediaIdMember( hash_id_b )
                            
                            media_id_b = self._DuplicatesGetMediaId( hash_id_b )
                            
                            superior_media_id = media_id_a
                            mergee_media_id = media_id_b
                            
                        elif not a_is_king:
                            
                            # if one of our files is not the king, merge into that group, as the king of that is better than all of the other
                            
                            superior_media_id = media_id_a
                            mergee_media_id = media_id_b
                            
                        elif not b_is_king:
                            
                            superior_media_id = media_id_b
                            mergee_media_id = media_id_a
                            
                        else:
                            
                            # if both are king, merge into A
                            
                            superior_media_id = media_id_a
                            mergee_media_id = media_id_b
                            
                        
                        self._DuplicatesMergeMedias( superior_media_id, mergee_media_id )
                        
                    
                
            elif duplicate_type == HC.DUPLICATE_POTENTIAL:
                
                potential_duplicate_media_ids_and_distances = [ ( media_id_b, 0 ) ]
                
                self._DuplicatesAddPotentialDuplicates( media_id_a, potential_duplicate_media_ids_and_distances )
                
            
        
    
    def _DuplicatesSetFalsePositive( self, alternates_group_id_a, alternates_group_id_b ):
        
        if alternates_group_id_a == alternates_group_id_b:
            
            return
            
        
        self._DuplicatesClearPotentialsBetweenAlternatesGroups( alternates_group_id_a, alternates_group_id_b )
        
        smaller_alternates_group_id = min( alternates_group_id_a, alternates_group_id_b )
        larger_alternates_group_id = max( alternates_group_id_a, alternates_group_id_b )
        
        self._c.execute( 'INSERT OR IGNORE INTO duplicate_false_positives ( smaller_alternates_group_id, larger_alternates_group_id ) VALUES ( ?, ? );', ( smaller_alternates_group_id, larger_alternates_group_id ) )
        
    
    def _DuplicatesSetKing( self, king_hash_id, media_id ):
        
        self._c.execute( 'UPDATE duplicate_files SET king_hash_id = ? WHERE media_id = ?;', ( king_hash_id, media_id ) )
        
    
    def _DuplicatesSetKingFromHash( self, hash ):
        
        hash_id = self._GetHashId( hash )
        
        media_id = self._DuplicatesGetMediaId( hash_id )
        
        self._DuplicatesSetKing( hash_id, media_id )
        
    
    def _FileMaintenanceAddJobs( self, hash_ids, job_type, time_can_start = 0 ):
        
        deletee_job_types =  ClientFiles.regen_file_enum_to_overruled_jobs[ job_type ]
        
        for deletee_job_type in deletee_job_types:
            
            self._c.executemany( 'DELETE FROM file_maintenance_jobs WHERE hash_id = ? AND job_type = ?;', ( ( hash_id, deletee_job_type ) for hash_id in hash_ids ) )
            
        
        #
        
        self._c.executemany( 'REPLACE INTO file_maintenance_jobs ( hash_id, job_type, time_can_start ) VALUES ( ?, ?, ? );', ( ( hash_id, job_type, time_can_start ) for hash_id in hash_ids ) )
        
    
    def _FileMaintenanceAddJobsHashes( self, hashes, job_type, time_can_start = 0 ):
        
        hash_ids = self._GetHashIds( hashes )
        
        self._FileMaintenanceAddJobs( hash_ids, job_type, time_can_start = time_can_start )
        
    
    def _FileMaintenanceCancelJobs( self, job_type ):
        
        self._c.execute( 'DELETE FROM file_maintenance_jobs WHERE job_type = ?;', ( job_type, ) )
        
    
    def _FileMaintenanceClearJobs( self, cleared_job_tuples ):
        
        new_file_info = set()
        
        for ( hash, job_type, additional_data ) in cleared_job_tuples:
            
            hash_id = self._GetHashId( hash )
            
            if additional_data is not None:
                
                if job_type == ClientFiles.REGENERATE_FILE_DATA_JOB_FILE_METADATA:
                    
                    ( size, mime, width, height, duration, num_frames, has_audio, num_words ) = additional_data
                    
                    self._c.execute( 'UPDATE files_info SET size = ?, mime = ?, width = ?, height = ?, duration = ?, num_frames = ?, has_audio = ?, num_words = ? WHERE hash_id = ?;', ( size, mime, width, height, duration, num_frames, has_audio, num_words, hash_id ) )
                    
                    new_file_info.add( ( hash_id, hash ) )
                    
                    if mime not in HC.HYDRUS_UPDATE_FILES:
                        
                        result = self._c.execute( 'SELECT 1 FROM local_hashes WHERE hash_id = ?;', ( hash_id, ) ).fetchone()
                        
                        if result is None:
                            
                            self._FileMaintenanceAddJobs( { hash_id }, ClientFiles.REGENERATE_FILE_DATA_JOB_OTHER_HASHES )
                            
                        
                        result = self._c.execute( 'SELECT 1 FROM file_modified_timestamps WHERE hash_id = ?;', ( hash_id, ) ).fetchone()
                        
                        if result is None:
                            
                            self._FileMaintenanceAddJobs( { hash_id }, ClientFiles.REGENERATE_FILE_DATA_JOB_FILE_MODIFIED_TIMESTAMP )
                            
                        
                    
                elif job_type == ClientFiles.REGENERATE_FILE_DATA_JOB_OTHER_HASHES:
                    
                    ( md5, sha1, sha512 ) = additional_data
                    
                    self._c.execute( 'INSERT OR IGNORE INTO local_hashes ( hash_id, md5, sha1, sha512 ) VALUES ( ?, ?, ?, ? );', ( hash_id, sqlite3.Binary( md5 ), sqlite3.Binary( sha1 ), sqlite3.Binary( sha512 ) ) )
                    
                elif job_type == ClientFiles.REGENERATE_FILE_DATA_JOB_FILE_MODIFIED_TIMESTAMP:
                    
                    file_modified_timestamp = additional_data
                    
                    self._c.execute( 'REPLACE INTO file_modified_timestamps ( hash_id, file_modified_timestamp ) VALUES ( ?, ? );', ( hash_id, file_modified_timestamp ) )
                    
                    new_file_info.add( ( hash_id, hash ) )
                    
                elif job_type == ClientFiles.REGENERATE_FILE_DATA_JOB_SIMILAR_FILES_METADATA:
                    
                    phashes = additional_data
                    
                    self._PHashesSetFileMetadata( hash_id, phashes )
                    
                elif job_type == ClientFiles.REGENERATE_FILE_DATA_JOB_CHECK_SIMILAR_FILES_MEMBERSHIP:
                    
                    should_include = additional_data
                    
                    if should_include:
                        
                        self._PHashesEnsureFileInSystem( hash_id )
                        
                    else:
                        
                        self._PHashesEnsureFileOutOfSystem( hash_id )
                        
                    
                
            
            job_types_to_delete = [ job_type ]
            
            # if a user-made 'force regen thumb' call happens to come in while a 'regen thumb if wrong size' job is queued, we can clear it
            
            job_types_to_delete.extend( ClientFiles.regen_file_enum_to_overruled_jobs[ job_type ] )
            
            self._c.executemany( 'DELETE FROM file_maintenance_jobs WHERE hash_id = ? AND job_type = ?;', ( ( hash_id, job_type_to_delete ) for job_type_to_delete in job_types_to_delete ) )
            
        
        if len( new_file_info ) > 0:
            
            hashes_that_need_refresh = set()
            
            for ( hash_id, hash ) in new_file_info:
                
                if self._weakref_media_result_cache.HasFile( hash_id ):
                    
                    self._weakref_media_result_cache.DropMediaResult( hash_id, hash )
                    
                    hashes_that_need_refresh.add( hash )
                    
                
            
            if len( hashes_that_need_refresh ) > 0:
                
                self._controller.pub( 'new_file_info', hashes_that_need_refresh )
                
            
        
    
    def _FileMaintenanceGetJob( self, job_types = None ):
        
        if job_types is None:
            
            possible_job_types = ClientFiles.ALL_REGEN_JOBS_IN_PREFERRED_ORDER
            
        else:
            
            possible_job_types = job_types
            
        
        for job_type in possible_job_types:
            
            hash_ids = self._STL( self._c.execute( 'SELECT hash_id FROM file_maintenance_jobs WHERE job_type = ? AND time_can_start < ? LIMIT ?;', ( job_type, HydrusData.GetNow(), 256 ) ) )
            
            if len( hash_ids ) > 0:
                
                hashes = self._GetHashes( hash_ids )
                
                return ( hashes, job_type )
                
            
        
        return None
        
    
    def _FileMaintenanceGetJobCounts( self ):
        
        result = self._c.execute( 'SELECT job_type, COUNT( * ) FROM file_maintenance_jobs WHERE time_can_start < ? GROUP BY job_type;', ( HydrusData.GetNow(), ) ).fetchall()
        
        job_types_to_count = dict( result )
        
        return job_types_to_count
        
    
    def _FillInParents( self, service_id, fill_in_tag_id, make_content_updates = False ):
        
        sibling_tag_ids = set()
        
        search_tag_ids = [ fill_in_tag_id ]
        
        while len( search_tag_ids ) > 0:
            
            tag_id = search_tag_ids.pop()
            
            sibling_tag_ids.add( tag_id )
            
            for ( tag_id_a, tag_id_b ) in self._c.execute( 'SELECT bad_tag_id, good_tag_id FROM tag_siblings WHERE ( bad_tag_id = ? OR good_tag_id = ? ) AND status = ?;', ( tag_id, tag_id, HC.CONTENT_STATUS_CURRENT ) ):
                
                if tag_id_a not in sibling_tag_ids:
                    
                    search_tag_ids.append( tag_id_a )
                    
                
                if tag_id_b not in sibling_tag_ids:
                    
                    search_tag_ids.append( tag_id_b )
                    
                
                sibling_tag_ids.add( tag_id_a )
                sibling_tag_ids.add( tag_id_b )
                
            
        
        # we now have all the siblings, worse or better, of fill_in_tag_id
        
        parent_tag_ids = set()
        
        search_tag_ids = list( sibling_tag_ids )
        
        while len( search_tag_ids ) > 0:
            
            tag_id = search_tag_ids.pop()
            
            for parent_tag_id in self._STI( self._c.execute( 'SELECT parent_tag_id FROM tag_parents WHERE child_tag_id = ? AND status = ?;', ( tag_id, HC.CONTENT_STATUS_CURRENT ) ) ):
                
                if parent_tag_id not in parent_tag_ids:
                    
                    search_tag_ids.append( parent_tag_id )
                    
                
                parent_tag_ids.add( parent_tag_id )
                
            
        
        # we now have all parents and grandparents of all siblings
        # all parents should apply to all siblings
        
        mappings_ids = []
        content_updates = []
        
        ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( service_id )
        
        child_hash_ids = self._STS( self._ExecuteManySelectSingleParam( 'SELECT hash_id FROM ' + current_mappings_table_name + ' WHERE tag_id = ?;', sibling_tag_ids ) )
        
        for parent_tag_id in parent_tag_ids:
            
            parent_hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM ' + current_mappings_table_name + ' WHERE tag_id = ?;', ( parent_tag_id, ) ) )
            
            needed_hash_ids = child_hash_ids.difference( parent_hash_ids )
            
            mappings_ids.append( ( parent_tag_id, needed_hash_ids ) )
            
            if make_content_updates:
                
                parent_tag = self._GetTag( parent_tag_id )
                
                needed_hashes = self._GetHashes( needed_hash_ids )
                
                content_update = HydrusData.ContentUpdate( HC.CONTENT_TYPE_MAPPINGS, HC.CONTENT_UPDATE_ADD, ( parent_tag, needed_hashes ) )
                
                content_updates.append( content_update )
                
            
        
        self._UpdateMappings( service_id, mappings_ids = mappings_ids )
        
        if len( content_updates ) > 0:
            
            service_key = self._GetService( service_id ).GetServiceKey()
            
            self.pub_content_updates_after_commit( { service_key : content_updates } )
            
        
    
    def _FilterExistingTags( self, service_key, tags ):
        
        service_id = self._GetServiceId( service_key )
        
        tag_ids_to_tags = { self._GetTagId( tag ) : tag for tag in tags }
        
        counts = self._CacheCombinedFilesMappingsGetAutocompleteCounts( service_id, list( tag_ids_to_tags.keys() ) )
        
        existing_tag_ids = [ tag_id for ( tag_id, current_count, pending_count ) in counts if current_count > 0 ]
        
        filtered_tags = { tag_ids_to_tags[ tag_id ] for tag_id in existing_tag_ids }
        
        return filtered_tags
        
    
    def _FilterHashes( self, hashes, file_service_key ):
        
        if file_service_key == CC.COMBINED_FILE_SERVICE_KEY:
            
            return hashes
            
        
        service_id = self._GetServiceId( file_service_key )
        
        hashes_result = []
        
        for hash in hashes:
            
            if not self._HashExists( hash ):
                
                continue
                
            
            hash_id = self._GetHashId( hash )
            
            result = self._c.execute( 'SELECT 1 FROM current_files WHERE hash_id = ? AND service_id = ?;', ( hash_id, service_id ) ).fetchone()
            
            if result is not None:
                
                hashes_result.append( hash )
                
            
        
        return hashes_result
        
    
    def _GenerateDBJob( self, job_type, synchronous, action, *args, **kwargs ):
        
        return JobDatabaseClient( job_type, synchronous, action, *args, **kwargs )
        
    
    def _GenerateMappingsTables( self, service_id ):
        
        ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( service_id )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS ' + current_mappings_table_name + ' ( tag_id INTEGER, hash_id INTEGER, PRIMARY KEY ( tag_id, hash_id ) ) WITHOUT ROWID;' )
        self._CreateIndex( current_mappings_table_name, [ 'hash_id', 'tag_id' ], unique = True )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS ' + deleted_mappings_table_name + ' ( tag_id INTEGER, hash_id INTEGER, PRIMARY KEY ( tag_id, hash_id ) ) WITHOUT ROWID;' )
        self._CreateIndex( deleted_mappings_table_name, [ 'hash_id', 'tag_id' ], unique = True )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS ' + pending_mappings_table_name + ' ( tag_id INTEGER, hash_id INTEGER, PRIMARY KEY ( tag_id, hash_id ) ) WITHOUT ROWID;' )
        self._CreateIndex( pending_mappings_table_name, [ 'hash_id', 'tag_id' ], unique = True )
        
        self._c.execute( 'CREATE TABLE IF NOT EXISTS ' + petitioned_mappings_table_name + ' ( tag_id INTEGER, hash_id INTEGER, reason_id INTEGER, PRIMARY KEY ( tag_id, hash_id ) ) WITHOUT ROWID;' )
        self._CreateIndex( petitioned_mappings_table_name, [ 'hash_id', 'tag_id' ], unique = True )
        
    
    def _GetAutocompleteCounts( self, tag_service_id, file_service_id, tag_ids, include_current, include_pending ):
        
        if tag_service_id == self._combined_tag_service_id:
            
            search_tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
        else:
            
            search_tag_service_ids = [ tag_service_id ]
            
        
        if file_service_id == self._combined_file_service_id:
            
            cache_results = self._CacheCombinedFilesMappingsGetAutocompleteCounts( tag_service_id, tag_ids )
            
        else:
            
            cache_results = []
            
            for search_tag_service_id in search_tag_service_ids:
                
                cache_results.extend( self._CacheSpecificMappingsGetAutocompleteCounts( file_service_id, search_tag_service_id, tag_ids ) )
                
            
        
        #
        
        ids_to_count = {}
        
        for ( tag_id, current_count, pending_count ) in cache_results:
            
            if not include_current:
                
                current_count = 0
                
            
            if not include_pending:
                
                pending_count = 0
                
            
            if tag_id in ids_to_count:
                
                ( current_min, current_max, pending_min, pending_max ) = ids_to_count[ tag_id ]
                
                ( current_min, current_max ) = ClientData.MergeCounts( current_min, current_max, current_count, None )
                ( pending_min, pending_max ) = ClientData.MergeCounts( pending_min, pending_max, pending_count, None )
                
            else:
                
                ( current_min, current_max, pending_min, pending_max ) = ( current_count, None, pending_count, None )
                
            
            ids_to_count[ tag_id ] = ( current_min, current_max, pending_min, pending_max )
            
        
        return ids_to_count
        
    
    def _GetAutocompleteTagIds( self, service_key, search_text, exact_match, job_key = None ):
        
        ( namespace, half_complete_searchable_subtag ) = HydrusTags.SplitTag( search_text )
        
        if half_complete_searchable_subtag == '':
            
            return set()
            
        
        table_join = 'tags'
        predicates = []
        parameters = []
        
        if exact_match:
            
            table_join = 'tags NATURAL JOIN subtags_searchable_map'
            
            searchable_subtag = half_complete_searchable_subtag
            
            if self._SubtagExists( searchable_subtag ):
                
                searchable_subtag_id = self._GetSubtagId( searchable_subtag )
                
                predicates.append( 'searchable_subtag_id = ?' )
                parameters.append( searchable_subtag_id )
                
            else:
                
                return set()
                
            
            if namespace != '':
                
                if self._NamespaceExists( namespace ):
                    
                    namespace_id = self._GetNamespaceId( namespace )
                    
                    predicates.append( 'namespace_id = ?' )
                    parameters.append( namespace_id )
                    
                else:
                    
                    return set()
                    
                
            
        else:
            
            # Note: you'll have trouble doing MATCH with other OR predicates. namespace LIKE "blah" OR subtag MATCH "blah" is trouble
            # AND is OK
            
            def GetSubTagSearchInfo( half_complete_searchable_subtag ):
                
                # complicated queries are passed to LIKE, because MATCH only supports appended wildcards 'gun*', and not complex stuff like '*gun*'
                
                if ClientSearch.IsComplexWildcard( half_complete_searchable_subtag ):
                    
                    # we search the 'searchable subtags', then link the various mappings back to real tags
                    
                    like_param = ConvertWildcardToSQLiteLikeParameter( half_complete_searchable_subtag )
                    
                    t_j = ', subtags_searchable_map, subtags ON ( tags.subtag_id = subtags_searchable_map.subtag_id AND subtags_searchable_map.searchable_subtag_id = subtags.subtag_id )'
                    pred = 'subtag LIKE ?'
                    param = like_param
                    
                else:
                    
                    # simple 'sam*' style subtag, so we can search fts4 no prob
                    
                    subtags_fts4_param = '"{}"'.format( half_complete_searchable_subtag )
                    
                    t_j = ', subtags_fts4 ON ( subtag_id = docid )'
                    pred = 'subtag MATCH ?'
                    param = subtags_fts4_param
                    
                
                return ( t_j, pred, param )
                
            
            if namespace != '':
                
                if namespace == '*':
                    
                    if service_key != CC.COMBINED_TAG_SERVICE_KEY:
                        
                        service_id = self._GetServiceId( service_key )
                        
                        ac_cache_table_name = GenerateCombinedFilesMappingsCacheTableName( service_id )
                        
                        table_join = 'tags NATURAL JOIN {}'.format( ac_cache_table_name )
                        
                    
                    predicates.append( '1=1' )
                    
                elif '*' in namespace:
                    
                    table_join = 'tags NATURAL JOIN namespaces'
                    
                    like_param = ConvertWildcardToSQLiteLikeParameter( namespace )
                    
                    predicates.append( 'namespace LIKE ?' )
                    
                    parameters.append( like_param )
                    
                else:
                    
                    result = self._c.execute( 'SELECT namespace_id FROM namespaces WHERE namespace = ?;', ( namespace, ) ).fetchone()
                    
                    if result is None:
                        
                        return set()
                        
                    else:
                        
                        ( namespace_id, ) = result
                        
                        predicates.append( 'namespace_id = ' + str( namespace_id ) )
                        
                    
                
            
            if half_complete_searchable_subtag == '*':
                
                if service_key != CC.COMBINED_TAG_SERVICE_KEY:
                    
                    service_id = self._GetServiceId( service_key )
                    
                    ac_cache_table_name = GenerateCombinedFilesMappingsCacheTableName( service_id )
                    
                    table_join += ' NATURAL JOIN {}'.format( ac_cache_table_name )
                    
                
                predicates.append( '1=1' )
                
            else:
                
                ( t_j, pred, param ) = GetSubTagSearchInfo( half_complete_searchable_subtag )
                
                table_join += t_j
                predicates.append( pred )
                parameters.append( param )
                
            
        
        predicates_phrase = ' AND '.join( predicates )
        
        tag_ids = set()
        
        query = 'SELECT DISTINCT tag_id FROM {} WHERE {};'.format( table_join, predicates_phrase )
        
        if len( parameters ) > 0:
            
            cursor = self._c.execute( query, parameters )
            
        else:
            
            cursor = self._c.execute( query )
            
        
        group_of_tag_id_tuples = cursor.fetchmany( 1000 )
        
        while len( group_of_tag_id_tuples ) > 0:
            
            if job_key is not None and job_key.IsCancelled():
                
                return set()
                
            
            tag_ids.update( ( tag_id for ( tag_id, ) in group_of_tag_id_tuples ) )
            
            group_of_tag_id_tuples = cursor.fetchmany( 1000 )
            
        
        # now fetch siblings, add to set
        
        if self._controller.new_options.GetBoolean( 'apply_all_siblings_to_all_services' ):
            
            sibling_service_key = CC.COMBINED_TAG_SERVICE_KEY
            
        else:
            
            sibling_service_key = service_key
            
        
        sibling_service_id = self._GetServiceId( sibling_service_key )
        
        tag_ids.update( self._CacheTagSiblingsLookupGetAdditionalSiblings( sibling_service_id, tag_ids ) )
        
        return tag_ids
        
    
    def _GetAutocompletePredicates(
        self,
        tag_search_context = None,
        file_service_key = CC.COMBINED_FILE_SERVICE_KEY,
        search_text = '',
        exact_match = False,
        inclusive = True,
        add_namespaceless = False,
        search_namespaces_into_full_tags = False,
        collapse_siblings = False,
        job_key = None
    ):
        
        if tag_search_context is None:
            
            tag_search_context = ClientSearch.TagSearchContext()
            
        
        tag_service_key = tag_search_context.service_key
        include_current = tag_search_context.include_current_tags
        include_pending = tag_search_context.include_pending_tags
        
        tag_ids = self._GetAutocompleteTagIds( tag_service_key, search_text, exact_match, job_key = job_key )
        
        if ':' not in search_text and search_namespaces_into_full_tags and not exact_match:
            
            special_search_text = '{}*:*'.format( search_text )
            
            tag_ids.update( self._GetAutocompleteTagIds( tag_service_key, special_search_text, exact_match, job_key = job_key ) )
            
        
        if job_key is not None and job_key.IsCancelled():
            
            return []
            
        
        tag_service_id = self._GetServiceId( tag_service_key )
        file_service_id = self._GetServiceId( file_service_key )
        
        if tag_service_id == self._combined_tag_service_id:
            
            search_tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
        else:
            
            search_tag_service_ids = [ tag_service_id ]
            
        
        all_predicates = []
        
        siblings_manager = HG.client_controller.tag_siblings_manager
        
        for search_tag_service_id in search_tag_service_ids:
            
            for group_of_tag_ids in HydrusData.SplitIteratorIntoChunks( tag_ids, 1000 ):
                
                if job_key is not None and job_key.IsCancelled():
                    
                    return []
                    
                
                search_tag_service_key = self._GetService( search_tag_service_id ).GetServiceKey()
                
                ids_to_count = self._GetAutocompleteCounts( search_tag_service_id, file_service_id, group_of_tag_ids, include_current, include_pending )
                
                if len( ids_to_count ) == 0:
                    
                    continue
                    
                
                #
                
                self._PopulateTagIdsToTagsCache( list( ids_to_count.keys() ) )
                
                tags_and_counts_generator = ( ( self._tag_ids_to_tags_cache[ id ], ids_to_count[ id ] ) for id in ids_to_count.keys() )
                
                predicates = [ ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_TAG, tag, inclusive, min_current_count = min_current_count, min_pending_count = min_pending_count, max_current_count = max_current_count, max_pending_count = max_pending_count ) for ( tag, ( min_current_count, max_current_count, min_pending_count, max_pending_count ) ) in tags_and_counts_generator ]
                
                if collapse_siblings:
                    
                    predicates = siblings_manager.CollapsePredicates( search_tag_service_key, predicates )
                    
                
                all_predicates.extend( predicates )
                
            
        
        if job_key is not None and job_key.IsCancelled():
            
            return []
            
        
        predicates = ClientData.MergePredicates( all_predicates, add_namespaceless = add_namespaceless )
        
        return predicates
        
    
    def _GetTableNamesDueAnalysis( self, force_reanalyze = False ):
        
        db_names = [ name for ( index, name, path ) in self._c.execute( 'PRAGMA database_list;' ) if name not in ( 'mem', 'temp', 'durable_temp' ) ]
        
        all_names = set()
        
        for db_name in db_names:
            
            all_names.update( ( name for ( name, ) in self._c.execute( 'SELECT name FROM ' + db_name + '.sqlite_master WHERE type = ?;', ( 'table', ) ) ) )
            
        
        all_names.discard( 'sqlite_stat1' )
        
        if force_reanalyze:
            
            names_to_analyze = list( all_names )
            
        else:
            
            # Some tables get huge real fast (usually after syncing to big repo)
            # If they have only ever been analyzed with incomplete or empty data, they work slow
            # Analyze on a small table takes ~1ms, so let's instead do smaller tables more frequently and try to catch them as they grow
            
            boundaries = []
            
            boundaries.append( ( 100, True, 6 * 3600 ) )
            boundaries.append( ( 10000, True, 3 * 86400 ) )
            boundaries.append( ( 100000, False, 3 * 30 * 86400 ) )
            # anything bigger than 100k rows will now not be analyzed
            
            existing_names_to_info = { name : ( num_rows, timestamp ) for ( name, num_rows, timestamp ) in self._c.execute( 'SELECT name, num_rows, timestamp FROM analyze_timestamps;' ) }
            
            names_to_analyze = []
            
            for name in all_names:
                
                if name in existing_names_to_info:
                    
                    ( num_rows, timestamp ) = existing_names_to_info[ name ]
                    
                    for ( row_limit_for_this_boundary, can_analyze_immediately, period ) in boundaries:
                        
                        if num_rows > row_limit_for_this_boundary:
                            
                            continue
                            
                        
                        if not HydrusData.TimeHasPassed( timestamp + period ):
                            
                            continue
                            
                        
                        if can_analyze_immediately:
                            
                            # if it has grown, send up to user, as it could be huge. else do it now
                            if self._TableHasAtLeastRowCount( name, row_limit_for_this_boundary ):
                                
                                names_to_analyze.append( name )
                                
                            else:
                                
                                self._AnalyzeTable( name )
                                
                            
                        else:
                            
                            names_to_analyze.append( name )
                            
                        
                    
                else:
                    
                    names_to_analyze.append( name )
                    
                
            
        
        return names_to_analyze
        
    
    def _GetBonedStats( self ):
        
        boned_stats = {}
        
        ( num_total, size_total ) = self._c.execute( 'SELECT COUNT( hash_id ), SUM( size ) FROM files_info NATURAL JOIN current_files WHERE service_id = ?;', ( self._local_file_service_id, ) ).fetchone()
        ( num_inbox, size_inbox ) = self._c.execute( 'SELECT COUNT( hash_id ), SUM( size ) FROM files_info NATURAL JOIN current_files NATURAL JOIN file_inbox WHERE service_id = ?;', ( self._local_file_service_id, ) ).fetchone()
        
        if size_total is None:
            
            size_total = 0
            
        
        if size_inbox is None:
            
            size_inbox = 0
            
        
        num_archive = num_total - num_inbox
        size_archive = size_total - size_inbox
        
        boned_stats[ 'num_inbox' ] = num_inbox
        boned_stats[ 'num_archive' ] = num_archive
        boned_stats[ 'size_inbox' ] = size_inbox
        boned_stats[ 'size_archive' ] = size_archive
        
        total_viewtime = self._c.execute( 'SELECT SUM( media_views ), SUM( media_viewtime ), SUM( preview_views ), SUM( preview_viewtime ) FROM file_viewing_stats;' ).fetchone()
        
        if total_viewtime is None:
            
            total_viewtime = ( 0, 0, 0, 0 )
            
        else:
            
            ( media_views, media_viewtime, preview_views, preview_viewtime ) = total_viewtime
            
            if media_views is None:
                
                total_viewtime = ( 0, 0, 0, 0 )
                
            
        
        boned_stats[ 'total_viewtime' ] = total_viewtime
        
        total_alternate_files = sum( ( count for ( alternates_group_id, count ) in self._c.execute( 'SELECT alternates_group_id, COUNT( * ) FROM alternate_file_group_members GROUP BY alternates_group_id;' ) if count > 1 ) )
        total_duplicate_files = sum( ( count for ( media_id, count ) in self._c.execute( 'SELECT media_id, COUNT( * ) FROM duplicate_file_members GROUP BY media_id;' ) if count > 1 ) )
        
        ( table_join, predicates_string ) = self._DuplicatesGetPotentialDuplicatePairsTableJoinInfoOnFileService( CC.LOCAL_FILE_SERVICE_KEY )
        
        ( total_potential_pairs, ) = self._c.execute( 'SELECT COUNT( * ) FROM ( SELECT DISTINCT smaller_media_id, larger_media_id FROM {} WHERE {} );'.format( table_join, predicates_string ) ).fetchone()
        
        boned_stats[ 'total_alternate_files' ] = total_alternate_files
        boned_stats[ 'total_duplicate_files' ] = total_duplicate_files
        boned_stats[ 'total_potential_pairs' ] = total_potential_pairs
        
        return boned_stats
        
    
    def _GetClientFilesLocations( self ):
        
        result = { prefix : HydrusPaths.ConvertPortablePathToAbsPath( location ) for ( prefix, location ) in self._c.execute( 'SELECT prefix, location FROM client_files_locations;' ) }
        
        if len( result ) < 512:
            
            message = 'When fetching the directories where your files are stored, the database discovered some entries were missing!'
            message += os.linesep * 2
            message += 'Default values will now be inserted. If you have previously migrated your files or thumbnails, and assuming this is occuring on boot, you will next be presented with a dialog to remap them to the correct location.'
            message += os.linesep * 2
            message += 'If this is not happening on client boot, you should kill the hydrus process right now, as a serious hard drive fault has likely recently occurred.'
            
            self._DisplayCatastrophicError( message )
            
            client_files_default = os.path.join( self._db_dir, 'client_files' )
            
            HydrusPaths.MakeSureDirectoryExists( client_files_default )
            
            location = HydrusPaths.ConvertAbsPathToPortablePath( client_files_default )
            
            for prefix in HydrusData.IterateHexPrefixes():
                
                self._c.execute( 'INSERT OR IGNORE INTO client_files_locations ( prefix, location ) VALUES ( ?, ? );', ( 'f' + prefix, location ) )
                self._c.execute( 'INSERT OR IGNORE INTO client_files_locations ( prefix, location ) VALUES ( ?, ? );', ( 't' + prefix, location ) )
                
            
        
        return result
        
    
    def _GetFileHashes( self, given_hashes, given_hash_type, desired_hash_type ):
        
        if given_hash_type == 'sha256':
            
            hash_ids = self._GetHashIds( given_hashes )
            
        else:
            
            hash_ids = []
            
            for given_hash in given_hashes:
                
                if given_hash is None:
                    
                    continue
                    
                
                result = self._c.execute( 'SELECT hash_id FROM local_hashes WHERE ' + given_hash_type + ' = ?;', ( sqlite3.Binary( given_hash ), ) ).fetchone()
                
                if result is not None:
                    
                    ( hash_id, ) = result
                    
                    hash_ids.append( hash_id )
                    
                
            
        
        if desired_hash_type == 'sha256':
            
            desired_hashes = self._GetHashes( hash_ids )
            
        else:
            
            desired_hashes = [ desired_hash for ( desired_hash, ) in self._c.execute( 'SELECT ' + desired_hash_type + ' FROM local_hashes WHERE hash_id IN ' + HydrusData.SplayListForDB( hash_ids ) + ';' ) ]
            
        
        return desired_hashes
        
    
    def _GetFileNotes( self, hash ):
        
        hash_id = self._GetHashId( hash )
        
        names_to_notes = { name : note for ( name, note ) in self._c.execute( 'SELECT label, note FROM file_notes, labels, notes ON ( file_notes.name_id = labels.label_id AND file_notes.note_id = notes.note_id ) WHERE hash_id = ?;', ( hash_id, ) ) }
        
        return names_to_notes
        
    
    def _GetFileSystemPredicates( self, service_key, force_system_everything = False ):
        
        service_id = self._GetServiceId( service_key )
        
        service = self._GetService( service_id )
        
        service_type = service.GetServiceType()
        
        have_ratings = len( self._GetServiceIds( HC.RATINGS_SERVICES ) ) > 0
        
        predicates = []
        
        system_everything_limit = 10000
        
        if service_type in ( HC.COMBINED_FILE, HC.COMBINED_TAG ):
            
            predicates.extend( [ ClientSearch.Predicate( predicate_type, None ) for predicate_type in [ ClientSearch.PREDICATE_TYPE_SYSTEM_EVERYTHING, ClientSearch.PREDICATE_TYPE_SYSTEM_NUM_TAGS, ClientSearch.PREDICATE_TYPE_SYSTEM_LIMIT, ClientSearch.PREDICATE_TYPE_SYSTEM_KNOWN_URLS, ClientSearch.PREDICATE_TYPE_SYSTEM_HASH, ClientSearch.PREDICATE_TYPE_SYSTEM_FILE_SERVICE, ClientSearch.PREDICATE_TYPE_SYSTEM_FILE_RELATIONSHIPS ] ] )
            
        elif service_type in HC.REAL_TAG_SERVICES:
            
            service_info = self._GetServiceInfoSpecific( service_id, service_type, { HC.SERVICE_INFO_NUM_FILES } )
            
            num_everything = service_info[ HC.SERVICE_INFO_NUM_FILES ]
            
            if force_system_everything or ( num_everything <= system_everything_limit or self._controller.new_options.GetBoolean( 'always_show_system_everything' ) ):
                
                predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_SYSTEM_EVERYTHING, min_current_count = num_everything ) )
                
            
            predicates.extend( [ ClientSearch.Predicate( predicate_type, None ) for predicate_type in [ ClientSearch.PREDICATE_TYPE_SYSTEM_NUM_TAGS, ClientSearch.PREDICATE_TYPE_SYSTEM_LIMIT, ClientSearch.PREDICATE_TYPE_SYSTEM_KNOWN_URLS, ClientSearch.PREDICATE_TYPE_SYSTEM_HASH ] ] )
            
            if have_ratings:
                
                predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_SYSTEM_RATING ) )
                
            
            predicates.extend( [ ClientSearch.Predicate( predicate_type, None ) for predicate_type in [ ClientSearch.PREDICATE_TYPE_SYSTEM_FILE_SERVICE, ClientSearch.PREDICATE_TYPE_SYSTEM_TAG_AS_NUMBER, ClientSearch.PREDICATE_TYPE_SYSTEM_FILE_RELATIONSHIPS ] ] )
            
        elif service_type in HC.FILE_SERVICES:
            
            service_info = self._GetServiceInfoSpecific( service_id, service_type, { HC.SERVICE_INFO_NUM_VIEWABLE_FILES, HC.SERVICE_INFO_NUM_INBOX } )
            
            num_everything = service_info[ HC.SERVICE_INFO_NUM_VIEWABLE_FILES ]
            num_inbox = service_info[ HC.SERVICE_INFO_NUM_INBOX ]
            num_archive = num_everything - num_inbox
            
            if service_type == HC.FILE_REPOSITORY:
                
                ( num_local, ) = self._c.execute( 'SELECT COUNT( * ) FROM current_files AS remote_current_files, current_files ON ( remote_current_files.hash_id = current_files.hash_id ) WHERE remote_current_files.service_id = ? AND current_files.service_id = ?;', ( service_id, self._combined_local_file_service_id ) ).fetchone()
                
                num_not_local = num_everything - num_local
                
                num_archive = num_local - num_inbox
                
            
            if force_system_everything or ( num_everything <= system_everything_limit or self._controller.new_options.GetBoolean( 'always_show_system_everything' ) ):
                
                predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_SYSTEM_EVERYTHING, min_current_count = num_everything ) )
                
            
            show_inbox_and_archive = True
            
            if self._controller.new_options.GetBoolean( 'filter_inbox_and_archive_predicates' ) and ( num_inbox == 0 or num_archive == 0 ):
                
                show_inbox_and_archive = False
                
            
            if show_inbox_and_archive:
                
                predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_SYSTEM_INBOX, min_current_count = num_inbox ) )
                predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_SYSTEM_ARCHIVE, min_current_count = num_archive ) )
                
            
            if service_type == HC.FILE_REPOSITORY:
                
                predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_SYSTEM_LOCAL, min_current_count = num_local ) )
                predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_SYSTEM_NOT_LOCAL, min_current_count = num_not_local ) )
                
            
            predicates.extend( [ ClientSearch.Predicate( predicate_type ) for predicate_type in [ ClientSearch.PREDICATE_TYPE_SYSTEM_NUM_TAGS, ClientSearch.PREDICATE_TYPE_SYSTEM_LIMIT, ClientSearch.PREDICATE_TYPE_SYSTEM_SIZE, ClientSearch.PREDICATE_TYPE_SYSTEM_AGE, ClientSearch.PREDICATE_TYPE_SYSTEM_MODIFIED_TIME, ClientSearch.PREDICATE_TYPE_SYSTEM_KNOWN_URLS, ClientSearch.PREDICATE_TYPE_SYSTEM_HASH, ClientSearch.PREDICATE_TYPE_SYSTEM_DIMENSIONS, ClientSearch.PREDICATE_TYPE_SYSTEM_DURATION, ClientSearch.PREDICATE_TYPE_SYSTEM_HAS_AUDIO, ClientSearch.PREDICATE_TYPE_SYSTEM_NOTES, ClientSearch.PREDICATE_TYPE_SYSTEM_NUM_WORDS, ClientSearch.PREDICATE_TYPE_SYSTEM_MIME ] ] )
            
            if have_ratings:
                
                predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_SYSTEM_RATING ) )
                
            
            predicates.extend( [ ClientSearch.Predicate( predicate_type ) for predicate_type in [ ClientSearch.PREDICATE_TYPE_SYSTEM_SIMILAR_TO, ClientSearch.PREDICATE_TYPE_SYSTEM_FILE_SERVICE, ClientSearch.PREDICATE_TYPE_SYSTEM_TAG_AS_NUMBER, ClientSearch.PREDICATE_TYPE_SYSTEM_FILE_RELATIONSHIPS, ClientSearch.PREDICATE_TYPE_SYSTEM_FILE_VIEWING_STATS ] ] )
            
        
        def sys_preds_key( s ):
            
            t = s.GetType()
            
            if t == ClientSearch.PREDICATE_TYPE_SYSTEM_EVERYTHING:
                
                return ( 0, 0 )
                
            elif t == ClientSearch.PREDICATE_TYPE_SYSTEM_INBOX:
                
                return ( 1, 0 )
                
            elif t == ClientSearch.PREDICATE_TYPE_SYSTEM_ARCHIVE:
                
                return ( 2, 0 )
                
            else:
                
                return ( 3, s.ToString() )
                
            
        
        predicates.sort( key = sys_preds_key )
        
        return predicates
        
    
    def _GetForceRefreshTagsManagers( self, hash_ids, hash_ids_to_current_file_service_ids = None ):
        
        if hash_ids_to_current_file_service_ids is None:
            
            hash_ids_to_current_file_service_ids = HydrusData.BuildKeyToListDict( self._ExecuteManySelectSingleParam( 'SELECT hash_id, service_id FROM current_files WHERE hash_id = ?;', hash_ids ) )
            
        
        # Let's figure out if there is a common specific file service to this batch
        
        file_service_id_counter = collections.Counter()
        
        for file_service_ids in hash_ids_to_current_file_service_ids.values():
            
            for file_service_id in file_service_ids:
                
                file_service_id_counter[ file_service_id ] += 1
                
            
        
        common_file_service_id = None
        
        for ( file_service_id, count ) in file_service_id_counter.items():
            
            if count == len( hash_ids ): # i.e. every hash has this file service
                
                ( file_service_type, ) = self._c.execute( 'SELECT service_type FROM services WHERE service_id = ?;', ( file_service_id, ) ).fetchone()
                
                if file_service_type in HC.AUTOCOMPLETE_CACHE_SPECIFIC_FILE_SERVICES:
                    
                    common_file_service_id = file_service_id
                    
                    break
                    
                
            
        
        #
        
        tag_data = []
        
        tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
        
        for tag_service_id in tag_service_ids:
            
            ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( tag_service_id )
            
            if common_file_service_id is None:
                
                tag_data.extend( ( hash_id, ( tag_service_id, HC.CONTENT_STATUS_CURRENT, tag_id ) ) for ( hash_id, tag_id ) in self._ExecuteManySelectSingleParam( 'SELECT hash_id, tag_id FROM ' + current_mappings_table_name + ' WHERE hash_id = ?;', hash_ids ) )
                tag_data.extend( ( hash_id, ( tag_service_id, HC.CONTENT_STATUS_DELETED, tag_id ) ) for ( hash_id, tag_id ) in self._ExecuteManySelectSingleParam( 'SELECT hash_id, tag_id FROM ' + deleted_mappings_table_name + ' WHERE hash_id = ?;', hash_ids ) )
                tag_data.extend( ( hash_id, ( tag_service_id, HC.CONTENT_STATUS_PENDING, tag_id ) ) for ( hash_id, tag_id ) in self._ExecuteManySelectSingleParam( 'SELECT hash_id, tag_id FROM ' + pending_mappings_table_name + ' WHERE hash_id = ?;', hash_ids ) )
                
            else:
                
                ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( common_file_service_id, tag_service_id )
                
                tag_data.extend( ( hash_id, ( tag_service_id, HC.CONTENT_STATUS_CURRENT, tag_id ) ) for ( hash_id, tag_id ) in self._ExecuteManySelectSingleParam( 'SELECT hash_id, tag_id FROM ' + cache_current_mappings_table_name + ' WHERE hash_id = ?;', hash_ids ) )
                tag_data.extend( ( hash_id, ( tag_service_id, HC.CONTENT_STATUS_DELETED, tag_id ) ) for ( hash_id, tag_id ) in self._ExecuteManySelectSingleParam( 'SELECT hash_id, tag_id FROM ' + cache_deleted_mappings_table_name + ' WHERE hash_id = ?;', hash_ids ) )
                tag_data.extend( ( hash_id, ( tag_service_id, HC.CONTENT_STATUS_PENDING, tag_id ) ) for ( hash_id, tag_id ) in self._ExecuteManySelectSingleParam( 'SELECT hash_id, tag_id FROM ' + cache_pending_mappings_table_name + ' WHERE hash_id = ?;', hash_ids ) )
                
            
            tag_data.extend( ( hash_id, ( tag_service_id, HC.CONTENT_STATUS_PETITIONED, tag_id ) ) for ( hash_id, tag_id ) in self._ExecuteManySelectSingleParam( 'SELECT hash_id, tag_id FROM ' + petitioned_mappings_table_name + ' WHERE hash_id = ?;', hash_ids ) )
            
        
        seen_tag_ids = { tag_id for ( hash_id, ( tag_service_id, status, tag_id ) ) in tag_data }
        
        hash_ids_to_raw_tag_data = HydrusData.BuildKeyToListDict( tag_data )
        
        self._PopulateTagIdsToTagsCache( seen_tag_ids )
        
        service_ids_to_service_keys = { service_id : service_key for ( service_id, service_key ) in self._c.execute( 'SELECT service_id, service_key FROM services;' ) }
        
        hash_ids_to_tag_managers = {}
        
        for hash_id in hash_ids:
            
            # service_id, status, tag_id
            raw_tag_data = hash_ids_to_raw_tag_data[ hash_id ]
            
            # service_id -> ( status, tag )
            service_ids_to_tag_data = HydrusData.BuildKeyToListDict( ( ( tag_service_id, ( status, self._tag_ids_to_tags_cache[ tag_id ] ) ) for ( tag_service_id, status, tag_id ) in raw_tag_data ) )
            
            service_keys_to_statuses_to_tags = collections.defaultdict( HydrusData.default_dict_set )
            
            service_keys_to_statuses_to_tags.update( { service_ids_to_service_keys[ service_id ] : HydrusData.BuildKeyToSetDict( tag_data ) for ( service_id, tag_data ) in list(service_ids_to_tag_data.items()) } )
            
            tags_manager = ClientMediaManagers.TagsManager( service_keys_to_statuses_to_tags )
            
            hash_ids_to_tag_managers[ hash_id ] = tags_manager
            
        
        return hash_ids_to_tag_managers
        
    
    def _GetHash( self, hash_id ):
        
        self._PopulateHashIdsToHashesCache( ( hash_id, ) )
        
        return self._hash_ids_to_hashes_cache[ hash_id ]
        
    
    def _GetHashes( self, hash_ids ):
        
        self._PopulateHashIdsToHashesCache( hash_ids )
        
        return [ self._hash_ids_to_hashes_cache[ hash_id ] for hash_id in hash_ids ]
        
    
    def _GetHashId( self, hash ):
        
        result = self._c.execute( 'SELECT hash_id FROM hashes WHERE hash = ?;', ( sqlite3.Binary( hash ), ) ).fetchone()
        
        if result is None:
            
            self._c.execute( 'INSERT INTO hashes ( hash ) VALUES ( ? );', ( sqlite3.Binary( hash ), ) )
            
            hash_id = self._c.lastrowid
            
        else:
            
            ( hash_id, ) = result
            
        
        return hash_id
        
    
    def _GetHashIds( self, hashes ):
        
        hash_ids = set()
        hashes_not_in_db = set()
        
        for hash in hashes:
            
            if hash is None:
                
                continue
                
            
            result = self._c.execute( 'SELECT hash_id FROM hashes WHERE hash = ?;', ( sqlite3.Binary( hash ), ) ).fetchone()
            
            if result is None:
                
                hashes_not_in_db.add( hash )
                
            else:
                
                ( hash_id, ) = result
                
                hash_ids.add( hash_id )
                
            
        
        if len( hashes_not_in_db ) > 0:
            
            self._c.executemany( 'INSERT INTO hashes ( hash ) VALUES ( ? );', ( ( sqlite3.Binary( hash ), ) for hash in hashes_not_in_db ) )
            
            for hash in hashes_not_in_db:
                
                ( hash_id, ) = self._c.execute( 'SELECT hash_id FROM hashes WHERE hash = ?;', ( sqlite3.Binary( hash ), ) ).fetchone()
                
                hash_ids.add( hash_id )
                
            
        
        return hash_ids
        
    
    def _GetHashIdsFromFileViewingStatistics( self, view_type, viewing_locations, operator, viewing_value ):
        
        # only works for positive values like '> 5'. won't work for '= 0' or '< 1' since those are absent from the table
        
        include_media = 'media' in viewing_locations
        include_preview = 'preview' in viewing_locations
        
        if include_media and include_preview:
            
            views_phrase = 'media_views + preview_views'
            viewtime_phrase = 'media_viewtime + preview_viewtime'
            
        elif include_media:
            
            views_phrase = 'media_views'
            viewtime_phrase = 'media_viewtime'
            
        elif include_preview:
            
            views_phrase = 'preview_views'
            viewtime_phrase = 'preview_viewtime'
            
        else:
            
            return []
            
        
        if view_type == 'views':
            
            content_phrase = views_phrase
            
        elif view_type == 'viewtime':
            
            content_phrase = viewtime_phrase
            
        
        if operator == '\u2248':
            
            lower_bound = int( 0.8 * viewing_value )
            upper_bound = int( 1.2 * viewing_value )
            
            test_phrase = content_phrase + ' BETWEEN ' + str( lower_bound ) + ' AND ' + str( upper_bound )
            
        else:
            
            test_phrase = content_phrase + operator + str( viewing_value )
            
        
        select_statement = 'SELECT hash_id FROM file_viewing_stats WHERE ' + test_phrase + ';'
        
        hash_ids = self._STS( self._c.execute( select_statement ) )
        
        return hash_ids
        
    
    def _GetHashIdsFromNamespace( self, file_service_key, tag_search_context: ClientSearch.TagSearchContext, namespace: str, include_siblings = False, hash_ids_table_name = None ):
        
        file_service_id = self._GetServiceId( file_service_key )
        
        tag_service_key = tag_search_context.service_key
        
        if tag_service_key == CC.COMBINED_TAG_SERVICE_KEY:
            
            search_tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
        else:
            
            tag_service_id = self._GetServiceId( tag_service_key )
            
            search_tag_service_ids = [ tag_service_id ]
            
        
        namespace_ids = self._GetNamespaceIdsFromWildcard( namespace )
        
        hash_ids = set()
        
        for namespace_id in namespace_ids:
            
            predicate_string = 'namespace_id = {}'.format( namespace_id )
            
            include_current_tags = tag_search_context.include_current_tags
            include_pending_tags = tag_search_context.include_pending_tags
            
            tables = self._GetMappingTables( file_service_id, search_tag_service_ids, include_current_tags, include_pending_tags )
            
            tables = [ table + ' NATURAL JOIN tags' for table in tables ]
            
            if hash_ids_table_name is not None:
                
                tables = [ table + ' NATURAL JOIN {}'.format( hash_ids_table_name ) for table in tables ]
                
            
            #
            
            for table in tables:
                
                select = 'SELECT hash_id FROM {} WHERE {};'.format( table, predicate_string )
                
                hash_ids.update( self._STI( self._c.execute( select ) ) )
                
            
            if include_siblings:
                
                # fetch all tag_ids where this namespace is a terminator
                # i.e. fetch all where it is 'better', recursively, and discount any chains where it is the 'worse'
                
                # for each of them, union the results of gethashidsfromtagids
                
                # OR maybe just wait for the better db sibling cache or a/c sibling-collapsed layer
                
                pass
                
            
        
        return hash_ids
        
    
    def _GetHashIdsFromNamespaceIdsSubtagIds( self, file_service_key, tag_service_key, namespace_ids, subtag_ids, include_current_tags, include_pending_tags, hash_ids_table_name = None ):
        
        file_service_id = self._GetServiceId( file_service_key )
        
        if tag_service_key == CC.COMBINED_TAG_SERVICE_KEY:
            
            search_tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
        else:
            
            search_tag_service_ids = [ self._GetServiceId( tag_service_key ) ]
            
        
        tables = self._GetMappingTables( file_service_id, search_tag_service_ids, include_current_tags, include_pending_tags )
        
        hash_ids = set()
        
        with HydrusDB.TemporaryIntegerTable( self._c, namespace_ids, 'namespace_id' ) as namespace_temp_table_name:
            
            self._AnalyzeTempTable( namespace_temp_table_name )
            
            with HydrusDB.TemporaryIntegerTable( self._c, subtag_ids, 'subtag_id' ) as subtag_temp_table_name:
                
                self._AnalyzeTempTable( subtag_temp_table_name )
                
                tables = [ table + ' NATURAL JOIN tags NATURAL JOIN {} NATURAL JOIN {}'.format( namespace_temp_table_name, subtag_temp_table_name ) for table in tables ]
                
                if hash_ids_table_name is not None:
                    
                    tables = [ table + ' NATURAL JOIN {}'.format( hash_ids_table_name ) for table in tables ]
                    
                
                for table in tables:
                    
                    select = 'SELECT DISTINCT hash_id FROM {};'.format( table )
                    
                    hash_ids.update( self._STI( self._c.execute( select ) ) )
                    
                
            
        
        return hash_ids
        
    
    def _GetHashIdsFromNoteName( self, name: str, hash_ids_table_name: str ):
        
        label_id = self._GetLabelId( name )
        
        return self._STS( self._c.execute( 'SELECT hash_id FROM file_notes NATURAL JOIN {} WHERE name_id = ?;'.format( hash_ids_table_name ), ( label_id, ) ) )
        
    
    def _GetHashIdsFromNumNotes( self, min_num_notes: typing.Optional[ int ], max_num_notes: typing.Optional[ int ], hash_ids_table_name: str ):
        
        has_notes = max_num_notes is None and min_num_notes == 1
        not_has_notes = ( min_num_notes is None or min_num_notes == 0 ) and max_num_notes is not None and max_num_notes == 0
        
        if has_notes or not_has_notes:
            
            has_hash_ids = self._STS( self._c.execute( 'SELECT DISTINCT hash_id FROM file_notes NATURAL JOIN {};'.format( hash_ids_table_name ) ) )
            
            if has_notes:
                
                hash_ids = has_hash_ids
                
            else:
                
                all_hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM {};'.format( hash_ids_table_name ) ) )
                
                hash_ids = all_hash_ids.difference( has_hash_ids )
                
            
        else:
            
            if min_num_notes is None:
                
                filt = lambda c: c <= max_num_notes
                
            elif max_num_notes is None:
                
                filt = lambda c: min_num_notes <= c
                
            else:
                
                filt = lambda c: min_num_notes <= c <= max_num_notes
                
            
            query = 'SELECT hash_id, COUNT( * ) FROM file_notes NATURAL JOIN {} GROUP BY hash_id;'.format( hash_ids_table_name )
            
            hash_ids = { hash_id for ( hash_id, count ) in self._c.execute( query ) if filt( count ) }
            
        
        return hash_ids
        
    
    def _GetHashIdsFromQuery( self, file_search_context: ClientSearch.FileSearchContext, job_key = None, query_hash_ids = None, apply_implicit_limit = True, sort_by = None, limit_sort_by = None ):
        
        if job_key is None:
            
            job_key = ClientThreading.JobKey( cancellable = True )
            
        
        if query_hash_ids is not None:
            
            query_hash_ids = set( query_hash_ids )
            
        
        have_cross_referenced_file_service = False
        
        self._controller.ResetIdleTimer()
        
        system_predicates = file_search_context.GetSystemPredicates()
        
        file_service_key = file_search_context.GetFileServiceKey()
        tag_search_context = file_search_context.GetTagSearchContext()
        
        tag_service_key = tag_search_context.service_key
        
        include_current_tags = tag_search_context.include_current_tags
        include_pending_tags = tag_search_context.include_pending_tags
        
        file_service_id = self._GetServiceId( file_service_key )
        tag_service_id = self._GetServiceId( tag_service_key )
        
        file_service = self._GetService( file_service_id )
        tag_service = self._GetService( tag_service_id )
        
        file_service_type = file_service.GetServiceType()
        
        tags_to_include = file_search_context.GetTagsToInclude()
        tags_to_exclude = file_search_context.GetTagsToExclude()
        
        namespaces_to_include = file_search_context.GetNamespacesToInclude()
        namespaces_to_exclude = file_search_context.GetNamespacesToExclude()
        
        wildcards_to_include = file_search_context.GetWildcardsToInclude()
        wildcards_to_exclude = file_search_context.GetWildcardsToExclude()
        
        simple_preds = system_predicates.GetSimpleInfo()
        
        king_filter = system_predicates.GetKingFilter()
        
        or_predicates = file_search_context.GetORPredicates()
        
        need_file_domain_cross_reference = file_service_key != CC.COMBINED_FILE_SERVICE_KEY
        there_are_tags_to_search = len( tags_to_include ) > 0 or len( namespaces_to_include ) > 0 or len( wildcards_to_include ) > 0
        
        # ok, let's set up the big list of simple search preds
        
        files_info_predicates = []
        
        if 'min_size' in simple_preds: files_info_predicates.append( 'size > ' + str( simple_preds[ 'min_size' ] ) )
        if 'size' in simple_preds: files_info_predicates.append( 'size = ' + str( simple_preds[ 'size' ] ) )
        if 'max_size' in simple_preds: files_info_predicates.append( 'size < ' + str( simple_preds[ 'max_size' ] ) )
        
        if 'mimes' in simple_preds:
            
            mimes = simple_preds[ 'mimes' ]
            
            if len( mimes ) == 1:
                
                ( mime, ) = mimes
                
                files_info_predicates.append( 'mime = ' + str( mime ) )
                
            else:
                
                files_info_predicates.append( 'mime IN ' + HydrusData.SplayListForDB( mimes ) )
                
            
        
        if 'has_audio' in simple_preds:
            
            has_audio = simple_preds[ 'has_audio' ]
            
            files_info_predicates.append( 'has_audio = {}'.format( int( has_audio ) ) )
            
        
        if file_service_key != CC.COMBINED_FILE_SERVICE_KEY:
            
            if 'min_import_timestamp' in simple_preds: files_info_predicates.append( 'timestamp >= ' + str( simple_preds[ 'min_import_timestamp' ] ) )
            if 'max_import_timestamp' in simple_preds: files_info_predicates.append( 'timestamp <= ' + str( simple_preds[ 'max_import_timestamp' ] ) )
            
        
        if 'min_width' in simple_preds: files_info_predicates.append( 'width > ' + str( simple_preds[ 'min_width' ] ) )
        if 'width' in simple_preds: files_info_predicates.append( 'width = ' + str( simple_preds[ 'width' ] ) )
        if 'max_width' in simple_preds: files_info_predicates.append( 'width < ' + str( simple_preds[ 'max_width' ] ) )
        
        if 'min_height' in simple_preds: files_info_predicates.append( 'height > ' + str( simple_preds[ 'min_height' ] ) )
        if 'height' in simple_preds: files_info_predicates.append( 'height = ' + str( simple_preds[ 'height' ] ) )
        if 'max_height' in simple_preds: files_info_predicates.append( 'height < ' + str( simple_preds[ 'max_height' ] ) )
        
        if 'min_num_pixels' in simple_preds: files_info_predicates.append( 'width * height > ' + str( simple_preds[ 'min_num_pixels' ] ) )
        if 'num_pixels' in simple_preds: files_info_predicates.append( 'width * height = ' + str( simple_preds[ 'num_pixels' ] ) )
        if 'max_num_pixels' in simple_preds: files_info_predicates.append( 'width * height < ' + str( simple_preds[ 'max_num_pixels' ] ) )
        
        if 'min_ratio' in simple_preds:
            
            ( ratio_width, ratio_height ) = simple_preds[ 'min_ratio' ]
            
            files_info_predicates.append( '( width * 1.0 ) / height > ' + str( float( ratio_width ) ) + ' / ' + str( ratio_height ) )
            
        if 'ratio' in simple_preds:
            
            ( ratio_width, ratio_height ) = simple_preds[ 'ratio' ]
            
            files_info_predicates.append( '( width * 1.0 ) / height = ' + str( float( ratio_width ) ) + ' / ' + str( ratio_height ) )
            
        if 'max_ratio' in simple_preds:
            
            ( ratio_width, ratio_height ) = simple_preds[ 'max_ratio' ]
            
            files_info_predicates.append( '( width * 1.0 ) / height < ' + str( float( ratio_width ) ) + ' / ' + str( ratio_height ) )
            
        
        if 'min_num_words' in simple_preds: files_info_predicates.append( 'num_words > ' + str( simple_preds[ 'min_num_words' ] ) )
        if 'num_words' in simple_preds:
            
            num_words = simple_preds[ 'num_words' ]
            
            if num_words == 0: files_info_predicates.append( '( num_words IS NULL OR num_words = 0 )' )
            else: files_info_predicates.append( 'num_words = ' + str( num_words ) )
            
        if 'max_num_words' in simple_preds:
            
            max_num_words = simple_preds[ 'max_num_words' ]
            
            if max_num_words == 0: files_info_predicates.append( 'num_words < ' + str( max_num_words ) )
            else: files_info_predicates.append( '( num_words < ' + str( max_num_words ) + ' OR num_words IS NULL )' )
            
        
        if 'min_duration' in simple_preds: files_info_predicates.append( 'duration > ' + str( simple_preds[ 'min_duration' ] ) )
        if 'duration' in simple_preds:
            
            duration = simple_preds[ 'duration' ]
            
            if duration == 0:
                
                files_info_predicates.append( '( duration = 0 OR duration IS NULL )' )
                
            else:
                
                files_info_predicates.append( 'duration = ' + str( duration ) )
                
            
        if 'max_duration' in simple_preds:
            
            max_duration = simple_preds[ 'max_duration' ]
            
            if max_duration == 0: files_info_predicates.append( 'duration < ' + str( max_duration ) )
            else: files_info_predicates.append( '( duration < ' + str( max_duration ) + ' OR duration IS NULL )' )
            
        
        if 'min_framerate' in simple_preds or 'framerate' in simple_preds or 'max_framerate' in simple_preds:
            
            min_framerate_sql = None
            max_framerate_sql = None
            
            if 'min_framerate' in simple_preds:
                
                min_framerate_sql = simple_preds[ 'min_framerate' ] * 1.05
                
            if 'framerate' in simple_preds:
                
                min_framerate_sql = simple_preds[ 'framerate' ] * 0.95
                max_framerate_sql = simple_preds[ 'framerate' ] * 1.05
                
            if 'max_framerate' in simple_preds:
                
                max_framerate_sql = simple_preds[ 'max_framerate' ] * 0.95
                
            
            pred = '( duration IS NOT NULL AND duration != 0 AND num_frames != 0 AND num_frames IS NOT NULL AND {})'
            
            if min_framerate_sql is None:
                
                pred = pred.format( '( num_frames * 1.0 ) / ( duration / 1000.0 ) < {}'.format( max_framerate_sql ) )
                
            elif max_framerate_sql is None:
                
                pred = pred.format( '( num_frames * 1.0 ) / ( duration / 1000.0 ) > {}'.format( min_framerate_sql ) )
                
            else:
                
                pred = pred.format( '( num_frames * 1.0 ) / ( duration / 1000.0 ) BETWEEN {} AND {}'.format( min_framerate_sql, max_framerate_sql ) )
                
            
            files_info_predicates.append( pred )
            
        
        if 'min_num_frames' in simple_preds: files_info_predicates.append( 'num_frames > ' + str( simple_preds[ 'min_num_frames' ] ) )
        if 'num_frames' in simple_preds:
            
            num_frames = simple_preds[ 'num_frames' ]
            
            if num_frames == 0: files_info_predicates.append( '( num_frames IS NULL OR num_frames = 0 )' )
            else: files_info_predicates.append( 'num_frames = ' + str( num_frames ) )
            
        if 'max_num_frames' in simple_preds:
            
            max_num_frames = simple_preds[ 'max_num_frames' ]
            
            if max_num_frames == 0: files_info_predicates.append( 'num_frames < ' + str( max_num_frames ) )
            else: files_info_predicates.append( '( num_frames < ' + str( max_num_frames ) + ' OR num_frames IS NULL )' )
            
        
        there_are_simple_files_info_preds_to_search_for = len( files_info_predicates ) > 0
        
        # start with some quick ways to populate query_hash_ids
        
        def intersection_update_qhi( query_hash_ids, some_hash_ids, force_create_new_set = False ):
            
            if query_hash_ids is None:
                
                if not isinstance( some_hash_ids, set ) or force_create_new_set:
                    
                    some_hash_ids = set( some_hash_ids )
                    
                
                return some_hash_ids
                
            else:
                
                query_hash_ids.intersection_update( some_hash_ids )
                
                return query_hash_ids
                
            
        
        #
        
        def do_or_preds( or_predicates, query_hash_ids ):
            
            # updating all this regular search code to do OR and AND naturally will be a big job getting right, so let's get a functional inefficient solution and then optimise later as needed
            # -tag stuff and various other exclude situations remain a pain to do quickly assuming OR
            # the future extension of this will be creating an OR_search_context with all the OR_pred's subpreds and have that naturally query_hash_ids.update throughout this func based on file_search_context search_type
            # this func is called at one of several potential points, kicking in if query_hash_ids are needed but preferring tags or system preds to step in
            
            or_predicates = list( or_predicates )
            
            # better typically to sort by fewest num of preds first, establishing query_hash_ids for longer chains
            def or_sort_key( p ):
                
                return len( p.GetValue() )
                
            
            or_predicates.sort( key = or_sort_key )
            
            for or_predicate in or_predicates:
                
                # blue eyes OR green eyes
                
                or_query_hash_ids = set()
                
                for or_subpredicate in or_predicate.GetValue():
                    
                    # blue eyes
                    
                    or_search_context = file_search_context.Duplicate()
                    
                    or_search_context.SetPredicates( [ or_subpredicate ] )
                    
                    # I pass current query_hash_ids here to make these inefficient sub-searches (like -tag) potentially much faster
                    or_query_hash_ids.update( self._GetHashIdsFromQuery( or_search_context, job_key, query_hash_ids = query_hash_ids ) )
                    
                    if job_key.IsCancelled():
                        
                        return set()
                        
                    
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, or_query_hash_ids )
                
            
            return query_hash_ids
            
        
        #
        
        done_or_predicates = False
        
        # OR round one--if nothing else will be fast, let's prep query_hash_ids now
        if not ( there_are_tags_to_search or there_are_simple_files_info_preds_to_search_for ):
            
            if len( or_predicates ) > 0:
                
                query_hash_ids = do_or_preds( or_predicates, query_hash_ids )
                
                have_cross_referenced_file_service = True
                
            
            done_or_predicates = True
            
        
        #
        
        if 'hash' in simple_preds:
            
            specific_hash_ids = set()
            
            ( search_hashes, search_hash_type ) = simple_preds[ 'hash' ]
            
            if search_hash_type == 'sha256':
                
                matching_sha256_hashes = [ search_hash for search_hash in search_hashes if self._HashExists( search_hash ) ]
                
            else:
                
                matching_sha256_hashes = self._GetFileHashes( search_hashes, search_hash_type, 'sha256' )
                
            
            specific_hash_ids = self._GetHashIds( matching_sha256_hashes )
            
            query_hash_ids = intersection_update_qhi( query_hash_ids, specific_hash_ids )
            
        
        #
        
        modified_timestamp_predicates = []
        
        if 'min_modified_timestamp' in simple_preds: modified_timestamp_predicates.append( 'file_modified_timestamp >= ' + str( simple_preds[ 'min_modified_timestamp' ] ) )
        if 'max_modified_timestamp' in simple_preds: modified_timestamp_predicates.append( 'file_modified_timestamp <= ' + str( simple_preds[ 'max_modified_timestamp' ] ) )
        
        if len( modified_timestamp_predicates ) > 0:
            
            pred_string = ' AND '.join( modified_timestamp_predicates )
            
            modified_timestamp_hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM file_modified_timestamps WHERE {};'.format( pred_string ) ) )
            
            query_hash_ids = intersection_update_qhi( query_hash_ids, modified_timestamp_hash_ids )
            
        
        #
        
        if system_predicates.HasSimilarTo():
            
            ( similar_to_hashes, max_hamming ) = system_predicates.GetSimilarTo()
            
            all_similar_hash_ids = set()
            
            for similar_to_hash in similar_to_hashes:
                
                hash_id = self._GetHashId( similar_to_hash )
                
                similar_hash_ids_and_distances = self._PHashesSearch( hash_id, max_hamming )
                
                similar_hash_ids = [ similar_hash_id for ( similar_hash_id, distance ) in similar_hash_ids_and_distances ]
                
                all_similar_hash_ids.update( similar_hash_ids )
                
            
            query_hash_ids = intersection_update_qhi( query_hash_ids, all_similar_hash_ids )
            
        
        for ( operator, value, rating_service_key ) in system_predicates.GetRatingsPredicates():
            
            service_id = self._GetServiceId( rating_service_key )
            
            if value == 'not rated':
                
                continue
                
            
            if value == 'rated':
                
                rating_hash_ids = self._STI( self._c.execute( 'SELECT hash_id FROM local_ratings WHERE service_id = ?;', ( service_id, ) ) )
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, rating_hash_ids )
                
            else:
                
                service = HG.client_controller.services_manager.GetService( rating_service_key )
                
                if service.GetServiceType() == HC.LOCAL_RATING_LIKE:
                    
                    half_a_star_value = 0.5
                    
                else:
                    
                    num_stars = service.GetNumStars()
                    
                    if service.AllowZero():
                        
                        num_stars += 1
                        
                    
                    half_a_star_value = 1.0 / ( ( num_stars - 1 ) * 2 )
                    
                
                if isinstance( value, str ):
                    
                    value = float( value )
                    
                
                # floats are a pain! as is storing rating as 0.0-1.0 and then allowing number of stars to change!
                
                if operator == '\u2248':
                    
                    predicate = str( ( value - half_a_star_value ) * 0.8 ) + ' < rating AND rating < ' + str( ( value + half_a_star_value ) * 1.2 )
                    
                elif operator == '<':
                    
                    predicate = 'rating <= ' + str( value - half_a_star_value )
                    
                elif operator == '>':
                    
                    predicate = 'rating > ' + str( value + half_a_star_value )
                    
                elif operator == '=':
                    
                    predicate = str( value - half_a_star_value ) + ' < rating AND rating <= ' + str( value + half_a_star_value )
                    
                
                rating_hash_ids = self._STI( self._c.execute( 'SELECT hash_id FROM local_ratings WHERE service_id = ? AND ' + predicate + ';', ( service_id, ) ) )
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, rating_hash_ids )
                
            
        
        is_inbox = system_predicates.MustBeInbox()
        
        if is_inbox:
            
            query_hash_ids = intersection_update_qhi( query_hash_ids, self._inbox_hash_ids, force_create_new_set = True )
            
        
        for ( operator, num_relationships, dupe_type ) in system_predicates.GetDuplicateRelationshipCountPredicates():
            
            only_do_zero = ( operator in ( '=', '\u2248' ) and num_relationships == 0 ) or ( operator == '<' and num_relationships == 1 )
            include_zero = operator == '<'
            
            if only_do_zero:
                
                continue
                
            elif include_zero:
                
                continue
                
            else:
                
                dupe_hash_ids = self._DuplicatesGetHashIdsFromDuplicateCountPredicate( file_service_key, operator, num_relationships, dupe_type )
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, dupe_hash_ids )
                
                have_cross_referenced_file_service = True
                
            
        
        for ( view_type, viewing_locations, operator, viewing_value ) in system_predicates.GetFileViewingStatsPredicates():
            
            only_do_zero = ( operator in ( '=', '\u2248' ) and viewing_value == 0 ) or ( operator == '<' and viewing_value == 1 )
            include_zero = operator == '<'
            
            if only_do_zero:
                
                continue
                
            elif include_zero:
                
                continue
                
            else:
                
                viewing_hash_ids = self._GetHashIdsFromFileViewingStatistics( view_type, viewing_locations, operator, viewing_value )
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, viewing_hash_ids )
                
            
        
        # first tags
        
        if there_are_tags_to_search:
            
            def sort_longest_first_key( s ):
                
                return -len( s )
                
            
            tags_to_include = list( tags_to_include )
            
            tags_to_include.sort( key = sort_longest_first_key )
            
            for tag in tags_to_include:
                
                if query_hash_ids is None:
                    
                    tag_query_hash_ids = self._GetHashIdsFromTag( file_service_key, tag_service_key, tag, include_current_tags, include_pending_tags )
                    
                elif is_inbox and len( query_hash_ids ) == len( self._inbox_hash_ids ):
                    
                    tag_query_hash_ids = self._GetHashIdsFromTag( file_service_key, tag_service_key, tag, include_current_tags, include_pending_tags, hash_ids_table_name = 'file_inbox' )
                    
                else:
                    
                    with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                        
                        self._AnalyzeTempTable( temp_table_name )
                        
                        tag_query_hash_ids = self._GetHashIdsFromTag( file_service_key, tag_service_key, tag, include_current_tags, include_pending_tags, hash_ids_table_name = temp_table_name )
                        
                    
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, tag_query_hash_ids )
                
                have_cross_referenced_file_service = True
                
                if query_hash_ids == set():
                    
                    return query_hash_ids
                    
                
            
            for namespace in namespaces_to_include:
                
                if query_hash_ids is None:
                    
                    namespace_query_hash_ids = self._GetHashIdsFromNamespace( file_service_key, tag_search_context, namespace, include_siblings = True )
                    
                elif is_inbox and len( query_hash_ids ) == len( self._inbox_hash_ids ):
                    
                    namespace_query_hash_ids = self._GetHashIdsFromNamespace( file_service_key, tag_search_context, namespace, include_siblings = True, hash_ids_table_name = 'file_inbox' )
                    
                else:
                    
                    with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                        
                        self._AnalyzeTempTable( temp_table_name )
                        
                        namespace_query_hash_ids = self._GetHashIdsFromNamespace( file_service_key, tag_search_context, namespace, include_siblings = True, hash_ids_table_name = temp_table_name )
                        
                    
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, namespace_query_hash_ids )
                
                have_cross_referenced_file_service = True
                
                if query_hash_ids == set():
                    
                    return query_hash_ids
                    
                
            
            for wildcard in wildcards_to_include:
                
                if query_hash_ids is None:
                    
                    wildcard_query_hash_ids = self._GetHashIdsFromWildcard( file_service_key, tag_service_key, wildcard, include_current_tags, include_pending_tags )
                    
                elif is_inbox and len( query_hash_ids ) == len( self._inbox_hash_ids ):
                    
                    wildcard_query_hash_ids = self._GetHashIdsFromWildcard( file_service_key, tag_service_key, wildcard, include_current_tags, include_pending_tags, hash_ids_table_name = 'file_inbox' )
                    
                else:
                    
                    with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                        
                        self._AnalyzeTempTable( temp_table_name )
                        
                        wildcard_query_hash_ids = self._GetHashIdsFromWildcard( file_service_key, tag_service_key, wildcard, include_current_tags, include_pending_tags, hash_ids_table_name = temp_table_name )
                        
                    
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, wildcard_query_hash_ids )
                
                have_cross_referenced_file_service = True
                
                if query_hash_ids == set():
                    
                    return query_hash_ids
                    
                
            
        
        #
        
        # OR round two--if file preds will not be fast, let's step in to reduce the file domain search space
        if not ( there_are_simple_files_info_preds_to_search_for or done_or_predicates ):
            
            if len( or_predicates ) > 0:
                
                query_hash_ids = do_or_preds( or_predicates, query_hash_ids )
                
                have_cross_referenced_file_service = True
                
            
            done_or_predicates = True
            
        
        # now the simple preds and desperate last shot to populate query_hash_ids
        
        done_files_info_predicates = False
        
        we_need_some_results = query_hash_ids is None
        we_need_to_cross_reference = file_service_key != CC.COMBINED_FILE_SERVICE_KEY and not have_cross_referenced_file_service
        
        if we_need_some_results or we_need_to_cross_reference:
            
            if file_service_key == CC.COMBINED_FILE_SERVICE_KEY:
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, self._GetHashIdsThatHaveTags( tag_service_key, include_current_tags, include_pending_tags ) )
                
            else:
                
                files_info_predicates.insert( 0, 'service_id = ' + str( file_service_id ) )
                
                if query_hash_ids is None:
                    
                    query_hash_ids = intersection_update_qhi( query_hash_ids, self._STS( self._c.execute( 'SELECT hash_id FROM current_files NATURAL JOIN files_info WHERE {};'.format( ' AND '.join( files_info_predicates ) ) ) ) )
                    
                else:
                    
                    if is_inbox and len( query_hash_ids ) == len( self._inbox_hash_ids ):
                        
                        query_hash_ids = intersection_update_qhi( query_hash_ids, self._STS( self._c.execute( 'SELECT hash_id FROM current_files NATURAL JOIN files_info NATURAL JOIN {} WHERE {};'.format( 'file_inbox', ' AND '.join( files_info_predicates ) ) ) ) )
                        
                    else:
                        
                        with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                            
                            self._AnalyzeTempTable( temp_table_name )
                            
                            query_hash_ids = intersection_update_qhi( query_hash_ids, self._STS( self._c.execute( 'SELECT hash_id FROM current_files NATURAL JOIN files_info NATURAL JOIN {} WHERE {};'.format( temp_table_name, ' AND '.join( files_info_predicates ) ) ) ) )
                            
                        
                    
                
                have_cross_referenced_file_service = True
                done_files_info_predicates = True
                
            
        
        # at this point, query_hash_ids has something in it
        
        if system_predicates.MustBeArchive():
            
            query_hash_ids.difference_update( self._inbox_hash_ids )
            
        
        if king_filter is not None and king_filter:
            
            king_hash_ids = self._DuplicatesFilterKingHashIds( query_hash_ids )
            
            query_hash_ids = intersection_update_qhi( query_hash_ids, king_hash_ids )
            
        
        if not done_files_info_predicates and ( need_file_domain_cross_reference or there_are_simple_files_info_preds_to_search_for ):
            
            with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                
                self._AnalyzeTempTable( temp_table_name )
                
                if file_service_key == CC.COMBINED_FILE_SERVICE_KEY:
                    
                    table = 'files_info'
                    
                else:
                    
                    table = 'current_files NATURAL JOIN files_info'
                    
                    files_info_predicates.insert( 0, 'service_id = ' + str( file_service_id ) )
                    
                
                table += ' NATURAL JOIN {}'.format( temp_table_name )
                
                if there_are_simple_files_info_preds_to_search_for:
                    
                    predicate_string = ' WHERE {}'.format( ' AND '.join( files_info_predicates ) )
                    
                else:
                    
                    predicate_string = ''
                    
                
                select = 'SELECT hash_id FROM {}{};'.format( table, predicate_string )
                
                files_info_hash_ids = self._STI( self._c.execute( select ) )
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, files_info_hash_ids )
                
            
            done_files_info_predicates = True
            
        
        if job_key.IsCancelled():
            
            return set()
            
        
        #
        
        # OR round three--final chance to kick in, and the preferred one. query_hash_ids is now set, so this shouldn't be super slow for most scenarios
        if not done_or_predicates:
            
            query_hash_ids = do_or_preds( or_predicates, query_hash_ids )
            
            done_or_predicates = True
            
        
        # hide update files
        
        if file_service_key == CC.COMBINED_LOCAL_FILE_SERVICE_KEY:
            
            repo_update_hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM current_files NATURAL JOIN files_info WHERE service_id = ?;', ( self._local_update_service_id, ) ) )
            
            query_hash_ids.difference_update( repo_update_hash_ids )
            
        
        # now subtract bad results
        
        for tag in tags_to_exclude:
            
            with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                
                self._AnalyzeTempTable( temp_table_name )
                
                unwanted_hash_ids = self._GetHashIdsFromTag( file_service_key, tag_service_key, tag, include_current_tags, include_pending_tags, hash_ids_table_name = temp_table_name )
                
                query_hash_ids.difference_update( unwanted_hash_ids )
                
            
            if len( query_hash_ids ) == 0:
                
                return query_hash_ids
                
            
        
        for namespace in namespaces_to_exclude:
            
            with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                
                self._AnalyzeTempTable( temp_table_name )
                
                unwanted_hash_ids = self._GetHashIdsFromNamespace( file_service_key, tag_search_context, namespace, include_siblings = True, hash_ids_table_name = temp_table_name )
                
                query_hash_ids.difference_update( unwanted_hash_ids )
                
            
            if len( query_hash_ids ) == 0:
                
                return query_hash_ids
                
            
        
        for wildcard in wildcards_to_exclude:
            
            with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                
                self._AnalyzeTempTable( temp_table_name )
                
                unwanted_hash_ids = self._GetHashIdsFromWildcard( file_service_key, tag_service_key, wildcard, include_current_tags, include_pending_tags, hash_ids_table_name = temp_table_name )
                
                query_hash_ids.difference_update( unwanted_hash_ids )
                
            
            if len( query_hash_ids ) == 0:
                
                return query_hash_ids
                
            
        
        if job_key.IsCancelled():
            
            return set()
            
        
        #
        
        ( file_services_to_include_current, file_services_to_include_pending, file_services_to_exclude_current, file_services_to_exclude_pending ) = system_predicates.GetFileServiceInfo()
        
        for service_key in file_services_to_include_current:
            
            service_id = self._GetServiceId( service_key )
            
            query_hash_ids = intersection_update_qhi( query_hash_ids, self._STI( self._c.execute( 'SELECT hash_id FROM current_files WHERE service_id = ?;', ( service_id, ) ) ) )
            
        
        for service_key in file_services_to_include_pending:
            
            service_id = self._GetServiceId( service_key )
            
            query_hash_ids = intersection_update_qhi( query_hash_ids, self._STI( self._c.execute( 'SELECT hash_id FROM file_transfers WHERE service_id = ?;', ( service_id, ) ) ) )
            
        
        for service_key in file_services_to_exclude_current:
            
            service_id = self._GetServiceId( service_key )
            
            query_hash_ids.difference_update( self._STI( self._c.execute( 'SELECT hash_id FROM current_files WHERE service_id = ?;', ( service_id, ) ) ) )
            
        
        for service_key in file_services_to_exclude_pending:
            
            service_id = self._GetServiceId( service_key )
            
            query_hash_ids.difference_update( self._STI( self._c.execute( 'SELECT hash_id FROM file_transfers WHERE service_id = ?;', ( service_id, ) ) ) )
            
        
        #
        
        for ( operator, value, service_key ) in system_predicates.GetRatingsPredicates():
            
            service_id = self._GetServiceId( service_key )
            
            if value == 'not rated':
                
                query_hash_ids.difference_update( self._STI( self._c.execute( 'SELECT hash_id FROM local_ratings WHERE service_id = ?;', ( service_id, ) ) ) )
                
            
        
        if king_filter is not None and not king_filter:
            
            king_hash_ids = self._DuplicatesFilterKingHashIds( query_hash_ids )
            
            query_hash_ids.difference_update( king_hash_ids )
            
        
        for ( operator, num_relationships, dupe_type ) in system_predicates.GetDuplicateRelationshipCountPredicates():
            
            only_do_zero = ( operator in ( '=', '\u2248' ) and num_relationships == 0 ) or ( operator == '<' and num_relationships == 1 )
            include_zero = operator == '<'
            
            if only_do_zero:
                
                nonzero_hash_ids = self._DuplicatesGetHashIdsFromDuplicateCountPredicate( file_service_key, '>', 0, dupe_type )
                
                query_hash_ids.difference_update( nonzero_hash_ids )
                
            elif include_zero:
                
                nonzero_hash_ids = self._DuplicatesGetHashIdsFromDuplicateCountPredicate( file_service_key, '>', 0, dupe_type )
                
                zero_hash_ids = query_hash_ids.difference( nonzero_hash_ids )
                
                accurate_except_zero_hash_ids = self._DuplicatesGetHashIdsFromDuplicateCountPredicate( file_service_key, operator, num_relationships, dupe_type )
                
                hash_ids = zero_hash_ids.union( accurate_except_zero_hash_ids )
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, hash_ids )
                
            
        
        min_num_notes = None
        max_num_notes = None
        
        if 'num_notes' in simple_preds:
            
            min_num_notes = simple_preds[ 'num_notes' ]
            max_num_notes = min_num_notes
            
        else:
            
            if 'min_num_notes' in simple_preds:
                
                min_num_notes = simple_preds[ 'min_num_notes' ] + 1
                
            if 'max_num_notes' in simple_preds:
                
                max_num_notes = simple_preds[ 'max_num_notes' ] - 1
                
            
        
        if min_num_notes is not None or max_num_notes is not None:
            
            with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                
                self._AnalyzeTempTable( temp_table_name )
                
                num_notes_hash_ids = self._GetHashIdsFromNumNotes( min_num_notes, max_num_notes, temp_table_name )
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, num_notes_hash_ids )
                
            
        
        if 'has_note_names' in simple_preds:
            
            inclusive_note_names = simple_preds[ 'has_note_names' ]
            
            for note_name in inclusive_note_names:
                
                with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                    
                    self._AnalyzeTempTable( temp_table_name )
                    
                    notes_hash_ids = self._GetHashIdsFromNoteName( note_name, temp_table_name )
                    
                    query_hash_ids = intersection_update_qhi( query_hash_ids, notes_hash_ids )
                    
                
            
        
        if 'not_has_note_names' in simple_preds:
            
            exclusive_note_names = simple_preds[ 'not_has_note_names' ]
            
            for note_name in exclusive_note_names:
                
                with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                    
                    self._AnalyzeTempTable( temp_table_name )
                    
                    notes_hash_ids = self._GetHashIdsFromNoteName( note_name, temp_table_name )
                    
                    query_hash_ids.difference_update( notes_hash_ids )
                    
                
            
        
        for ( view_type, viewing_locations, operator, viewing_value ) in system_predicates.GetFileViewingStatsPredicates():
            
            only_do_zero = ( operator in ( '=', '\u2248' ) and viewing_value == 0 ) or ( operator == '<' and viewing_value == 1 )
            include_zero = operator == '<'
            
            if only_do_zero:
                
                nonzero_hash_ids = self._GetHashIdsFromFileViewingStatistics( view_type, viewing_locations, '>', 0 )
                
                query_hash_ids.difference_update( nonzero_hash_ids )
                
            elif include_zero:
                
                nonzero_hash_ids = self._GetHashIdsFromFileViewingStatistics( view_type, viewing_locations, '>', 0 )
                
                zero_hash_ids = query_hash_ids.difference( nonzero_hash_ids )
                
                accurate_except_zero_hash_ids = self._GetHashIdsFromFileViewingStatistics( view_type, viewing_locations, operator, viewing_value )
                
                hash_ids = zero_hash_ids.union( accurate_except_zero_hash_ids )
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, hash_ids )
                
            
        
        if job_key.IsCancelled():
            
            return set()
            
        
        #
        
        must_be_local = system_predicates.MustBeLocal() or system_predicates.MustBeArchive()
        must_not_be_local = system_predicates.MustNotBeLocal()
        
        if file_service_type in HC.LOCAL_FILE_SERVICES:
            
            if must_not_be_local:
                
                query_hash_ids = set()
                
            
        elif must_be_local or must_not_be_local:
            
            local_hash_ids = self._STL( self._c.execute( 'SELECT hash_id FROM current_files WHERE service_id = ?;', ( self._combined_local_file_service_id, ) ) )
            
            if must_be_local:
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, local_hash_ids )
                
            elif must_not_be_local:
                
                query_hash_ids.difference_update( local_hash_ids )
                
            
        
        #
        
        if 'known_url_rules' in simple_preds:
            
            for ( operator, rule_type, rule ) in simple_preds[ 'known_url_rules' ]:
                
                if rule_type == 'exact_match':
                    
                    url_hash_ids = self._GetHashIdsFromURLRule( rule_type, rule )
                    
                else:
                    
                    with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                        
                        self._AnalyzeTempTable( temp_table_name )
                        
                        url_hash_ids = self._GetHashIdsFromURLRule( rule_type, rule, hash_ids_table_name = temp_table_name )
                        
                    
                
                if operator: # inclusive
                    
                    query_hash_ids = intersection_update_qhi( query_hash_ids, url_hash_ids )
                    
                else:
                    
                    query_hash_ids.difference_update( url_hash_ids )
                    
                
            
        
        #
        
        num_tags_zero = False
        num_tags_nonzero = False
        
        tag_predicates = []
        
        if 'min_num_tags' in simple_preds:
            
            min_num_tags = simple_preds[ 'min_num_tags' ]
            
            if min_num_tags == 0:
                
                num_tags_nonzero = True
                
            else:
                
                tag_predicates.append( lambda x: x > min_num_tags )
                
            
        
        if 'num_tags' in simple_preds:
            
            num_tags = simple_preds[ 'num_tags' ]
            
            if num_tags == 0:
                
                num_tags_zero = True
                
            else:
                
                tag_predicates.append( lambda x: x == num_tags )
                
            
        
        if 'max_num_tags' in simple_preds:
            
            max_num_tags = simple_preds[ 'max_num_tags' ]
            
            if max_num_tags == 1:
                
                num_tags_zero = True
                
            else:
                
                tag_predicates.append( lambda x: x < max_num_tags )
                
            
        
        tag_predicates_care_about_zero_counts = len( tag_predicates ) > 0 and False not in ( pred( 0 ) for pred in tag_predicates )
        
        if num_tags_zero or num_tags_nonzero or tag_predicates_care_about_zero_counts:
            
            nonzero_tag_query_hash_ids = self._GetHashIdsThatHaveTags( tag_service_key, include_current_tags, include_pending_tags, query_hash_ids )
            
            if num_tags_zero:
                
                query_hash_ids.difference_update( nonzero_tag_query_hash_ids )
                
            elif num_tags_nonzero:
                
                query_hash_ids = intersection_update_qhi( query_hash_ids, nonzero_tag_query_hash_ids )
                
            
        
        if len( tag_predicates ) > 0:
            
            hash_id_tag_counts = self._GetHashIdsTagCounts( tag_service_key, include_current_tags, include_pending_tags, query_hash_ids )
            
            good_tag_count_hash_ids = { id for ( id, count ) in hash_id_tag_counts if False not in ( pred( count ) for pred in tag_predicates ) }
            
            if tag_predicates_care_about_zero_counts:
                
                zero_hash_ids = query_hash_ids.difference( nonzero_tag_query_hash_ids )
                
                good_tag_count_hash_ids.update( zero_hash_ids )
                
            
            query_hash_ids = intersection_update_qhi( query_hash_ids, good_tag_count_hash_ids )
            
        
        if job_key.IsCancelled():
            
            return set()
            
        
        #
        
        if 'min_tag_as_number' in simple_preds:
            
            ( namespace, num ) = simple_preds[ 'min_tag_as_number' ]
            
            with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                
                self._AnalyzeTempTable( temp_table_name )
                
                good_hash_ids = self._GetHashIdsThatHaveTagAsNum( file_service_key, tag_service_key, namespace, num, '>', include_current_tags, include_pending_tags, hash_ids_table_name = temp_table_name )
                
            
            query_hash_ids = intersection_update_qhi( query_hash_ids, good_hash_ids )
            
        
        if 'max_tag_as_number' in simple_preds:
            
            ( namespace, num ) = simple_preds[ 'max_tag_as_number' ]
            
            with HydrusDB.TemporaryIntegerTable( self._c, query_hash_ids, 'hash_id' ) as temp_table_name:
                
                self._AnalyzeTempTable( temp_table_name )
                
                good_hash_ids = self._GetHashIdsThatHaveTagAsNum( file_service_key, tag_service_key, namespace, num, '<', include_current_tags, include_pending_tags, hash_ids_table_name = temp_table_name )
                
            
            query_hash_ids = intersection_update_qhi( query_hash_ids, good_hash_ids )
            
        
        if job_key.IsCancelled():
            
            return set()
            
        
        #
        
        query_hash_ids = list( query_hash_ids )
        
        #
        
        limit = system_predicates.GetLimit( apply_implicit_limit = apply_implicit_limit )
        
        we_are_applying_limit = limit is not None and limit < len( query_hash_ids )
        
        if we_are_applying_limit and limit_sort_by is not None and sort_by is None:
            
            sort_by = limit_sort_by
            
        
        did_sort = False
        
        if sort_by is not None and file_service_id != self._combined_file_service_id:
            
            ( did_sort, query_hash_ids ) = self._TryToSortHashIds( file_service_id, query_hash_ids, sort_by )
            
        
        #
        
        if we_are_applying_limit:
            
            if not did_sort:
                
                query_hash_ids = random.sample( query_hash_ids, limit )
                
            else:
                
                query_hash_ids = query_hash_ids[:limit]
                
            
        
        return query_hash_ids
        
    
    def _GetHashIdsFromSubtagIds( self, file_service_key, tag_service_key, subtag_ids, include_current_tags, include_pending_tags, hash_ids_table_name = None ):
        
        file_service_id = self._GetServiceId( file_service_key )
        
        if tag_service_key == CC.COMBINED_TAG_SERVICE_KEY:
            
            search_tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
        else:
            
            search_tag_service_ids = [ self._GetServiceId( tag_service_key ) ]
            
        
        tables = self._GetMappingTables( file_service_id, search_tag_service_ids, include_current_tags, include_pending_tags )
        
        hash_ids = set()
        
        with HydrusDB.TemporaryIntegerTable( self._c, subtag_ids, 'subtag_id' ) as subtag_temp_table_name:
            
            self._AnalyzeTempTable( subtag_temp_table_name )
            
            tables = [ table + ' NATURAL JOIN tags NATURAL JOIN {}'.format( subtag_temp_table_name ) for table in tables ]
            
            if hash_ids_table_name is not None:
                
                tables = [ table + ' NATURAL JOIN {}'.format( hash_ids_table_name ) for table in tables ]
                
            
            for table in tables:
                
                select = 'SELECT DISTINCT hash_id FROM {};'.format( table )
                
                hash_ids.update( self._STI( self._c.execute( select ) ) )
                
            
        
        return hash_ids
        
    
    def _GetHashIdsFromTag( self, file_service_key, tag_service_key, search_tag, include_current_tags, include_pending_tags, hash_ids_table_name = None ):
        
        siblings_manager = self._controller.tag_siblings_manager
        
        tags = siblings_manager.GetAllSiblings( tag_service_key, search_tag )
        
        predicate_strings = []
        
        for tag in tags:
            
            ( namespace, subtag ) = HydrusTags.SplitTag( tag )
            
            # "tag != search_tag" here because if a sibling is unnamespaced of a namespaced search, we end up getting all namespaced versions of that unnamespaced tag!!
            # e.g. search 'character:samus aran'
            # 'samus aran' is a sibling
            # we hence search anything:samus aran!
            
            if namespace != '' or tag != search_tag:
                
                if not self._TagExists( tag ):
                    
                    continue
                    
                
                namespace_id = self._GetNamespaceId( namespace )
                subtag_id = self._GetSubtagId( subtag )
                
                predicate_strings.append( 'namespace_id = {} AND subtag_id = {}'.format( namespace_id, subtag_id ) )
                
            else:
                
                if not self._SubtagExists( subtag ):
                    
                    continue
                    
                
                subtag_id = self._GetSubtagId( subtag )
                
                predicate_strings.append( 'subtag_id = {}'.format( subtag_id ) )
                
            
        
        file_service_id = self._GetServiceId( file_service_key )
        
        if tag_service_key == CC.COMBINED_TAG_SERVICE_KEY:
            
            search_tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
        else:
            
            search_tag_service_ids = [ self._GetServiceId( tag_service_key ) ]
            
        
        tables = self._GetMappingTables( file_service_id, search_tag_service_ids, include_current_tags, include_pending_tags )
        
        tables = [ table + ' NATURAL JOIN tags' for table in tables ]
        
        if hash_ids_table_name is not None:
            
            tables = [ table + ' NATURAL JOIN {}'.format( hash_ids_table_name ) for table in tables ]
            
        
        #
        
        hash_ids = set()
        
        for ( table, predicate_string ) in itertools.product( tables, predicate_strings ):
            
            select = 'SELECT hash_id FROM {} WHERE {};'.format( table, predicate_string )
            
            hash_ids.update( self._STI( self._c.execute( select ) ) )
            
        
        return hash_ids
        
    
    def _GetHashIdsFromURLRule( self, rule_type, rule, hash_ids_table_name = None ):
        
        if rule_type == 'exact_match':
            
            url = rule
            
            table = 'url_map NATURAL JOIN urls'
            
            if hash_ids_table_name is not None:
                
                table += ' NATURAL JOIN {}'.format( hash_ids_table_name )
                
            
            select = 'SELECT hash_id FROM {} WHERE url = ?;'.format( table )
            
            result_hash_ids = self._STS( self._c.execute( select, ( url, ) ) )
            
            return result_hash_ids
            
        elif rule_type in ( 'url_class', 'url_match' ):
            
            url_class = rule
            
            domain = url_class.GetDomain()
            
            if url_class.MatchesSubdomains():
                
                domain_ids = self._GetURLDomainAndSubdomainIds( domain )
                
            else:
                
                domain_ids = self._GetURLDomainAndSubdomainIds( domain, only_www_subdomains = True )
                
            
            table = 'url_map NATURAL JOIN urls'
            
            if hash_ids_table_name is not None:
                
                table += ' NATURAL JOIN {}'.format( hash_ids_table_name )
                
            
            result_hash_ids = set()
            
            with HydrusDB.TemporaryIntegerTable( self._c, domain_ids, 'domain_id' ) as domain_temp_table_name:
                
                self._AnalyzeTempTable( domain_temp_table_name )
                
                table += ' NATURAL JOIN {}'.format( domain_temp_table_name )
                
                select = 'SELECT hash_id, url FROM {};'.format( table )
                
                for ( hash_id, url ) in self._c.execute( select ):
                    
                    if url_class.Matches( url ):
                        
                        result_hash_ids.add( hash_id )
                        
                    
                
            
            return result_hash_ids
            
        elif rule_type in 'domain':
            
            domain = rule
            
            # if we search for site.com, we also want artist.site.com or www.site.com or cdn2.site.com
            domain_ids = self._GetURLDomainAndSubdomainIds( domain )
            
            result_hash_ids = set()
            
            table = 'url_map NATURAL JOIN urls'
            
            if hash_ids_table_name is not None:
                
                table += ' NATURAL JOIN {}'.format( hash_ids_table_name )
                
            
            with HydrusDB.TemporaryIntegerTable( self._c, domain_ids, 'domain_id' ) as domain_temp_table_name:
                
                self._AnalyzeTempTable( domain_temp_table_name )
                
                table += ' NATURAL JOIN {}'.format( domain_temp_table_name )
                
                select = 'SELECT hash_id FROM {};'.format( table )
                
                result_hash_ids = self._STS( self._c.execute( select ) )
                
            
            return result_hash_ids
            
        else:
            
            regex = rule
            
            table = 'url_map NATURAL JOIN urls'
            
            if hash_ids_table_name is not None:
                
                table += ' NATURAL JOIN {}'.format( hash_ids_table_name )
                
            
            select = 'SELECT hash_id, url FROM {};'.format( table )
            
            result_hash_ids = set()
            
            for ( hash_id, url ) in self._c.execute( select ):
                
                if re.search( regex, url ) is not None:
                    
                    result_hash_ids.add( hash_id )
                    
                
            
            return result_hash_ids
            
        
    
    def _GetHashIdsFromWildcard( self, file_service_key, tag_service_key, wildcard, include_current_tags, include_pending_tags, hash_ids_table_name = None ):
        
        ( namespace_wildcard, subtag_wildcard ) = HydrusTags.SplitTag( wildcard )
        
        possible_subtag_ids = self._GetSubtagIdsFromWildcard( subtag_wildcard )
        
        if namespace_wildcard != '':
            
            possible_namespace_ids = self._GetNamespaceIdsFromWildcard( namespace_wildcard )
            
            return self._GetHashIdsFromNamespaceIdsSubtagIds( file_service_key, tag_service_key, possible_namespace_ids, possible_subtag_ids, include_current_tags, include_pending_tags, hash_ids_table_name = hash_ids_table_name )
            
        else:
            
            return self._GetHashIdsFromSubtagIds( file_service_key, tag_service_key, possible_subtag_ids, include_current_tags, include_pending_tags, hash_ids_table_name = hash_ids_table_name )
            
        
    
    def _GetHashIdsTagCounts( self, tag_service_key, include_current, include_pending, hash_ids ):
        
        if tag_service_key == CC.COMBINED_TAG_SERVICE_KEY:
            
            search_tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
        else:
            
            search_tag_service_ids = [ self._GetServiceId( tag_service_key ) ]
            
        
        table_names = []
        
        for search_tag_service_id in search_tag_service_ids:
            
            ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( search_tag_service_id )
            
            if include_current:
                
                table_names.append( current_mappings_table_name )
                
            
            if include_pending:
                
                table_names.append( pending_mappings_table_name )
                
            
        
        # this is only fast because of the very simple union and the hash_id IN (blah). If you try to natural join to some table, it falls over.
        
        if len( table_names ) == 0:
            
            return []
            
    
        table_union_to_select_from = '( ' + ' UNION ALL '.join( ( 'SELECT * FROM ' + table_name for table_name in table_names ) ) + ' )'
        
        select_statement = 'SELECT hash_id, COUNT( DISTINCT tag_id ) FROM ' + table_union_to_select_from + ' WHERE hash_id = ?;'
        
        hash_id_tag_counts = list( self._ExecuteManySelectSingleParam( select_statement, hash_ids ) )
        
        return hash_id_tag_counts
        
    
    def _GetHashIdsThatHaveTags( self, tag_service_key, include_current, include_pending, hash_ids = None ):
        
        if tag_service_key == CC.COMBINED_TAG_SERVICE_KEY:
            
            search_tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
        else:
            
            search_tag_service_ids = [ self._GetServiceId( tag_service_key ) ]
            
        
        nonzero_tag_hash_ids = set()
        
        if hash_ids is None or len( hash_ids ) > 20000:
            
            for search_tag_service_id in search_tag_service_ids:
                
                ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( search_tag_service_id )
                
                if include_current:
                    
                    nonzero_tag_hash_ids.update( self._STI( self._c.execute( 'SELECT DISTINCT hash_id FROM ' + current_mappings_table_name + ';' ) ) )
                    
                
                if include_pending:
                    
                    nonzero_tag_hash_ids.update( self._STI( self._c.execute( 'SELECT DISTINCT hash_id FROM ' + pending_mappings_table_name + ';' ) ) )
                    
                
            
        else:
            
            with HydrusDB.TemporaryIntegerTable( self._c, hash_ids, 'hash_id' ) as temp_table_name:
                
                for search_tag_service_id in search_tag_service_ids:
                    
                    ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( search_tag_service_id )
                    
                    if include_current and include_pending:
                        
                        nonzero_tag_hash_ids.update( self._STI( self._c.execute( 'SELECT hash_id as h FROM ' + temp_table_name + ' WHERE EXISTS ( SELECT 1 FROM ' + current_mappings_table_name + ' WHERE hash_id = h ) OR EXISTS ( SELECT 1 FROM ' + pending_mappings_table_name + ' WHERE hash_id = h );' ) ) )
                        
                    elif include_current:
                        
                        nonzero_tag_hash_ids.update( self._STI( self._c.execute( 'SELECT hash_id as h FROM ' + temp_table_name + ' WHERE EXISTS ( SELECT 1 FROM ' + current_mappings_table_name + ' WHERE hash_id = h );' ) ) )
                        
                    elif include_pending:
                        
                        nonzero_tag_hash_ids.update( self._STI( self._c.execute( 'SELECT hash_id as h FROM ' + temp_table_name + ' WHERE EXISTS ( SELECT 1 FROM ' + pending_mappings_table_name + ' WHERE hash_id = h );' ) ) )
                        
                    
                
            
        
        return nonzero_tag_hash_ids
        
    
    def _GetHashIdsThatHaveTagAsNum( self, file_service_key, tag_service_key, namespace, num, operator, include_current_tags, include_pending_tags, hash_ids_table_name = None ):
        
        possible_subtag_ids = self._STS( self._c.execute( 'SELECT subtag_id FROM integer_subtags WHERE integer_subtag ' + operator + ' ' + str( num ) + ';' ) )
        
        if namespace == '':
            
            return self._GetHashIdsFromSubtagIds( file_service_key, tag_service_key, possible_subtag_ids, include_current_tags, include_pending_tags, hash_ids_table_name = hash_ids_table_name )
            
        else:
            
            namespace_id = self._GetNamespaceId( namespace )
            
            possible_namespace_ids = { namespace_id }
            
            return self._GetHashIdsFromNamespaceIdsSubtagIds( file_service_key, tag_service_key, possible_namespace_ids, possible_subtag_ids, include_current_tags, include_pending_tags, hash_ids_table_name = hash_ids_table_name )
            
        
    
    def _GetHashIdsToHashes( self, hash_ids = None, hashes = None ):
        
        if hash_ids is not None:
            
            self._PopulateHashIdsToHashesCache( hash_ids, exception_on_error = True )
            
            hash_ids_to_hashes = { hash_id : self._hash_ids_to_hashes_cache[ hash_id ] for hash_id in hash_ids }
            
        elif hashes is not None:
            
            hash_ids_to_hashes = { self._GetHashId( hash ) : hash for hash in hashes }
            
        
        return hash_ids_to_hashes
        
    
    def _GetHashIdStatus( self, hash_id, prefix = '' ):
        
        if prefix != '':
            
            prefix += ': '
            
        
        result = self._c.execute( 'SELECT reason_id FROM local_file_deletion_reasons WHERE hash_id = ?;', ( hash_id, ) ).fetchone()
        
        if result is None:
            
            file_deletion_reason = 'Unknown deletion reason.'
            
        else:
            
            ( reason_id, ) = result
            
            file_deletion_reason = self._GetText( reason_id )
            
        
        hash = self._GetHash( hash_id )
        
        result = self._c.execute( 'SELECT 1 FROM deleted_files WHERE service_id = ? AND hash_id = ?;', ( self._combined_local_file_service_id, hash_id ) ).fetchone()
        
        if result is not None:
            
            return ( CC.STATUS_DELETED, hash, prefix + file_deletion_reason )
            
        
        result = self._c.execute( 'SELECT timestamp FROM current_files WHERE service_id = ? AND hash_id = ?;', ( self._trash_service_id, hash_id ) ).fetchone()
        
        if result is not None:
            
            ( timestamp, ) = result
            
            note = 'Currently in trash ({}). Sent there at {}, which was {} before this check.'.format( file_deletion_reason, HydrusData.ConvertTimestampToPrettyTime( timestamp ), HydrusData.TimestampToPrettyTimeDelta( timestamp, just_now_threshold = 0 ) )
            
            return ( CC.STATUS_DELETED, hash, prefix + note )
            
        
        result = self._c.execute( 'SELECT timestamp FROM current_files WHERE service_id = ? AND hash_id = ?;', ( self._combined_local_file_service_id, hash_id ) ).fetchone()
        
        if result is not None:
            
            ( timestamp, ) = result
            
            result = self._c.execute( 'SELECT mime FROM files_info WHERE hash_id = ?;', ( hash_id, ) ).fetchone()
            
            if result is not None:
                
                ( mime, ) = result
                
                try:
                    
                    self._controller.client_files_manager.LocklessGetFilePath( hash, mime )
                    
                except HydrusExceptions.FileMissingException:
                    
                    note = 'The client believed this file was already in the db, but it was truly missing! Import will go ahead, in an attempt to fix the situation.'
                    
                    return ( CC.STATUS_UNKNOWN, hash, prefix + note )
                    
                
            
            note = 'Imported at {}, which was {} before this check.'.format( HydrusData.ConvertTimestampToPrettyTime( timestamp ), HydrusData.TimestampToPrettyTimeDelta( timestamp, just_now_threshold = 0 ) )
            
            return ( CC.STATUS_SUCCESSFUL_BUT_REDUNDANT, hash, prefix + note )
            
        
        return ( CC.STATUS_UNKNOWN, hash, '' )
        
    
    def _GetHashStatus( self, hash_type, hash, prefix = None ):
        
        if prefix is None:
            
            prefix = hash_type + ' recognised'
            
        
        if hash_type == 'sha256':
            
            if not self._HashExists( hash ):
                
                return ( CC.STATUS_UNKNOWN, hash, '' )
                
            else:
                
                hash_id = self._GetHashId( hash )
                
                return self._GetHashIdStatus( hash_id, prefix = prefix )
                
            
        else:
            
            if hash_type == 'md5':
                
                result = self._c.execute( 'SELECT hash_id FROM local_hashes WHERE md5 = ?;', ( sqlite3.Binary( hash ), ) ).fetchone()
                
            elif hash_type == 'sha1':
                
                result = self._c.execute( 'SELECT hash_id FROM local_hashes WHERE sha1 = ?;', ( sqlite3.Binary( hash ), ) ).fetchone()
                
            elif hash_type == 'sha512':
                
                result = self._c.execute( 'SELECT hash_id FROM local_hashes WHERE sha512 = ?;', ( sqlite3.Binary( hash ), ) ).fetchone()
                
            
            if result is None:
                
                return ( CC.STATUS_UNKNOWN, None, '' )
                
            else:
                
                ( hash_id, ) = result
                
                return self._GetHashIdStatus( hash_id, prefix = prefix )
                
            
        
    
    def _GetIdealClientFilesLocations( self ):
        
        locations_to_ideal_weights = {}
        
        for ( portable_location, weight ) in self._c.execute( 'SELECT location, weight FROM ideal_client_files_locations;' ):
            
            abs_location = HydrusPaths.ConvertPortablePathToAbsPath( portable_location )
            
            locations_to_ideal_weights[ abs_location ] = weight
            
        
        result = self._c.execute( 'SELECT location FROM ideal_thumbnail_override_location;' ).fetchone()
        
        if result is None:
            
            abs_ideal_thumbnail_override_location = None
            
        else:
            
            ( portable_ideal_thumbnail_override_location, ) = result
            
            abs_ideal_thumbnail_override_location = HydrusPaths.ConvertPortablePathToAbsPath( portable_ideal_thumbnail_override_location )
            
        
        return ( locations_to_ideal_weights, abs_ideal_thumbnail_override_location )
        
    
    def _GetMaintenanceDue( self, stop_time ):
        
        jobs_to_do = []
        
        # vacuum
        
        maintenance_vacuum_period_days = self._controller.new_options.GetNoneableInteger( 'maintenance_vacuum_period_days' )
        
        if maintenance_vacuum_period_days is not None:
            
            stale_time_delta = maintenance_vacuum_period_days * 86400
            
            existing_names_to_timestamps = dict( self._c.execute( 'SELECT name, timestamp FROM vacuum_timestamps;' ).fetchall() )
            
            db_names = [ name for ( index, name, path ) in self._c.execute( 'PRAGMA database_list;' ) if name not in ( 'mem', 'temp', 'durable_temp' ) ]
            
            due_names = { name for name in db_names if name not in existing_names_to_timestamps or HydrusData.TimeHasPassed( existing_names_to_timestamps[ name ] + stale_time_delta ) }
            
            possible_due_names = set()
            
            if len( due_names ) > 0:
                
                self._CloseDBCursor()
                
                try:
                    
                    for name in due_names:
                        
                        db_path = os.path.join( self._db_dir, self._db_filenames[ name ] )
                        
                        try:
                            
                            HydrusDB.CheckCanVacuum( db_path, stop_time = stop_time )
                            
                        except Exception as e:
                            
                            continue
                            
                        
                        possible_due_names.add( name )
                        
                    
                    possible_due_names = sorted( possible_due_names )
                    
                    if len( possible_due_names ) > 0:
                        
                        jobs_to_do.append( 'vacuum ' + ', '.join( possible_due_names ) )
                        
                    
                finally:
                    
                    self._InitDBCursor()
                    
                
            
        
        # analyze
        
        names_to_analyze = self._GetTableNamesDueAnalysis()
        
        if len( names_to_analyze ) > 0:
            
            jobs_to_do.append( 'analyze ' + HydrusData.ToHumanInt( len( names_to_analyze ) ) + ' tables' )
            
        
        similar_files_due = self._PHashesMaintenanceDue()
        
        if similar_files_due:
            
            jobs_to_do.append( 'similar files work' )
            
        
        return jobs_to_do
        
    
    def _GetJSONDump( self, dump_type ):
        
        result = self._c.execute( 'SELECT version, dump FROM json_dumps WHERE dump_type = ?;', ( dump_type, ) ).fetchone()
        
        if result is None:
            
            return result
            
        else:
            
            ( version, dump ) = result
            
            try:
                
                if isinstance( dump, bytes ):
                    
                    dump = str( dump, 'utf-8' )
                    
                
                serialisable_info = json.loads( dump )
                
            except:
                
                self._c.execute( 'DELETE FROM json_dumps WHERE dump_type = ?;', ( dump_type, ) )
                
                if self._in_transaction:
                    
                    self._Commit()
                    
                    self._BeginImmediate()
                    
                
                DealWithBrokenJSONDump( self._db_dir, dump, 'dump_type {}'.format( dump_type ) )
                
            
            return HydrusSerialisable.CreateFromSerialisableTuple( ( dump_type, version, serialisable_info ) )
            
        
    
    def _GetJSONDumpNamed( self, dump_type, dump_name = None, timestamp = None ):
        
        if dump_name is None:
            
            results = self._c.execute( 'SELECT dump_name, version, dump, timestamp FROM json_dumps_named WHERE dump_type = ?;', ( dump_type, ) ).fetchall()
            
            objs = []
            
            for ( dump_name, version, dump, object_timestamp ) in results:
                
                try:
                    
                    if isinstance( dump, bytes ):
                        
                        dump = str( dump, 'utf-8' )
                        
                    
                    serialisable_info = json.loads( dump )
                    
                    objs.append( HydrusSerialisable.CreateFromSerialisableTuple( ( dump_type, dump_name, version, serialisable_info ) ) )
                    
                except:
                    
                    self._c.execute( 'DELETE FROM json_dumps_named WHERE dump_type = ? AND dump_name = ? AND timestamp = ?;', ( dump_type, dump_name, object_timestamp ) )
                    
                    if self._in_transaction:
                        
                        self._Commit()
                        
                        self._BeginImmediate()
                        
                    
                    DealWithBrokenJSONDump( self._db_dir, dump, 'dump_type {} dump_name {} timestamp {}'.format( dump_type, dump_name[:10], timestamp ) )
                    
                
            
            return objs
            
        else:
            
            if timestamp is None:
                
                ( version, dump, object_timestamp ) = self._c.execute( 'SELECT version, dump, timestamp FROM json_dumps_named WHERE dump_type = ? AND dump_name = ? ORDER BY timestamp DESC;', ( dump_type, dump_name ) ).fetchone()
                
            else:
                
                ( version, dump, object_timestamp ) = self._c.execute( 'SELECT version, dump, timestamp FROM json_dumps_named WHERE dump_type = ? AND dump_name = ? AND timestamp = ?;', ( dump_type, dump_name, timestamp ) ).fetchone()
                
            
            try:
                
                if isinstance( dump, bytes ):
                    
                    dump = str( dump, 'utf-8' )
                    
                
                serialisable_info = json.loads( dump )
                
            except:
                
                self._c.execute( 'DELETE FROM json_dumps_named WHERE dump_type = ? AND dump_name = ? AND timestamp = ?;', ( dump_type, dump_name, object_timestamp ) )
                
                if self._in_transaction:
                    
                    self._Commit()
                    
                    self._BeginImmediate()
                    
                
                DealWithBrokenJSONDump( self._db_dir, dump, 'dump_type {} dump_name {} timestamp {}'.format( dump_type, dump_name[:10], object_timestamp ) )
                
            
            return HydrusSerialisable.CreateFromSerialisableTuple( ( dump_type, dump_name, version, serialisable_info ) )
            
        
    
    def _GetJSONDumpNames( self, dump_type ):
        
        names = [ name for ( name, ) in self._c.execute( 'SELECT DISTINCT dump_name FROM json_dumps_named WHERE dump_type = ?;', ( dump_type, ) ) ]
        
        return names
        
    
    def _GetJSONDumpNamesToBackupTimestamps( self, dump_type ):
        
        names_to_backup_timestamps = HydrusData.BuildKeyToListDict( self._c.execute( 'SELECT dump_name, timestamp FROM json_dumps_named WHERE dump_type = ? ORDER BY timestamp ASC;', ( dump_type, ) ) )
        
        for ( name, timestamp_list ) in list( names_to_backup_timestamps.items() ):
            
            timestamp_list.pop( -1 ) # remove the non backup timestamp
            
            if len( timestamp_list ) == 0:
                
                del names_to_backup_timestamps[ name ]
                
            
        
        return names_to_backup_timestamps
        
    
    def _GetJSONSimple( self, name ):
        
        result = self._c.execute( 'SELECT dump FROM json_dict WHERE name = ?;', ( name, ) ).fetchone()
        
        if result is None:
            
            return None
            
        
        ( dump, ) = result
        
        if isinstance( dump, bytes ):
            
            dump = str( dump, 'utf-8' )
            
        
        value = json.loads( dump )
        
        return value
        
    
    def _GetLabelId( self, label ):
        
        result = self._c.execute( 'SELECT label_id FROM labels WHERE label = ?;', ( label, ) ).fetchone()
        
        if result is None:
            
            self._c.execute( 'INSERT INTO labels ( label ) VALUES ( ? );', ( label, ) )
            
            label_id = self._c.lastrowid
            
        else:
            
            ( label_id, ) = result
            
        
        return label_id
        
    
    def _GetLastShutdownWorkTime( self ):
        
        result = self._c.execute( 'SELECT last_shutdown_work_time FROM last_shutdown_work_time;' ).fetchone()
        
        if result is None:
            
            return 0
            
        
        ( last_shutdown_work_time, ) = result
        
        return last_shutdown_work_time
        
    
    def _GetMappingTables( self, file_service_id, tag_service_ids, include_current, include_pending ):
        
        current_tables = []
        pending_tables = []
        
        for tag_service_id in tag_service_ids:
            
            if file_service_id == self._combined_file_service_id:
                
                ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( tag_service_id )
                
                current_tables.append( current_mappings_table_name )
                pending_tables.append( pending_mappings_table_name )
                
            else:
                
                ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
                
                current_tables.append( cache_current_mappings_table_name )
                pending_tables.append( cache_pending_mappings_table_name )
                
            
        
        tables = []
        
        if include_current:
            
            tables.extend( current_tables )
            
        
        if include_pending:
            
            tables.extend( pending_tables )
            
        
        return tables
        
    
    def _GetMediaResults( self, hash_ids: typing.Iterable[ int ] ):
        
        ( cached_media_results, missing_hash_ids ) = self._weakref_media_result_cache.GetMediaResultsAndMissing( hash_ids )
        
        if len( missing_hash_ids ) > 0:
            
            hash_ids = missing_hash_ids
            
            # get first detailed results
            
            self._PopulateHashIdsToHashesCache( hash_ids )
            
            with HydrusDB.TemporaryIntegerTable( self._c, hash_ids, 'hash_id' ) as temp_table_name:
                
                self._AnalyzeTempTable( temp_table_name )
                
                hash_ids_to_info = { hash_id : ClientMediaManagers.FileInfoManager( hash_id, self._hash_ids_to_hashes_cache[ hash_id ], size, mime, width, height, duration, num_frames, has_audio, num_words ) for ( hash_id, size, mime, width, height, duration, num_frames, has_audio, num_words ) in self._c.execute( 'SELECT * FROM files_info NATURAL JOIN {};'.format( temp_table_name ) ) }
                
                hash_ids_to_current_file_service_ids_and_timestamps = HydrusData.BuildKeyToListDict( ( ( hash_id, ( service_id, timestamp ) ) for ( hash_id, service_id, timestamp ) in self._c.execute( 'SELECT hash_id, service_id, timestamp FROM current_files NATURAL JOIN {};'.format( temp_table_name ) ) ) )
                
                hash_ids_to_deleted_file_service_ids = HydrusData.BuildKeyToListDict( self._c.execute( 'SELECT hash_id, service_id FROM deleted_files NATURAL JOIN {};'.format( temp_table_name ) ) )
                
                hash_ids_to_pending_file_service_ids = HydrusData.BuildKeyToListDict( self._c.execute( 'SELECT hash_id, service_id FROM file_transfers NATURAL JOIN {};'.format( temp_table_name ) ) )
                
                hash_ids_to_petitioned_file_service_ids = HydrusData.BuildKeyToListDict( self._c.execute( 'SELECT hash_id, service_id FROM file_petitions NATURAL JOIN {};'.format( temp_table_name ) ) )
                
                hash_ids_to_urls = HydrusData.BuildKeyToSetDict( self._c.execute( 'SELECT hash_id, url FROM url_map NATURAL JOIN urls NATURAL JOIN {};'.format( temp_table_name ) ) )
                
                hash_ids_to_service_ids_and_filenames = HydrusData.BuildKeyToListDict( ( ( hash_id, ( service_id, filename ) ) for ( hash_id, service_id, filename ) in self._c.execute( 'SELECT hash_id, service_id, filename FROM service_filenames NATURAL JOIN {};'.format( temp_table_name ) ) ) )
                
                hash_ids_to_local_ratings = HydrusData.BuildKeyToListDict( ( ( hash_id, ( service_id, rating ) ) for ( service_id, hash_id, rating ) in self._c.execute( 'SELECT service_id, hash_id, rating FROM local_ratings NATURAL JOIN {};'.format( temp_table_name ) ) ) )
                
                hash_ids_to_names_and_notes = HydrusData.BuildKeyToListDict( ( ( hash_id, ( name, note ) ) for ( hash_id, name, note ) in self._c.execute( 'SELECT file_notes.hash_id, label, note FROM file_notes, labels, notes, {} ON ( file_notes.name_id = labels.label_id AND file_notes.note_id = notes.note_id AND file_notes.hash_id = {}.hash_id );'.format( temp_table_name, temp_table_name ) ) ) )
                
                hash_ids_to_file_viewing_stats_managers = { hash_id : ClientMediaManagers.FileViewingStatsManager( preview_views, preview_viewtime, media_views, media_viewtime ) for ( hash_id, preview_views, preview_viewtime, media_views, media_viewtime ) in self._c.execute( 'SELECT hash_id, preview_views, preview_viewtime, media_views, media_viewtime FROM file_viewing_stats NATURAL JOIN {};'.format( temp_table_name ) ) }
                
                hash_ids_to_file_modified_timestamps = dict( self._c.execute( 'SELECT hash_id, file_modified_timestamp FROM file_modified_timestamps NATURAL JOIN {};'.format( temp_table_name ) ) )
                
            
            hash_ids_to_current_file_service_ids = { hash_id : [ file_service_id for ( file_service_id, timestamp ) in file_service_ids_and_timestamps ] for ( hash_id, file_service_ids_and_timestamps ) in list(hash_ids_to_current_file_service_ids_and_timestamps.items()) }
            
            hash_ids_to_tags_managers = self._GetForceRefreshTagsManagers( hash_ids, hash_ids_to_current_file_service_ids = hash_ids_to_current_file_service_ids )
            
            # build it
            
            service_ids_to_service_keys = { service_id : service_key for ( service_id, service_key ) in self._c.execute( 'SELECT service_id, service_key FROM services;' ) }
            
            missing_media_results = []
            
            for hash_id in hash_ids:
                
                tags_manager = hash_ids_to_tags_managers[ hash_id ]
                
                #
                
                current_file_service_keys = { service_ids_to_service_keys[ service_id ] for ( service_id, timestamp ) in hash_ids_to_current_file_service_ids_and_timestamps[ hash_id ] }
                
                deleted_file_service_keys = { service_ids_to_service_keys[ service_id ] for service_id in hash_ids_to_deleted_file_service_ids[ hash_id ] }
                
                pending_file_service_keys = { service_ids_to_service_keys[ service_id ] for service_id in hash_ids_to_pending_file_service_ids[ hash_id ] }
                
                petitioned_file_service_keys = { service_ids_to_service_keys[ service_id ] for service_id in hash_ids_to_petitioned_file_service_ids[ hash_id ] }
                
                inbox = hash_id in self._inbox_hash_ids
                
                urls = hash_ids_to_urls[ hash_id ]
                
                service_ids_to_filenames = HydrusData.BuildKeyToListDict( hash_ids_to_service_ids_and_filenames[ hash_id ] )
                
                service_keys_to_filenames = { service_ids_to_service_keys[ service_id ] : filenames for ( service_id, filenames ) in list(service_ids_to_filenames.items()) }
                
                current_file_service_keys_to_timestamps = { service_ids_to_service_keys[ service_id ] : timestamp for ( service_id, timestamp ) in hash_ids_to_current_file_service_ids_and_timestamps[ hash_id ] }
                
                if hash_id in hash_ids_to_file_modified_timestamps:
                    
                    file_modified_timestamp = hash_ids_to_file_modified_timestamps[ hash_id ]
                    
                else:
                    
                    file_modified_timestamp = None
                    
                
                locations_manager = ClientMediaManagers.LocationsManager( current_file_service_keys, deleted_file_service_keys, pending_file_service_keys, petitioned_file_service_keys, inbox, urls, service_keys_to_filenames, current_to_timestamps = current_file_service_keys_to_timestamps, file_modified_timestamp = file_modified_timestamp )
                
                #
                
                local_ratings = { service_ids_to_service_keys[ service_id ] : rating for ( service_id, rating ) in hash_ids_to_local_ratings[ hash_id ] }
                
                ratings_manager = ClientMediaManagers.RatingsManager( local_ratings )
                
                #
                
                if hash_id in hash_ids_to_names_and_notes:
                    
                    names_to_notes = dict( hash_ids_to_names_and_notes[ hash_id ] )
                    
                else:
                    
                    names_to_notes = dict()
                    
                
                notes_manager = ClientMediaManagers.NotesManager( names_to_notes )
                
                #
                
                if hash_id in hash_ids_to_file_viewing_stats_managers:
                    
                    file_viewing_stats_manager = hash_ids_to_file_viewing_stats_managers[ hash_id ]
                    
                else:
                    
                    file_viewing_stats_manager = ClientMediaManagers.FileViewingStatsManager.STATICGenerateEmptyManager()
                    
                
                #
                
                if hash_id in hash_ids_to_info:
                    
                    file_info_manager = hash_ids_to_info[ hash_id ]
                    
                else:
                    
                    hash = self._hash_ids_to_hashes_cache[ hash_id ]
                    
                    file_info_manager = ClientMediaManagers.FileInfoManager( hash_id, hash )
                    
                
                missing_media_results.append( ClientMediaResult.MediaResult( file_info_manager, tags_manager, locations_manager, ratings_manager, notes_manager, file_viewing_stats_manager ) )
                
            
            self._weakref_media_result_cache.AddMediaResults( missing_media_results )
            
            cached_media_results.extend( missing_media_results )
            
        
        media_results = cached_media_results
        
        return media_results
        
    
    def _GetMediaResultFromHash( self, hash ) -> ClientMediaResult.MediaResult:
        
        media_results = self._GetMediaResultsFromHashes( [ hash ] )
        
        return media_results[0]
        
    
    def _GetMediaResultsFromHashes( self, hashes: typing.Iterable[ bytes ], sorted: bytes = False ) -> typing.List[ ClientMediaResult.MediaResult ]:
        
        query_hash_ids = set( self._GetHashIds( hashes ) )
        
        media_results = self._GetMediaResults( query_hash_ids )
        
        if sorted:
            
            hashes_to_media_results = { media_result.GetHash() : media_result for media_result in media_results }
            
            media_results = [ hashes_to_media_results[ hash ] for hash in hashes if hash in hashes_to_media_results ]
            
        
        return media_results
        
    
    def _GetMime( self, hash_id ):
        
        result = self._c.execute( 'SELECT mime FROM files_info WHERE hash_id = ?;', ( hash_id, ) ).fetchone()
        
        if result is None:
            
            raise HydrusExceptions.FileMissingException( 'Did not have mime information for that file!' )
            
        
        ( mime, ) = result
        
        return mime
        
    
    def _GetNamespaceId( self, namespace ):
        
        if namespace == '':
            
            return self._null_namespace_id
            
        
        result = self._c.execute( 'SELECT namespace_id FROM namespaces WHERE namespace = ?;', ( namespace, ) ).fetchone()
        
        if result is None:
            
            self._c.execute( 'INSERT INTO namespaces ( namespace ) VALUES ( ? );', ( namespace, ) )
            
            namespace_id = self._c.lastrowid
            
        else:
            
            ( namespace_id, ) = result
            
        
        return namespace_id
        
    
    def _GetNamespaceIdsFromWildcard( self, namespace_wildcard ):
        
        if '*' in namespace_wildcard:
            
            like_param = ConvertWildcardToSQLiteLikeParameter( namespace_wildcard )
            
            return self._STL( self._c.execute( 'SELECT namespace_id FROM namespaces WHERE namespace LIKE ?;', ( like_param, ) ) )
            
        else:
            
            if self._NamespaceExists( namespace_wildcard ):
                
                namespace_id = self._GetNamespaceId( namespace_wildcard )
                
                return [ namespace_id ]
                
            else:
                
                return []
                
            
        
    
    def _GetNoteId( self, note ):
        
        result = self._c.execute( 'SELECT note_id FROM notes WHERE note = ?;', ( note, ) ).fetchone()
        
        if result is None:
            
            self._c.execute( 'INSERT INTO notes ( note ) VALUES ( ? );', ( note, ) )
            
            note_id = self._c.lastrowid
            
            self._c.execute( 'REPLACE INTO notes_fts4 ( docid, note ) VALUES ( ?, ? );', ( note_id, note ) )
            
        else:
            
            ( note_id, ) = result
            
        
        return note_id
        
    
    def _GetNumsPending( self ):
        
        services = self._GetServices( ( HC.TAG_REPOSITORY, HC.FILE_REPOSITORY, HC.IPFS ) )
        
        pendings = {}
        
        for service in services:
            
            service_key = service.GetServiceKey()
            service_type = service.GetServiceType()
            
            service_id = self._GetServiceId( service_key )
            
            if service_type in ( HC.FILE_REPOSITORY, HC.IPFS ):
                
                info_types = { HC.SERVICE_INFO_NUM_PENDING_FILES, HC.SERVICE_INFO_NUM_PETITIONED_FILES }
                
            elif service_type == HC.TAG_REPOSITORY:
                
                info_types = { HC.SERVICE_INFO_NUM_PENDING_MAPPINGS, HC.SERVICE_INFO_NUM_PETITIONED_MAPPINGS, HC.SERVICE_INFO_NUM_PENDING_TAG_SIBLINGS, HC.SERVICE_INFO_NUM_PETITIONED_TAG_SIBLINGS, HC.SERVICE_INFO_NUM_PENDING_TAG_PARENTS, HC.SERVICE_INFO_NUM_PETITIONED_TAG_PARENTS }
                
            
            pendings[ service_key ] = self._GetServiceInfoSpecific( service_id, service_type, info_types )
            
        
        return pendings
        
    
    def _GetOptions( self ):
        
        result = self._c.execute( 'SELECT options FROM options;' ).fetchone()
        
        if result is None:
            
            options = ClientDefaults.GetClientDefaultOptions()
            
            self._c.execute( 'INSERT INTO options ( options ) VALUES ( ? );', ( options, ) )
            
        else:
            
            ( options, ) = result
            
            default_options = ClientDefaults.GetClientDefaultOptions()
            
            for key in default_options:
                
                if key not in options: options[ key ] = default_options[ key ]
                
            
        
        return options
        
    
    def _GetPending( self, service_key ):
        
        service_id = self._GetServiceId( service_key )
        
        service = self._GetService( service_id )
        
        service_type = service.GetServiceType()
        
        client_to_server_update = HydrusNetwork.ClientToServerUpdate()
        
        if service_type in HC.REPOSITORIES:
            
            if service_type == HC.TAG_REPOSITORY:
                
                # mappings
                
                ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( service_id )
                
                pending_dict = HydrusData.BuildKeyToListDict( self._c.execute( 'SELECT tag_id, hash_id FROM ' + pending_mappings_table_name + ' ORDER BY tag_id LIMIT 100;' ) )
                
                for ( tag_id, hash_ids ) in list(pending_dict.items()):
                    
                    tag = self._GetTag( tag_id )
                    hashes = self._GetHashes( hash_ids )
                    
                    content = HydrusNetwork.Content( HC.CONTENT_TYPE_MAPPINGS, ( tag, hashes ) )
                    
                    client_to_server_update.AddContent( HC.CONTENT_UPDATE_PEND, content )
                    
                
                petitioned_dict = HydrusData.BuildKeyToListDict( [ ( ( tag_id, reason_id ), hash_id ) for ( tag_id, hash_id, reason_id ) in self._c.execute( 'SELECT tag_id, hash_id, reason_id FROM ' + petitioned_mappings_table_name + ' ORDER BY reason_id LIMIT 100;' ) ] )
                
                for ( ( tag_id, reason_id ), hash_ids ) in list(petitioned_dict.items()):
                    
                    tag = self._GetTag( tag_id )
                    hashes = self._GetHashes( hash_ids )
                    
                    reason = self._GetText( reason_id )
                    
                    content = HydrusNetwork.Content( HC.CONTENT_TYPE_MAPPINGS, ( tag, hashes ) )
                    
                    client_to_server_update.AddContent( HC.CONTENT_UPDATE_PETITION, content, reason )
                    
                
                # tag parents
                
                pending = self._c.execute( 'SELECT child_tag_id, parent_tag_id, reason_id FROM tag_parent_petitions WHERE service_id = ? AND status = ? ORDER BY reason_id LIMIT 1;', ( service_id, HC.CONTENT_STATUS_PENDING ) ).fetchall()
                
                for ( child_tag_id, parent_tag_id, reason_id ) in pending:
                    
                    child_tag = self._GetTag( child_tag_id )
                    parent_tag = self._GetTag( parent_tag_id )
                    
                    reason = self._GetText( reason_id )
                    
                    content = HydrusNetwork.Content( HC.CONTENT_TYPE_TAG_PARENTS, ( child_tag, parent_tag ) )
                    
                    client_to_server_update.AddContent( HC.CONTENT_UPDATE_PEND, content, reason )
                    
                
                petitioned = self._c.execute( 'SELECT child_tag_id, parent_tag_id, reason_id FROM tag_parent_petitions WHERE service_id = ? AND status = ? ORDER BY reason_id LIMIT 100;', ( service_id, HC.CONTENT_STATUS_PETITIONED ) ).fetchall()
                
                for ( child_tag_id, parent_tag_id, reason_id ) in petitioned:
                    
                    child_tag = self._GetTag( child_tag_id )
                    parent_tag = self._GetTag( parent_tag_id )
                    
                    reason = self._GetText( reason_id )
                    
                    content = HydrusNetwork.Content( HC.CONTENT_TYPE_TAG_PARENTS, ( child_tag, parent_tag ) )
                    
                    client_to_server_update.AddContent( HC.CONTENT_UPDATE_PETITION, content, reason )
                    
                
                # tag siblings
                
                pending = self._c.execute( 'SELECT bad_tag_id, good_tag_id, reason_id FROM tag_sibling_petitions WHERE service_id = ? AND status = ? ORDER BY reason_id LIMIT 100;', ( service_id, HC.CONTENT_STATUS_PENDING ) ).fetchall()
                
                for ( bad_tag_id, good_tag_id, reason_id ) in pending:
                    
                    bad_tag = self._GetTag( bad_tag_id )
                    good_tag = self._GetTag( good_tag_id )
                    
                    reason = self._GetText( reason_id )
                    
                    content = HydrusNetwork.Content( HC.CONTENT_TYPE_TAG_SIBLINGS, ( bad_tag, good_tag ) )
                    
                    client_to_server_update.AddContent( HC.CONTENT_UPDATE_PEND, content, reason )
                    
                
                petitioned = self._c.execute( 'SELECT bad_tag_id, good_tag_id, reason_id FROM tag_sibling_petitions WHERE service_id = ? AND status = ? ORDER BY reason_id LIMIT 100;', ( service_id, HC.CONTENT_STATUS_PETITIONED ) ).fetchall()
                
                for ( bad_tag_id, good_tag_id, reason_id ) in petitioned:
                    
                    bad_tag = self._GetTag( bad_tag_id )
                    good_tag = self._GetTag( good_tag_id )
                    
                    reason = self._GetText( reason_id )
                    
                    content = HydrusNetwork.Content( HC.CONTENT_TYPE_TAG_SIBLINGS, ( bad_tag, good_tag ) )
                    
                    client_to_server_update.AddContent( HC.CONTENT_UPDATE_PETITION, content, reason )
                    
                
            elif service_type == HC.FILE_REPOSITORY:
                
                result = self._c.execute( 'SELECT hash_id FROM file_transfers WHERE service_id = ?;', ( service_id, ) ).fetchone()
                
                if result is not None:
                    
                    ( hash_id, ) = result
                    
                    media_result = self._GetMediaResults( ( hash_id, ) )[ 0 ]
                    
                    return media_result
                    
                
                petitioned = list(HydrusData.BuildKeyToListDict( self._c.execute( 'SELECT reason_id, hash_id FROM file_petitions WHERE service_id = ? ORDER BY reason_id LIMIT 100;', ( service_id, ) ) ).items())
                
                for ( reason_id, hash_ids ) in petitioned:
                    
                    hashes = self._GetHashes( hash_ids )
                    
                    reason = self._GetText( reason_id )
                    
                    content = HydrusNetwork.Content( HC.CONTENT_TYPE_FILES, hashes )
                    
                    client_to_server_update.AddContent( HC.CONTENT_UPDATE_PETITION, content, reason )
                    
                
            
            if client_to_server_update.HasContent():
                
                return client_to_server_update
                
            
        elif service_type == HC.IPFS:
            
            result = self._c.execute( 'SELECT hash_id FROM file_transfers WHERE service_id = ?;', ( service_id, ) ).fetchone()
            
            if result is not None:
                
                ( hash_id, ) = result
                
                media_result = self._GetMediaResults( ( hash_id, ) )[ 0 ]
                
                return media_result
                
            
            result = self._c.execute( 'SELECT hash_id FROM file_petitions WHERE service_id = ?;', ( service_id, ) ).fetchone()
            
            if result is not None:
                
                ( hash_id, ) = result
                
                hash = self._GetHash( hash_id )
                
                multihash = self._GetServiceFilename( service_id, hash_id )
                
                return ( hash, multihash )
                
            
        
        return None
        
    
    def _GetRecentTags( self, service_key ):
        
        service_id = self._GetServiceId( service_key )
        
        # we could be clever and do LIMIT and ORDER BY in the delete, but not all compilations of SQLite have that turned on, so let's KISS
        
        tag_ids_to_timestamp = { tag_id : timestamp for ( tag_id, timestamp ) in self._c.execute( 'SELECT tag_id, timestamp FROM recent_tags WHERE service_id = ?;', ( service_id, ) ) }
        
        def sort_key( key ):
            
            return tag_ids_to_timestamp[ key ]
            
        
        newest_first = list(tag_ids_to_timestamp.keys())
        
        newest_first.sort( key = sort_key, reverse = True )
        
        num_we_want = HG.client_controller.new_options.GetNoneableInteger( 'num_recent_tags' )
        
        if num_we_want == None:
            
            num_we_want = 20
            
        
        decayed = newest_first[ num_we_want : ]
        
        if len( decayed ) > 0:
            
            self._c.executemany( 'DELETE FROM recent_tags WHERE service_id = ? AND tag_id = ?;', ( ( service_id, tag_id ) for tag_id in decayed ) )
            
        
        sorted_recent_tag_ids = newest_first[ : num_we_want ]
        
        self._PopulateTagIdsToTagsCache( sorted_recent_tag_ids )
        
        sorted_recent_tags = [ self._tag_ids_to_tags_cache[ tag_id ] for tag_id in sorted_recent_tag_ids ]
        
        return sorted_recent_tags
        
    
    def _GetRelatedTags( self, service_key, skip_hash, search_tags, max_results, max_time_to_take ):
        
        siblings_manager = HG.client_controller.tag_siblings_manager
        
        stop_time_for_finding_files = HydrusData.GetNowPrecise() + ( max_time_to_take / 2 )
        stop_time_for_finding_tags = HydrusData.GetNowPrecise() + ( max_time_to_take / 2 )
        
        search_tags = siblings_manager.CollapseTags( service_key, search_tags, service_strict = True )
        
        service_id = self._GetServiceId( service_key )
        
        skip_hash_id = self._GetHashId( skip_hash )
        
        ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( service_id )
        
        tag_ids = [ self._GetTagId( tag ) for tag in search_tags ]
        
        random.shuffle( tag_ids )
        
        hash_ids_counter = collections.Counter()
        
        query = self._c.execute( 'SELECT hash_id FROM ' + current_mappings_table_name + ' WHERE tag_id IN ' + HydrusData.SplayListForDB( tag_ids ) + ';' )
        
        results = self._STL( query.fetchmany( 100 ) )
        
        while len( results ) > 0:
            
            for hash_id in results:
                
                hash_ids_counter[ hash_id ] += 1
                
            
            if HydrusData.TimeHasPassedPrecise( stop_time_for_finding_files ):
                
                break
                
            
            results = self._STL( query.fetchmany( 100 ) )
            
        
        if skip_hash_id in hash_ids_counter:
            
            del hash_ids_counter[ skip_hash_id ]
            
        
        #
        
        if len( hash_ids_counter ) == 0:
            
            return []
            
        
        # this stuff is often 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.....
        # the 1 stuff often produces large quantities of the same very popular tag, so your search for [ 'eva', 'female' ] will produce 'touhou' because so many 2hu images have 'female'
        # so we want to do a 'soft' intersect, only picking the files that have the greatest number of shared search_tags
        # this filters to only the '2' results, which gives us eva females and their hair colour and a few choice other popular tags for that particular domain
        
        [ ( gumpf, largest_count ) ] = hash_ids_counter.most_common( 1 )
        
        hash_ids = [ hash_id for ( hash_id, count ) in hash_ids_counter.items() if count > largest_count * 0.8 ]
        
        counter = collections.Counter()
        
        random.shuffle( hash_ids )
        
        for hash_id in hash_ids:
            
            for tag_id in self._STI( self._c.execute( 'SELECT tag_id FROM ' + current_mappings_table_name + ' WHERE hash_id = ?;', ( hash_id, ) ) ):
                
                counter[ tag_id ] += 1
                
            
            if HydrusData.TimeHasPassedPrecise( stop_time_for_finding_tags ):
                
                break
                
            
        
        #
        
        for tag_id in tag_ids:
            
            if tag_id in counter:
                
                del counter[ tag_id ]
                
            
        
        results = counter.most_common( max_results )
        
        tags_to_counts = { self._GetTag( tag_id ) : count for ( tag_id, count ) in results }
        
        tags_to_counts = siblings_manager.CollapseTagsToCount( service_key, tags_to_counts )
        
        inclusive = True
        pending_count = 0
        
        predicates = [ ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_TAG, tag, inclusive, current_count, pending_count ) for ( tag, current_count ) in tags_to_counts.items() ]
        
        return predicates
        
    
    def _GetRepositoryProgress( self, service_key ):
        
        service_id = self._GetServiceId( service_key )
        
        repository_updates_table_name = GenerateRepositoryRepositoryUpdatesTableName( service_id )
        
        ( num_updates, ) = self._c.execute( 'SELECT COUNT( * ) FROM ' + repository_updates_table_name + ';' ).fetchone()
        
        ( num_processed_updates, ) = self._c.execute( 'SELECT COUNT( * ) FROM ' + repository_updates_table_name + ' WHERE processed = ?;', ( True, ) ).fetchone()
        
        ( num_local_updates, ) = self._c.execute( 'SELECT COUNT( * ) FROM current_files NATURAL JOIN ' + repository_updates_table_name + ' WHERE service_id = ?;', ( self._local_update_service_id, ) ).fetchone()
        
        return ( num_local_updates, num_processed_updates, num_updates )
        
    
    def _GetRepositoryThumbnailHashesIDoNotHave( self, service_key ):
        
        service_id = self._GetServiceId( service_key )
        
        needed_hash_ids = self._STL( self._c.execute( 'SELECT hash_id FROM current_files NATURAL JOIN files_info WHERE mime IN ' + HydrusData.SplayListForDB( HC.MIMES_WITH_THUMBNAILS ) + ' and service_id = ? EXCEPT SELECT hash_id FROM remote_thumbnails WHERE service_id = ?;', ( service_id, service_id ) ) )
        
        needed_hashes = []
        
        client_files_manager = HG.client_controller.client_files_manager
        
        for hash_id in needed_hash_ids:
            
            hash = self._GetHash( hash_id )
            
            if client_files_manager.LocklessHasThumbnail( hash ):
                
                self._c.execute( 'INSERT OR IGNORE INTO remote_thumbnails ( service_id, hash_id ) VALUES ( ?, ? );', ( service_id, hash_id ) )
                
            else:
                
                needed_hashes.append( hash )
                
                if len( needed_hashes ) == 10000:
                    
                    return needed_hashes
                    
                
            
        
        return needed_hashes
        
    
    def _GetRepositoryUpdateHashesICanProcess( self, service_key ):
        
        service_id = self._GetServiceId( service_key )
        
        repository_updates_table_name = GenerateRepositoryRepositoryUpdatesTableName( service_id )
        
        result = self._c.execute( 'SELECT 1 FROM {} NATURAL JOIN files_info WHERE mime = ? AND processed = ?;'.format( repository_updates_table_name ), ( HC.APPLICATION_HYDRUS_UPDATE_DEFINITIONS, True ) ).fetchone()
        
        this_is_first_definitions_work = result is None
        
        result = self._c.execute( 'SELECT 1 FROM {} NATURAL JOIN files_info WHERE mime = ? AND processed = ?;'.format( repository_updates_table_name ), ( HC.APPLICATION_HYDRUS_UPDATE_CONTENT, True ) ).fetchone()
        
        this_is_first_content_work = result is None
        
        update_indices_to_unprocessed_hash_ids = HydrusData.BuildKeyToSetDict( self._c.execute( 'SELECT update_index, hash_id FROM {} WHERE processed = ?;'.format( repository_updates_table_name ), ( False, ) ) )
        
        hash_ids_i_can_process = set()
        
        update_indices = sorted( update_indices_to_unprocessed_hash_ids.keys() )
        
        for update_index in update_indices:
            
            unprocessed_hash_ids = update_indices_to_unprocessed_hash_ids[ update_index ]
            
            select_statement = 'SELECT hash_id FROM current_files WHERE service_id = ? and hash_id = ?;'
            select_args_iterator = ( ( self._local_update_service_id, hash_id ) for hash_id in unprocessed_hash_ids )
            
            local_hash_ids = self._STS( self._ExecuteManySelect( select_statement, select_args_iterator ) )
            
            if unprocessed_hash_ids == local_hash_ids:
                
                hash_ids_i_can_process.update( unprocessed_hash_ids )
                
            else:
                
                break
                
            
        
        select_statement = 'SELECT hash, mime FROM files_info NATURAL JOIN hashes WHERE hash_id = ?;'
        
        definition_hashes = set()
        content_hashes = set()
        
        for ( hash, mime ) in self._ExecuteManySelectSingleParam( select_statement, hash_ids_i_can_process ):
            
            if mime == HC.APPLICATION_HYDRUS_UPDATE_DEFINITIONS:
                
                definition_hashes.add( hash )
                
            elif mime == HC.APPLICATION_HYDRUS_UPDATE_CONTENT:
                
                content_hashes.add( hash )
                
            
        
        return ( this_is_first_definitions_work, definition_hashes, this_is_first_content_work, content_hashes )
        
    
    def _GetRepositoryUpdateHashesIDoNotHave( self, service_key ):
        
        service_id = self._GetServiceId( service_key )
        
        repository_updates_table_name = GenerateRepositoryRepositoryUpdatesTableName( service_id )
        
        desired_hash_ids = self._STL( self._c.execute( 'SELECT hash_id FROM {} ORDER BY update_index ASC;'.format( repository_updates_table_name ) ) )
        
        existing_hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM current_files WHERE service_id = ?;', ( self._local_update_service_id, ) ) )
        
        needed_hash_ids = [ hash_id for hash_id in desired_hash_ids if hash_id not in existing_hash_ids ]
        
        needed_hashes = self._GetHashes( needed_hash_ids )
        
        return needed_hashes
        
    
    def _GetRepositoryUpdateHashesUnprocessed( self, service_key ):
        
        service_id = self._GetServiceId( service_key )
        
        repository_updates_table_name = GenerateRepositoryRepositoryUpdatesTableName( service_id )
        
        unprocessed_hash_ids = self._STL( self._c.execute( 'SELECT hash_id FROM {} WHERE processed = ?;'.format( repository_updates_table_name ), ( False, ) ) )
        
        hashes = self._GetHashes( unprocessed_hash_ids )
        
        return hashes
        
    
    def _GetService( self, service_id ):
        
        if service_id in self._service_cache:
            
            service = self._service_cache[ service_id ]
            
        else:
            
            result = self._c.execute( 'SELECT service_key, service_type, name, dictionary_string FROM services WHERE service_id = ?;', ( service_id, ) ).fetchone()
            
            if result is None:
                
                raise HydrusExceptions.DataMissing( 'That service does not exist!' )
                
            
            ( service_key, service_type, name, dictionary_string ) = result
            
            dictionary = HydrusSerialisable.CreateFromString( dictionary_string )
            
            service = ClientServices.GenerateService( service_key, service_type, name, dictionary )
            
            self._service_cache[ service_id ] = service
            
        
        return service
        
    
    def _GetServiceDirectoryHashes( self, service_key, dirname ):
        
        service_id = self._GetServiceId( service_key )
        directory_id = self._GetTextId( dirname )
        
        hash_ids = self._STL( self._c.execute( 'SELECT hash_id FROM service_directory_file_map WHERE service_id = ? AND directory_id = ?;', ( service_id, directory_id ) ) )
        
        hashes = self._GetHashes( hash_ids )
        
        return hashes
        
    
    def _GetServiceDirectoriesInfo( self, service_key ):
        
        service_id = self._GetServiceId( service_key )
        
        incomplete_info = self._c.execute( 'SELECT directory_id, num_files, total_size, note FROM service_directories WHERE service_id = ?;', ( service_id, ) ).fetchall()
        
        info = [ ( self._GetText( directory_id ), num_files, total_size, note ) for ( directory_id, num_files, total_size, note ) in incomplete_info ]
        
        return info
        
    
    def _GetServiceFilename( self, service_id, hash_id ):
        
        result = self._c.execute( 'SELECT filename FROM service_filenames WHERE service_id = ? AND hash_id = ?;', ( service_id, hash_id ) ).fetchone()
        
        if result is None:
            
            raise HydrusExceptions.DataMissing( 'Service filename not found!' )
            
        
        ( filename, ) = result
        
        return filename
        
    
    def _GetServiceFilenames( self, service_key, hashes ):
        
        service_id = self._GetServiceId( service_key )
        hash_ids = self._GetHashIds( hashes )
        
        result = sorted( ( filename for ( filename, ) in self._c.execute( 'SELECT filename FROM service_filenames WHERE service_id = ? AND hash_id IN ' + HydrusData.SplayListForDB( hash_ids ) + ';', ( service_id, ) ) ) )
        
        return result
        
    
    def _GetServices( self, limited_types = HC.ALL_SERVICES ):
        
        service_ids = self._STL( self._c.execute( 'SELECT service_id FROM services WHERE service_type IN ' + HydrusData.SplayListForDB( limited_types ) + ';' ) )
        
        services = [ self._GetService( service_id ) for service_id in service_ids ]
        
        return services
        
    
    def _GetServiceId( self, service_key ):
        
        result = self._c.execute( 'SELECT service_id FROM services WHERE service_key = ?;', ( sqlite3.Binary( service_key ), ) ).fetchone()
        
        if result is None:
            
            raise HydrusExceptions.DataMissing( 'Service id error in database' )
            
        
        ( service_id, ) = result
        
        return service_id
        
    
    def _GetServiceIds( self, service_types ):
        
        return self._STL( self._c.execute( 'SELECT service_id FROM services WHERE service_type IN ' + HydrusData.SplayListForDB( service_types ) + ';' ) )
        
    
    def _GetServiceInfo( self, service_key ):
        
        service_id = self._GetServiceId( service_key )
        
        service = self._GetService( service_id )
        
        service_type = service.GetServiceType()
        
        if service_type == HC.COMBINED_LOCAL_FILE:
            
            info_types = { HC.SERVICE_INFO_NUM_FILES, HC.SERVICE_INFO_NUM_VIEWABLE_FILES, HC.SERVICE_INFO_TOTAL_SIZE, HC.SERVICE_INFO_NUM_DELETED_FILES }
            
        elif service_type in ( HC.LOCAL_FILE_DOMAIN, HC.LOCAL_FILE_TRASH_DOMAIN ):
            
            info_types = { HC.SERVICE_INFO_NUM_FILES, HC.SERVICE_INFO_NUM_VIEWABLE_FILES, HC.SERVICE_INFO_TOTAL_SIZE }
            
        elif service_type == HC.FILE_REPOSITORY:
            
            info_types = { HC.SERVICE_INFO_NUM_FILES, HC.SERVICE_INFO_NUM_VIEWABLE_FILES, HC.SERVICE_INFO_TOTAL_SIZE, HC.SERVICE_INFO_NUM_DELETED_FILES }
            
        elif service_type == HC.IPFS:
            
            info_types = { HC.SERVICE_INFO_NUM_FILES, HC.SERVICE_INFO_NUM_VIEWABLE_FILES, HC.SERVICE_INFO_TOTAL_SIZE }
            
        elif service_type == HC.LOCAL_TAG:
            
            info_types = { HC.SERVICE_INFO_NUM_FILES, HC.SERVICE_INFO_NUM_TAGS, HC.SERVICE_INFO_NUM_MAPPINGS }
            
        elif service_type == HC.TAG_REPOSITORY:
            
            info_types = { HC.SERVICE_INFO_NUM_FILES, HC.SERVICE_INFO_NUM_TAGS, HC.SERVICE_INFO_NUM_MAPPINGS, HC.SERVICE_INFO_NUM_DELETED_MAPPINGS }
            
        elif service_type in ( HC.LOCAL_RATING_LIKE, HC.LOCAL_RATING_NUMERICAL ):
            
            info_types = { HC.SERVICE_INFO_NUM_FILES }
            
        elif service_type == HC.LOCAL_BOORU:
            
            info_types = { HC.SERVICE_INFO_NUM_SHARES }
            
        else:
            
            info_types = set()
            
        
        service_info = self._GetServiceInfoSpecific( service_id, service_type, info_types )
        
        return service_info
        
    
    def _GetServiceInfoSpecific( self, service_id, service_type, info_types ):
        
        info_types = set( info_types )
        
        results = { info_type : info for ( info_type, info ) in self._c.execute( 'SELECT info_type, info FROM service_info WHERE service_id = ? AND info_type IN ' + HydrusData.SplayListForDB( info_types ) + ';', ( service_id, ) ) }
        
        if len( results ) != len( info_types ):
            
            info_types_hit = list( results.keys() )
            
            info_types_missed = info_types.difference( info_types_hit )
            
            if service_type in HC.REAL_TAG_SERVICES:
                
                common_tag_info_types = { HC.SERVICE_INFO_NUM_FILES, HC.SERVICE_INFO_NUM_TAGS }
                
                if common_tag_info_types <= info_types_missed:
                    
                    ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( service_id )
                    
                    ( num_files, num_tags ) = self._c.execute( 'SELECT COUNT( DISTINCT hash_id ), COUNT( DISTINCT tag_id ) FROM ' + current_mappings_table_name + ';' ).fetchone()
                    
                    results[ HC.SERVICE_INFO_NUM_FILES ] = num_files
                    results[ HC.SERVICE_INFO_NUM_TAGS ] = num_tags
                    
                    self._c.execute( 'INSERT INTO service_info ( service_id, info_type, info ) VALUES ( ?, ?, ? );', ( service_id, HC.SERVICE_INFO_NUM_FILES, num_files ) )
                    self._c.execute( 'INSERT INTO service_info ( service_id, info_type, info ) VALUES ( ?, ?, ? );', ( service_id, HC.SERVICE_INFO_NUM_TAGS, num_tags ) )
                    
                    info_types_missed.difference_update( common_tag_info_types )
                    
                
            
            for info_type in info_types_missed:
                
                save_it = True
                
                if service_type in HC.FILE_SERVICES:
                    
                    if info_type in ( HC.SERVICE_INFO_NUM_PENDING_FILES, HC.SERVICE_INFO_NUM_PETITIONED_FILES ):
                        
                        save_it = False
                        
                    
                    if info_type == HC.SERVICE_INFO_NUM_FILES: result = self._c.execute( 'SELECT COUNT( * ) FROM current_files WHERE service_id = ?;', ( service_id, ) ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_VIEWABLE_FILES: result = self._c.execute( 'SELECT COUNT( * ) FROM current_files NATURAL JOIN files_info WHERE service_id = ? AND mime IN ' + HydrusData.SplayListForDB( HC.SEARCHABLE_MIMES ) + ';', ( service_id, ) ).fetchone()
                    elif info_type == HC.SERVICE_INFO_TOTAL_SIZE: result = self._c.execute( 'SELECT SUM( size ) FROM current_files NATURAL JOIN files_info WHERE service_id = ?;', ( service_id, ) ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_DELETED_FILES: result = self._c.execute( 'SELECT COUNT( * ) FROM deleted_files WHERE service_id = ?;', ( service_id, ) ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_PENDING_FILES: result = self._c.execute( 'SELECT COUNT( * ) FROM file_transfers WHERE service_id = ?;', ( service_id, ) ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_PETITIONED_FILES: result = self._c.execute( 'SELECT COUNT( * ) FROM file_petitions where service_id = ?;', ( service_id, ) ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_INBOX: result = self._c.execute( 'SELECT COUNT( * ) FROM file_inbox NATURAL JOIN current_files WHERE service_id = ?;', ( service_id, ) ).fetchone()
                    
                elif service_type in HC.REAL_TAG_SERVICES:
                    
                    ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( service_id )
                    
                    if info_type in ( HC.SERVICE_INFO_NUM_PENDING_TAG_SIBLINGS, HC.SERVICE_INFO_NUM_PETITIONED_TAG_SIBLINGS, HC.SERVICE_INFO_NUM_PENDING_TAG_PARENTS, HC.SERVICE_INFO_NUM_PETITIONED_TAG_PARENTS ):
                        
                        save_it = False
                        
                    
                    if info_type == HC.SERVICE_INFO_NUM_FILES: result = self._c.execute( 'SELECT COUNT( DISTINCT hash_id ) FROM ' + current_mappings_table_name + ';' ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_TAGS: result = self._c.execute( 'SELECT COUNT( DISTINCT tag_id ) FROM ' + current_mappings_table_name + ';' ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_MAPPINGS: result = self._c.execute( 'SELECT COUNT( * ) FROM ' + current_mappings_table_name + ';' ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_DELETED_MAPPINGS: result = self._c.execute( 'SELECT COUNT( * ) FROM ' + deleted_mappings_table_name + ';' ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_PENDING_MAPPINGS: result = self._c.execute( 'SELECT COUNT( * ) FROM ' + pending_mappings_table_name + ';' ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_PETITIONED_MAPPINGS: result = self._c.execute( 'SELECT COUNT( * ) FROM ' + petitioned_mappings_table_name + ';' ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_PENDING_TAG_SIBLINGS: result = self._c.execute( 'SELECT COUNT( * ) FROM tag_sibling_petitions WHERE service_id = ? AND status = ?;', ( service_id, HC.CONTENT_STATUS_PENDING ) ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_PETITIONED_TAG_SIBLINGS: result = self._c.execute( 'SELECT COUNT( * ) FROM tag_sibling_petitions WHERE service_id = ? AND status = ?;', ( service_id, HC.CONTENT_STATUS_PETITIONED ) ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_PENDING_TAG_PARENTS: result = self._c.execute( 'SELECT COUNT( * ) FROM tag_parent_petitions WHERE service_id = ? AND status = ?;', ( service_id, HC.CONTENT_STATUS_PENDING ) ).fetchone()
                    elif info_type == HC.SERVICE_INFO_NUM_PETITIONED_TAG_PARENTS: result = self._c.execute( 'SELECT COUNT( * ) FROM tag_parent_petitions WHERE service_id = ? AND status = ?;', ( service_id, HC.CONTENT_STATUS_PETITIONED ) ).fetchone()
                    
                elif service_type in ( HC.LOCAL_RATING_LIKE, HC.LOCAL_RATING_NUMERICAL ):
                    
                    if info_type == HC.SERVICE_INFO_NUM_FILES: result = self._c.execute( 'SELECT COUNT( * ) FROM local_ratings WHERE service_id = ?;', ( service_id, ) ).fetchone()
                    
                elif service_type == HC.LOCAL_BOORU:
                    
                    if info_type == HC.SERVICE_INFO_NUM_SHARES: result = self._c.execute( 'SELECT COUNT( * ) FROM yaml_dumps WHERE dump_type = ?;', ( YAML_DUMP_ID_LOCAL_BOORU, ) ).fetchone()
                    
                
                if result is None:
                    
                    info = 0
                    
                else:
                    
                    ( info, ) = result
                    
                
                if info is None:
                    
                    info = 0
                    
                
                if save_it:
                    
                    self._c.execute( 'INSERT INTO service_info ( service_id, info_type, info ) VALUES ( ?, ?, ? );', ( service_id, info_type, info ) )
                    
                
                results[ info_type ] = info
                
            
        
        return results
        
    
    def _GetSiteId( self, name ):
        
        result = self._c.execute( 'SELECT site_id FROM imageboard_sites WHERE name = ?;', ( name, ) ).fetchone()
        
        if result is None:
            
            self._c.execute( 'INSERT INTO imageboard_sites ( name ) VALUES ( ? );', ( name, ) )
            
            site_id = self._c.lastrowid
            
        else:
            
            ( site_id, ) = result
            
        
        return site_id
        
    
    def _GetSubtagId( self, subtag ):
        
        result = self._c.execute( 'SELECT subtag_id FROM subtags WHERE subtag = ?;', ( subtag, ) ).fetchone()
        
        if result is None:
            
            self._c.execute( 'INSERT INTO subtags ( subtag ) VALUES ( ? );', ( subtag, ) )
            
            subtag_id = self._c.lastrowid
            
            #
            
            subtag_searchable = ClientSearch.ConvertSubtagToSearchable( subtag )
            
            #
            
            self._c.execute( 'REPLACE INTO subtags_fts4 ( docid, subtag ) VALUES ( ?, ? );', ( subtag_id, subtag_searchable ) )
            
            #
            
            if subtag_searchable == subtag:
                
                searchable_subtag_id = subtag_id
                
            else:
                
                searchable_subtag_id = self._GetSubtagId( subtag_searchable )
                
            
            self._c.execute( 'REPLACE INTO subtags_searchable_map ( subtag_id, searchable_subtag_id ) VALUES ( ?, ? );', ( subtag_id, searchable_subtag_id ) )
            
            #
            
            if subtag.isdecimal():
                
                try:
                    
                    integer_subtag = int( subtag )
                    
                    if CanCacheInteger( integer_subtag ):
                        
                        self._c.execute( 'REPLACE INTO integer_subtags ( subtag_id, integer_subtag ) VALUES ( ?, ? );', ( subtag_id, integer_subtag ) )
                        
                    
                except ValueError:
                    
                    pass
                    
                
            
        else:
            
            ( subtag_id, ) = result
            
        
        return subtag_id
        
    
    def _GetSubtagIdsFromWildcard( self, subtag_wildcard ):
        
        if '*' in subtag_wildcard:
            
            if ClientSearch.IsComplexWildcard( subtag_wildcard ):
                
                # we search the 'searchable subtags', then link the various mappings back to real tags
                
                like_param = ConvertWildcardToSQLiteLikeParameter( subtag_wildcard )
                
                return self._STL( self._c.execute( 'SELECT subtags_searchable_map.subtag_id FROM subtags_searchable_map, subtags ON ( subtags_searchable_map.searchable_subtag_id = subtags.subtag_id ) WHERE subtag LIKE ?;', ( like_param, ) ) )
                
            else:
                
                # simple 'sam*' style subtag, so we can search fts4 no prob
                
                subtags_fts4_param = '"{}"'.format( subtag_wildcard )
                
                return self._STL( self._c.execute( 'SELECT docid FROM subtags_fts4 WHERE subtag MATCH ?;', ( subtags_fts4_param, ) ) )
                
            
        else:
            
            if self._SubtagExists( subtag_wildcard ):
                
                return self._STL( self._c.execute( 'SELECT subtags_searchable_map.subtag_id FROM subtags_searchable_map, subtags ON ( subtags_searchable_map.searchable_subtag_id = subtags.subtag_id ) WHERE subtag = ?;', ( subtag_wildcard, ) ) )
                
            else:
                
                return []
                
            
        
    
    def _GetTag( self, tag_id ):
        
        self._PopulateTagIdsToTagsCache( ( tag_id, ) )
        
        return self._tag_ids_to_tags_cache[ tag_id ]
        
    
    def _GetTagId( self, tag ):
        
        tag = HydrusTags.CleanTag( tag )
        
        HydrusTags.CheckTagNotEmpty( tag )
        
        ( namespace, subtag ) = HydrusTags.SplitTag( tag )
        
        result = self._c.execute( 'SELECT tag_id FROM tags NATURAL JOIN namespaces NATURAL JOIN subtags WHERE namespace = ? AND subtag = ?;', ( namespace, subtag ) ).fetchone()
        
        if result is None:
            
            namespace_id = self._GetNamespaceId( namespace )
            subtag_id = self._GetSubtagId( subtag )
            
            self._c.execute( 'INSERT INTO tags ( namespace_id, subtag_id ) VALUES ( ?, ? );', ( namespace_id, subtag_id ) )
            
            tag_id = self._c.lastrowid
            
        else:
            
            ( tag_id, ) = result
            
        
        return tag_id
        
    
    def _GetTagParents( self, service_key = None ):
        
        def convert_statuses_and_pair_ids_to_statuses_to_pairs( statuses_and_pair_ids ):
            
            all_tag_ids = set()
            
            for ( status, child_tag_id, parent_tag_id ) in statuses_and_pair_ids:
                
                all_tag_ids.add( child_tag_id )
                all_tag_ids.add( parent_tag_id )
                
            
            self._PopulateTagIdsToTagsCache( all_tag_ids )
            
            statuses_to_pairs = HydrusData.BuildKeyToSetDict( ( ( status, ( self._tag_ids_to_tags_cache[ child_tag_id ], self._tag_ids_to_tags_cache[ parent_tag_id ] ) ) for ( status, child_tag_id, parent_tag_id ) in statuses_and_pair_ids ) )
            
            return statuses_to_pairs
            
        
        if service_key is None:
            
            service_ids_to_statuses_and_pair_ids = HydrusData.BuildKeyToListDict( ( ( service_id, ( status, child_tag_id, parent_tag_id ) ) for ( service_id, status, child_tag_id, parent_tag_id ) in self._c.execute( 'SELECT service_id, status, child_tag_id, parent_tag_id FROM tag_parents UNION SELECT service_id, status, child_tag_id, parent_tag_id FROM tag_parent_petitions;' ) ) )
            
            service_keys_to_statuses_to_pairs = collections.defaultdict( HydrusData.default_dict_set )
            
            for ( service_id, statuses_and_pair_ids ) in list(service_ids_to_statuses_and_pair_ids.items()):
                
                try:
                    
                    service = self._GetService( service_id )
                    
                except HydrusExceptions.DataMissing:
                    
                    self._c.execute( 'DELETE FROM tag_parents WHERE service_id = ?;', ( service_id, ) )
                    self._c.execute( 'DELETE FROM tag_parent_petitions WHERE service_id = ?;', ( service_id, ) )
                    
                    continue
                    
                
                service_key = service.GetServiceKey()
                
                statuses_to_pairs = convert_statuses_and_pair_ids_to_statuses_to_pairs( statuses_and_pair_ids )
                
                service_keys_to_statuses_to_pairs[ service_key ] = statuses_to_pairs
                
            
            return service_keys_to_statuses_to_pairs
            
        else:
            
            service_id = self._GetServiceId( service_key )
            
            statuses_and_pair_ids = self._c.execute( 'SELECT status, child_tag_id, parent_tag_id FROM tag_parents WHERE service_id = ? UNION SELECT status, child_tag_id, parent_tag_id FROM tag_parent_petitions WHERE service_id = ?;', ( service_id, service_id ) ).fetchall()
            
            statuses_to_pairs = convert_statuses_and_pair_ids_to_statuses_to_pairs( statuses_and_pair_ids )
            
            return statuses_to_pairs
            
        
    
    def _GetTagSiblings( self, service_key = None ):
        
        def convert_statuses_and_pair_ids_to_statuses_to_pairs( statuses_and_pair_ids ):
            
            all_tag_ids = set()
            
            for ( status, bad_tag_id, good_tag_id ) in statuses_and_pair_ids:
                
                all_tag_ids.add( bad_tag_id )
                all_tag_ids.add( good_tag_id )
                
            
            self._PopulateTagIdsToTagsCache( all_tag_ids )
            
            statuses_to_pairs = HydrusData.BuildKeyToSetDict( ( ( status, ( self._tag_ids_to_tags_cache[ bad_tag_id ], self._tag_ids_to_tags_cache[ good_tag_id ] ) ) for ( status, bad_tag_id, good_tag_id ) in statuses_and_pair_ids ) )
            
            return statuses_to_pairs
            
        
        if service_key is None:
            
            service_ids_to_statuses_and_pair_ids = HydrusData.BuildKeyToListDict( ( ( service_id, ( status, bad_tag_id, good_tag_id ) ) for ( service_id, status, bad_tag_id, good_tag_id ) in self._c.execute( 'SELECT service_id, status, bad_tag_id, good_tag_id FROM tag_siblings UNION SELECT service_id, status, bad_tag_id, good_tag_id FROM tag_sibling_petitions;' ) ) )
            
            service_keys_to_statuses_to_pairs = collections.defaultdict( HydrusData.default_dict_set )
            
            for ( service_id, statuses_and_pair_ids ) in list( service_ids_to_statuses_and_pair_ids.items() ):
                
                try:
                    
                    service = self._GetService( service_id )
                    
                except HydrusExceptions.DataMissing:
                    
                    self._c.execute( 'DELETE FROM tag_siblings WHERE service_id = ?;', ( service_id, ) )
                    self._c.execute( 'DELETE FROM tag_sibling_petitions WHERE service_id = ?;', ( service_id, ) )
                    
                    continue
                    
                
                statuses_to_pairs = convert_statuses_and_pair_ids_to_statuses_to_pairs( statuses_and_pair_ids )
                
                service_key = service.GetServiceKey()
                
                service_keys_to_statuses_to_pairs[ service_key ] = statuses_to_pairs
                
            
            return service_keys_to_statuses_to_pairs
            
        else:
            
            service_id = self._GetServiceId( service_key )
            
            statuses_and_pair_ids = self._c.execute( 'SELECT status, bad_tag_id, good_tag_id FROM tag_siblings WHERE service_id = ? UNION SELECT status, bad_tag_id, good_tag_id FROM tag_sibling_petitions WHERE service_id = ?;', ( service_id, service_id ) ).fetchall()
            
            statuses_to_pairs = convert_statuses_and_pair_ids_to_statuses_to_pairs( statuses_and_pair_ids )
            
            return statuses_to_pairs
            
        
    
    def _GetText( self, text_id ):
        
        result = self._c.execute( 'SELECT text FROM texts WHERE text_id = ?;', ( text_id, ) ).fetchone()
        
        if result is None:
            
            raise HydrusExceptions.DataMissing( 'Text lookup error in database' )
            
        
        ( text, ) = result
        
        return text
        
    
    def _GetTextId( self, text ):
        
        result = self._c.execute( 'SELECT text_id FROM texts WHERE text = ?;', ( text, ) ).fetchone()
        
        if result is None:
            
            self._c.execute( 'INSERT INTO texts ( text ) VALUES ( ? );', ( text, ) )
            
            text_id = self._c.lastrowid
            
        else:
            
            ( text_id, ) = result
            
        
        return text_id
        
    
    def _GetTrashHashes( self, limit = None, minimum_age = None ):
        
        if limit is None:
            
            limit_phrase = ''
            
        else:
            
            limit_phrase = ' LIMIT ' + str( limit )
            
        
        if minimum_age is None:
            
            age_phrase = ' ORDER BY timestamp ASC' # when deleting until trash is small enough, let's delete oldest first
            
        else:
            
            timestamp_cutoff = HydrusData.GetNow() - minimum_age
            
            age_phrase = ' AND timestamp < ' + str( timestamp_cutoff )
            
        
        hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM current_files WHERE service_id = ?' + age_phrase + limit_phrase + ';', ( self._trash_service_id, ) ) )
        
        if HG.db_report_mode:
            
            message = 'When asked for '
            
            if limit is None:
                
                message += 'all the'
                
            else:
                
                message += 'at most ' + HydrusData.ToHumanInt( limit )
                
            
            message += ' trash files,'
            
            if minimum_age is not None:
                
                message += ' with minimum age ' + HydrusData.TimestampToPrettyTimeDelta( timestamp_cutoff, just_now_threshold = 0 ) + ','
                
            
            message += ' I found ' + HydrusData.ToHumanInt( len( hash_ids ) ) + '.'
            
            HydrusData.ShowText( message )
            
        
        return self._GetHashes( hash_ids )
        
    
    def _GetURLDomainId( self, domain ):
        
        result = self._c.execute( 'SELECT domain_id FROM url_domains WHERE domain = ?;', ( domain, ) ).fetchone()
        
        if result is None:
            
            self._c.execute( 'INSERT INTO url_domains ( domain ) VALUES ( ? );', ( domain, ) )
            
            domain_id = self._c.lastrowid
            
        else:
            
            ( domain_id, ) = result
            
        
        return domain_id
        
    
    def _GetURLDomainAndSubdomainIds( self, domain, only_www_subdomains = False ):
        
        domain = ClientNetworkingDomain.RemoveWWWFromDomain( domain )
        
        domain_ids = set()
        
        domain_ids.add( self._GetURLDomainId( domain ) )
        
        if only_www_subdomains:
            
            search_phrase = 'www%.{}'.format( domain )
            
        else:
            
            search_phrase = '%.{}'.format( domain )
            
        
        for ( domain_id, ) in self._c.execute( 'SELECT domain_id FROM url_domains WHERE domain LIKE ?;', ( search_phrase, ) ):
            
            domain_ids.add( domain_id )
            
        
        return domain_ids
        
    
    def _GetURLId( self, url ):
        
        result = self._c.execute( 'SELECT url_id FROM urls WHERE url = ?;', ( url, ) ).fetchone()
        
        if result is None:
            
            try:
                
                domain = ClientNetworkingDomain.ConvertURLIntoDomain( url )
                
            except HydrusExceptions.URLClassException:
                
                domain = 'unknown.com'
                
            
            domain_id = self._GetURLDomainId( domain )
            
            self._c.execute( 'INSERT INTO urls ( domain_id, url ) VALUES ( ?, ? );', ( domain_id, url ) )
            
            url_id = self._c.lastrowid
            
        else:
            
            ( url_id, ) = result
            
        
        return url_id
        
    
    def _GetURLStatuses( self, url ):
        
        search_urls = ClientNetworkingDomain.GetSearchURLs( url )
        
        hash_ids = set()
        
        for search_url in search_urls:
            
            results = self._STS( self._c.execute( 'SELECT hash_id FROM url_map NATURAL JOIN urls WHERE url = ?;', ( search_url, ) ) )
            
            hash_ids.update( results )
            
        
        results = [ self._GetHashIdStatus( hash_id, prefix = 'url recognised' ) for hash_id in hash_ids ]
        
        return results
        
    
    def _GetYAMLDump( self, dump_type, dump_name = None ):
        
        if dump_name is None:
            
            result = { dump_name : data for ( dump_name, data ) in self._c.execute( 'SELECT dump_name, dump FROM yaml_dumps WHERE dump_type = ?;', ( dump_type, ) ) }
            
            if dump_type == YAML_DUMP_ID_LOCAL_BOORU:
                
                result = { bytes.fromhex( dump_name ) : data for ( dump_name, data ) in list(result.items()) }
                
            
        else:
            
            if dump_type == YAML_DUMP_ID_LOCAL_BOORU: dump_name = dump_name.hex()
            
            result = self._c.execute( 'SELECT dump FROM yaml_dumps WHERE dump_type = ? AND dump_name = ?;', ( dump_type, dump_name ) ).fetchone()
            
            if result is None:
                
                if result is None:
                    
                    raise HydrusExceptions.DataMissing( dump_name + ' was not found!' )
                    
                
            else:
                
                ( result, ) = result
                
            
        
        return result
        
    
    def _GetYAMLDumpNames( self, dump_type ):
        
        names = [ name for ( name, ) in self._c.execute( 'SELECT dump_name FROM yaml_dumps WHERE dump_type = ?;', ( dump_type, ) ) ]
        
        if dump_type == YAML_DUMP_ID_LOCAL_BOORU:
            
            names = [ bytes.fromhex( name ) for name in names ]
            
        
        return names
        
    
    def _HandleCriticalRepositoryDefinitionError( self, service_id ):
        
        self._ReprocessRepositoryFromServiceId( service_id, ( HC.APPLICATION_HYDRUS_UPDATE_DEFINITIONS, ) )
        
        self._ScheduleRepositoryUpdateFileMaintenance( service_id, ClientFiles.REGENERATE_FILE_DATA_JOB_FILE_INTEGRITY_DATA )
        self._ScheduleRepositoryUpdateFileMaintenance( service_id, ClientFiles.REGENERATE_FILE_DATA_JOB_FILE_METADATA )
        
        self._Commit()
        
        self._BeginImmediate()
        
        raise Exception( 'A critical error was discovered with one of your repositories: its definition reference is in an invalid state. Your repository should now be paused, and all update files have been scheduled for an integrity and metadata check. Please permit file maintenance to check them, or tell it to do so manually, before unpausing your repository. Once unpaused, it will reprocess your definition files and attempt to fill the missing entries. If this error occurs again once that is complete, please inform hydrus dev.' )
        
    
    def _HashExists( self, hash ):
        
        result = self._c.execute( 'SELECT 1 FROM hashes WHERE hash = ?;', ( sqlite3.Binary( hash ), ) ).fetchone()
        
        if result is None:
            
            return False
            
        else:
            
            return True
            
        
    
    def _ImportFile( self, file_import_job ):
        
        if HG.file_import_report_mode:
            
            HydrusData.ShowText( 'File import job starting db job' )
            
        
        hash = file_import_job.GetHash()
        
        hash_id = self._GetHashId( hash )
        
        ( status, status_hash, note ) = self._GetHashIdStatus( hash_id, prefix = 'file recognised' )
        
        if status != CC.STATUS_SUCCESSFUL_BUT_REDUNDANT:
            
            if HG.file_import_report_mode:
                
                HydrusData.ShowText( 'File import job adding new file' )
                
            
            ( size, mime, width, height, duration, num_frames, has_audio, num_words ) = file_import_job.GetFileInfo()
            
            timestamp = HydrusData.GetNow()
            
            phashes = file_import_job.GetPHashes()
            
            if phashes is not None:
                
                if HG.file_import_report_mode:
                    
                    HydrusData.ShowText( 'File import job associating phashes' )
                    
                
                self._PHashesAssociatePHashes( hash_id, phashes )
                
            
            if HG.file_import_report_mode:
                
                HydrusData.ShowText( 'File import job adding file info row' )
                
            
            self._AddFilesInfo( [ ( hash_id, size, mime, width, height, duration, num_frames, has_audio, num_words ) ], overwrite = True )
            
            if HG.file_import_report_mode:
                
                HydrusData.ShowText( 'File import job mapping file to local file service' )
                
            
            self._AddFiles( self._local_file_service_id, [ ( hash_id, timestamp ) ] )
            
            file_info_manager = ClientMediaManagers.FileInfoManager( hash_id, hash, size, mime, width, height, duration, num_frames, has_audio, num_words )
            
            content_update = HydrusData.ContentUpdate( HC.CONTENT_TYPE_FILES, HC.CONTENT_UPDATE_ADD, ( file_info_manager, timestamp ) )
            
            self.pub_content_updates_after_commit( { CC.LOCAL_FILE_SERVICE_KEY : [ content_update ] } )
            
            ( md5, sha1, sha512 ) = file_import_job.GetExtraHashes()
            
            self._c.execute( 'INSERT OR IGNORE INTO local_hashes ( hash_id, md5, sha1, sha512 ) VALUES ( ?, ?, ?, ? );', ( hash_id, sqlite3.Binary( md5 ), sqlite3.Binary( sha1 ), sqlite3.Binary( sha512 ) ) )
            
            file_modified_timestamp = file_import_job.GetFileModifiedTimestamp()
            
            self._c.execute( 'REPLACE INTO file_modified_timestamps ( hash_id, file_modified_timestamp ) VALUES ( ?, ? );', ( hash_id, file_modified_timestamp ) )
            
            file_import_options = file_import_job.GetFileImportOptions()
            
            if file_import_options.AutomaticallyArchives():
                
                if HG.file_import_report_mode:
                    
                    HydrusData.ShowText( 'File import job archiving new file' )
                    
                
                self._ArchiveFiles( ( hash_id, ) )
                
            else:
                
                if HG.file_import_report_mode:
                    
                    HydrusData.ShowText( 'File import job inboxing new file' )
                    
                
                self._InboxFiles( ( hash_id, ) )
                
            
            status = CC.STATUS_SUCCESSFUL_AND_NEW
            
            if self._weakref_media_result_cache.HasFile( hash_id ):
                
                self._weakref_media_result_cache.DropMediaResult( hash_id, hash )
                
                self._controller.pub( 'new_file_info', set( ( hash, ) ) )
                
            
        
        if HG.file_import_report_mode:
            
            HydrusData.ShowText( 'File import job done at db level, final status: {}, {}'.format( CC.status_string_lookup[ status ], note ) )
            
        
        return ( status, note )
        
    
    def _ImportUpdate( self, update_network_bytes, update_hash, mime ):
        
        try:
            
            update = HydrusSerialisable.CreateFromNetworkBytes( update_network_bytes )
            
        except:
            
            HydrusData.ShowText( 'Was unable to parse an incoming update!' )
            
            raise
            
        
        hash_id = self._GetHashId( update_hash )
        
        size = len( update_network_bytes )
        
        width = None
        height = None
        duration = None
        num_frames = None
        has_audio = None
        num_words = None
        
        client_files_manager = self._controller.client_files_manager
        
        client_files_manager.LocklessAddFileFromBytes( update_hash, mime, update_network_bytes )
        
        self._AddFilesInfo( [ ( hash_id, size, mime, width, height, duration, num_frames, has_audio, num_words ) ], overwrite = True )
        
        now = HydrusData.GetNow()
        
        self._AddFiles( self._local_update_service_id, [ ( hash_id, now ) ] )
        
    
    def _InboxFiles( self, hash_ids ):
        
        self._c.executemany( 'INSERT OR IGNORE INTO file_inbox VALUES ( ? );', ( ( hash_id, ) for hash_id in hash_ids ) )
        
        num_added = self._GetRowCount()
        
        if num_added > 0:
            
            splayed_hash_ids = HydrusData.SplayListForDB( hash_ids )
            
            updates = self._c.execute( 'SELECT service_id, COUNT( * ) FROM current_files WHERE hash_id IN ' + splayed_hash_ids + ' GROUP BY service_id;' ).fetchall()
            
            self._c.executemany( 'UPDATE service_info SET info = info + ? WHERE service_id = ? AND info_type = ?;', [ ( count, service_id, HC.SERVICE_INFO_NUM_INBOX ) for ( service_id, count ) in updates ] )
            
            self._inbox_hash_ids.update( hash_ids )
            
        
    
    def _InitCaches( self ):
        
        HG.client_controller.pub( 'splash_set_status_text', 'preparing db caches' )
        
        HG.client_controller.pub( 'splash_set_status_subtext', 'services' )
        
        self._local_file_service_id = self._GetServiceId( CC.LOCAL_FILE_SERVICE_KEY )
        self._trash_service_id = self._GetServiceId( CC.TRASH_SERVICE_KEY )
        self._local_update_service_id = self._GetServiceId( CC.LOCAL_UPDATE_SERVICE_KEY )
        self._combined_local_file_service_id = self._GetServiceId( CC.COMBINED_LOCAL_FILE_SERVICE_KEY )
        self._combined_file_service_id = self._GetServiceId( CC.COMBINED_FILE_SERVICE_KEY )
        self._combined_tag_service_id = self._GetServiceId( CC.COMBINED_TAG_SERVICE_KEY )
        
        self._subscriptions_cache = {}
        self._service_cache = {}
        
        self._weakref_media_result_cache = ClientMediaResultCache.MediaResultCache()
        self._hash_ids_to_hashes_cache = {}
        self._tag_ids_to_tags_cache = {}
        
        ( self._null_namespace_id, ) = self._c.execute( 'SELECT namespace_id FROM namespaces WHERE namespace = ?;', ( '', ) ).fetchone()
        
        HG.client_controller.pub( 'splash_set_status_subtext', 'inbox' )
        
        self._inbox_hash_ids = self._STS( self._c.execute( 'SELECT hash_id FROM file_inbox;' ) )
        
    
    def _InitDiskCache( self ):
        
        new_options = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_CLIENT_OPTIONS )
        
        disk_cache_init_period = new_options.GetNoneableInteger( 'disk_cache_init_period' )
        
        if disk_cache_init_period is not None:
            
            HG.client_controller.pub( 'splash_set_status_text', 'preparing disk cache' )
            
            stop_time = HydrusData.GetNow() + disk_cache_init_period
            
            self._LoadIntoDiskCache( stop_time = stop_time )
            
        
    
    def _InitExternalDatabases( self ):
        
        self._db_filenames[ 'external_caches' ] = 'client.caches.db'
        self._db_filenames[ 'external_mappings' ] = 'client.mappings.db'
        self._db_filenames[ 'external_master' ] = 'client.master.db'
        
    
    def _InInbox( self, hash_param ):
        
        if isinstance( hash_param, bytes ):
            
            hash = hash_param
            
            hash_id = self._GetHashId( hash )
            
            return hash_id in self._inbox_hash_ids
            
        elif isinstance( hash_param, ( list, tuple, set ) ):
            
            hashes = hash_param
            
            inbox_hashes = []
            
            for hash in hashes:
                
                hash_id = self._GetHashId( hash )
                
                if hash_id in self._inbox_hash_ids:
                    
                    inbox_hashes.append( hash )
                    
                
            
            return inbox_hashes
            
        else:
            
            raise NotImplementedError( 'Did not understand hashes parameter!' )
            
        
    
    def _IsAnOrphan( self, test_type, possible_hash ):
        
        if self._HashExists( possible_hash ):
            
            hash = possible_hash
            
            if test_type == 'file':
                
                hash_id = self._GetHashId( hash )
                
                result = self._c.execute( 'SELECT 1 FROM current_files WHERE service_id = ? AND hash_id = ?;', ( self._combined_local_file_service_id, hash_id ) ).fetchone()
                
                if result is None:
                    
                    return True
                    
                else:
                    
                    return False
                    
                
            elif test_type == 'thumbnail':
                
                hash_id = self._GetHashId( hash )
                
                result = self._c.execute( 'SELECT 1 FROM current_files WHERE hash_id = ?;', ( hash_id, ) ).fetchone()
                
                if result is None:
                    
                    return True
                    
                else:
                    
                    return False
                    
                
            
        else:
            
            return True
            
        
    
    def _LoadIntoDiskCache( self, stop_time = None, caller_limit = None, for_processing = False ):
        
        self._CloseDBCursor()
        
        try:
            
            approx_disk_cache_size = psutil.virtual_memory().available * 4 / 5
            
            disk_cache_limit = approx_disk_cache_size / 3
            
        except psutil.Error:
            
            disk_cache_limit = 512 * 1024 * 1024
            
        
        so_far_read = 0
        
        try:
            
            next_stop_time_presentation = 0
            next_gc_collect = 0
            
            filenames = self._db_filenames.values()
            
            if not for_processing:
                
                filenames = [ filename for filename in filenames if 'mappings' not in filename and 'master' not in filename ]
                
            
            paths = [ os.path.join( self._db_dir, filename ) for filename in filenames ]
            
            paths.sort( key = os.path.getsize )
            
            for path in paths:
                
                with open( path, 'rb' ) as f:
                    
                    while len( f.read( HC.READ_BLOCK_SIZE ) ) > 0:
                        
                        if stop_time is not None:
                            
                            if HydrusData.TimeHasPassed( next_stop_time_presentation ):
                                
                                if HydrusData.TimeHasPassed( stop_time ):
                                    
                                    return False
                                    
                                
                                HG.client_controller.pub( 'splash_set_status_subtext', 'cached ' + HydrusData.TimestampToPrettyTimeDelta( stop_time, just_now_string = 'ok', just_now_threshold = 1 ) )
                                
                                next_stop_time_presentation = HydrusData.GetNow() + 1
                                
                            
                        
                        so_far_read += HC.READ_BLOCK_SIZE
                        
                        if so_far_read > disk_cache_limit:
                            
                            return True
                            
                        
                        if caller_limit is not None and so_far_read > caller_limit:
                            
                            return False
                            
                        
                        if HydrusData.TimeHasPassed( next_gc_collect ):
                            
                            gc.collect()
                            
                            next_gc_collect = HydrusData.GetNow() + 1
                            
                            time.sleep( 0.00001 )
                            
                        
                    
                
            
        finally:
            
            gc.collect()
            
            self._InitDBCursor()
            
        
        return True
        
    
    def _ManageDBError( self, job, e ):
        
        if isinstance( e, MemoryError ):
            
            HydrusData.ShowText( 'The client is running out of memory! Restart it ASAP!' )
            
        
        tb = traceback.format_exc()
        
        if 'malformed' in tb:
            
            HydrusData.ShowText( 'A database exception looked like it could be a very serious \'database image is malformed\' error! Unless you know otherwise, please shut down the client immediately and check the \'help my db is broke.txt\' under install_dir/db.' )
            
        
        if job.IsSynchronous():
            
            db_traceback = 'Database ' + tb
            
            first_line = str( type( e ).__name__ ) + ': ' + str( e )
            
            new_e = HydrusExceptions.DBException( first_line, db_traceback )
            
            job.PutResult( new_e )
            
        else:
            
            HydrusData.ShowException( e )
            
        
    
    def _MigrationClearJob( self, database_temp_job_name ):
        
        self._c.execute( 'DROP TABLE {};'.format( database_temp_job_name ) )
        
    
    def _MigrationGetMappings( self, database_temp_job_name, file_service_key, tag_service_key, hash_type, tag_filter, content_statuses ):
        
        time_started_precise = HydrusData.GetNowPrecise()
        
        data = []
        
        tag_service_id = self._GetServiceId( tag_service_key )
        
        ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( tag_service_id )
        
        statuses_to_tables = {}
        
        if file_service_key == CC.COMBINED_FILE_SERVICE_KEY:
            
            ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( tag_service_id )
            
            statuses_to_tables[ HC.CONTENT_STATUS_CURRENT ] = current_mappings_table_name
            statuses_to_tables[ HC.CONTENT_STATUS_DELETED ] = deleted_mappings_table_name
            statuses_to_tables[ HC.CONTENT_STATUS_PENDING ] = pending_mappings_table_name
            
        else:
            
            file_service_id = self._GetServiceId( file_service_key )
            
            ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
            
            statuses_to_tables[ HC.CONTENT_STATUS_CURRENT ] = cache_current_mappings_table_name
            statuses_to_tables[ HC.CONTENT_STATUS_DELETED ] = cache_deleted_mappings_table_name
            statuses_to_tables[ HC.CONTENT_STATUS_PENDING ] = cache_pending_mappings_table_name
            
        
        select_queries = []
        
        for content_status in content_statuses:
            
            table_name = statuses_to_tables[ content_status ]
            
            select_query = 'SELECT tag_id FROM {} WHERE hash_id = ?;'.format( table_name )
            
            select_queries.append( select_query )
            
        
        we_should_stop = False
        
        while not we_should_stop:
            
            result = self._c.execute( 'SELECT hash_id FROM {};'.format( database_temp_job_name ) ).fetchone()
            
            if result is None:
                
                break
                
            
            ( hash_id, ) = result
            
            self._c.execute( 'DELETE FROM {} WHERE hash_id = ?;'.format( database_temp_job_name ), ( hash_id, ) )
            
            if hash_type == 'sha256':
                
                desired_hash = self._GetHash( hash_id )
                
            else:
                
                result = self._c.execute( 'SELECT ' + hash_type + ' FROM local_hashes WHERE hash_id = ?;', ( hash_id, ) ).fetchone()
                
                if result is None:
                    
                    continue
                    
                
                ( desired_hash, ) = result
                
            
            tags = set()
            
            for select_query in select_queries:
                
                tag_ids = self._STL( self._c.execute( select_query, ( hash_id, ) ) )
                
                self._PopulateTagIdsToTagsCache( tag_ids )
                
                tags.update( ( self._tag_ids_to_tags_cache[ tag_id ] for tag_id in tag_ids ) )
                
            
            if not tag_filter.AllowsEverything():
                
                tags = tag_filter.Filter( tags )
                
            
            if len( tags ) > 0:
                
                data.append( ( desired_hash, tags ) )
                
            
            we_should_stop = len( data ) >= 256 or ( len( data ) > 0 and HydrusData.TimeHasPassedPrecise( time_started_precise + 1.0 ) )
            
        
        return data
        
    
    def _MigrationGetPairs( self, database_temp_job_name, left_tag_filter, right_tag_filter ):
        
        time_started_precise = HydrusData.GetNowPrecise()
        
        data = []
        
        we_should_stop = False
        
        while not we_should_stop:
            
            result = self._c.execute( 'SELECT left_tag_id, right_tag_id FROM {};'.format( database_temp_job_name ) ).fetchone()
            
            if result is None:
                
                break
                
            
            ( left_tag_id, right_tag_id ) = result
            
            self._c.execute( 'DELETE FROM {} WHERE left_tag_id = ? AND right_tag_id = ?;'.format( database_temp_job_name ), ( left_tag_id, right_tag_id ) )
            
            left_tag = self._GetTag( left_tag_id )
            
            if not left_tag_filter.TagOK( left_tag ):
                
                continue
                
            
            right_tag = self._GetTag( right_tag_id )
            
            if not right_tag_filter.TagOK( right_tag ):
                
                continue
                
            
            data.append( ( left_tag, right_tag ) )
            
            we_should_stop = len( data ) >= 256 or ( len( data ) > 0 and HydrusData.TimeHasPassedPrecise( time_started_precise + 1.0 ) )
            
        
        return data
        
    
    def _MigrationStartMappingsJob( self, database_temp_job_name, file_service_key, tag_service_key, hashes, content_statuses ):
        
        self._c.execute( 'CREATE TABLE durable_temp.{} ( hash_id INTEGER PRIMARY KEY );'.format( database_temp_job_name ) )
        
        if hashes is not None:
            
            hash_ids = self._GetHashIds( hashes )
            
            self._c.executemany( 'INSERT INTO {} ( hash_id ) VALUES ( ? );'.format( database_temp_job_name ), ( ( hash_id, ) for hash_id in hash_ids ) )
            
        else:
            
            tag_service_id = self._GetServiceId( tag_service_key )
            
            statuses_to_tables = {}
            
            use_hashes_table = False
            
            if file_service_key == CC.COMBINED_FILE_SERVICE_KEY:
                
                # if our tag service is the biggest, and if it basically accounts for all the hashes we know about, it is much faster to just use the hashes table
                
                our_results = self._GetServiceInfo( tag_service_key )
                
                our_num_files = our_results[ HC.SERVICE_INFO_NUM_FILES ]
                
                other_services = [ service for service in self._GetServices( HC.REAL_TAG_SERVICES ) if service.GetServiceKey() != tag_service_key ]
                
                other_num_files = []
                
                for other_service in other_services:
                    
                    other_results = self._GetServiceInfo( other_service.GetServiceKey() )
                    
                    other_num_files.append( other_results[ HC.SERVICE_INFO_NUM_FILES ] )
                    
                
                if len( other_num_files ) == 0:
                    
                    we_are_big = True
                    
                else:
                    
                    we_are_big = our_num_files >= 0.75 * max( other_num_files )
                    
                
                if we_are_big:
                    
                    local_files_results = self._GetServiceInfo( CC.COMBINED_LOCAL_FILE_SERVICE_KEY )
                    
                    local_files_num_files = local_files_results[ HC.SERVICE_INFO_NUM_FILES ]
                    
                    if local_files_num_files > our_num_files:
                        
                        # probably a small local tags service, ok to pull from current_mappings
                        
                        we_are_big = False
                        
                    
                
                if we_are_big:
                    
                    use_hashes_table = True
                    
                
            
            if use_hashes_table:
                
                # this obviously just pulls literally all known files
                # makes migration take longer if the tag service does not cover many of these files, but saves huge startup time since it is a simple list
                select_subqueries = [ 'SELECT hash_id FROM hashes' ]
                
            else:
                
                if file_service_key == CC.COMBINED_FILE_SERVICE_KEY:
                    
                    ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( tag_service_id )
                    
                    statuses_to_tables[ HC.CONTENT_STATUS_CURRENT ] = current_mappings_table_name
                    statuses_to_tables[ HC.CONTENT_STATUS_DELETED ] = deleted_mappings_table_name
                    statuses_to_tables[ HC.CONTENT_STATUS_PENDING ] = pending_mappings_table_name
                    
                else:
                    
                    file_service_id = self._GetServiceId( file_service_key )
                    
                    ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id )
                    
                    statuses_to_tables[ HC.CONTENT_STATUS_CURRENT ] = cache_current_mappings_table_name
                    statuses_to_tables[ HC.CONTENT_STATUS_DELETED ] = cache_deleted_mappings_table_name
                    statuses_to_tables[ HC.CONTENT_STATUS_PENDING ] = cache_pending_mappings_table_name
                    
                
                select_subqueries = []
                
                for content_status in content_statuses:
                    
                    table_name = statuses_to_tables[ content_status ]
                    
                    select_subquery = 'SELECT DISTINCT hash_id FROM {}'.format( table_name )
                    
                    select_subqueries.append( select_subquery )
                    
                
            
            for select_subquery in select_subqueries:
                
                self._c.execute( 'INSERT OR IGNORE INTO {} ( hash_id ) {};'.format( database_temp_job_name, select_subquery ) )
                
            
        
    
    def _MigrationStartPairsJob( self, database_temp_job_name, tag_service_key, content_type, content_statuses ):
        
        self._c.execute( 'CREATE TABLE durable_temp.{} ( left_tag_id INTEGER, right_tag_id INTEGER, PRIMARY KEY ( left_tag_id, right_tag_id ) );'.format( database_temp_job_name ) )
        
        tag_service_id = self._GetServiceId( tag_service_key )
        
        if content_type == HC.CONTENT_TYPE_TAG_PARENTS:
            
            source_table_names = [ 'tag_parents', 'tag_parent_petitions' ]
            left_column_name = 'child_tag_id'
            right_column_name = 'parent_tag_id'
            
        elif content_type == HC.CONTENT_TYPE_TAG_SIBLINGS:
            
            source_table_names = [ 'tag_siblings', 'tag_sibling_petitions' ]
            left_column_name = 'bad_tag_id'
            right_column_name = 'good_tag_id'
            
        
        for source_table_name in source_table_names:
            
            self._c.execute( 'INSERT OR IGNORE INTO {} ( left_tag_id, right_tag_id ) SELECT {}, {} FROM {} WHERE service_id = ? AND status IN {};'.format( database_temp_job_name, left_column_name, right_column_name, source_table_name, HydrusData.SplayListForDB( content_statuses ) ), ( tag_service_id, ) )
            
        
    
    def _NamespaceExists( self, namespace ):
        
        if namespace == '':
            
            return True
            
        
        result = self._c.execute( 'SELECT 1 FROM namespaces WHERE namespace = ?;', ( namespace, ) ).fetchone()
        
        if result is None:
            
            return False
            
        else:
            
            return True
            
        
    
    def _OverwriteJSONDumps( self, dump_types, objs ):
        
        for dump_type in dump_types:
            
            self._DeleteJSONDumpNamed( dump_type )
            
        
        for obj in objs:
            
            self._SetJSONDump( obj )
            
        
    
    def _PHashesAddLeaf( self, phash_id, phash ):
        
        result = self._c.execute( 'SELECT phash_id FROM shape_vptree WHERE parent_id IS NULL;' ).fetchone()
        
        if result is None:
            
            parent_id = None
            
        else:
            
            ( root_node_phash_id, ) = result
            
            ancestors_we_are_inside = []
            ancestors_we_are_outside = []
            
            an_ancestor_is_unbalanced = False
            
            next_ancestor_id = root_node_phash_id
            
            while next_ancestor_id is not None:
                
                ancestor_id = next_ancestor_id
                
                ( ancestor_phash, ancestor_radius, ancestor_inner_id, ancestor_inner_population, ancestor_outer_id, ancestor_outer_population ) = self._c.execute( 'SELECT phash, radius, inner_id, inner_population, outer_id, outer_population FROM shape_perceptual_hashes NATURAL JOIN shape_vptree WHERE phash_id = ?;', ( ancestor_id, ) ).fetchone()
                
                distance_to_ancestor = HydrusData.Get64BitHammingDistance( phash, ancestor_phash )
                
                if ancestor_radius is None or distance_to_ancestor <= ancestor_radius:
                    
                    ancestors_we_are_inside.append( ancestor_id )
                    ancestor_inner_population += 1
                    next_ancestor_id = ancestor_inner_id
                    
                    if ancestor_inner_id is None:
                        
                        self._c.execute( 'UPDATE shape_vptree SET inner_id = ?, radius = ? WHERE phash_id = ?;', ( phash_id, distance_to_ancestor, ancestor_id ) )
                        
                        parent_id = ancestor_id
                        
                    
                else:
                    
                    ancestors_we_are_outside.append( ancestor_id )
                    ancestor_outer_population += 1
                    next_ancestor_id = ancestor_outer_id
                    
                    if ancestor_outer_id is None:
                        
                        self._c.execute( 'UPDATE shape_vptree SET outer_id = ? WHERE phash_id = ?;', ( phash_id, ancestor_id ) )
                        
                        parent_id = ancestor_id
                        
                    
                
                if not an_ancestor_is_unbalanced and ancestor_inner_population + ancestor_outer_population > 16:
                    
                    larger = max( ancestor_inner_population, ancestor_outer_population )
                    smaller = min( ancestor_inner_population, ancestor_outer_population )
                    
                    if smaller / larger < 0.5:
                        
                        self._c.execute( 'INSERT OR IGNORE INTO shape_maintenance_branch_regen ( phash_id ) VALUES ( ? );', ( ancestor_id, ) )
                        
                        # we only do this for the eldest ancestor, as the eventual rebalancing will affect all children
                        
                        an_ancestor_is_unbalanced = True
                        
                    
                
            
            self._c.executemany( 'UPDATE shape_vptree SET inner_population = inner_population + 1 WHERE phash_id = ?;', ( ( ancestor_id, ) for ancestor_id in ancestors_we_are_inside ) )
            self._c.executemany( 'UPDATE shape_vptree SET outer_population = outer_population + 1 WHERE phash_id = ?;', ( ( ancestor_id, ) for ancestor_id in ancestors_we_are_outside ) )
            
        
        radius = None
        inner_id = None
        inner_population = 0
        outer_id = None
        outer_population = 0
        
        self._c.execute( 'INSERT OR REPLACE INTO shape_vptree ( phash_id, parent_id, radius, inner_id, inner_population, outer_id, outer_population ) VALUES ( ?, ?, ?, ?, ?, ?, ? );', ( phash_id, parent_id, radius, inner_id, inner_population, outer_id, outer_population ) )
        
    
    def _PHashesAssociatePHashes( self, hash_id, phashes ):
        
        phash_ids = set()
        
        for phash in phashes:
            
            phash_id = self._PHashesGetPHashId( phash )
            
            phash_ids.add( phash_id )
            
        
        self._c.executemany( 'INSERT OR IGNORE INTO shape_perceptual_hash_map ( phash_id, hash_id ) VALUES ( ?, ? );', ( ( phash_id, hash_id ) for phash_id in phash_ids ) )
        
        if self._GetRowCount() > 0:
            
            self._c.execute( 'REPLACE INTO shape_search_cache ( hash_id, searched_distance ) VALUES ( ?, ? );', ( hash_id, None ) )
            
        
        return phash_ids
        
    
    def _PHashesEnsureFileInSystem( self, hash_id ):
        
        result = self._c.execute( 'SELECT 1 FROM shape_search_cache WHERE hash_id = ?;', ( hash_id, ) ).fetchone()
        
        if result is None:
            
            self._FileMaintenanceAddJobs( ( hash_id, ), ClientFiles.REGENERATE_FILE_DATA_JOB_SIMILAR_FILES_METADATA )
            
        
    def _PHashesEnsureFileOutOfSystem( self, hash_id ):
        
        self._DuplicatesRemoveMediaIdMember( hash_id )
        
        current_phash_ids = self._STS( self._c.execute( 'SELECT phash_id FROM shape_perceptual_hash_map WHERE hash_id = ?;', ( hash_id, ) ) )
        
        if len( current_phash_ids ) > 0:
            
            self._PHashesDisassociatePHashes( hash_id, current_phash_ids )
            
        
        self._c.execute( 'DELETE FROM shape_search_cache WHERE hash_id = ?;', ( hash_id, ) )
        
    
    def _PHashesDeleteFile( self, hash_id ):
        
        phash_ids = self._STS( self._c.execute( 'SELECT phash_id FROM shape_perceptual_hash_map WHERE hash_id = ?;', ( hash_id, ) ) )
        
        self._PHashesDisassociatePHashes( hash_id, phash_ids )
        
        self._c.execute( 'DELETE FROM shape_search_cache WHERE hash_id = ?;', ( hash_id, ) )
        
    
    def _PHashesDisassociatePHashes( self, hash_id, phash_ids ):
        
        self._c.executemany( 'DELETE FROM shape_perceptual_hash_map WHERE phash_id = ? AND hash_id = ?;', ( ( phash_id, hash_id ) for phash_id in phash_ids ) )
        
        useful_phash_ids = { phash for ( phash, ) in self._c.execute( 'SELECT phash_id FROM shape_perceptual_hash_map WHERE phash_id IN ' + HydrusData.SplayListForDB( phash_ids ) + ';' ) }
        
        useless_phash_ids = phash_ids.difference( useful_phash_ids )
        
        self._c.executemany( 'INSERT OR IGNORE INTO shape_maintenance_branch_regen ( phash_id ) VALUES ( ? );', ( ( phash_id, ) for phash_id in useless_phash_ids ) )
        
    
    def _PHashesGenerateBranch( self, job_key, parent_id, phash_id, phash, children ):
        
        process_queue = collections.deque()
        
        process_queue.append( ( parent_id, phash_id, phash, children ) )
        
        insert_rows = []
        
        num_done = 0
        num_to_do = len( children ) + 1
        
        while len( process_queue ) > 0:
            
            job_key.SetVariable( 'popup_text_2', 'generating new branch -- ' + HydrusData.ConvertValueRangeToPrettyString( num_done, num_to_do ) )
            
            ( parent_id, phash_id, phash, children ) = process_queue.popleft()
            
            if len( children ) == 0:
                
                inner_id = None
                inner_population = 0
                
                outer_id = None
                outer_population = 0
                
                radius = None
                
            else:
                
                children = sorted( ( ( HydrusData.Get64BitHammingDistance( phash, child_phash ), child_id, child_phash ) for ( child_id, child_phash ) in children ) )
                
                median_index = len( children ) // 2
                
                median_radius = children[ median_index ][0]
                
                inner_children = [ ( child_id, child_phash ) for ( distance, child_id, child_phash ) in children if distance < median_radius ]
                radius_children = [ ( child_id, child_phash ) for ( distance, child_id, child_phash ) in children if distance == median_radius ]
                outer_children = [ ( child_id, child_phash ) for ( distance, child_id, child_phash ) in children if distance > median_radius ]
                
                if len( inner_children ) <= len( outer_children ):
                    
                    radius = median_radius
                    
                    inner_children.extend( radius_children )
                    
                else:
                    
                    radius = median_radius - 1
                    
                    outer_children.extend( radius_children )
                    
                
                inner_population = len( inner_children )
                outer_population = len( outer_children )
                
                ( inner_id, inner_phash ) = self._PHashesPopBestRootNode( inner_children ) #HydrusData.MedianPop( inner_children )
                
                if len( outer_children ) == 0:
                    
                    outer_id = None
                    
                else:
                    
                    ( outer_id, outer_phash ) = self._PHashesPopBestRootNode( outer_children ) #HydrusData.MedianPop( outer_children )
                    
                
            
            insert_rows.append( ( phash_id, parent_id, radius, inner_id, inner_population, outer_id, outer_population ) )
            
            if inner_id is not None:
                
                process_queue.append( ( phash_id, inner_id, inner_phash, inner_children ) )
                
            
            if outer_id is not None:
                
                process_queue.append( ( phash_id, outer_id, outer_phash, outer_children ) )
                
            
            num_done += 1
            
        
        job_key.SetVariable( 'popup_text_2', 'branch constructed, now committing' )
        
        self._c.executemany( 'INSERT OR REPLACE INTO shape_vptree ( phash_id, parent_id, radius, inner_id, inner_population, outer_id, outer_population ) VALUES ( ?, ?, ?, ?, ?, ?, ? );', insert_rows )
        
    
    def _PHashesGetMaintenanceStatus( self ):
        
        searched_distances_to_count = collections.Counter( dict( self._c.execute( 'SELECT searched_distance, COUNT( * ) FROM shape_search_cache GROUP BY searched_distance;' ) ) )
        
        return searched_distances_to_count
        
    
    def _PHashesGetPHashId( self, phash ):
        
        result = self._c.execute( 'SELECT phash_id FROM shape_perceptual_hashes WHERE phash = ?;', ( sqlite3.Binary( phash ), ) ).fetchone()
        
        if result is None:
            
            self._c.execute( 'INSERT INTO shape_perceptual_hashes ( phash ) VALUES ( ? );', ( sqlite3.Binary( phash ), ) )
            
            phash_id = self._c.lastrowid
            
            self._PHashesAddLeaf( phash_id, phash )
            
        else:
            
            ( phash_id, ) = result
            
        
        return phash_id
        
    
    def _PHashesMaintainTree( self, maintenance_mode = HC.MAINTENANCE_FORCED, job_key = None, stop_time = None ):
        
        time_started = HydrusData.GetNow()
        pub_job_key = False
        job_key_pubbed = False
        
        if job_key is None:
            
            job_key = ClientThreading.JobKey( cancellable = True )
            
            pub_job_key = True
            
        
        try:
            
            job_key.SetVariable( 'popup_title', 'similar files metadata maintenance' )
            
            rebalance_phash_ids = self._STL( self._c.execute( 'SELECT phash_id FROM shape_maintenance_branch_regen;' ) )
            
            num_to_do = len( rebalance_phash_ids )
            
            while len( rebalance_phash_ids ) > 0:
                
                if pub_job_key and not job_key_pubbed and HydrusData.TimeHasPassed( time_started + 5 ):
                    
                    self._controller.pub( 'modal_message', job_key )
                    
                    job_key_pubbed = True
                    
                
                ( i_paused, should_quit ) = job_key.WaitIfNeeded()
                
                should_stop = HG.client_controller.ShouldStopThisWork( maintenance_mode, stop_time = stop_time )
                
                if should_quit or should_stop:
                    
                    return
                    
                
                num_done = num_to_do - len( rebalance_phash_ids )
                
                text = 'rebalancing similar file metadata - ' + HydrusData.ConvertValueRangeToPrettyString( num_done, num_to_do )
                
                HG.client_controller.pub( 'splash_set_status_subtext', text )
                job_key.SetVariable( 'popup_text_1', text )
                job_key.SetVariable( 'popup_gauge_1', ( num_done, num_to_do ) )
                
                with HydrusDB.TemporaryIntegerTable( self._c, rebalance_phash_ids, 'phash_id' ) as temp_table_name:
                    
                    self._AnalyzeTempTable( temp_table_name )
                    
                    # can't turn this into an ExecuteManySelect due to the order clause. we need to do it all at once
                    
                    ( biggest_phash_id, ) = self._c.execute( 'SELECT phash_id FROM shape_vptree NATURAL JOIN ' + temp_table_name + ' ORDER BY inner_population + outer_population DESC;' ).fetchone()
                    
                
                self._PHashesRegenerateBranch( job_key, biggest_phash_id )
                
                rebalance_phash_ids = self._STL( self._c.execute( 'SELECT phash_id FROM shape_maintenance_branch_regen;' ) )
                
            
        finally:
            
            job_key.SetVariable( 'popup_text_1', 'done!' )
            job_key.DeleteVariable( 'popup_gauge_1' )
            job_key.DeleteVariable( 'popup_text_2' ) # used in the regenbranch call
            
            job_key.Finish()
            
            job_key.Delete( 5 )
            
        
    
    def _PHashesMaintenanceDue( self ):
        
        new_options = HG.client_controller.new_options
        
        if new_options.GetBoolean( 'maintain_similar_files_duplicate_pairs_during_idle' ):
            
            search_distance = new_options.GetInteger( 'similar_files_duplicate_pairs_search_distance' )
            
            ( count, ) = self._c.execute( 'SELECT COUNT( * ) FROM ( SELECT 1 FROM shape_search_cache WHERE searched_distance IS NULL or searched_distance < ? LIMIT 100 );', ( search_distance, ) ).fetchone()
            
            if count >= 100:
                
                return True
                
            
        
        return False
        
    
    def _PHashesPopBestRootNode( self, node_rows ):
        
        if len( node_rows ) == 1:
            
            root_row = node_rows.pop()
            
            return root_row
            
        
        MAX_VIEWPOINTS = 256
        MAX_SAMPLE = 64
        
        if len( node_rows ) > MAX_VIEWPOINTS:
            
            viewpoints = random.sample( node_rows, MAX_VIEWPOINTS )
            
        else:
            
            viewpoints = node_rows
            
        
        if len( node_rows ) > MAX_SAMPLE:
            
            sample = random.sample( node_rows, MAX_SAMPLE )
            
        else:
            
            sample = node_rows
            
        
        final_scores = []
        
        for ( v_id, v_phash ) in viewpoints:
            
            views = sorted( ( HydrusData.Get64BitHammingDistance( v_phash, s_phash ) for ( s_id, s_phash ) in sample if v_id != s_id ) )
            
            # let's figure out the ratio of left_children to right_children, preferring 1:1, and convert it to a discrete integer score
            
            median_index = len( views ) // 2
            
            radius = views[ median_index ]
            
            num_left = len( [ 1 for view in views if view < radius ] )
            num_radius = len( [ 1 for view in views if view == radius ] )
            num_right = len( [ 1 for view in views if view > radius ] )
            
            if num_left <= num_right:
                
                num_left += num_radius
                
            else:
                
                num_right += num_radius
                
            
            smaller = min( num_left, num_right )
            larger = max( num_left, num_right )
            
            ratio = smaller / larger
            
            ratio_score = int( ratio * MAX_SAMPLE / 2 )
            
            # now let's calc the standard deviation--larger sd tends to mean less sphere overlap when searching
            
            mean_view = sum( views ) / len( views )
            squared_diffs = [ ( view - mean_view  ) ** 2 for view in views ]
            sd = ( sum( squared_diffs ) / len( squared_diffs ) ) ** 0.5
            
            final_scores.append( ( ratio_score, sd, v_id ) )
            
        
        final_scores.sort()
        
        # we now have a list like [ ( 11, 4.0, [id] ), ( 15, 3.7, [id] ), ( 15, 4.3, [id] ) ]
        
        ( ratio_gumpf, sd_gumpf, root_id ) = final_scores.pop()
        
        for ( i, ( v_id, v_phash ) ) in enumerate( node_rows ):
            
            if v_id == root_id:
                
                root_row = node_rows.pop( i )
                
                return root_row
                
            
        
    
    def _PHashesRegenerateBranch( self, job_key, phash_id ):
        
        job_key.SetVariable( 'popup_text_2', 'reviewing existing branch' )
        
        # grab everything in the branch
        
        ( parent_id, ) = self._c.execute( 'SELECT parent_id FROM shape_vptree WHERE phash_id = ?;', ( phash_id, ) ).fetchone()
        
        cte_table_name = 'branch ( branch_phash_id )'
        initial_select = 'SELECT ?'
        recursive_select = 'SELECT phash_id FROM shape_vptree, branch ON parent_id = branch_phash_id'
        
        with_clause = 'WITH RECURSIVE ' + cte_table_name + ' AS ( ' + initial_select + ' UNION ALL ' +  recursive_select +  ')'
        
        unbalanced_nodes = self._c.execute( with_clause + ' SELECT branch_phash_id, phash FROM branch, shape_perceptual_hashes ON phash_id = branch_phash_id;', ( phash_id, ) ).fetchall()
        
        # removal of old branch, maintenance schedule, and orphan phashes
        
        job_key.SetVariable( 'popup_text_2', HydrusData.ToHumanInt( len( unbalanced_nodes ) ) + ' leaves found--now clearing out old branch' )
        
        unbalanced_phash_ids = { p_id for ( p_id, p_h ) in unbalanced_nodes }
        
        self._c.executemany( 'DELETE FROM shape_vptree WHERE phash_id = ?;', ( ( p_id, ) for p_id in unbalanced_phash_ids ) )
        
        self._c.executemany( 'DELETE FROM shape_maintenance_branch_regen WHERE phash_id = ?;', ( ( p_id, ) for p_id in unbalanced_phash_ids ) )
        
        useful_phash_ids = self._STS( self._ExecuteManySelectSingleParam( 'SELECT phash_id FROM shape_perceptual_hash_map WHERE phash_id = ?;', unbalanced_phash_ids ) )
        
        orphan_phash_ids = unbalanced_phash_ids.difference( useful_phash_ids )
        
        self._c.executemany( 'DELETE FROM shape_perceptual_hashes WHERE phash_id = ?;', ( ( p_id, ) for p_id in orphan_phash_ids ) )
        
        useful_nodes = [ row for row in unbalanced_nodes if row[0] in useful_phash_ids ]
        
        useful_population = len( useful_nodes )
        
        # now create the new branch, starting by choosing a new root and updating the parent's left/right reference to that
        
        if useful_population > 0:
            
            ( new_phash_id, new_phash ) = self._PHashesPopBestRootNode( useful_nodes ) #HydrusData.RandomPop( useful_nodes )
            
        else:
            
            new_phash_id = None
            
        
        if parent_id is not None:
            
            ( parent_inner_id, ) = self._c.execute( 'SELECT inner_id FROM shape_vptree WHERE phash_id = ?;', ( parent_id, ) ).fetchone()
            
            if parent_inner_id == phash_id:
                
                query = 'UPDATE shape_vptree SET inner_id = ?, inner_population = ? WHERE phash_id = ?;'
                
            else:
                
                query = 'UPDATE shape_vptree SET outer_id = ?, outer_population = ? WHERE phash_id = ?;'
                
            
            self._c.execute( query, ( new_phash_id, useful_population, parent_id ) )
            
        
        if useful_population > 0:
            
            self._PHashesGenerateBranch( job_key, parent_id, new_phash_id, new_phash, useful_nodes )
            
        
    
    def _PHashesRegenerateTree( self ):
        
        job_key = ClientThreading.JobKey()
        
        try:
            
            job_key.SetVariable( 'popup_title', 'regenerating similar file search data' )
            
            self._controller.pub( 'modal_message', job_key )
            
            job_key.SetVariable( 'popup_text_1', 'purging search info of orphans' )
            
            self._c.execute( 'DELETE FROM shape_perceptual_hash_map WHERE hash_id NOT IN ( SELECT hash_id FROM current_files );' )
            
            job_key.SetVariable( 'popup_text_1', 'gathering all leaves' )
            
            self._c.execute( 'DELETE FROM shape_vptree;' )
            
            all_nodes = self._c.execute( 'SELECT phash_id, phash FROM shape_perceptual_hashes;' ).fetchall()
            
            job_key.SetVariable( 'popup_text_1', HydrusData.ToHumanInt( len( all_nodes ) ) + ' leaves found, now regenerating' )
            
            ( root_id, root_phash ) = self._PHashesPopBestRootNode( all_nodes ) #HydrusData.RandomPop( all_nodes )
            
            self._PHashesGenerateBranch( job_key, None, root_id, root_phash, all_nodes )
            
        finally:
            
            job_key.SetVariable( 'popup_text_1', 'done!' )
            job_key.DeleteVariable( 'popup_text_2' )
            
            job_key.Finish()
            
            job_key.Delete( 5 )
            
        
    
    def _PHashesResetSearch( self, hash_ids ):
        
        self._c.executemany( 'UPDATE shape_search_cache SET searched_distance = NULL WHERE hash_id = ?;', ( ( hash_id, ) for hash_id in hash_ids ) )
        
    
    def _PHashesResetSearchFromHashes( self, hashes ):
        
        hash_ids = self._GetHashIds( hashes )
        
        self._PHashesResetSearch( hash_ids )
        
    
    def _PHashesSearchForPotentialDuplicates( self, search_distance, maintenance_mode = HC.MAINTENANCE_FORCED, job_key = None, stop_time = None ):
        
        time_started = HydrusData.GetNow()
        pub_job_key = False
        job_key_pubbed = False
        
        if job_key is None:
            
            job_key = ClientThreading.JobKey( cancellable = True )
            
            pub_job_key = True
            
        
        try:
            
            ( total_num_hash_ids_in_cache, ) = self._c.execute( 'SELECT COUNT( * ) FROM shape_search_cache;' ).fetchone()
            
            hash_ids = self._STL( self._c.execute( 'SELECT hash_id FROM shape_search_cache WHERE searched_distance IS NULL or searched_distance < ?;', ( search_distance, ) ) )
            
            total_done_previously = total_num_hash_ids_in_cache - len( hash_ids )
            
            for ( i, hash_id ) in enumerate( hash_ids ):
                
                job_key.SetVariable( 'popup_title', 'similar files duplicate pair discovery' )
                
                if pub_job_key and not job_key_pubbed and HydrusData.TimeHasPassed( time_started + 5 ):
                    
                    self._controller.pub( 'modal_message', job_key )
                    
                    job_key_pubbed = True
                    
                
                ( i_paused, should_quit ) = job_key.WaitIfNeeded()
                
                should_stop = HG.client_controller.ShouldStopThisWork( maintenance_mode, stop_time = stop_time )
                
                if should_quit or should_stop:
                    
                    return
                    
                
                if i % 25 == 0:
                    
                    text = 'searched ' + HydrusData.ConvertValueRangeToPrettyString( total_done_previously + i, total_num_hash_ids_in_cache ) + ' files'
                    
                    job_key.SetVariable( 'popup_text_1', text )
                    job_key.SetVariable( 'popup_gauge_1', ( total_done_previously + i, total_num_hash_ids_in_cache ) )
                    
                    HG.client_controller.pub( 'splash_set_status_subtext', text )
                    
                
                media_id = self._DuplicatesGetMediaId( hash_id )
                
                potential_duplicate_media_ids_and_distances = [ ( self._DuplicatesGetMediaId( duplicate_hash_id ), distance ) for ( duplicate_hash_id, distance ) in self._PHashesSearch( hash_id, search_distance ) if duplicate_hash_id != hash_id ]
                
                self._DuplicatesAddPotentialDuplicates( media_id, potential_duplicate_media_ids_and_distances )
                
                self._c.execute( 'UPDATE shape_search_cache SET searched_distance = ? WHERE hash_id = ?;', ( search_distance, hash_id ) )
                
            
        finally:
            
            job_key.SetVariable( 'popup_text_1', 'done!' )
            job_key.DeleteVariable( 'popup_gauge_1' )
            
            job_key.Finish()
            
            job_key.Delete( 5 )
            
        
    
    def _PHashesSearch( self, hash_id, max_hamming_distance ):
        
        if max_hamming_distance == 0:
            
            similar_hash_ids = self._STL( self._c.execute( 'SELECT hash_id FROM shape_perceptual_hash_map WHERE phash_id IN ( SELECT phash_id FROM shape_perceptual_hash_map WHERE hash_id = ? );', ( hash_id, ) ) )
            
            similar_hash_ids_and_distances = [ ( similar_hash_id, 0 ) for similar_hash_id in similar_hash_ids ]
            
        else:
            
            search_radius = max_hamming_distance
            
            top_node_result = self._c.execute( 'SELECT phash_id FROM shape_vptree WHERE parent_id IS NULL;' ).fetchone()
            
            if top_node_result is None:
                
                return []
                
            
            ( root_node_phash_id, ) = top_node_result
            
            search_phashes = self._STL( self._c.execute( 'SELECT phash FROM shape_perceptual_hashes NATURAL JOIN shape_perceptual_hash_map WHERE hash_id = ?;', ( hash_id, ) ) )
            
            if len( search_phashes ) == 0:
                
                return []
                
            
            similar_phash_ids_to_distances = {}
            
            num_cycles = 0
            
            for search_phash in search_phashes:
                
                next_potentials = [ root_node_phash_id ]
                
                while len( next_potentials ) > 0:
                    
                    current_potentials = next_potentials
                    next_potentials = []
                    
                    num_cycles += 1
                    
                    for group_of_current_potentials in HydrusData.SplitListIntoChunks( current_potentials, 1024 ):
                        
                        # this is split into fixed lists of results of subgroups because as an iterable it was causing crashes on linux!!
                        # after investigation, it seemed to be SQLite having a problem with part of Get64BitHammingDistance touching phashes it presumably was still hanging on to
                        # the crash was in sqlite code, again presumably on subsequent fetch
                        # adding a delay in seemed to fix it as well. guess it was some memory maintenance buffer/bytes thing
                        # anyway, we now just get the whole lot of results first and then work on the whole lot
                        
                        select_statement = 'SELECT phash_id, phash, radius, inner_id, outer_id FROM shape_perceptual_hashes NATURAL JOIN shape_vptree WHERE phash_id = ?;'
                        
                        results = list( self._ExecuteManySelectSingleParam( select_statement, group_of_current_potentials ) )
                        
                        for ( node_phash_id, node_phash, node_radius, inner_phash_id, outer_phash_id ) in results:
                            
                            # first check the node itself--is it similar?
                            
                            node_hamming_distance = HydrusData.Get64BitHammingDistance( search_phash, node_phash )
                            
                            if node_hamming_distance <= search_radius:
                                
                                similar_phash_ids_to_distances[ node_phash_id ] = node_hamming_distance
                                
                            
                            # now how about its children?
                            
                            if node_radius is not None:
                                
                                # we have two spheres--node and search--their centers separated by node_hamming_distance
                                # we want to search inside/outside the node_sphere if the search_sphere intersects with those spaces
                                # there are four possibles:
                                # (----N----)-(--S--)    intersects with outer only - distance between N and S > their radii
                                # (----N---(-)-S--)      intersects with both
                                # (----N-(--S-)-)        intersects with both
                                # (---(-N-S--)-)         intersects with inner only - distance between N and S + radius_S does not exceed radius_N
                                
                                if inner_phash_id is not None:
                                    
                                    spheres_disjoint = node_hamming_distance > ( node_radius + search_radius )
                                    
                                    if not spheres_disjoint: # i.e. they intersect at some point
                                        
                                        next_potentials.append( inner_phash_id )
                                        
                                    
                                
                                if outer_phash_id is not None:
                                    
                                    search_sphere_subset_of_node_sphere = ( node_hamming_distance + search_radius ) <= node_radius
                                    
                                    if not search_sphere_subset_of_node_sphere: # i.e. search sphere intersects with non-node sphere space at some point
                                        
                                        next_potentials.append( outer_phash_id )
                                        
                                    
                                
                            
                        
                    
                
            
            if HG.db_report_mode:
                
                HydrusData.ShowText( 'Similar file search completed in ' + HydrusData.ToHumanInt( num_cycles ) + ' cycles.' )
                
            
            # so, so now we have phash_ids and distances. let's map that to actual files.
            # files can have multiple phashes, and phashes can refer to multiple files, so let's make sure we are setting the smallest distance we found
            
            similar_phash_ids = list( similar_phash_ids_to_distances.keys() )
            
            similar_phash_ids_to_hash_ids = HydrusData.BuildKeyToListDict( self._ExecuteManySelectSingleParam( 'SELECT phash_id, hash_id FROM shape_perceptual_hash_map WHERE phash_id = ?;', similar_phash_ids ) )
            
            similar_hash_ids_to_distances = {}
            
            for ( phash_id, hash_ids ) in similar_phash_ids_to_hash_ids.items():
                
                distance = similar_phash_ids_to_distances[ phash_id ]
                
                for hash_id in hash_ids:
                    
                    if hash_id not in similar_hash_ids_to_distances:
                        
                        similar_hash_ids_to_distances[ hash_id ] = distance
                        
                    else:
                        
                        current_distance = similar_hash_ids_to_distances[ hash_id ]
                        
                        if distance < current_distance:
                            
                            similar_hash_ids_to_distances[ hash_id ] = distance
                            
                        
                    
                
            
            similar_hash_ids_and_distances = list( similar_hash_ids_to_distances.items() )
            
        
        return similar_hash_ids_and_distances
        
    
    def _PHashesSetFileMetadata( self, hash_id, phashes ):
        
        current_phash_ids = self._STS( self._c.execute( 'SELECT phash_id FROM shape_perceptual_hash_map WHERE hash_id = ?;', ( hash_id, ) ) )
        
        if len( current_phash_ids ) > 0:
            
            self._PHashesDisassociatePHashes( hash_id, current_phash_ids )
            
        
        if len( phashes ) > 0:
            
            self._PHashesAssociatePHashes( hash_id, phashes )
            
        
    
    def _PopulateHashIdsToHashesCache( self, hash_ids, exception_on_error = False ):
        
        if len( self._hash_ids_to_hashes_cache ) > 100000:
            
            self._hash_ids_to_hashes_cache = {}
            
        
        uncached_hash_ids = { hash_id for hash_id in hash_ids if hash_id not in self._hash_ids_to_hashes_cache }
        
        if len( uncached_hash_ids ) > 0:
            
            pubbed_error = False
            
            if len( uncached_hash_ids ) > 100:
                
                with HydrusDB.TemporaryIntegerTable( self._c, uncached_hash_ids, 'hash_id' ) as temp_table_name:
                    
                    self._AnalyzeTempTable( temp_table_name )
                    
                    uncached_hash_ids_to_hashes = dict( self._c.execute( 'SELECT hash_id, hash FROM hashes NATURAL JOIN {};'.format( temp_table_name ) ) )
                    
                
            else:
                
                uncached_hash_ids_to_hashes = dict( self._ExecuteManySelectSingleParam( 'SELECT hash_id, hash FROM hashes WHERE hash_id = ?;', uncached_hash_ids ) )
                
            
            if len( uncached_hash_ids_to_hashes ) < len( uncached_hash_ids ):
                
                for hash_id in uncached_hash_ids:
                    
                    if hash_id not in uncached_hash_ids_to_hashes:
                        
                        if exception_on_error:
                            
                            raise HydrusExceptions.DataMissing( 'Did not find all entries for those hash ids!' )
                            
                        
                        HydrusData.DebugPrint( 'Database hash error: hash_id ' + str( hash_id ) + ' was missing!' )
                        
                        if not pubbed_error:
                            
                            HydrusData.ShowText( 'A file identifier was missing! This is a serious error that likely needs a repository reset to fix! Think about contacting hydrus dev!' )
                            
                            pubbed_error = True
                            
                        
                        hash = bytes.fromhex( 'aaaaaaaaaaaaaaaa' ) + os.urandom( 16 )
                        
                        uncached_hash_ids_to_hashes[ hash_id ] = hash
                        
                    
                
            
            self._hash_ids_to_hashes_cache.update( uncached_hash_ids_to_hashes )
            
        
    
    def _PopulateTagIdsToTagsCache( self, tag_ids ):
        
        if len( self._tag_ids_to_tags_cache ) > 100000:
            
            self._tag_ids_to_tags_cache = {}
            
        
        uncached_tag_ids = { tag_id for tag_id in tag_ids if tag_id not in self._tag_ids_to_tags_cache }
        
        if len( uncached_tag_ids ) > 0:
            
            if len( uncached_tag_ids ) > 100:
                
                with HydrusDB.TemporaryIntegerTable( self._c, uncached_tag_ids, 'tag_id' ) as temp_table_name:
                    
                    self._AnalyzeTempTable( temp_table_name )
                    
                    local_uncached_tag_ids_to_tags = { tag_id : tag for ( tag_id, tag ) in self._c.execute( 'SELECT tag_id, tag FROM local_tags_cache NATURAL JOIN {};'.format( temp_table_name ) ) }
                    
                
            else:
                
                local_uncached_tag_ids_to_tags = { tag_id : tag for ( tag_id, tag ) in self._ExecuteManySelectSingleParam( 'SELECT tag_id, tag FROM local_tags_cache WHERE tag_id = ?;', uncached_tag_ids ) }
                
            
            self._tag_ids_to_tags_cache.update( local_uncached_tag_ids_to_tags )
            
            uncached_tag_ids = { tag_id for tag_id in uncached_tag_ids if tag_id not in self._tag_ids_to_tags_cache }
            
        
        if len( uncached_tag_ids ) > 0:
            
            if len( uncached_tag_ids ) > 100:
                
                with HydrusDB.TemporaryIntegerTable( self._c, uncached_tag_ids, 'tag_id' ) as temp_table_name:
                    
                    self._AnalyzeTempTable( temp_table_name )
                    
                    select_statement = 'SELECT tag_id, namespace, subtag FROM tags NATURAL JOIN namespaces NATURAL JOIN subtags NATURAL JOIN {};'.format( temp_table_name )
                    
                    uncached_tag_ids_to_tags = { tag_id : HydrusTags.CombineTag( namespace, subtag ) for ( tag_id, namespace, subtag ) in self._c.execute( select_statement ) }
                    
                
            else:
                
                select_statement = 'SELECT tag_id, namespace, subtag FROM tags NATURAL JOIN namespaces NATURAL JOIN subtags WHERE tag_id = ?;'
                
                uncached_tag_ids_to_tags = { tag_id : HydrusTags.CombineTag( namespace, subtag ) for ( tag_id, namespace, subtag ) in self._ExecuteManySelectSingleParam( select_statement, uncached_tag_ids ) }
                
            
            if len( uncached_tag_ids_to_tags ) < len( uncached_tag_ids ):
                
                for tag_id in uncached_tag_ids:
                    
                    if tag_id not in uncached_tag_ids_to_tags:
                        
                        tag = 'unknown tag:' + HydrusData.GenerateKey().hex()
                        
                        ( namespace, subtag ) = HydrusTags.SplitTag( tag )
                        
                        namespace_id = self._GetNamespaceId( namespace )
                        subtag_id = self._GetSubtagId( subtag )
                        
                        self._c.execute( 'REPLACE INTO tags ( tag_id, namespace_id, subtag_id ) VALUES ( ?, ?, ? );', ( tag_id, namespace_id, subtag_id ) )
                        
                        uncached_tag_ids_to_tags[ tag_id ] = tag
                        
                    
                
            
            self._tag_ids_to_tags_cache.update( uncached_tag_ids_to_tags )
            
        
    
    def _ProcessContentUpdates( self, service_keys_to_content_updates, do_pubsubs = True ):
        
        notify_new_downloads = False
        notify_new_pending = False
        notify_new_parents = False
        notify_new_siblings = False
        notify_new_force_refresh_tags = False
        
        for ( service_key, content_updates ) in service_keys_to_content_updates.items():
            
            try:
                
                service_id = self._GetServiceId( service_key )
                
            except HydrusExceptions.DataMissing:
                
                continue
                
            
            service = self._GetService( service_id )
            
            service_type = service.GetServiceType()
            
            ultimate_mappings_ids = []
            ultimate_deleted_mappings_ids = []
            
            ultimate_pending_mappings_ids = []
            ultimate_pending_rescinded_mappings_ids = []
            
            ultimate_petitioned_mappings_ids = []
            ultimate_petitioned_rescinded_mappings_ids = []
            
            for content_update in content_updates:
                
                ( data_type, action, row ) = content_update.ToTuple()
                
                if service_type in HC.FILE_SERVICES:
                    
                    if data_type == HC.CONTENT_TYPE_FILES:
                        
                        if action == HC.CONTENT_UPDATE_ADVANCED:
                            
                            ( sub_action, sub_row ) = row
                            
                            if sub_action == 'delete_deleted':
                                
                                hashes = sub_row
                                
                                if hashes is None:
                                    
                                    self._c.execute( 'DELETE FROM deleted_files WHERE service_id = ?;', ( service_id, ) )
                                    
                                    self._c.execute( 'DELETE FROM local_file_deletion_reasons;' )
                                    
                                else:
                                    
                                    hash_ids = self._GetHashIds( hashes )
                                    
                                    self._c.executemany( 'DELETE FROM deleted_files WHERE service_id = ? AND hash_id = ?;', ( ( service_id, hash_id ) for hash_id in hash_ids ) )
                                    
                                    self._c.executemany( 'DELETE FROM local_file_deletion_reasons WHERE hash_id = ?;', ( ( hash_id, ) for hash_id in hash_ids ) )
                                    
                                
                            
                            self._c.execute( 'DELETE FROM service_info WHERE service_id = ?;', ( service_id, ) )
                            
                        elif action == HC.CONTENT_UPDATE_ADD:
                            
                            if service_type in HC.LOCAL_FILE_SERVICES or service_type == HC.FILE_REPOSITORY:
                                
                                ( file_info_manager, timestamp ) = row
                                
                                ( hash_id, hash, size, mime, width, height, duration, num_frames, has_audio, num_words ) = file_info_manager.ToTuple()
                                
                                self._AddFilesInfo( [ ( hash_id, size, mime, width, height, duration, num_frames, has_audio, num_words ) ] )
                                
                            elif service_type == HC.IPFS:
                                
                                ( file_info_manager, multihash ) = row
                                
                                hash_id = file_info_manager.hash_id
                                
                                self._SetServiceFilename( service_id, hash_id, multihash )
                                
                                timestamp = HydrusData.GetNow()
                                
                            
                            self._AddFiles( service_id, [ ( hash_id, timestamp ) ] )
                            
                        elif action == HC.CONTENT_UPDATE_PEND:
                            
                            hashes = row
                            
                            hash_ids = self._GetHashIds( hashes )
                            
                            self._c.executemany( 'INSERT OR IGNORE INTO file_transfers ( service_id, hash_id ) VALUES ( ?, ? );', ( ( service_id, hash_id ) for hash_id in hash_ids ) )
                            
                            if service_key == CC.COMBINED_LOCAL_FILE_SERVICE_KEY: notify_new_downloads = True
                            else: notify_new_pending = True
                            
                        elif action == HC.CONTENT_UPDATE_PETITION:
                            
                            hashes = row
                            
                            reason = content_update.GetReason()
                            
                            hash_ids = self._GetHashIds( hashes )
                            
                            reason_id = self._GetTextId( reason )
                            
                            self._c.executemany( 'DELETE FROM file_petitions WHERE service_id = ? AND hash_id = ?;', ( ( service_id, hash_id ) for hash_id in hash_ids ) )
                            
                            self._c.executemany( 'INSERT OR IGNORE INTO file_petitions ( service_id, hash_id, reason_id ) VALUES ( ?, ?, ? );', ( ( service_id, hash_id, reason_id ) for hash_id in hash_ids ) )
                            
                            notify_new_pending = True
                            
                        elif action == HC.CONTENT_UPDATE_RESCIND_PEND:
                            
                            hashes = row
                            
                            hash_ids = self._GetHashIds( hashes )
                            
                            self._c.executemany( 'DELETE FROM file_transfers WHERE service_id = ? AND hash_id = ?;', ( ( service_id, hash_id ) for hash_id in hash_ids ) )
                            
                            notify_new_pending = True
                            
                        elif action == HC.CONTENT_UPDATE_RESCIND_PETITION:
                            
                            hashes = row
                            
                            hash_ids = self._GetHashIds( hashes )
                            
                            self._c.executemany( 'DELETE FROM file_petitions WHERE service_id = ? AND hash_id = ?;', ( ( service_id, hash_id ) for hash_id in hash_ids ) )
                            
                            notify_new_pending = True
                            
                        else:
                            
                            hashes = row
                            
                            hash_ids = self._GetHashIds( hashes )
                            
                            if action == HC.CONTENT_UPDATE_ARCHIVE:
                                
                                self._ArchiveFiles( hash_ids )
                                
                            elif action == HC.CONTENT_UPDATE_INBOX:
                                
                                self._InboxFiles( hash_ids )
                                
                            elif action == HC.CONTENT_UPDATE_DELETE:
                                
                                if service_id == self._local_file_service_id:
                                    
                                    reason = content_update.GetReason()
                                    
                                    self._SetLocalFileDeletionReason( hash_ids, reason )
                                    
                                
                                self._DeleteFiles( service_id, hash_ids )
                                
                                if service_id == self._trash_service_id:
                                    
                                    self._DeleteFiles( self._combined_local_file_service_id, hash_ids )
                                    
                                
                            elif action == HC.CONTENT_UPDATE_UNDELETE:
                                
                                splayed_hash_ids = HydrusData.SplayListForDB( hash_ids )
                                
                                rows = self._c.execute( 'SELECT hash_id, timestamp FROM current_files WHERE service_id = ? AND hash_id IN ' + splayed_hash_ids + ';', ( self._combined_local_file_service_id, ) ).fetchall()
                                
                                self._AddFiles( self._local_file_service_id, rows )
                                
                            
                        
                    elif data_type == HC.CONTENT_TYPE_DIRECTORIES:
                        
                        if action == HC.CONTENT_UPDATE_ADD:
                            
                            ( hashes, dirname, note ) = row
                            
                            hash_ids = self._GetHashIds( hashes )
                            
                            self._SetServiceDirectory( service_id, hash_ids, dirname, note )
                            
                        elif action == HC.CONTENT_UPDATE_DELETE:
                            
                            dirname = row
                            
                            self._DeleteServiceDirectory( service_id, dirname )
                            
                        
                    elif data_type == HC.CONTENT_TYPE_URLS:
                        
                        if action == HC.CONTENT_UPDATE_ADD:
                            
                            ( urls, hashes ) = row
                            
                            url_ids = { self._GetURLId( url ) for url in urls }
                            hash_ids = self._GetHashIds( hashes )
                            
                            self._c.executemany( 'INSERT OR IGNORE INTO url_map ( hash_id, url_id ) VALUES ( ?, ? );', itertools.product( hash_ids, url_ids ) )
                            
                        elif action == HC.CONTENT_UPDATE_DELETE:
                            
                            ( urls, hashes ) = row
                            
                            url_ids = { self._GetURLId( url ) for url in urls }
                            hash_ids = self._GetHashIds( hashes )
                            
                            self._c.executemany( 'DELETE FROM url_map WHERE hash_id = ? AND url_id = ?;', itertools.product( hash_ids, url_ids ) )
                            
                        
                    elif data_type == HC.CONTENT_TYPE_FILE_VIEWING_STATS:
                        
                        if action == HC.CONTENT_UPDATE_ADVANCED:
                            
                            action = row
                            
                            if action == 'clear':
                                
                                self._c.execute( 'DELETE FROM file_viewing_stats;' )
                                
                            
                        elif action == HC.CONTENT_UPDATE_ADD:
                            
                            ( hash, preview_views_delta, preview_viewtime_delta, media_views_delta, media_viewtime_delta ) = row
                            
                            hash_id = self._GetHashId( hash )
                            
                            self._c.execute( 'INSERT OR IGNORE INTO file_viewing_stats ( hash_id, preview_views, preview_viewtime, media_views, media_viewtime ) VALUES ( ?, ?, ?, ?, ? );', ( hash_id, 0, 0, 0, 0 ) )
                            
                            self._c.execute( 'UPDATE file_viewing_stats SET preview_views = preview_views + ?, preview_viewtime = preview_viewtime + ?, media_views = media_views + ?, media_viewtime = media_viewtime + ? WHERE hash_id = ?;', ( preview_views_delta, preview_viewtime_delta, media_views_delta, media_viewtime_delta, hash_id ) )
                            
                        elif action == HC.CONTENT_UPDATE_DELETE:
                            
                            hashes = row
                            
                            hash_ids = self._GetHashIds( hashes )
                            
                            self._c.executemany( 'DELETE FROM file_viewing_stats WHERE hash_id = ?;', ( ( hash_id, ) for hash_id in hash_ids ) )
                            
                        
                    
                elif service_type in HC.REAL_TAG_SERVICES:
                    
                    if data_type == HC.CONTENT_TYPE_MAPPINGS:
                        
                        ( tag, hashes ) = row
                        
                        try:
                            
                            tag_id = self._GetTagId( tag )
                            
                        except HydrusExceptions.TagSizeException:
                            
                            continue
                            
                        
                        hash_ids = self._GetHashIds( hashes )
                        
                        if action == HC.CONTENT_UPDATE_ADD:
                            
                            if not HG.client_controller.tag_display_manager.TagOK( ClientTags.TAG_DISPLAY_STORAGE, service_key, tag ):
                                
                                continue
                                
                            
                            ultimate_mappings_ids.append( ( tag_id, hash_ids ) )
                            
                        elif action == HC.CONTENT_UPDATE_DELETE:
                            
                            ultimate_deleted_mappings_ids.append( ( tag_id, hash_ids ) )
                            
                        elif action == HC.CONTENT_UPDATE_PEND:
                            
                            if not HG.client_controller.tag_display_manager.TagOK( ClientTags.TAG_DISPLAY_STORAGE, service_key, tag ):
                                
                                continue
                                
                            
                            ultimate_pending_mappings_ids.append( ( tag_id, hash_ids ) )
                            
                        elif action == HC.CONTENT_UPDATE_RESCIND_PEND:
                            
                            ultimate_pending_rescinded_mappings_ids.append( ( tag_id, hash_ids ) )
                            
                        elif action == HC.CONTENT_UPDATE_PETITION:
                            
                            reason = content_update.GetReason()
                            
                            reason_id = self._GetTextId( reason )
                            
                            ultimate_petitioned_mappings_ids.append( ( tag_id, hash_ids, reason_id ) )
                            
                        elif action == HC.CONTENT_UPDATE_RESCIND_PETITION:
                            
                            ultimate_petitioned_rescinded_mappings_ids.append( ( tag_id, hash_ids ) )
                            
                        elif action == HC.CONTENT_UPDATE_CLEAR_DELETE_RECORD:
                            
                            ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( service_id )
                            
                            self._c.executemany( 'DELETE FROM {} WHERE tag_id = ? AND hash_id = ?;'.format( deleted_mappings_table_name ), ( ( tag_id, hash_id ) for hash_id in hash_ids ) )
                            
                            self._c.execute( 'DELETE FROM service_info WHERE service_id = ? AND info_type = ?;', ( service_id, HC.SERVICE_INFO_NUM_DELETED_MAPPINGS ) )
                            
                            cache_file_service_ids = self._GetServiceIds( HC.AUTOCOMPLETE_CACHE_SPECIFIC_FILE_SERVICES )
                            
                            for cache_file_service_id in cache_file_service_ids:
                                
                                ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( cache_file_service_id, service_id )
                                
                                self._c.executemany( 'DELETE FROM ' + cache_deleted_mappings_table_name + ' WHERE hash_id = ? AND tag_id = ?;', ( ( hash_id, tag_id ) for hash_id in hash_ids ) )
                                
                            
                        
                    elif data_type == HC.CONTENT_TYPE_TAG_PARENTS:
                        
                        if action in ( HC.CONTENT_UPDATE_ADD, HC.CONTENT_UPDATE_DELETE ):
                            
                            ( child_tag, parent_tag ) = row
                            
                            try:
                                
                                child_tag_id = self._GetTagId( child_tag )
                                
                                parent_tag_id = self._GetTagId( parent_tag )
                                
                            except HydrusExceptions.TagSizeException:
                                
                                continue
                                
                            
                            pairs = ( ( child_tag_id, parent_tag_id ), )
                            
                            if action == HC.CONTENT_UPDATE_ADD:
                                
                                self._AddTagParents( service_id, pairs, make_content_updates = True )
                                
                            elif action == HC.CONTENT_UPDATE_DELETE:
                                
                                self._DeleteTagParents( service_id, pairs )
                                
                            
                        elif action in ( HC.CONTENT_UPDATE_PEND, HC.CONTENT_UPDATE_PETITION ):
                            
                            if action == HC.CONTENT_UPDATE_PEND:
                                
                                new_status = HC.CONTENT_STATUS_PENDING
                                
                            elif action == HC.CONTENT_UPDATE_PETITION:
                                
                                new_status = HC.CONTENT_STATUS_PETITIONED
                                
                            
                            ( child_tag, parent_tag ) = row
                            
                            try:
                                
                                child_tag_id = self._GetTagId( child_tag )
                                
                                parent_tag_id = self._GetTagId( parent_tag )
                                
                            except HydrusExceptions.TagSizeException:
                                
                                continue
                                
                            
                            reason = content_update.GetReason()
                            
                            reason_id = self._GetTextId( reason )
                            
                            self._c.execute( 'DELETE FROM tag_parent_petitions WHERE service_id = ? AND child_tag_id = ? AND parent_tag_id = ?;', ( service_id, child_tag_id, parent_tag_id ) )
                            
                            self._c.execute( 'INSERT OR IGNORE INTO tag_parent_petitions ( service_id, child_tag_id, parent_tag_id, reason_id, status ) VALUES ( ?, ?, ?, ?, ? );', ( service_id, child_tag_id, parent_tag_id, reason_id, new_status ) )
                            
                            notify_new_pending = True
                            
                        elif action in ( HC.CONTENT_UPDATE_RESCIND_PEND, HC.CONTENT_UPDATE_RESCIND_PETITION ):
                            
                            if action == HC.CONTENT_UPDATE_RESCIND_PEND:
                                
                                deletee_status = HC.CONTENT_STATUS_PENDING
                                
                            elif action == HC.CONTENT_UPDATE_RESCIND_PETITION:
                                
                                deletee_status = HC.CONTENT_STATUS_PETITIONED
                                
                            
                            ( child_tag, parent_tag ) = row
                            
                            try:
                                
                                child_tag_id = self._GetTagId( child_tag )
                                
                                parent_tag_id = self._GetTagId( parent_tag )
                                
                            except HydrusExceptions.TagSizeException:
                                
                                continue
                                
                            
                            self._c.execute( 'DELETE FROM tag_parent_petitions WHERE service_id = ? AND child_tag_id = ? AND parent_tag_id = ? AND status = ?;', ( service_id, child_tag_id, parent_tag_id, deletee_status ) )
                            
                            notify_new_pending = True
                            
                        
                        notify_new_parents = True
                        
                    elif data_type == HC.CONTENT_TYPE_TAG_SIBLINGS:
                        
                        if action in ( HC.CONTENT_UPDATE_ADD, HC.CONTENT_UPDATE_DELETE ):
                            
                            ( bad_tag, good_tag ) = row
                            
                            try:
                                
                                bad_tag_id = self._GetTagId( bad_tag )
                                
                                good_tag_id = self._GetTagId( good_tag )
                                
                            except HydrusExceptions.TagSizeException:
                                
                                continue
                                
                            
                            pairs = ( ( bad_tag_id, good_tag_id ), )
                            
                            if action == HC.CONTENT_UPDATE_ADD:
                                
                                self._AddTagSiblings( service_id, pairs, make_content_updates = True )
                                
                            elif action == HC.CONTENT_UPDATE_DELETE:
                                
                                self._DeleteTagSiblings( service_id, pairs )
                                
                            
                        elif action in ( HC.CONTENT_UPDATE_PEND, HC.CONTENT_UPDATE_PETITION ):
                            
                            if action == HC.CONTENT_UPDATE_PEND:
                                
                                new_status = HC.CONTENT_STATUS_PENDING
                                
                            elif action == HC.CONTENT_UPDATE_PETITION:
                                
                                new_status = HC.CONTENT_STATUS_PETITIONED
                                
                            
                            ( bad_tag, good_tag ) = row
                            
                            try:
                                
                                bad_tag_id = self._GetTagId( bad_tag )
                                
                                good_tag_id = self._GetTagId( good_tag )
                                
                            except HydrusExceptions.TagSizeException:
                                
                                continue
                                
                            
                            reason = content_update.GetReason()
                            
                            reason_id = self._GetTextId( reason )
                            
                            self._c.execute( 'DELETE FROM tag_sibling_petitions WHERE service_id = ? AND bad_tag_id = ? AND good_tag_id = ?;', ( service_id, bad_tag_id, good_tag_id ) )
                            
                            self._c.execute( 'INSERT OR IGNORE INTO tag_sibling_petitions ( service_id, bad_tag_id, good_tag_id, reason_id, status ) VALUES ( ?, ?, ?, ?, ? );', ( service_id, bad_tag_id, good_tag_id, reason_id, new_status ) )
                            
                            self._CacheTagSiblingsUpdateChains( service_id, { bad_tag_id, good_tag_id } )
                            
                            notify_new_pending = True
                            
                        elif action in ( HC.CONTENT_UPDATE_RESCIND_PEND, HC.CONTENT_UPDATE_RESCIND_PETITION ):
                            
                            if action == HC.CONTENT_UPDATE_RESCIND_PEND:
                                
                                deletee_status = HC.CONTENT_STATUS_PENDING
                                
                            elif action == HC.CONTENT_UPDATE_RESCIND_PETITION:
                                
                                deletee_status = HC.CONTENT_STATUS_PETITIONED
                                
                            
                            ( bad_tag, good_tag ) = row
                            
                            try:
                                
                                bad_tag_id = self._GetTagId( bad_tag )
                                
                            except HydrusExceptions.TagSizeException:
                                
                                continue
                                
                            
                            self._c.execute( 'DELETE FROM tag_sibling_petitions WHERE service_id = ? AND bad_tag_id = ? AND status = ?;', ( service_id, bad_tag_id, deletee_status ) )
                            
                            self._CacheTagSiblingsUpdateChains( service_id, { bad_tag_id } )
                            
                            notify_new_pending = True
                            
                        
                        notify_new_siblings = True
                        
                    
                elif service_type in HC.RATINGS_SERVICES:
                    
                    if action == HC.CONTENT_UPDATE_ADD:
                        
                        ( rating, hashes ) = row
                        
                        hash_ids = self._GetHashIds( hashes )
                        
                        splayed_hash_ids = HydrusData.SplayListForDB( hash_ids )
                        
                        if service_type in ( HC.LOCAL_RATING_LIKE, HC.LOCAL_RATING_NUMERICAL ):
                            
                            ratings_added = 0
                            
                            self._c.executemany( 'DELETE FROM local_ratings WHERE service_id = ? AND hash_id = ?;', ( ( service_id, hash_id ) for hash_id in hash_ids ) )
                            
                            ratings_added -= self._GetRowCount()
                            
                            if rating is not None:
                                
                                self._c.executemany( 'INSERT INTO local_ratings ( service_id, hash_id, rating ) VALUES ( ?, ?, ? );', [ ( service_id, hash_id, rating ) for hash_id in hash_ids ] )
                                
                                ratings_added += self._GetRowCount()
                                
                            
                            self._c.execute( 'UPDATE service_info SET info = info + ? WHERE service_id = ? AND info_type = ?;', ( ratings_added, service_id, HC.SERVICE_INFO_NUM_FILES ) )
                            
                        
                    elif action == HC.CONTENT_UPDATE_ADVANCED:
                        
                        action = row
                        
                        if action == 'delete_for_deleted_files':
                            
                            self._c.execute( 'DELETE FROM local_ratings WHERE local_ratings.service_id = ? and hash_id IN ( SELECT hash_id FROM deleted_files WHERE deleted_files.service_id = ? );', ( service_id, self._combined_local_file_service_id ) )
                            
                            ratings_deleted = self._GetRowCount()
                            
                            self._c.execute( 'UPDATE service_info SET info = info - ? WHERE service_id = ? AND info_type = ?;', ( ratings_deleted, service_id, HC.SERVICE_INFO_NUM_FILES ) )
                            
                        elif action == 'delete_for_non_local_files':
                            
                            self._c.execute( 'DELETE FROM local_ratings WHERE local_ratings.service_id = ? and hash_id NOT IN ( SELECT hash_id FROM current_files WHERE current_files.service_id = ? );', ( service_id, self._combined_local_file_service_id ) )
                            
                            ratings_deleted = self._GetRowCount()
                            
                            self._c.execute( 'UPDATE service_info SET info = info - ? WHERE service_id = ? AND info_type = ?;', ( ratings_deleted, service_id, HC.SERVICE_INFO_NUM_FILES ) )
                            
                        elif action == 'delete_for_all_files':
                            
                            self._c.execute( 'DELETE FROM local_ratings WHERE service_id = ?;', ( service_id, ) )
                            
                            self._c.execute( 'UPDATE service_info SET info = ? WHERE service_id = ? AND info_type = ?;', ( 0, service_id, HC.SERVICE_INFO_NUM_FILES ) )
                            
                        
                    
                elif service_type == HC.LOCAL_NOTES:
                    
                    if action == HC.CONTENT_UPDATE_SET:
                        
                        ( hash, name, note ) = row
                        
                        hash_id = self._GetHashId( hash )
                        name_id = self._GetLabelId( name )
                        
                        self._c.execute( 'DELETE FROM file_notes WHERE hash_id = ? AND name_id = ?;', ( hash_id, name_id ) )
                        
                        if len( note ) > 0:
                            
                            note_id = self._GetNoteId( note )
                            
                            self._c.execute( 'INSERT OR IGNORE INTO file_notes ( hash_id, name_id, note_id ) VALUES ( ?, ?, ? );', ( hash_id, name_id, note_id ) )
                            
                        
                    elif action == HC.CONTENT_UPDATE_DELETE:
                        
                        ( hash, name ) = row
                        
                        hash_id = self._GetHashId( hash )
                        name_id = self._GetLabelId( name )
                        
                        self._c.execute( 'DELETE FROM file_notes WHERE hash_id = ? AND name_id = ?;', ( hash_id, name_id ) )
                        
                    
                
            
            if len( ultimate_mappings_ids ) + len( ultimate_deleted_mappings_ids ) + len( ultimate_pending_mappings_ids ) + len( ultimate_pending_rescinded_mappings_ids ) + len( ultimate_petitioned_mappings_ids ) + len( ultimate_petitioned_rescinded_mappings_ids ) > 0:
                
                self._UpdateMappings( service_id, mappings_ids = ultimate_mappings_ids, deleted_mappings_ids = ultimate_deleted_mappings_ids, pending_mappings_ids = ultimate_pending_mappings_ids, pending_rescinded_mappings_ids = ultimate_pending_rescinded_mappings_ids, petitioned_mappings_ids = ultimate_petitioned_mappings_ids, petitioned_rescinded_mappings_ids = ultimate_petitioned_rescinded_mappings_ids )
                
                notify_new_pending = True
                
            
        
        if do_pubsubs:
            
            if notify_new_downloads:
                
                self.pub_after_job( 'notify_new_downloads' )
                
            if notify_new_pending:
                
                self.pub_after_job( 'notify_new_pending' )
                
            if notify_new_siblings:
                
                self.pub_after_job( 'notify_new_siblings_data' )
                self.pub_after_job( 'notify_new_parents' )
                
            elif notify_new_parents:
                
                self.pub_after_job( 'notify_new_parents' )
                
            if notify_new_force_refresh_tags:
                
                self.pub_after_job( 'notify_new_force_refresh_tags_data' )
                
            
            self.pub_content_updates_after_commit( service_keys_to_content_updates )
            
        
    
    def _ProcessRepositoryContent( self, service_key, content_hash, content_iterator_dict, job_key, work_time ):
        
        FILES_INITIAL_CHUNK_SIZE = 20
        MAPPINGS_INITIAL_CHUNK_SIZE = 50
        NEW_TAG_PARENTS_INITIAL_CHUNK_SIZE = 1
        PAIR_ROWS_INITIAL_CHUNK_SIZE = 100
        
        service_id = self._GetServiceId( service_key )
        
        precise_time_to_stop = HydrusData.GetNowPrecise() + work_time
        
        num_rows_processed = 0
        
        if 'new_files' in content_iterator_dict:
            
            has_audio = None # hack until we figure this out better
            
            i = content_iterator_dict[ 'new_files' ]
            
            for chunk in HydrusData.SplitIteratorIntoAutothrottledChunks( i, FILES_INITIAL_CHUNK_SIZE, precise_time_to_stop ):
                
                files_info_rows = []
                files_rows = []
                
                for ( service_hash_id, size, mime, timestamp, width, height, duration, num_frames, num_words ) in chunk:
                    
                    hash_id = self._CacheRepositoryNormaliseServiceHashId( service_id, service_hash_id )
                    
                    files_info_rows.append( ( hash_id, size, mime, width, height, duration, num_frames, has_audio, num_words ) )
                    
                    files_rows.append( ( hash_id, timestamp ) )
                    
                
                self._AddFilesInfo( files_info_rows )
                
                self._AddFiles( service_id, files_rows )
                
                num_rows_processed += len( files_rows )
                
                if HydrusData.TimeHasPassedPrecise( precise_time_to_stop ) or job_key.IsCancelled():
                    
                    return num_rows_processed
                    
                
            
            del content_iterator_dict[ 'new_files' ]
            
        
        #
        
        if 'deleted_files' in content_iterator_dict:
            
            i = content_iterator_dict[ 'deleted_files' ]
            
            for chunk in HydrusData.SplitIteratorIntoAutothrottledChunks( i, FILES_INITIAL_CHUNK_SIZE, precise_time_to_stop ):
                
                service_hash_ids = chunk
                
                hash_ids = self._CacheRepositoryNormaliseServiceHashIds( service_id, service_hash_ids )
                
                self._DeleteFiles( service_id, hash_ids )
                
                num_rows_processed += len( hash_ids )
                
                if HydrusData.TimeHasPassedPrecise( precise_time_to_stop ) or job_key.IsCancelled():
                    
                    return num_rows_processed
                    
                
            
            del content_iterator_dict[ 'deleted_files' ]
            
        
        #
        
        if 'new_mappings' in content_iterator_dict:
            
            i = content_iterator_dict[ 'new_mappings' ]
            
            for chunk in HydrusData.SplitMappingIteratorIntoAutothrottledChunks( i, MAPPINGS_INITIAL_CHUNK_SIZE, precise_time_to_stop ):
                
                mappings_ids = []
                
                num_rows = 0
                
                for ( service_tag_id, service_hash_ids ) in chunk:
                    
                    tag_id = self._CacheRepositoryNormaliseServiceTagId( service_id, service_tag_id )
                    hash_ids = self._CacheRepositoryNormaliseServiceHashIds( service_id, service_hash_ids )
                    
                    mappings_ids.append( ( tag_id, hash_ids ) )
                    
                    num_rows += len( service_hash_ids )
                    
                
                self._UpdateMappings( service_id, mappings_ids = mappings_ids )
                
                num_rows_processed += num_rows
                
                if HydrusData.TimeHasPassedPrecise( precise_time_to_stop ) or job_key.IsCancelled():
                    
                    return num_rows_processed
                    
                
            
            del content_iterator_dict[ 'new_mappings' ]
            
        
        #
        
        if 'deleted_mappings' in content_iterator_dict:
            
            i = content_iterator_dict[ 'deleted_mappings' ]
            
            for chunk in HydrusData.SplitMappingIteratorIntoAutothrottledChunks( i, MAPPINGS_INITIAL_CHUNK_SIZE, precise_time_to_stop ):
                
                deleted_mappings_ids = []
                
                num_rows = 0
                
                for ( service_tag_id, service_hash_ids ) in chunk:
                    
                    tag_id = self._CacheRepositoryNormaliseServiceTagId( service_id, service_tag_id )
                    hash_ids = self._CacheRepositoryNormaliseServiceHashIds( service_id, service_hash_ids )
                    
                    deleted_mappings_ids.append( ( tag_id, hash_ids ) )
                    
                    num_rows += len( service_hash_ids )
                    
                
                self._UpdateMappings( service_id, deleted_mappings_ids = deleted_mappings_ids )
                
                num_rows_processed += num_rows
                
                if HydrusData.TimeHasPassedPrecise( precise_time_to_stop ) or job_key.IsCancelled():
                    
                    return num_rows_processed
                    
                
            
            del content_iterator_dict[ 'deleted_mappings' ]
            
        
        #
        
        if 'new_parents' in content_iterator_dict:
            
            i = content_iterator_dict[ 'new_parents' ]
            
            for chunk in HydrusData.SplitIteratorIntoAutothrottledChunks( i, NEW_TAG_PARENTS_INITIAL_CHUNK_SIZE, precise_time_to_stop ):
                
                parent_ids = []
                
                for ( service_child_tag_id, service_parent_tag_id ) in chunk:
                    
                    child_tag_id = self._CacheRepositoryNormaliseServiceTagId( service_id, service_child_tag_id )
                    parent_tag_id = self._CacheRepositoryNormaliseServiceTagId( service_id, service_parent_tag_id )
                    
                    parent_ids.append( ( child_tag_id, parent_tag_id ) )
                    
                
                self._AddTagParents( service_id, parent_ids )
                
                num_rows_processed += len( parent_ids )
                
                if HydrusData.TimeHasPassedPrecise( precise_time_to_stop ) or job_key.IsCancelled():
                    
                    return num_rows_processed
                    
                
            
            del content_iterator_dict[ 'new_parents' ]
            
        
        #
        
        if 'deleted_parents' in content_iterator_dict:
            
            i = content_iterator_dict[ 'deleted_parents' ]
            
            for chunk in HydrusData.SplitIteratorIntoAutothrottledChunks( i, PAIR_ROWS_INITIAL_CHUNK_SIZE, precise_time_to_stop ):
                
                parent_ids = []
                
                for ( service_child_tag_id, service_parent_tag_id ) in chunk:
                    
                    child_tag_id = self._CacheRepositoryNormaliseServiceTagId( service_id, service_child_tag_id )
                    parent_tag_id = self._CacheRepositoryNormaliseServiceTagId( service_id, service_parent_tag_id )
                    
                    parent_ids.append( ( child_tag_id, parent_tag_id ) )
                    
                
                self._DeleteTagParents( service_id, parent_ids )
                
                num_rows = len( parent_ids )
                
                num_rows_processed += num_rows
                
                if HydrusData.TimeHasPassedPrecise( precise_time_to_stop ) or job_key.IsCancelled():
                    
                    return num_rows_processed
                    
                
            
            del content_iterator_dict[ 'deleted_parents' ]
            
        
        #
        
        if 'new_siblings' in content_iterator_dict:
            
            i = content_iterator_dict[ 'new_siblings' ]
            
            for chunk in HydrusData.SplitIteratorIntoAutothrottledChunks( i, PAIR_ROWS_INITIAL_CHUNK_SIZE, precise_time_to_stop ):
                
                sibling_ids = []
                
                for ( service_bad_tag_id, service_good_tag_id ) in chunk:
                    
                    bad_tag_id = self._CacheRepositoryNormaliseServiceTagId( service_id, service_bad_tag_id )
                    good_tag_id = self._CacheRepositoryNormaliseServiceTagId( service_id, service_good_tag_id )
                    
                    sibling_ids.append( ( bad_tag_id, good_tag_id ) )
                    
                
                self._AddTagSiblings( service_id, sibling_ids )
                
                num_rows = len( sibling_ids )
                
                num_rows_processed += num_rows
                
                if HydrusData.TimeHasPassedPrecise( precise_time_to_stop ) or job_key.IsCancelled():
                    
                    return num_rows_processed
                    
                
            
            del content_iterator_dict[ 'new_siblings' ]
            
        
        #
        
        if 'deleted_siblings' in content_iterator_dict:
            
            i = content_iterator_dict[ 'deleted_siblings' ]
            
            for chunk in HydrusData.SplitIteratorIntoAutothrottledChunks( i, PAIR_ROWS_INITIAL_CHUNK_SIZE, precise_time_to_stop ):
                
                sibling_ids = []
                
                for ( service_bad_tag_id, service_good_tag_id ) in chunk:
                    
                    bad_tag_id = self._CacheRepositoryNormaliseServiceTagId( service_id, service_bad_tag_id )
                    good_tag_id = self._CacheRepositoryNormaliseServiceTagId( service_id, service_good_tag_id )
                    
                    sibling_ids.append( ( bad_tag_id, good_tag_id ) )
                    
                
                self._DeleteTagSiblings( service_id, sibling_ids )
                
                num_rows_processed += len( sibling_ids )
                
                if HydrusData.TimeHasPassedPrecise( precise_time_to_stop ) or job_key.IsCancelled():
                    
                    return num_rows_processed
                    
                
            
            del content_iterator_dict[ 'deleted_siblings' ]
            
        
        repository_updates_table_name = GenerateRepositoryRepositoryUpdatesTableName( service_id )
        
        update_hash_id = self._GetHashId( content_hash )
        
        self._c.execute( 'UPDATE {} SET processed = ? WHERE hash_id = ?;'.format( repository_updates_table_name ), ( True, update_hash_id ) )
        
        return num_rows_processed
        
    
    def _ProcessRepositoryDefinitions( self, service_key, definition_hash, definition_iterator_dict, job_key, work_time ):
        
        service_id = self._GetServiceId( service_key )
        
        precise_time_to_stop = HydrusData.GetNowPrecise() + work_time
        
        ( hash_id_map_table_name, tag_id_map_table_name ) = GenerateRepositoryMasterCacheTableNames( service_id )
        
        num_rows_processed = 0
        
        if 'service_hash_ids_to_hashes' in definition_iterator_dict:
            
            i = definition_iterator_dict[ 'service_hash_ids_to_hashes' ]
            
            for chunk in HydrusData.SplitIteratorIntoAutothrottledChunks( i, 50, precise_time_to_stop ):
                
                inserts = []
                
                for ( service_hash_id, hash ) in chunk:
                    
                    hash_id = self._GetHashId( hash )
                    
                    inserts.append( ( service_hash_id, hash_id ) )
                    
                
                self._c.executemany( 'INSERT OR IGNORE INTO {} ( service_hash_id, hash_id ) VALUES ( ?, ? );'.format( hash_id_map_table_name ), inserts )
                
                num_rows_processed += len( inserts )
                
                if HydrusData.TimeHasPassedPrecise( precise_time_to_stop ) or job_key.IsCancelled():
                    
                    return num_rows_processed
                    
                
            
            del definition_iterator_dict[ 'service_hash_ids_to_hashes' ]
            
        
        if 'service_tag_ids_to_tags' in definition_iterator_dict:
            
            i = definition_iterator_dict[ 'service_tag_ids_to_tags' ]
            
            for chunk in HydrusData.SplitIteratorIntoAutothrottledChunks( i, 50, precise_time_to_stop ):
                
                inserts = []
                
                for ( service_tag_id, tag ) in chunk:
                    
                    tag_id = self._GetTagId( tag )
                    
                    inserts.append( ( service_tag_id, tag_id ) )
                    
                
                self._c.executemany( 'INSERT OR IGNORE INTO {} ( service_tag_id, tag_id ) VALUES ( ?, ? );'.format( tag_id_map_table_name ), inserts )
                
                num_rows_processed += len( inserts )
                
                if HydrusData.TimeHasPassedPrecise( precise_time_to_stop ) or job_key.IsCancelled():
                    
                    return num_rows_processed
                    
                
            
            del definition_iterator_dict[ 'service_tag_ids_to_tags' ]
            
        
        repository_updates_table_name = GenerateRepositoryRepositoryUpdatesTableName( service_id )
        
        update_hash_id = self._GetHashId( definition_hash )
        
        self._c.execute( 'UPDATE {} SET processed = ? WHERE hash_id = ?;'.format( repository_updates_table_name ), ( True, update_hash_id ) )
        
        return num_rows_processed
        
    
    def _PushRecentTags( self, service_key, tags ):
        
        service_id = self._GetServiceId( service_key )
        
        if tags is None:
            
            self._c.execute( 'DELETE FROM recent_tags WHERE service_id = ?;', ( service_id, ) )
            
        else:
            
            now = HydrusData.GetNow()
            
            tag_ids = [ self._GetTagId( tag ) for tag in tags ]
            
            self._c.executemany( 'REPLACE INTO recent_tags ( service_id, tag_id, timestamp ) VALUES ( ?, ?, ? );', ( ( service_id, tag_id, now ) for tag_id in tag_ids ) )
            
        
    
    def _Read( self, action, *args, **kwargs ):
        
        if action == 'autocomplete_predicates': result = self._GetAutocompletePredicates( *args, **kwargs )
        elif action == 'boned_stats': result = self._GetBonedStats( *args, **kwargs )
        elif action == 'client_files_locations': result = self._GetClientFilesLocations( *args, **kwargs )
        elif action == 'duplicate_pairs_for_filtering': result = self._DuplicatesGetPotentialDuplicatePairsForFiltering( *args, **kwargs )
        elif action == 'file_duplicate_hashes': result = self._DuplicatesGetFileHashesByDuplicateType( *args, **kwargs )
        elif action == 'file_duplicate_info': result = self._DuplicatesGetFileDuplicateInfo( *args, **kwargs )
        elif action == 'file_hashes': result = self._GetFileHashes( *args, **kwargs )
        elif action == 'file_maintenance_get_job': result = self._FileMaintenanceGetJob( *args, **kwargs )
        elif action == 'file_maintenance_get_job_counts': result = self._FileMaintenanceGetJobCounts( *args, **kwargs )
        elif action == 'file_query_ids': result = self._GetHashIdsFromQuery( *args, **kwargs )
        elif action == 'file_system_predicates': result = self._GetFileSystemPredicates( *args, **kwargs )
        elif action == 'filter_existing_tags': result = self._FilterExistingTags( *args, **kwargs )
        elif action == 'filter_hashes': result = self._FilterHashes( *args, **kwargs )
        elif action == 'force_refresh_tags_managers': result = self._GetForceRefreshTagsManagers( *args, **kwargs )
        elif action == 'hash_ids_to_hashes': result = self._GetHashIdsToHashes( *args, **kwargs )
        elif action == 'hash_status': result = self._GetHashStatus( *args, **kwargs )
        elif action == 'ideal_client_files_locations': result = self._GetIdealClientFilesLocations( *args, **kwargs )
        elif action == 'imageboards': result = self._GetYAMLDump( YAML_DUMP_ID_IMAGEBOARD, *args, **kwargs )
        elif action == 'in_inbox': result = self._InInbox( *args, **kwargs )
        elif action == 'is_an_orphan': result = self._IsAnOrphan( *args, **kwargs )
        elif action == 'last_shutdown_work_time': result = self._GetLastShutdownWorkTime( *args, **kwargs )
        elif action == 'load_into_disk_cache': result = self._LoadIntoDiskCache( *args, **kwargs )
        elif action == 'local_booru_share_keys': result = self._GetYAMLDumpNames( YAML_DUMP_ID_LOCAL_BOORU )
        elif action == 'local_booru_share': result = self._GetYAMLDump( YAML_DUMP_ID_LOCAL_BOORU, *args, **kwargs )
        elif action == 'local_booru_shares': result = self._GetYAMLDump( YAML_DUMP_ID_LOCAL_BOORU )
        elif action == 'maintenance_due': result = self._GetMaintenanceDue( *args, **kwargs )
        elif action == 'media_result': result = self._GetMediaResultFromHash( *args, **kwargs )
        elif action == 'media_results': result = self._GetMediaResultsFromHashes( *args, **kwargs )
        elif action == 'media_results_from_ids': result = self._GetMediaResults( *args, **kwargs )
        elif action == 'migration_get_mappings': result = self._MigrationGetMappings( *args, **kwargs )
        elif action == 'migration_get_pairs': result = self._MigrationGetPairs( *args, **kwargs )
        elif action == 'missing_repository_update_hashes': result = self._GetRepositoryUpdateHashesIDoNotHave( *args, **kwargs )
        elif action == 'missing_thumbnail_hashes': result = self._GetRepositoryThumbnailHashesIDoNotHave( *args, **kwargs )
        elif action == 'nums_pending': result = self._GetNumsPending( *args, **kwargs )
        elif action == 'trash_hashes': result = self._GetTrashHashes( *args, **kwargs )
        elif action == 'options': result = self._GetOptions( *args, **kwargs )
        elif action == 'pending': result = self._GetPending( *args, **kwargs )
        elif action == 'random_potential_duplicate_hashes': result = self._DuplicatesGetRandomPotentialDuplicateHashes( *args, **kwargs )
        elif action == 'recent_tags': result = self._GetRecentTags( *args, **kwargs )
        elif action == 'repository_progress': result = self._GetRepositoryProgress( *args, **kwargs )
        elif action == 'repository_unprocessed_hashes': result = self._GetRepositoryUpdateHashesUnprocessed( *args, **kwargs )
        elif action == 'repository_update_hashes_to_process': result = self._GetRepositoryUpdateHashesICanProcess( *args, **kwargs )
        elif action == 'serialisable': result = self._GetJSONDump( *args, **kwargs )
        elif action == 'serialisable_simple': result = self._GetJSONSimple( *args, **kwargs )
        elif action == 'serialisable_named': result = self._GetJSONDumpNamed( *args, **kwargs )
        elif action == 'serialisable_names': result = self._GetJSONDumpNames( *args, **kwargs )
        elif action == 'serialisable_names_to_backup_timestamps': result = self._GetJSONDumpNamesToBackupTimestamps( *args, **kwargs )
        elif action == 'service_directory': result = self._GetServiceDirectoryHashes( *args, **kwargs )
        elif action == 'service_directories': result = self._GetServiceDirectoriesInfo( *args, **kwargs )
        elif action == 'service_filenames': result = self._GetServiceFilenames( *args, **kwargs )
        elif action == 'service_info': result = self._GetServiceInfo( *args, **kwargs )
        elif action == 'services': result = self._GetServices( *args, **kwargs )
        elif action == 'similar_files_maintenance_status': result = self._PHashesGetMaintenanceStatus( *args, **kwargs )
        elif action == 'related_tags': result = self._GetRelatedTags( *args, **kwargs )
        elif action == 'tag_parents': result = self._GetTagParents( *args, **kwargs )
        elif action == 'tag_siblings': result = self._GetTagSiblings( *args, **kwargs )
        elif action == 'potential_duplicates_count': result = self._DuplicatesGetPotentialDuplicatesCount( *args, **kwargs )
        elif action == 'url_statuses': result = self._GetURLStatuses( *args, **kwargs )
        else: raise Exception( 'db received an unknown read command: ' + action )
        
        return result
        
    
    def _RegenerateTagMappingsCache( self ):
        
        job_key = ClientThreading.JobKey( cancellable = True )
        
        try:
            
            job_key.SetVariable( 'popup_title', 'regenerating tag mappings cache' )
            
            self._controller.pub( 'modal_message', job_key )
            
            # need this here to ensure that local_tags_cache exists, as the mappings cache regens use it
            # we can't move it up, as it relies on them for its own regen. just make an empty table here to get repopulated
            self._CreateDBCaches()
            
            tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            file_service_ids = self._GetServiceIds( HC.AUTOCOMPLETE_CACHE_SPECIFIC_FILE_SERVICES )
            
            time.sleep( 0.01 )
            
            for ( file_service_id, tag_service_id ) in itertools.product( file_service_ids, tag_service_ids ):
                
                if job_key.IsCancelled():
                    
                    break
                    
                
                message = 'generating specific ac_cache {}_{}'.format( file_service_id, tag_service_id )
                
                job_key.SetVariable( 'popup_text_1', message )
                self._controller.pub( 'splash_set_status_subtext', message )
                
                time.sleep( 0.01 )
                
                self._CacheSpecificMappingsDrop( file_service_id, tag_service_id )
                
                self._CacheSpecificMappingsGenerate( file_service_id, tag_service_id )
                
            
            for tag_service_id in tag_service_ids:
                
                if job_key.IsCancelled():
                    
                    break
                    
                
                message = 'generating combined files ac_cache {}'.format( tag_service_id )
                
                job_key.SetVariable( 'popup_text_1', message )
                self._controller.pub( 'splash_set_status_subtext', message )
                
                time.sleep( 0.01 )
                
                self._CacheCombinedFilesMappingsDrop( tag_service_id )
                
                self._CacheCombinedFilesMappingsGenerate( tag_service_id )
                
            
            message = 'generating local tag cache'
            
            job_key.SetVariable( 'popup_text_1', message )
            self._controller.pub( 'splash_set_status_subtext', message )
            
            self._CacheLocalTagIdsGenerate()
            
        finally:
            
            job_key.SetVariable( 'popup_text_1', 'done!' )
            
            job_key.Finish()
            
            job_key.Delete( 5 )
            
        
    
    def _RegenerateTagSiblingsCache( self ):
        
        job_key = ClientThreading.JobKey( cancellable = True )
        
        try:
            
            job_key.SetVariable( 'popup_title', 'regenerating tag siblings cache' )
            
            self._controller.pub( 'modal_message', job_key )
            
            tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
            time.sleep( 0.01 )
            
            for tag_service_id in tag_service_ids:
                
                if job_key.IsCancelled():
                    
                    break
                    
                
                message = 'generating specific tag siblings cache {}'.format( tag_service_id )
                
                job_key.SetVariable( 'popup_text_1', message )
                self._controller.pub( 'splash_set_status_subtext', message )
                
                time.sleep( 0.01 )
                
                self._CacheTagSiblingsLookupDrop( tag_service_id )
                
                self._CacheTagSiblingsLookupGenerate( tag_service_id )
                
            
            self._CacheTagSiblingsLookupDrop( self._combined_tag_service_id )
            
            self._CacheTagSiblingsLookupGenerate( self._combined_tag_service_id )
            
        finally:
            
            job_key.SetVariable( 'popup_text_1', 'done!' )
            
            job_key.Finish()
            
            job_key.Delete( 5 )
            
        
    
    def _RelocateClientFiles( self, prefix, source, dest ):
        
        full_source = os.path.join( source, prefix )
        full_dest = os.path.join( dest, prefix )
        
        if os.path.exists( full_source ):
            
            HydrusPaths.MergeTree( full_source, full_dest )
            
        elif not os.path.exists( full_dest ):
            
            HydrusPaths.MakeSureDirectoryExists( full_dest )
            
        
        portable_dest = HydrusPaths.ConvertAbsPathToPortablePath( dest )
        
        self._c.execute( 'UPDATE client_files_locations SET location = ? WHERE prefix = ?;', ( portable_dest, prefix ) )
        
        if os.path.exists( full_source ):
            
            try: HydrusPaths.RecyclePath( full_source )
            except: pass
            
        
    
    def _RepairClientFiles( self, correct_rows ):
        
        for ( incorrect_location, prefix, correct_location ) in correct_rows:
            
            portable_incorrect_location = HydrusPaths.ConvertAbsPathToPortablePath( incorrect_location )
            portable_correct_location = HydrusPaths.ConvertAbsPathToPortablePath( correct_location )
            
            full_abs_correct_location = os.path.join( correct_location, prefix )
            
            HydrusPaths.MakeSureDirectoryExists( full_abs_correct_location )
            
            if portable_correct_location != portable_incorrect_location:
                
                self._c.execute( 'UPDATE client_files_locations SET location = ? WHERE location = ? AND prefix = ?;', ( portable_correct_location, portable_incorrect_location, prefix ) )
                
            
        
    
    def _RepairDB( self ):
        
        ( version, ) = self._c.execute( 'SELECT version FROM version;' ).fetchone()
        
        HydrusDB.HydrusDB._RepairDB( self )
        
        self._local_file_service_id = self._GetServiceId( CC.LOCAL_FILE_SERVICE_KEY )
        self._trash_service_id = self._GetServiceId( CC.TRASH_SERVICE_KEY )
        self._local_update_service_id = self._GetServiceId( CC.LOCAL_UPDATE_SERVICE_KEY )
        self._combined_local_file_service_id = self._GetServiceId( CC.COMBINED_LOCAL_FILE_SERVICE_KEY )
        self._combined_file_service_id = self._GetServiceId( CC.COMBINED_FILE_SERVICE_KEY )
        self._combined_tag_service_id = self._GetServiceId( CC.COMBINED_TAG_SERVICE_KEY )
        
        self._subscriptions_cache = {}
        self._service_cache = {}
        
        self._weakref_media_result_cache = ClientMediaResultCache.MediaResultCache()
        self._hash_ids_to_hashes_cache = {}
        self._tag_ids_to_tags_cache = {}
        
        ( self._null_namespace_id, ) = self._c.execute( 'SELECT namespace_id FROM namespaces WHERE namespace = ?;', ( '', ) ).fetchone()
        
        tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
        file_service_ids = self._GetServiceIds( HC.AUTOCOMPLETE_CACHE_SPECIFIC_FILE_SERVICES )
        
        repository_service_ids = self._GetServiceIds( HC.REPOSITORIES )
        
        # master
        
        existing_master_tables = self._STS( self._c.execute( 'SELECT name FROM external_master.sqlite_master WHERE type = ?;', ( 'table', ) ) )
        
        main_master_tables = set()
        
        main_master_tables.add( 'hashes' )
        main_master_tables.add( 'namespaces' )
        main_master_tables.add( 'subtags' )
        main_master_tables.add( 'tags' )
        main_master_tables.add( 'texts' )
        
        if version >= 396:
            
            main_master_tables.add( 'labels' )
            main_master_tables.add( 'notes' )
            
        
        missing_main_tables = main_master_tables.difference( existing_master_tables )
        
        if len( missing_main_tables ) > 0:
            
            message = 'On boot, some required master tables were missing. This could be due to the entire \'master\' database file being missing or due to some other problem. Critical data is missing, so the client cannot boot! The exact missing tables were:'
            message += os.linesep * 2
            message += os.linesep.join( missing_main_tables )
            message += os.linesep * 2
            message += 'The boot will fail once you click ok. If you do not know what happened and how to fix this, please take a screenshot and contact hydrus dev.'
            
            self._controller.SafeShowCriticalMessage( 'Error', message )
            
            raise Exception( 'Master database was invalid!' )
            
        
        if 'local_hashes' not in existing_master_tables:
            
            message = 'On boot, the \'local_hashes\' tables was missing.'
            message += os.linesep * 2
            message += 'If you wish, click ok on this message and the client will recreate it--empty, without data--which should at least let the client boot. The client can repopulate the table in through the file maintenance jobs, the \'regenerate non-standard hashes\' job. But if you want to solve this problem otherwise, kill the hydrus process now.'
            message += os.linesep * 2
            message += 'If you do not already know what caused this, it was likely a hard drive fault--either due to a recent abrupt power cut or actual hardware failure. Check \'help my db is broke.txt\' in the install_dir/db directory as soon as you can.'
            
            BlockingSafeShowMessage( message )
            
            self._c.execute( 'CREATE TABLE external_master.local_hashes ( hash_id INTEGER PRIMARY KEY, md5 BLOB_BYTES, sha1 BLOB_BYTES, sha512 BLOB_BYTES );' )
            self._CreateIndex( 'external_master.local_hashes', [ 'md5' ] )
            self._CreateIndex( 'external_master.local_hashes', [ 'sha1' ] )
            self._CreateIndex( 'external_master.local_hashes', [ 'sha512' ] )
            
        
        if version >= 392:
            
            # tag sibling caches
            
            existing_cache_tables = self._STS( self._c.execute( 'SELECT name FROM external_caches.sqlite_master WHERE type = ?;', ( 'table', ) ) )
            
            tag_sibling_cache_service_ids = list( self._GetServiceIds( HC.REAL_TAG_SERVICES ) )
            
            tag_sibling_cache_service_ids.append( self._combined_tag_service_id )
            
            missing_tag_sibling_cache_tables = []
            
            for tag_service_id in tag_sibling_cache_service_ids:
                
                cache_tag_siblings_lookup_table_name = GenerateTagSiblingsLookupCacheTableName( tag_service_id )
                
                if cache_tag_siblings_lookup_table_name.split( '.' )[1] not in existing_cache_tables:
                    
                    self._CacheTagSiblingsLookupGenerate( tag_service_id )
                    
                    missing_tag_sibling_cache_tables.append( cache_tag_siblings_lookup_table_name )
                    
                
            
            if len( missing_tag_sibling_cache_tables ) > 0:
                
                missing_tag_sibling_cache_tables.sort()
                
                message = 'On boot, some important tag sibling cache tables were missing! This could be due to the entire \'caches\' database file being missing or some other problem. All of this data can be regenerated. The exact missing tables were:'
                message += os.linesep * 2
                message += os.linesep.join( missing_tag_sibling_cache_tables )
                message += os.linesep * 2
                message += 'If you wish, click ok on this message and the client will recreate and repopulate these tables with the correct data. But if you want to solve this problem otherwise, kill the hydrus process now.'
                message += os.linesep * 2
                message += 'If you do not already know what caused this, it was likely a hard drive fault--either due to a recent abrupt power cut or actual hardware failure. Check \'help my db is broke.txt\' in the install_dir/db directory as soon as you can.'
                
                BlockingSafeShowMessage( message )
                
            
        
        # mappings
        
        existing_mapping_tables = self._STS( self._c.execute( 'SELECT name FROM external_mappings.sqlite_master WHERE type = ?;', ( 'table', ) ) )
        
        main_mappings_tables = set()
        
        for service_id in tag_service_ids:
            
            main_mappings_tables.update( ( name.split( '.' )[1] for name in GenerateMappingsTableNames( service_id ) ) )
            
        
        missing_main_tables = sorted( main_mappings_tables.difference( existing_mapping_tables ) )
        
        if len( missing_main_tables ) > 0:
            
            message = 'On boot, some important mappings tables were missing! This could be due to the entire \'mappings\' database file being missing or some other problem. The tags in these tables are lost. The exact missing tables were:'
            message += os.linesep * 2
            message += os.linesep.join( missing_main_tables )
            message += os.linesep * 2
            message += 'If you wish, click ok on this message and the client will recreate these tables--empty, without data--which should at least let the client boot. If the affected tag service(s) are tag repositories, you will want to reset the processing cache so the client can repopulate the tables from your cached update files. But if you want to solve this problem otherwise, kill the hydrus process now.'
            message += os.linesep * 2
            message += 'If you do not already know what caused this, it was likely a hard drive fault--either due to a recent abrupt power cut or actual hardware failure. Check \'help my db is broke.txt\' in the install_dir/db directory as soon as you can.'
            
            BlockingSafeShowMessage( message )
            
            for service_id in tag_service_ids:
                
                self._GenerateMappingsTables( service_id )
                
            
        
        # caches
        
        existing_cache_tables = self._STS( self._c.execute( 'SELECT name FROM external_caches.sqlite_master WHERE type = ?;', ( 'table', ) ) )
        
        main_cache_tables = set()
        
        main_cache_tables.add( 'shape_perceptual_hashes' )
        main_cache_tables.add( 'shape_perceptual_hash_map' )
        main_cache_tables.add( 'shape_vptree' )
        main_cache_tables.add( 'shape_maintenance_branch_regen' )
        main_cache_tables.add( 'shape_search_cache' )
        
        if version >= 396:
            
            main_cache_tables.add( 'subtags_fts4' )
            main_cache_tables.add( 'subtags_searchable_map' )
            
        
        main_cache_tables.add( 'integer_subtags' )
        
        missing_main_tables = sorted( main_cache_tables.difference( existing_cache_tables ) )
        
        if len( missing_main_tables ) > 0:
            
            message = 'On boot, some important caches tables were missing! This could be due to the entire \'caches\' database file being missing or some other problem. Data related to duplicate file search may have been lost. The exact missing tables were:'
            message += os.linesep * 2
            message += os.linesep.join( missing_main_tables )
            message += os.linesep * 2
            message += 'If you wish, click ok on this message and the client will recreate these tables--empty, without data--which should at least let the client boot. But if you want to solve this problem otherwise, kill the hydrus process now.'
            message += os.linesep * 2
            message += 'If you do not already know what caused this, it was likely a hard drive fault--either due to a recent abrupt power cut or actual hardware failure. Check \'help my db is broke.txt\' in the install_dir/db directory as soon as you can.'
            
            BlockingSafeShowMessage( message )
            
            self._CreateDBCaches()
            
        
        mappings_cache_tables = set()
        
        for ( file_service_id, tag_service_id ) in itertools.product( file_service_ids, tag_service_ids ):
            
            mappings_cache_tables.update( ( name.split( '.' )[1] for name in GenerateSpecificMappingsCacheTableNames( file_service_id, tag_service_id ) ) )
            
        
        for tag_service_id in tag_service_ids:
            
            mappings_cache_tables.add( GenerateCombinedFilesMappingsCacheTableName( tag_service_id ).split( '.' )[1] )
            
        
        if version >= 351:
            
            mappings_cache_tables.add( 'local_tags_cache' )
            
        
        missing_main_tables = sorted( mappings_cache_tables.difference( existing_cache_tables ) )
        
        if len( missing_main_tables ) > 0:
            
            message = 'On boot, some mapping caches tables were missing! This could be due to the entire \'caches\' database file being missing or due to some other problem. All of this data can be regenerated. The exact missing tables were:'
            message += os.linesep * 2
            message += os.linesep.join( missing_main_tables )
            message += os.linesep * 2
            message += 'If you wish, click ok on this message and the client will recreate and repopulate these tables with the correct data. This may take a few minutes. But if you want to solve this problem otherwise, kill the hydrus process now.'
            message += os.linesep * 2
            message += 'If you do not already know what caused this, it was likely a hard drive fault--either due to a recent abrupt power cut or actual hardware failure. Check \'help my db is broke.txt\' in the install_dir/db directory as soon as you can.'
            
            BlockingSafeShowMessage( message )
            
            self._RegenerateTagMappingsCache()
            
        
        #
        
        new_options = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_CLIENT_OPTIONS )
        
        if new_options is None:
            
            message = 'On boot, your main options object was missing!'
            message += os.linesep * 2
            message += 'If you wish, click ok on this message and the client will re-add fresh options with default values. But if you want to solve this problem otherwise, kill the hydrus process now.'
            message += os.linesep * 2
            message += 'If you do not already know what caused this, it was likely a hard drive fault--either due to a recent abrupt power cut or actual hardware failure. Check \'help my db is broke.txt\' in the install_dir/db directory as soon as you can.'
            
            BlockingSafeShowMessage( message )
            
            new_options = ClientOptions.ClientOptions()
            
            new_options.SetSimpleDownloaderFormulae( ClientDefaults.GetDefaultSimpleDownloaderFormulae() )
            
            self._SetJSONDump( new_options )
            
        
    
    def _RepopulateAndUpdateTagSearchCache( self, status_hook: typing.Optional[ typing.Callable[ [ str ], None ] ] = None, do_fts = True, do_searchable = True, do_integers = True ):
        
        BLOCK_SIZE = 1000
        
        select_statement = 'SELECT subtag_id FROM subtags;'
        
        for ( i, group_of_subtag_ids ) in enumerate( HydrusDB.ReadLargeIdQueryInSeparateChunks( self._c, select_statement, BLOCK_SIZE ) ):
            
            if status_hook is not None:
                
                message = 'Regenerating tag search cache\u2026 {}'.format( HydrusData.ToHumanInt( i * BLOCK_SIZE ) )
                
                status_hook( message )
                
            
            for subtag_id in group_of_subtag_ids:
                
                ( subtag, ) = self._c.execute( 'SELECT subtag FROM subtags WHERE subtag_id = ?;', ( subtag_id, ) ).fetchone()
                
                subtag_searchable = ClientSearch.ConvertSubtagToSearchable( subtag )
                
                if do_fts:
                    
                    do_it = True
                    
                    result = self._c.execute( 'SELECT subtag FROM subtags_fts4 WHERE docid = ?;', ( subtag_id, ) ).fetchone()
                    
                    if result is not None:
                        
                        ( current_subtag_fts, ) = result
                        
                        if current_subtag_fts == subtag_searchable:
                            
                            do_it = False
                            
                        
                    
                    if do_it:
                        
                        self._c.execute( 'REPLACE INTO subtags_fts4 ( docid, subtag ) VALUES ( ?, ? );', ( subtag_id, subtag_searchable ) )
                        
                    
                
                if do_searchable:
                    
                    if subtag_searchable == subtag:
                        
                        searchable_subtag_id = subtag_id
                        
                    else:
                        
                        searchable_subtag_id = self._GetSubtagId( subtag_searchable )
                        
                    
                    self._c.execute( 'REPLACE INTO subtags_searchable_map ( subtag_id, searchable_subtag_id ) VALUES ( ?, ? );', ( subtag_id, searchable_subtag_id ) )
                    
                
                if do_integers:
                    
                    if subtag.isdecimal():
                        
                        try:
                            
                            integer_subtag = int( subtag )
                            
                            if CanCacheInteger( integer_subtag ):
                                
                                self._c.execute( 'REPLACE INTO integer_subtags ( subtag_id, integer_subtag ) VALUES ( ?, ? );', ( subtag_id, integer_subtag ) )
                                
                            
                        except ValueError:
                            
                            pass
                            
                        
                    
                
            
        
    
    def _ReportOverupdatedDB( self, version ):
        
        message = 'This client\'s database is version {}, but the software is version {}! This situation only sometimes works, and when it does not, it can break things! If you are not sure what is going on, or if you accidentally installed an older version of the software to a newer database, force-kill this client in Task Manager right now. Otherwise, ok this dialog box to continue.'.format( HydrusData.ToHumanInt( version ), HydrusData.ToHumanInt( HC.SOFTWARE_VERSION ) )
        
        BlockingSafeShowMessage( message )
        
    
    def _ReportUnderupdatedDB( self, version ):
        
        message = 'This client\'s database is version {}, but the software is significantly later, {}! Trying to update many versions in one go can be dangerous due to bitrot. I suggest you try at most to only do 10 versions at once. If you want to try a big jump anyway, you should make sure you have a backup beforehand so you can roll back to it in case the update makes your db unbootable. If you would rather try smaller updates, or you do not have a backup, force-kill this client in Task Manager right now. Otherwise, ok this dialog box to continue.'.format( HydrusData.ToHumanInt( version ), HydrusData.ToHumanInt( HC.SOFTWARE_VERSION ) )
        
        BlockingSafeShowMessage( message )
        
    
    def _ReprocessRepository( self, service_key, update_mime_types ):
        
        service_id = self._GetServiceId( service_key )
        
        self._ReprocessRepositoryFromServiceId( service_id, update_mime_types )
        
    
    def _ReprocessRepositoryFromServiceId( self, service_id, update_mime_types ):
        
        repository_updates_table_name = GenerateRepositoryRepositoryUpdatesTableName( service_id )
        
        update_hash_ids = set()
        
        for update_mime_type in update_mime_types:
            
            hash_ids = self._STL( self._c.execute( 'SELECT hash_id FROM {} NATURAL JOIN files_info WHERE mime = ? AND processed = ?;'.format( repository_updates_table_name ), ( update_mime_type, True ) ) )
            
            update_hash_ids.update( hash_ids )
            
        
        self._c.executemany( 'UPDATE {} SET processed = ? WHERE hash_id = ?;'.format( repository_updates_table_name ), ( ( False, hash_id ) for hash_id in update_hash_ids ) )
        
    
    def _ResetRepository( self, service ):
        
        self._Commit()
        
        self._c.execute( 'PRAGMA foreign_keys = ON;' )
        
        self._BeginImmediate()
        
        ( service_key, service_type, name, dictionary ) = service.ToTuple()
        
        service_id = self._GetServiceId( service_key )
        
        prefix = 'resetting ' + name
        
        job_key = ClientThreading.JobKey()
        
        try:
            
            job_key.SetVariable( 'popup_text_1', prefix + ': deleting service' )
            
            self._controller.pub( 'modal_message', job_key )
            
            self._DeleteService( service_id )
            
            job_key.SetVariable( 'popup_text_1', prefix + ': recreating service' )
            
            self._AddService( service_key, service_type, name, dictionary )
            
            self.pub_after_job( 'notify_unknown_accounts' )
            self.pub_after_job( 'notify_new_pending' )
            self.pub_after_job( 'notify_new_services_data' )
            self.pub_after_job( 'notify_new_services_gui' )
            
            job_key.SetVariable( 'popup_text_1', prefix + ': done!' )
            
        finally:
            
            self._CloseDBCursor()
            
            self._InitDBCursor()
            
            job_key.Finish()
            
        
    
    def _SaveDirtyServices( self, dirty_services ):
        
        # if allowed to save objects
        
        self._SaveServices( dirty_services )
        
    
    def _SaveServices( self, services ):
        
        for service in services:
            
            ( service_key, service_type, name, dictionary ) = service.ToTuple()
            
            dictionary_string = dictionary.DumpToString()
            
            self._c.execute( 'UPDATE services SET dictionary_string = ? WHERE service_key = ?;', ( dictionary_string, sqlite3.Binary( service_key ) ) )
            
            service.SetClean()
            
        
    
    def _SaveOptions( self, options ):
        
        try:
            
            self._c.execute( 'UPDATE options SET options = ?;', ( options, ) )
            
        except:
            
            HydrusData.Print( 'Failed options save dump:' )
            HydrusData.Print( options )
            
            raise
            
        
        self.pub_after_job( 'reset_thumbnail_cache' )
        self.pub_after_job( 'notify_new_options' )
        
    
    def _ScheduleRepositoryUpdateFileMaintenance( self, service_id, job_type ):
        
        repository_updates_table_name = GenerateRepositoryRepositoryUpdatesTableName( service_id )
        
        update_hash_ids = self._STL( self._c.execute( 'SELECT hash_id FROM {};'.format( repository_updates_table_name ) ) )
        
        self._FileMaintenanceAddJobs( update_hash_ids, job_type )
        
    
    def _ScheduleRepositoryUpdateFileMaintenanceFromServiceKey( self, service_key, job_type ):
        
        service_id = self._GetServiceId( service_key )
        
        self._ScheduleRepositoryUpdateFileMaintenance( service_id, job_type )
        
    
    def _SetIdealClientFilesLocations( self, locations_to_ideal_weights, ideal_thumbnail_override_location ):
        
        if len( locations_to_ideal_weights ) == 0:
            
            raise Exception( 'No locations passed in ideal locations list!' )
            
        
        self._c.execute( 'DELETE FROM ideal_client_files_locations;' )
        
        for ( abs_location, weight ) in locations_to_ideal_weights.items():
            
            portable_location = HydrusPaths.ConvertAbsPathToPortablePath( abs_location )
            
            self._c.execute( 'INSERT INTO ideal_client_files_locations ( location, weight ) VALUES ( ?, ? );', ( portable_location, weight ) )
            
        
        self._c.execute( 'DELETE FROM ideal_thumbnail_override_location;' )
        
        if ideal_thumbnail_override_location is not None:
            
            portable_ideal_thumbnail_override_location = HydrusPaths.ConvertAbsPathToPortablePath( ideal_thumbnail_override_location )
            
            self._c.execute( 'INSERT INTO ideal_thumbnail_override_location ( location ) VALUES ( ? );', ( portable_ideal_thumbnail_override_location, ) )
            
        
    
    def _SetJSONDump( self, obj ):
        
        if isinstance( obj, HydrusSerialisable.SerialisableBaseNamed ):
            
            ( dump_type, dump_name, version, serialisable_info ) = obj.GetSerialisableTuple()
            
            try:
                
                dump = json.dumps( serialisable_info )
                
            except Exception as e:
                
                HydrusData.ShowException( e )
                HydrusData.Print( obj )
                HydrusData.Print( serialisable_info )
                
                raise Exception( 'Trying to json dump the object ' + str( obj ) + ' with name ' + dump_name + ' caused an error. Its serialisable info has been dumped to the log.' )
                
            
            store_backups = False
            
            if dump_type == HydrusSerialisable.SERIALISABLE_TYPE_GUI_SESSION:
                
                store_backups = True
                backup_depth = HG.client_controller.new_options.GetInteger( 'number_of_gui_session_backups' )
                
            
            object_timestamp = HydrusData.GetNow()
            
            if store_backups:
                
                existing_timestamps = sorted( self._STI( self._c.execute( 'SELECT timestamp FROM json_dumps_named WHERE dump_type = ? AND dump_name = ?;', ( dump_type, dump_name ) ) ) )
                
                if len( existing_timestamps ) > 0:
                    
                    # the user has changed their system clock, so let's make sure the new timestamp is larger at least
                    
                    largest_existing_timestamp = max( existing_timestamps )
                    
                    if largest_existing_timestamp > object_timestamp:
                        
                        object_timestamp = largest_existing_timestamp + 1
                        
                    
                
                deletee_timestamps = existing_timestamps[ : - backup_depth ] # keep highest n values
                
                deletee_timestamps.append( object_timestamp ) # if save gets spammed twice in one second, we'll overwrite
                
                self._c.executemany( 'DELETE FROM json_dumps_named WHERE dump_type = ? AND dump_name = ? AND timestamp = ?;', [ ( dump_type, dump_name, timestamp ) for timestamp in deletee_timestamps ] )
                
            else:
                
                self._c.execute( 'DELETE FROM json_dumps_named WHERE dump_type = ? AND dump_name = ?;', ( dump_type, dump_name ) )
                
            
            dump_buffer = sqlite3.Binary( bytes( dump, 'utf-8' ) )
            
            try:
                
                self._c.execute( 'INSERT INTO json_dumps_named ( dump_type, dump_name, version, timestamp, dump ) VALUES ( ?, ?, ?, ?, ? );', ( dump_type, dump_name, version, object_timestamp, dump_buffer ) )
                
            except:
                
                HydrusData.DebugPrint( dump )
                HydrusData.ShowText( 'Had a problem saving a JSON object. The dump has been printed to the log.' )
                
                raise
                
            
        else:
            
            ( dump_type, version, serialisable_info ) = obj.GetSerialisableTuple()
            
            try:
                
                dump = json.dumps( serialisable_info )
                
            except Exception as e:
                
                HydrusData.ShowException( e )
                HydrusData.Print( obj )
                HydrusData.Print( serialisable_info )
                
                raise Exception( 'Trying to json dump the object ' + str( obj ) + ' caused an error. Its serialisable info has been dumped to the log.' )
                
            
            self._c.execute( 'DELETE FROM json_dumps WHERE dump_type = ?;', ( dump_type, ) )
            
            dump_buffer = sqlite3.Binary( bytes( dump, 'utf-8' ) )
            
            try:
                
                self._c.execute( 'INSERT INTO json_dumps ( dump_type, version, dump ) VALUES ( ?, ?, ? );', ( dump_type, version, dump_buffer ) )
                
            except:
                
                HydrusData.DebugPrint( dump )
                HydrusData.ShowText( 'Had a problem saving a JSON object. The dump has been printed to the log.' )
                
                raise
                
            
        
    
    def _SetJSONSimple( self, name, value ):
        
        if value is None:
            
            self._c.execute( 'DELETE FROM json_dict WHERE name = ?;', ( name, ) )
            
        else:
            
            dump = json.dumps( value )
            
            dump_buffer = sqlite3.Binary( bytes( dump, 'utf-8' ) )
            
            try:
                
                self._c.execute( 'REPLACE INTO json_dict ( name, dump ) VALUES ( ?, ? );', ( name, dump_buffer ) )
                
            except:
                
                HydrusData.DebugPrint( dump )
                HydrusData.ShowText( 'Had a problem saving a JSON object. The dump has been printed to the log.' )
                
                raise
                
            
        
    
    def _SetLastShutdownWorkTime( self, timestamp ):
        
        self._c.execute( 'DELETE from last_shutdown_work_time;' )
        
        self._c.execute( 'INSERT INTO last_shutdown_work_time ( last_shutdown_work_time ) VALUES ( ? );', ( timestamp, ) )
        
    
    def _SetLocalFileDeletionReason( self, hash_ids, reason ):
        
        if reason is not None:
            
            reason_id = self._GetTextId( reason )
            
            self._c.executemany( 'REPLACE INTO local_file_deletion_reasons ( hash_id, reason_id ) VALUES ( ?, ? );', ( ( hash_id, reason_id ) for hash_id in hash_ids ) )
            
        
    
    def _SetPassword( self, password ):
        
        if password is not None:
            
            password_bytes = bytes( password, 'utf-8' )
            
            password = hashlib.sha256( password_bytes ).digest()
            
        
        self._controller.options[ 'password' ] = password
        
        self._SaveOptions( self._controller.options )
        
    
    def _SetServiceFilename( self, service_id, hash_id, filename ):
        
        self._c.execute( 'REPLACE INTO service_filenames ( service_id, hash_id, filename ) VALUES ( ?, ?, ? );', ( service_id, hash_id, filename ) )
        
    
    def _SetServiceDirectory( self, service_id, hash_ids, dirname, note ):
        
        directory_id = self._GetTextId( dirname )
        
        self._c.execute( 'DELETE FROM service_directories WHERE service_id = ? AND directory_id = ?;', ( service_id, directory_id ) )
        self._c.execute( 'DELETE FROM service_directory_file_map WHERE service_id = ? AND directory_id = ?;', ( service_id, directory_id ) )
        
        num_files = len( hash_ids )
        
        result = self._c.execute( 'SELECT SUM( size ) FROM files_info WHERE hash_id IN ' + HydrusData.SplayListForDB( hash_ids ) + ';' ).fetchone()
        
        if result is None:
            
            total_size = 0
            
        else:
            
            ( total_size, ) = result
            
        
        self._c.execute( 'INSERT INTO service_directories ( service_id, directory_id, num_files, total_size, note ) VALUES ( ?, ?, ?, ?, ? );', ( service_id, directory_id, num_files, total_size, note ) )
        self._c.executemany( 'INSERT INTO service_directory_file_map ( service_id, directory_id, hash_id ) VALUES ( ?, ?, ? );', ( ( service_id, directory_id, hash_id ) for hash_id in hash_ids ) )
        
    
    def _SetYAMLDump( self, dump_type, dump_name, data ):
        
        if dump_type == YAML_DUMP_ID_LOCAL_BOORU:
            
            dump_name = dump_name.hex()
            
        
        self._c.execute( 'DELETE FROM yaml_dumps WHERE dump_type = ? AND dump_name = ?;', ( dump_type, dump_name ) )
        
        try: self._c.execute( 'INSERT INTO yaml_dumps ( dump_type, dump_name, dump ) VALUES ( ?, ?, ? );', ( dump_type, dump_name, data ) )
        except:
            
            HydrusData.Print( ( dump_type, dump_name, data ) )
            
            raise
            
        
        if dump_type == YAML_DUMP_ID_LOCAL_BOORU:
            
            service_id = self._GetServiceId( CC.LOCAL_BOORU_SERVICE_KEY )
            
            self._c.execute( 'DELETE FROM service_info WHERE service_id = ? AND info_type = ?;', ( service_id, HC.SERVICE_INFO_NUM_SHARES ) )
            
            self._controller.pub( 'refresh_local_booru_shares' )
            
        
    
    def _SubtagExists( self, subtag ):
        
        try:
            
            HydrusTags.CheckTagNotEmpty( subtag )
            
        except HydrusExceptions.TagSizeException:
            
            return False
            
        
        result = self._c.execute( 'SELECT 1 FROM subtags WHERE subtag = ?;', ( subtag, ) ).fetchone()
        
        if result is None:
            
            return False
            
        else:
            
            return True
            
        
    
    def _TagExists( self, tag ):
        
        tag = HydrusTags.CleanTag( tag )
        
        try:
            
            HydrusTags.CheckTagNotEmpty( tag )
            
        except HydrusExceptions.TagSizeException:
            
            return False
            
        
        ( namespace, subtag ) = HydrusTags.SplitTag( tag )
        
        if self._NamespaceExists( namespace ):
            
            namespace_id = self._GetNamespaceId( namespace )
            
        else:
            
            return False
            
        
        if self._SubtagExists( subtag ):
            
            subtag_id = self._GetSubtagId( subtag )
            
            result = self._c.execute( 'SELECT 1 FROM tags WHERE namespace_id = ? AND subtag_id = ?;', ( namespace_id, subtag_id ) ).fetchone()
            
            if result is None:
                
                return False
                
            else:
                
                return True
                
            
        else:
            
            return False
            
        
    
    def _TryToSortHashIds( self, file_service_id, hash_ids, sort_by ):
        
        did_sort = False
        
        ( sort_metadata, sort_data ) = sort_by.sort_type
        sort_asc = sort_by.sort_asc
        
        query = None
        select_args_iterator = None
        
        if sort_metadata == 'system':
            
            simple_sorts = []
            
            simple_sorts.append( CC.SORT_FILES_BY_IMPORT_TIME )
            simple_sorts.append( CC.SORT_FILES_BY_FILESIZE )
            simple_sorts.append( CC.SORT_FILES_BY_DURATION )
            simple_sorts.append( CC.SORT_FILES_BY_FRAMERATE )
            simple_sorts.append( CC.SORT_FILES_BY_NUM_FRAMES )
            simple_sorts.append( CC.SORT_FILES_BY_WIDTH )
            simple_sorts.append( CC.SORT_FILES_BY_HEIGHT )
            simple_sorts.append( CC.SORT_FILES_BY_RATIO )
            simple_sorts.append( CC.SORT_FILES_BY_NUM_PIXELS )
            simple_sorts.append( CC.SORT_FILES_BY_MEDIA_VIEWS )
            simple_sorts.append( CC.SORT_FILES_BY_MEDIA_VIEWTIME )
            simple_sorts.append( CC.SORT_FILES_BY_APPROX_BITRATE )
            simple_sorts.append( CC.SORT_FILES_BY_FILE_MODIFIED_TIMESTAMP )
            
            if sort_data in simple_sorts:
                
                if sort_data == CC.SORT_FILES_BY_IMPORT_TIME:
                    
                    query = 'SELECT hash_id, timestamp FROM files_info NATURAL JOIN current_files WHERE hash_id = ? AND service_id = ?;'
                    
                    select_args_iterator = ( ( hash_id, file_service_id ) for hash_id in hash_ids )
                    
                else:
                    
                    if sort_data == CC.SORT_FILES_BY_FILESIZE:
                        
                        query = 'SELECT hash_id, size FROM files_info WHERE hash_id = ?;'
                        
                    elif sort_data == CC.SORT_FILES_BY_DURATION:
                        
                        query = 'SELECT hash_id, duration FROM files_info WHERE hash_id = ?;'
                        
                    elif sort_data == CC.SORT_FILES_BY_FRAMERATE:
                        
                        query = 'SELECT hash_id, num_frames, duration FROM files_info WHERE hash_id = ?;'
                        
                    elif sort_data == CC.SORT_FILES_BY_NUM_FRAMES:
                        
                        query = 'SELECT hash_id, num_frames FROM files_info WHERE hash_id = ?;'
                        
                    elif sort_data == CC.SORT_FILES_BY_WIDTH:
                        
                        query = 'SELECT hash_id, width FROM files_info WHERE hash_id = ?;'
                        
                    elif sort_data == CC.SORT_FILES_BY_HEIGHT:
                        
                        query = 'SELECT hash_id, height FROM files_info WHERE hash_id = ?;'
                        
                    elif sort_data == CC.SORT_FILES_BY_RATIO:
                        
                        query = 'SELECT hash_id, width, height FROM files_info WHERE hash_id = ?;'
                        
                    elif sort_data == CC.SORT_FILES_BY_NUM_PIXELS:
                        
                        query = 'SELECT hash_id, width, height FROM files_info WHERE hash_id = ?;'
                        
                    elif sort_data == CC.SORT_FILES_BY_MEDIA_VIEWS:
                        
                        query = 'SELECT hash_id, media_views FROM file_viewing_stats WHERE hash_id = ?;'
                        
                    elif sort_data == CC.SORT_FILES_BY_MEDIA_VIEWTIME:
                        
                        query = 'SELECT hash_id, media_viewtime FROM file_viewing_stats WHERE hash_id = ?;'
                        
                    elif sort_data == CC.SORT_FILES_BY_APPROX_BITRATE:
                        
                        query = 'SELECT hash_id, duration, num_frames, size, width, height FROM files_info WHERE hash_id = ?;'
                        
                    elif sort_data == CC.SORT_FILES_BY_FILE_MODIFIED_TIMESTAMP:
                        
                        query = 'SELECT hash_id, file_modified_timestamp FROM file_modified_timestamps WHERE hash_id = ?;'
                        
                    
                    select_args_iterator = ( ( hash_id, ) for hash_id in hash_ids )
                    
                
                if sort_data == CC.SORT_FILES_BY_RATIO:
                    
                    def key( row ):
                        
                        width = row[1]
                        height = row[2]
                        
                        if width is None or height is None:
                            
                            return -1
                            
                        else:
                            
                            return width / height
                            
                        
                    
                elif sort_data == CC.SORT_FILES_BY_FRAMERATE:
                    
                    def key( row ):
                        
                        num_frames = row[1]
                        duration = row[2]
                        
                        if num_frames is None or duration is None or num_frames == 0 or duration == 0:
                            
                            return -1
                            
                        else:
                            
                            return num_frames / duration
                            
                        
                    
                elif sort_data == CC.SORT_FILES_BY_NUM_PIXELS:
                    
                    def key( row ):
                        
                        width = row[1]
                        height = row[2]
                        
                        if width is None or height is None or width == 0 or height == 0:
                            
                            return -1
                            
                        else:
                            
                            return width * height
                            
                        
                    
                elif sort_data == CC.SORT_FILES_BY_APPROX_BITRATE:
                    
                    def key( row ):
                        
                        duration = row[1]
                        num_frames = row[2]
                        size = row[3]
                        width = row[4]
                        height = row[5]
                        
                        if duration is None or duration == 0:
                            
                            if size is None or size == 0:
                                
                                duration_bitrate = -1
                                frame_bitrate = -1
                                
                            else:
                                
                                duration_bitrate = 0
                                
                                if width is None or height is None:
                                    
                                    frame_bitrate = 0
                                    
                                else:
                                    
                                    num_pixels = width * height
                                    
                                    if size is None or size == 0 or num_pixels == 0:
                                        
                                        frame_bitrate = -1
                                        
                                    else:
                                        
                                        frame_bitrate = size / num_pixels
                                        
                                    
                                
                            
                        else:
                            
                            if size is None or size == 0:
                                
                                duration_bitrate = -1
                                frame_bitrate = -1
                                
                            else:
                                
                                duration_bitrate = size / duration
                                
                                if num_frames is None or num_frames == 0:
                                    
                                    frame_bitrate = 0
                                    
                                else:
                                    
                                    frame_bitrate = duration_bitrate / num_frames
                                    
                                
                            
                        
                        return ( duration_bitrate, frame_bitrate )
                        
                    
                else:
                    
                    key = lambda row: -1 if row[1] is None else row[1]
                    
                
                reverse = sort_asc == CC.SORT_DESC
                
            
        
        if query is not None:
            
            hash_ids_and_other_data = list( self._ExecuteManySelect( query, select_args_iterator ) )
            
            hash_ids_and_other_data.sort( key = key, reverse = reverse )
            
            original_hash_ids = set( hash_ids )
            
            hash_ids = [ row[0] for row in hash_ids_and_other_data ]
            
            # some stuff like media views won't have rows
            missing_hash_ids = original_hash_ids.difference( hash_ids )
            
            hash_ids.extend( missing_hash_ids )
            
            did_sort = True
            
        
        return ( did_sort, hash_ids )
        
    
    def _UpdateDB( self, version ):
        
        self._controller.pub( 'splash_set_status_text', 'updating db to v' + str( version + 1 ) )
        
        if version == 341:
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ 'gelbooru 0.2.5 file page parser' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some url classes and parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 344:
            
            message = 'The client now only uses one thumbnail per file (previously it needed two). Your \'resized\' thumbnails will now be deleted. This is a significant step that could take some time to complete. It will also significantly impact your next backup run.'
            message += os.linesep * 2
            message += 'In order to keep your recycle bin sane, the thumbnails will be permanently deleted. Therefore, this operation cannot be undone. If you are not ready to do this yet (for instance if you do not have a recent backup), kill the hydrus process in Task Manager now.'
            message += os.linesep * 2
            message += 'BTW: If you previously put your resized thumbnails on an SSD but not your \'full-size\' ones, you should check the \'migrate database\' dialog once the client boots so you can move the remaining thumbnail directories to fast storage.'
            
            BlockingSafeShowMessage( message )
            
            new_options = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_CLIENT_OPTIONS )
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS ideal_client_files_locations ( location TEXT, weight INTEGER );' )
            self._c.execute( 'CREATE TABLE IF NOT EXISTS ideal_thumbnail_override_location ( location TEXT );' )
            
            for ( location, weight ) in new_options._dictionary[ 'client_files_locations_ideal_weights' ]:
                
                self._c.execute( 'INSERT INTO ideal_client_files_locations ( location, weight ) VALUES ( ?, ? );', ( location, weight ) )
                
            
            thumbnail_override_location = new_options._dictionary[ 'client_files_locations_full_size_thumbnail_override' ]
            
            if thumbnail_override_location is not None:
                
                self._c.execute( 'INSERT INTO ideal_thumbnail_override_location ( location ) VALUES ( ? );', ( thumbnail_override_location, ) )
                
            
            self._SetJSONDump( new_options )
            
            #
            
            error_occurred = False
            
            for ( i, prefix ) in enumerate( HydrusData.IterateHexPrefixes() ):
                
                self._controller.pub( 'splash_set_status_subtext', 'deleting resized thumbnails {}'.format( HydrusData.ConvertValueRangeToPrettyString( i + 1, 256 ) ) )
                
                resized_prefix = 'r' + prefix
                
                try:
                    
                    ( location, ) = self._c.execute( 'SELECT location FROM client_files_locations WHERE prefix = ?;', ( resized_prefix, ) ).fetchone()
                    
                except:
                    
                    continue
                    
                
                full_path = os.path.join( HydrusPaths.ConvertPortablePathToAbsPath( location ), resized_prefix )
                
                if os.path.exists( full_path ):
                    
                    try:
                        
                        HydrusPaths.DeletePath( full_path )
                        
                    except Exception as e:
                        
                        HydrusData.PrintException( e )
                        
                        if not error_occurred:
                            
                            error_occurred = True
                            
                            message = 'There was a problem deleting one or more of your old \'rxx\' resized thumbnail directories, perhaps because of some old read-only files. There is no big harm here, since the old directories are no longer needed, but you will want to delete them yourself. Additional error information has been written to the log. Please contact hydrus dev if you need help.'
                            
                            self.pub_initial_message( message )
                            
                        
                    
                
                self._c.execute( 'DELETE FROM client_files_locations WHERE prefix = ?;', ( resized_prefix, ) )
                
            
        
        if version == 345:
            
            # I screwed up the permissions setting on 344 update so that certain non-windows users got de-execution-permissioned rxx folders, which then made them non-traversable and -deletable
            # so, let's give it another spin, albeit with less information since we have to guess potential location from remaining locations
            
            if not HC.PLATFORM_WINDOWS:
                
                locations_where_r_folders_were_found = set()
                
                locations = self._STL( self._c.execute( 'SELECT DISTINCT location FROM client_files_locations;' ) )
                
                possible_resized_paths = []
                
                error_occurred = False
                
                for prefix in HydrusData.IterateHexPrefixes():
                    
                    resized_prefix = 'r' + prefix
                    
                    for location in locations:
                        
                        full_path = os.path.join( HydrusPaths.ConvertPortablePathToAbsPath( location ), resized_prefix )
                        
                        if os.path.exists( full_path ):
                            
                            possible_resized_paths.append( full_path )
                            
                            locations_where_r_folders_were_found.add( location )
                            
                        
                    
                
                num_possible_resized_paths = len( possible_resized_paths )
                
                if num_possible_resized_paths > 0:
                    
                    message = 'It appears that the update code from last week\'s release, 345, did not successfully delete all your old (and now unneeded) resized thumbnail directories.'
                    message += os.linesep * 2
                    message += 'I have found {} spare \'rxx\' directories (this number should be less than or equal to 256) in these current locations:'.format( num_possible_resized_paths )
                    message += os.linesep * 2
                    message += os.linesep.join( [ HydrusPaths.ConvertPortablePathToAbsPath( location ) for location in locations_where_r_folders_were_found ] )
                    message += os.linesep * 2
                    message += 'I will now attempt to delete these directories again, this time with fixed permissions. If you are not ready to do this, kill the hydrus process now.'
                    
                    BlockingSafeShowMessage( message )
                    
                    for ( i, full_path ) in enumerate( possible_resized_paths ):
                        
                        self._controller.pub( 'splash_set_status_subtext', 'deleting resized thumbnails 2: electric boogaloo {}'.format( HydrusData.ConvertValueRangeToPrettyString( i + 1, num_possible_resized_paths ) ) )
                        
                        try:
                            
                            stat_result = os.stat( full_path )
                            
                            current_bits = stat_result.st_mode
                            
                            if not stat.S_IXUSR & current_bits:
                                
                                os.chmod( full_path, current_bits | stat.S_IXUSR )
                                
                            
                            HydrusPaths.DeletePath( full_path )
                            
                        except Exception as e:
                            
                            HydrusData.PrintException( e )
                            
                            if not error_occurred:
                                
                                error_occurred = True
                                
                                message = 'The second attempt to delete old resized directories also failed. Error information has been written to the log. Please consult hydrus dev if you cannot figure this out on your own.'
                                
                                self.pub_initial_message( message )
                                
                            
                        
                    
                
            
        
        if version == 346:
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS local_file_deletion_reasons ( hash_id INTEGER PRIMARY KEY, reason_id INTEGER );' )
            
        
        if version == 347:
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultURLClasses( [ 'yiff.party file attachment long' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some url classes and parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 349:
            
            try:
                
                new_options = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_CLIENT_OPTIONS )
                
                default_gug = new_options.GetString( 'default_gug_name' )
                
                if default_gug == 'artstation artist lookup':
                    
                    new_options.SetKey( 'default_gug_key', b'00' )
                    new_options.SetString( 'default_gug_name', 'safebooru tag search' )
                    
                    self._SetJSONDump( new_options )
                    
                
            except Exception as e:
                
                pass # nbd
                
            
        
        if version == 350:
            
            self._controller.pub( 'splash_set_status_subtext', 'generating new local tag cache' )
            
            try:
                
                self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.local_tags_cache ( tag_id INTEGER PRIMARY KEY, tag TEXT UNIQUE );' )
                
                combined_local_file_service_id = self._GetServiceId( CC.COMBINED_LOCAL_FILE_SERVICE_KEY )
                
                tag_ids = set()
                
                tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
                
                for tag_service_id in tag_service_ids:
                    
                    ( cache_files_table_name, cache_current_mappings_table_name, cache_deleted_mappings_table_name, cache_pending_mappings_table_name, ac_cache_table_name ) = GenerateSpecificMappingsCacheTableNames( combined_local_file_service_id, tag_service_id )
                    
                    service_tag_ids = self._STL( self._c.execute( 'SELECT tag_id FROM ' + ac_cache_table_name + ' WHERE current_count > 0;' ) )
                    
                    tag_ids.update( service_tag_ids )
                    
                
                num_to_do = len( tag_ids )
                
                i = 0
                
                self._tag_ids_to_tags_cache = {}
                
                for block_of_tag_ids in HydrusData.SplitListIntoChunks( tag_ids, 1000 ):
                    
                    self._controller.pub( 'splash_set_status_subtext', 'generating new local tag cache: {}'.format( HydrusData.ConvertValueRangeToPrettyString( i, num_to_do ) ) )
                    
                    self._PopulateTagIdsToTagsCache( block_of_tag_ids )
                    
                    self._c.executemany( 'INSERT OR IGNORE INTO local_tags_cache ( tag_id, tag ) VALUES ( ?, ? );', ( ( tag_id, self._tag_ids_to_tags_cache[ tag_id ] ) for tag_id in block_of_tag_ids ) )
                    
                    i += 1000
                    
                
            except:
                
                self._controller.SafeShowCriticalMessage( 'problem updating!', 'When trying to update, I could not create a new local tag cache! Error information will follow. Please let hydrus dev know!' )
                
                raise
                
            
        
        if version == 352:
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.file_maintenance_jobs ( hash_id INTEGER, job_type INTEGER, time_can_start INTEGER, PRIMARY KEY ( hash_id, job_type ) );' )
            
        
        if version == 353:
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS duplicate_files ( media_id INTEGER PRIMARY KEY, king_hash_id INTEGER UNIQUE );' )
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS duplicate_file_members ( media_id INTEGER, hash_id INTEGER UNIQUE, PRIMARY KEY ( media_id, hash_id ) );' )
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS duplicate_false_positives ( smaller_alternates_group_id INTEGER, larger_alternates_group_id INTEGER, PRIMARY KEY ( smaller_alternates_group_id, larger_alternates_group_id ) );' )
            self._CreateIndex( 'duplicate_false_positives', [ 'larger_alternates_group_id', 'smaller_alternates_group_id' ], unique = True )
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS alternate_file_groups ( alternates_group_id INTEGER PRIMARY KEY );' )
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS alternate_file_group_members ( alternates_group_id INTEGER, media_id INTEGER UNIQUE, PRIMARY KEY ( alternates_group_id, media_id ) );' )
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS potential_duplicate_pairs ( smaller_media_id INTEGER, larger_media_id INTEGER, distance INTEGER, PRIMARY KEY ( smaller_media_id, larger_media_id ) );' )
            self._CreateIndex( 'potential_duplicate_pairs', [ 'larger_media_id', 'smaller_media_id' ], unique = True )
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS confirmed_alternate_pairs ( smaller_media_id INTEGER, larger_media_id INTEGER, PRIMARY KEY ( smaller_media_id, larger_media_id ) );' )
            self._CreateIndex( 'confirmed_alternate_pairs', [ 'larger_media_id', 'smaller_media_id' ], unique = True )
            
            # now do it
            
            alternate_pairs = self._c.execute( 'SELECT smaller_hash_id, larger_hash_id FROM duplicate_pairs WHERE duplicate_type = ?;', ( HC.DUPLICATE_ALTERNATE, ) ).fetchall()
            
            for ( hash_id_a, hash_id_b ) in alternate_pairs:
                
                media_id_a = self._DuplicatesGetMediaId( hash_id_a )
                media_id_b = self._DuplicatesGetMediaId( hash_id_b )
                
                self._DuplicatesSetAlternates( media_id_a, media_id_b )
                
            
            self._c.execute( 'DELETE FROM duplicate_pairs WHERE duplicate_type = ?;', ( HC.DUPLICATE_ALTERNATE, ) )
            
            false_positive_pairs = self._c.execute( 'SELECT smaller_hash_id, larger_hash_id FROM duplicate_pairs WHERE duplicate_type = ?;', ( HC.DUPLICATE_FALSE_POSITIVE, ) ).fetchall()
            
            for ( hash_id_a, hash_id_b ) in false_positive_pairs:
                
                media_id_a = self._DuplicatesGetMediaId( hash_id_a )
                media_id_b = self._DuplicatesGetMediaId( hash_id_b )
                
                alternates_group_id_a = self._DuplicatesGetAlternatesGroupId( media_id_a )
                alternates_group_id_b = self._DuplicatesGetAlternatesGroupId( media_id_b )
                
                self._DuplicatesSetFalsePositive( alternates_group_id_a, alternates_group_id_b )
                
            
            self._c.execute( 'DELETE FROM duplicate_pairs WHERE duplicate_type = ?;', ( HC.DUPLICATE_FALSE_POSITIVE, ) )
            
        
        if version == 355:
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS potential_duplicate_pairs ( smaller_media_id INTEGER, larger_media_id INTEGER, distance INTEGER, PRIMARY KEY ( smaller_media_id, larger_media_id ) );' )
            self._CreateIndex( 'potential_duplicate_pairs', [ 'larger_media_id', 'smaller_media_id' ], unique = True )
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS confirmed_alternate_pairs ( smaller_media_id INTEGER, larger_media_id INTEGER, PRIMARY KEY ( smaller_media_id, larger_media_id ) );' )
            self._CreateIndex( 'confirmed_alternate_pairs', [ 'larger_media_id', 'smaller_media_id' ], unique = True )
            
            better_worse_pairs = []
            
            better_worse_pairs.extend( self._c.execute( 'SELECT smaller_hash_id, larger_hash_id FROM duplicate_pairs WHERE duplicate_type = ?;', ( HC.DUPLICATE_SMALLER_BETTER, ) ) )
            better_worse_pairs.extend( self._c.execute( 'SELECT larger_hash_id, smaller_hash_id FROM duplicate_pairs WHERE duplicate_type = ?;', ( HC.DUPLICATE_LARGER_BETTER, ) ) )
            
            same_pairs = self._c.execute( 'SELECT smaller_hash_id, larger_hash_id FROM duplicate_pairs WHERE duplicate_type = ?;', ( HC.DUPLICATE_SAME_QUALITY, ) ).fetchall()
            
            # do better/worse before same quality, because there are some scenarios where existing data that is incomplete will let a same quality overrule valid better/worse data on reconstruction
            
            for ( hash_id_better, hash_id_worse ) in better_worse_pairs:
                
                superior_media_id = self._DuplicatesGetMediaId( hash_id_better )
                mergee_media_id = self._DuplicatesGetMediaId( hash_id_worse )
                
                self._DuplicatesMergeMedias( superior_media_id, mergee_media_id )
                
            
            for ( hash_id_a, hash_id_b ) in same_pairs:
                
                superior_media_id = self._DuplicatesGetMediaId( hash_id_a )
                mergee_media_id = self._DuplicatesGetMediaId( hash_id_b )
                
                self._DuplicatesMergeMedias( superior_media_id, mergee_media_id )
                
            
            self._c.execute( 'DELETE FROM duplicate_pairs WHERE duplicate_type IN ( ?, ?, ? );', ( HC.DUPLICATE_SMALLER_BETTER, HC.DUPLICATE_LARGER_BETTER, HC.DUPLICATE_SAME_QUALITY ) )
            
        
        if version == 356:
            
            try:
                
                new_options = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_CLIENT_OPTIONS )
                
                new_options.SetInteger( 'duplicate_comparison_score_higher_jpeg_quality', 10 )
                new_options.SetInteger( 'duplicate_comparison_score_much_higher_jpeg_quality', 20 )
                new_options.SetInteger( 'duplicate_comparison_score_higher_filesize', 10 )
                new_options.SetInteger( 'duplicate_comparison_score_much_higher_filesize', 20 )
                new_options.SetInteger( 'duplicate_comparison_score_higher_resolution', 20 )
                new_options.SetInteger( 'duplicate_comparison_score_much_higher_resolution', 50 )
                new_options.SetInteger( 'duplicate_comparison_score_more_tags', 8 )
                new_options.SetInteger( 'duplicate_comparison_score_older', 4 )
                
                self._SetJSONDump( new_options )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to set new simple downloader parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 357:
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS potential_duplicate_pairs ( smaller_media_id INTEGER, larger_media_id INTEGER, distance INTEGER, PRIMARY KEY ( smaller_media_id, larger_media_id ) );' )
            self._CreateIndex( 'potential_duplicate_pairs', [ 'larger_media_id', 'smaller_media_id' ], unique = True )
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS confirmed_alternate_pairs ( smaller_media_id INTEGER, larger_media_id INTEGER, PRIMARY KEY ( smaller_media_id, larger_media_id ) );' )
            self._CreateIndex( 'confirmed_alternate_pairs', [ 'larger_media_id', 'smaller_media_id' ], unique = True )
            
            result = self._c.execute( 'SELECT 1 FROM external_caches.sqlite_master WHERE name = ?;', ( 'duplicate_pairs', ) ).fetchone()
            
            if result is not None:
                
                potential_pairs = self._c.execute( 'SELECT smaller_hash_id, larger_hash_id FROM duplicate_pairs WHERE duplicate_type = ?;', ( HC.DUPLICATE_POTENTIAL, ) ).fetchall()
                
                self._controller.pub( 'splash_set_status_subtext', 'updating potential duplicate storage' )
                
                smaller_hash_ids_to_larger_hash_ids = HydrusData.BuildKeyToListDict( potential_pairs )
                
                for ( smaller_hash_id, larger_hash_ids ) in smaller_hash_ids_to_larger_hash_ids.items():
                    
                    # we can't figure out searched distance quickly, so let's fudge an approx solution
                    
                    result = self._c.execute( 'SELECT searched_distance FROM shape_search_cache WHERE hash_id = ?;', ( smaller_hash_id, ) ).fetchone()
                    
                    if result is None:
                        
                        searched_distance = 0
                        
                    else:
                        
                        ( searched_distance, ) = result
                        
                        if searched_distance is None:
                            
                            searched_distance = 0
                            
                        
                    
                    media_id_a = self._DuplicatesGetMediaId( smaller_hash_id )
                    
                    potential_duplicate_media_ids_and_distances = [ ( self._DuplicatesGetMediaId( larger_hash_id ), searched_distance ) for larger_hash_id in larger_hash_ids ]
                    
                    self._DuplicatesAddPotentialDuplicates( media_id_a, potential_duplicate_media_ids_and_distances )
                    
                
                self._c.execute( 'DROP TABLE duplicate_pairs;' )
                
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultParsers( ( 'pixiv file page api parser', ) )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 358:
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultParsers( ( 'shimmie file page parser', 'deviant gallery page api parser', 'deviant art file page parser' ) )
                
                domain_manager.OverwriteDefaultGUGs( ( 'deviant art tag search', 'deviant art artist lookup' ) )
                
                domain_manager.OverwriteDefaultURLClasses( ( 'deviant art artist gallery page api', 'deviant art tag gallery page api' ) )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
                #
                
                login_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_LOGIN_MANAGER )
                
                login_manager.Initialise()
                
                #
                
                
                login_manager.OverwriteDefaultLoginScripts( ( 'deviant art login', ) )
                
                login_scripts = login_manager.GetLoginScripts()
                
                login_scripts = [ login_script for login_script in login_scripts if login_script.GetName() != 'deviant art login (only works on a client that has already done some downloading)' ]
                
                login_manager.SetLoginScripts( login_scripts )
                
                login_manager.TryToLinkMissingLoginScripts( ( 'www.deviantart.com', ) )
                
                #
                
                self._SetJSONDump( login_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 359:
            
            self._c.execute( 'ANALYZE duplicate_files;' )
            self._c.execute( 'ANALYZE duplicate_file_members;' )
            self._c.execute( 'ANALYZE duplicate_false_positives;' )
            self._c.execute( 'ANALYZE alternate_file_groups;' )
            self._c.execute( 'ANALYZE alternate_file_group_members;' )
            self._c.execute( 'ANALYZE potential_duplicate_pairs;' )
            self._c.execute( 'ANALYZE confirmed_alternate_pairs;' )
            
            #
            
            result = self._c.execute( 'SELECT 1 FROM external_caches.sqlite_master WHERE name = ?;', ( 'shape_maintenance_phash_regen', ) ).fetchone()
            
            if result is not None:
                
                try:
                    
                    self._c.execute( 'INSERT OR IGNORE INTO file_maintenance_jobs ( hash_id, job_type, time_can_start ) SELECT hash_id, ?, ? FROM shape_maintenance_phash_regen;', ( ClientFiles.REGENERATE_FILE_DATA_JOB_SIMILAR_FILES_METADATA, 0 ) )
                    
                    self._c.execute( 'DROP TABLE shape_maintenance_phash_regen;' )
                    
                except Exception as e:
                    
                    HydrusData.PrintException( e )
                    
                    message = 'Trying to migrate similar files maintenance schedule failed! Please let hydrus dev know!'
                    
                    self.pub_initial_message( message )
                    
                
            
            self._c.execute( 'ANALYZE file_maintenance_jobs;' )
            
        
        if version == 361:
            
            service_id = self._GetServiceId( CC.COMBINED_LOCAL_FILE_SERVICE_KEY )
            
            self._c.execute( 'DELETE FROM file_transfers WHERE service_id = ?;', ( service_id, ) )
            
            service_id = self._GetServiceId( CC.LOCAL_FILE_SERVICE_KEY )
            
            self._c.execute( 'DELETE FROM file_transfers WHERE service_id = ?;', ( service_id, ) )
            
        
        if version == 362:
            
            # complete job no longer does thumbs
            
            self._c.execute( 'INSERT OR IGNORE INTO file_maintenance_jobs ( hash_id, job_type, time_can_start ) SELECT hash_id, ?, time_can_start FROM file_maintenance_jobs WHERE job_type = ?;', ( ClientFiles.REGENERATE_FILE_DATA_JOB_FORCE_THUMBNAIL, ClientFiles.REGENERATE_FILE_DATA_JOB_FILE_METADATA ) )
            
            #
            
            one_row = self._c.execute( 'SELECT * FROM files_info;' ).fetchone()
            
            if one_row is None or len( one_row ) == 8: # doesn't have has_audio yet
                
                self._controller.pub( 'splash_set_status_subtext', 'adding \'has audio\' metadata column' )
                
                existing_files_info = self._c.execute( 'SELECT * FROM files_info;' ).fetchall()
                
                self._c.execute( 'DROP TABLE files_info;' )
                
                self._c.execute( 'CREATE TABLE files_info ( hash_id INTEGER PRIMARY KEY, size INTEGER, mime INTEGER, width INTEGER, height INTEGER, duration INTEGER, num_frames INTEGER, has_audio INTEGER_BOOLEAN, num_words INTEGER );' )
                
                insert_iterator = ( ( hash_id, size, mime, width, height, duration, num_frames, mime in HC.MIMES_THAT_DEFINITELY_HAVE_AUDIO, num_words ) for ( hash_id, size, mime, width, height, duration, num_frames, num_words ) in existing_files_info )
                
                self._c.executemany( 'INSERT INTO files_info VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ? );', insert_iterator )
                
                self._CreateIndex( 'files_info', [ 'size' ] )
                self._CreateIndex( 'files_info', [ 'mime' ] )
                self._CreateIndex( 'files_info', [ 'width' ] )
                self._CreateIndex( 'files_info', [ 'height' ] )
                self._CreateIndex( 'files_info', [ 'duration' ] )
                self._CreateIndex( 'files_info', [ 'num_frames' ] )
                
                self._c.execute( 'ANALYZE files_info;' )
                
                try:
                    
                    service_id = self._GetServiceId( CC.COMBINED_LOCAL_FILE_SERVICE_KEY )
                    
                    self._c.execute( 'INSERT OR IGNORE INTO file_maintenance_jobs ( hash_id, job_type, time_can_start ) SELECT hash_id, ?, ? FROM files_info NATURAL JOIN current_files WHERE service_id = ? AND mime IN ' + HydrusData.SplayListForDB( HC.MIMES_THAT_MAY_HAVE_AUDIO ) + ';', ( ClientFiles.REGENERATE_FILE_DATA_JOB_FILE_METADATA, 0, service_id ) )
                    
                except Exception as e:
                    
                    HydrusData.PrintException( e )
                    
                    message = 'Trying to schedule audio detection on videos failed! Please let hydrus dev know!'
                    
                    self.pub_initial_message( message )
                    
                
            
            #
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultParsers( ( 'deviant art file page parser', ) )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some url classes and parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 364:
            
            try:
                
                ( options, ) = self._c.execute( 'SELECT options FROM options;' ).fetchone()
                
                new_options = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_CLIENT_OPTIONS )
                
                default_collect = options[ 'default_collect' ]
                
                if default_collect is None:
                    
                    default_collect = []
                    
                
                namespaces = [ n for ( t, n ) in default_collect if t == 'namespace' ]
                rating_service_keys = [ bytes.fromhex( r ) for ( t, r ) in default_collect if t == 'rating' ]
                
                default_media_collect = ClientMedia.MediaCollect( namespaces = namespaces, rating_service_keys = rating_service_keys )
                
                new_options.SetDefaultCollect( default_media_collect )
                
                self._SetJSONDump( new_options )
                
            except:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update your default collection settings failed! Please check them in the options dialog.'
                
                self.pub_initial_message( message )
                
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultParsers( ( 'deviant art file page parser', ) )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some url classes and parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 365:
            
            self._controller.pub( 'splash_set_status_subtext', 'doing some db optimisation' )
            
            self._c.execute( 'ANALYZE main;' )
            
        
        if version == 367:
            
            try:
                
                result = self._c.execute( 'SELECT name FROM services WHERE service_key = ?;', ( sqlite3.Binary( CC.DEFAULT_LOCAL_TAG_SERVICE_KEY ), ) ).fetchone()
                
                if result is not None:
                    
                    ( service_name, ) = result
                    
                    if service_name == 'local tags':
                        
                        self._c.execute( 'UPDATE services SET name = ? WHERE service_key = ?;', ( 'my tags', sqlite3.Binary( CC.DEFAULT_LOCAL_TAG_SERVICE_KEY ), ) )
                        
                    
                
            except:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update default local tag service name failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
            #
            
            try:
                
                # increasing default limit, let's see how it goes
                
                bandwidth_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_BANDWIDTH_MANAGER )
                
                #
                
                hydrus_default_nc = ClientNetworkingContexts.NetworkContext( CC.NETWORK_CONTEXT_HYDRUS )
                
                current_rules = bandwidth_manager.GetRules( hydrus_default_nc )
                
                old_defaults = HydrusNetworking.BandwidthRules()
                
                old_defaults.AddRule( HC.BANDWIDTH_TYPE_DATA, 86400, 64 * 1024 * 1024 )
                
                if current_rules.GetSerialisableTuple() == old_defaults.GetSerialisableTuple():
                    
                    new_rules = HydrusNetworking.BandwidthRules()
                    
                    new_rules.AddRule( HC.BANDWIDTH_TYPE_DATA, 86400, 512 * 1024 * 1024 )
                    
                    bandwidth_manager.SetRules( hydrus_default_nc, new_rules )
                    
                    self._SetJSONDump( bandwidth_manager )
                    
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update default hydrus bandwidth rules failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
            try:
                
                session_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_SESSION_MANAGER )
                
                #
                
                # late hackery, just clear all hydrus sessions due to ptr switch
                
                services = self._GetServices( HC.REPOSITORIES )
                
                for service in services:
                    
                    service_key = service.GetServiceKey()
                    
                    nc = ClientNetworkingContexts.NetworkContext( CC.NETWORK_CONTEXT_HYDRUS, service_key )
                    
                    session_manager.ClearSession( nc )
                    
                
                self._SetJSONDump( session_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to clear repository session info failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
            #
            
            try:
                
                services = self._GetServices( HC.REPOSITORIES )
                
                for service in services:
                    
                    name = service.GetName()
                    credentials = service.GetCredentials()
                    
                    ( host, port ) = credentials.GetAddress()
                    
                    do_transfer = False
                    do_pause = False
                    
                    if host == 'hydrus.no-ip.org':
                        
                        if port == 45872:
                            
                            do_pause = True
                            
                        elif port == 45871:
                            
                            def ask_what_to_do():
                                
                                message = 'The PTR is no longer run by hydrus dev! A user on the discord has kindly offered to host it to relieve the bandwidth issues. A new janitorial team will also help deal with the piled-up petitions. Please see the v368 release post for more information, or check here:'
                                message += os.linesep * 2
                                message += 'https://hydrus.tumblr.com/post/187561442294'
                                message += os.linesep * 2
                                message += 'The PTR is at a new address, "https://ptr.hydrus.network:45871". Would you like to automatically redirect your client\'s PTR service, "{}", to that new location and keep using it?'.format( name )
                                
                                from hydrus.client.gui import ClientGUIDialogsQuick
                                
                                result = ClientGUIDialogsQuick.GetYesNo( None, message, title = 'PTR has moved!', yes_label = 'yes, move me to the new location', no_label = 'no, pause my ptr as it is' )
                                
                                return result
                                
                            
                            result = self._controller.CallBlockingToQt( None, ask_what_to_do )
                            
                            if result == QW.QDialog.Accepted:
                                
                                do_transfer = True
                                
                            else:
                                
                                do_pause = True
                                
                            
                        
                    
                    if do_pause:
                        
                        if not service.IsPaused():
                            
                            service.PausePlay()
                            
                        
                    elif do_transfer:
                        
                        credentials.SetAddress( 'ptr.hydrus.network', port )
                        
                    
                    if do_transfer or do_pause:
                        
                        ( service_key, service_type, name, dictionary ) = service.ToTuple()
                        
                        dictionary_string = dictionary.DumpToString()
                        
                        self._c.execute( 'UPDATE services SET dictionary_string = ? WHERE service_key = ?;', ( dictionary_string, sqlite3.Binary( service_key ) ) )
                        
                    
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to check or update PTR service(s) to the new location failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 368:
            
            self._c.execute( 'CREATE TABLE IF NOT EXISTS file_modified_timestamps ( hash_id INTEGER PRIMARY KEY, file_modified_timestamp INTEGER );' )
            self._CreateIndex( 'file_modified_timestamps', [ 'file_modified_timestamp' ] )
            
            try:
                
                self._controller.pub( 'splash_set_status_subtext', 'queueing up modified timestamp jobs' )
                
                service_id = self._GetServiceId( CC.COMBINED_LOCAL_FILE_SERVICE_KEY )
                
                self._c.execute( 'INSERT OR IGNORE INTO file_maintenance_jobs ( hash_id, job_type, time_can_start ) SELECT hash_id, ?, ? FROM files_info NATURAL JOIN current_files WHERE service_id = ?;', ( ClientFiles.REGENERATE_FILE_DATA_JOB_FILE_MODIFIED_TIMESTAMP, 0, service_id ) )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to schedule file modified timestamp generation failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 369:
            
            try:
                
                # async processing came in 364. it truncated some data in certain large-list, slower-processing situations, so we want to reset some processing
                # let's say 8 weeks to cover most of the problem for most people
                
                eight_weeks_previous = HydrusData.GetNow() - ( 8 * 7 * 86400 )
                
                service_ids = self._GetServiceIds( ( HC.TAG_REPOSITORY, ) )
                
                for service_id in service_ids:
                    
                    service = self._GetService( service_id )
                    
                    metadata = service.GetMetadata()
                    
                    repository_updates_table_name = GenerateRepositoryRepositoryUpdatesTableName( service_id )
                    
                    update_indices_to_reset = set()
                    
                    for ( update_index, begin, end ) in metadata.GetUpdateIndicesAndTimes():
                        
                        if begin > eight_weeks_previous:
                            
                            update_indices_to_reset.add( update_index )
                            
                        
                    
                    content_hash_ids_to_reset = set()
                    
                    for update_index in update_indices_to_reset:
                        
                        content_hash_ids = self._STS( self._c.execute( 'SELECT hash_id from {} NATURAL JOIN files_info WHERE update_index = ? AND mime = ?;'.format( repository_updates_table_name ), ( update_index, HC.APPLICATION_HYDRUS_UPDATE_CONTENT ) ) )
                        
                        content_hash_ids_to_reset.update( content_hash_ids )
                        
                    
                    self._c.executemany( 'UPDATE {} SET processed = ? WHERE hash_id = ?;'.format( repository_updates_table_name ), ( ( False, hash_id ) for hash_id in content_hash_ids_to_reset ) )
                    
                
            except:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to rewind some processing failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
            #
            
            result = self._c.execute( 'SELECT 1 FROM main.sqlite_master WHERE name = ?;', ( 'tag_censorship', ) ).fetchone()
            
            try:
                
                if result is not None:
                    
                    tag_display_manager = ClientTags.TagDisplayManager()
                    
                    old_tag_censorship = self._c.execute( 'SELECT service_id, blacklist, tags FROM tag_censorship;' ).fetchall()
                    
                    for ( service_id, blacklist, tags ) in old_tag_censorship:
                        
                        try:
                            
                            service = self._GetService( service_id )
                            
                        except HydrusExceptions.DataMissing:
                            
                            continue
                            
                        
                        service_key = service.GetServiceKey()
                        
                        tag_filter = ClientTags.TagFilter()
                        
                        if blacklist:
                            
                            rule_type = CC.FILTER_BLACKLIST
                            
                        else:
                            
                            rule_type = CC.FILTER_WHITELIST
                            
                        
                        for tag in tags:
                            
                            tag_filter.SetRule( tag, rule_type )
                            
                        
                        tag_display_manager.SetTagFilter( ClientTags.TAG_DISPLAY_SINGLE_MEDIA, service_key, tag_filter )
                        
                    
                    self._SetJSONDump( tag_display_manager )
                    
                    self._c.execute( 'DROP TABLE tag_censorship;' )
                    
                
            except:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update tag censorship system to tag display system failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
            #
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultURLClasses( ( 'pixiv file page new format (without language)', 'pixiv file page new format (with language)' ) )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some url classes failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 370:
            
            try:
                
                new_options = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_CLIENT_OPTIONS )
                
                names_to_tag_filters = {}
                
                tag_filter = ClientTags.TagFilter()
                
                tag_filter.SetRule( 'diaper', CC.FILTER_BLACKLIST )
                tag_filter.SetRule( 'gore', CC.FILTER_BLACKLIST )
                tag_filter.SetRule( 'guro', CC.FILTER_BLACKLIST )
                tag_filter.SetRule( 'scat', CC.FILTER_BLACKLIST )
                tag_filter.SetRule( 'vore', CC.FILTER_BLACKLIST )
                
                names_to_tag_filters[ 'example blacklist' ] = tag_filter
                
                tag_filter = ClientTags.TagFilter()
                
                tag_filter.SetRule( '', CC.FILTER_BLACKLIST )
                tag_filter.SetRule( ':', CC.FILTER_BLACKLIST )
                tag_filter.SetRule( 'series:', CC.FILTER_WHITELIST )
                tag_filter.SetRule( 'creator:', CC.FILTER_WHITELIST )
                tag_filter.SetRule( 'studio:', CC.FILTER_WHITELIST )
                tag_filter.SetRule( 'character:', CC.FILTER_WHITELIST )
                
                names_to_tag_filters[ 'basic namespaces only' ] = tag_filter
                
                tag_filter = ClientTags.TagFilter()
                
                tag_filter.SetRule( ':', CC.FILTER_BLACKLIST )
                tag_filter.SetRule( 'series:', CC.FILTER_WHITELIST )
                tag_filter.SetRule( 'creator:', CC.FILTER_WHITELIST )
                tag_filter.SetRule( 'studio:', CC.FILTER_WHITELIST )
                tag_filter.SetRule( 'character:', CC.FILTER_WHITELIST )
                tag_filter.SetRule( '', CC.FILTER_WHITELIST )
                
                names_to_tag_filters[ 'basic booru tags only' ] = tag_filter
                
                tag_filter = ClientTags.TagFilter()
                
                tag_filter.SetRule( 'title:', CC.FILTER_BLACKLIST )
                tag_filter.SetRule( 'filename:', CC.FILTER_BLACKLIST )
                tag_filter.SetRule( 'source:', CC.FILTER_BLACKLIST )
                tag_filter.SetRule( 'booru:', CC.FILTER_BLACKLIST )
                tag_filter.SetRule( 'url:', CC.FILTER_BLACKLIST )
                
                names_to_tag_filters[ 'exclude long/spammy namespaces' ] = tag_filter
                
                new_options.SetFavouriteTagFilters( names_to_tag_filters )
                
                self._SetJSONDump( new_options )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to save new default favourite tag filters failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 374:
            
            try:
                
                login_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_LOGIN_MANAGER )
                
                login_manager.Initialise()
                
                #
                
                login_manager.OverwriteDefaultLoginScripts( [ 'danbooru login' ] )
                
                #
                
                self._SetJSONDump( login_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some login scripts failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 375:
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultGUGs( ( 'pixiv tag search', 'twitter username lookup' ) )
                domain_manager.OverwriteDefaultURLClasses( ( 'pixiv search api', 'twitter tweets api - media only' ) )
                domain_manager.OverwriteDefaultParsers( ( 'pixiv tag search api parser', 'twitter tweet parser (video from koto.reisen)', 'twitter media tweets api parser' ) )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 376:
            
            result = self._c.execute( 'SELECT 1 FROM external_master.sqlite_master WHERE name = ?;', ( 'url_domains', ) ).fetchone()
            
            try:
                
                if result is None:
                    
                    self._controller.pub( 'splash_set_status_subtext', 'compressing url storage--creating' )
                    
                    self._c.execute( 'ALTER TABLE urls RENAME TO urls_old;' )
                    
                    self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.url_domains ( domain_id INTEGER PRIMARY KEY, domain TEXT UNIQUE );' )
                    
                    self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.urls ( url_id INTEGER PRIMARY KEY, domain_id INTEGER, url TEXT UNIQUE );' )
                    
                    self._controller.pub( 'splash_set_status_subtext', 'compressing url storage--populating domains' )
                    
                    self._c.execute( 'INSERT INTO url_domains ( domain ) SELECT DISTINCT domain FROM urls_old;' )
                    
                    self._controller.pub( 'splash_set_status_subtext', 'compressing url storage--populating urls' )
                    
                    self._c.execute( 'INSERT INTO urls ( url_id, domain_id, url ) SELECT url_id, domain_id, url FROM urls_old NATURAL JOIN url_domains;' )
                    
                    self._controller.pub( 'splash_set_status_subtext', 'compressing url storage--indexing' )
                    
                    self._CreateIndex( 'external_master.urls', [ 'domain_id' ] )
                    
                    self._c.execute( 'DROP TABLE urls_old;' )
                    
                    self._controller.pub( 'splash_set_status_subtext', 'compressing url storage--optimising' )
                    
                    self._c.execute( 'ANALYZE external_master.urls;' )
                    
                
            except Exception as e:
                
                HydrusData.Print( 'Could not update URL storage!' )
                HydrusData.PrintException( e )
                
                raise
                
            
        
        if version == 378:
            
            try:
                
                login_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_LOGIN_MANAGER )
                
                login_manager.Initialise()
                
                domains_to_login_info = login_manager.GetDomainsToLoginInfo()
                
                for ( login_domain, ( login_script_key_and_name, credentials, login_access_type, login_access_text, active, validity, validity_error_text, no_work_until, no_work_until_reason ) ) in list( domains_to_login_info.items() ):
                    
                    ( login_script_key, login_script_name ) = login_script_key_and_name
                    
                    if login_domain == 'www.pixiv.net' and login_script_name == 'pixiv login' and active:
                        
                        active = False
                        
                        domains_to_login_info[ login_domain ] = ( login_script_key_and_name, credentials, login_access_type, login_access_text, active, validity, validity_error_text, no_work_until, no_work_until_reason )
                        
                        login_manager.SetDomainsToLoginInfo( domains_to_login_info )
                        
                        self._SetJSONDump( login_manager )
                        
                        self.pub_initial_message( 'The default Pixiv login script no longer works. It appeared to be active for you, so it has been deactivated. Please use the Hydrus Companion web browser addon to log in to Pixiv.' )
                        
                        break
                        
                    
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to deactivate pixiv login failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultGUGs( [ 'derpibooru tag search', 'derpibooru tag search - no filter' ] )
                
                #
                
                domain_manager.OverwriteDefaultURLClasses( [ 'derpibooru gallery page', 'derpibooru file page' ] )
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ 'derpibooru.org file page parser', 'derpibooru gallery page parser' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update derpibooru failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 379:
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultURLClasses( [ 'pixiv artist page', '8kun thread', '8kun thread json api', 'vch.moe thread', 'vch.moe thread json api' ] )
                
                domain_manager.DeleteURLClasses( [ 'pixiv artist gallery page' ] )
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ '4chan-style thread api parser', '8kun thread api parser' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some downloader objects failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 380:
            
            try:
                
                new_options = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_CLIENT_OPTIONS )
                
                default_view_options = new_options.GetDefaultMediaViewOptions()
                
                new_options.SetMediaViewOptions( default_view_options )
                
                self._SetJSONDump( new_options )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update the media view options failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 382:
            
            existing_shortcut_names = self._GetJSONDumpNames( HydrusSerialisable.SERIALISABLE_TYPE_SHORTCUT_SET )
            
            if 'global' not in existing_shortcut_names:
                
                list_of_shortcuts = ClientDefaults.GetDefaultShortcuts()
                
                for shortcuts in list_of_shortcuts:
                    
                    if shortcuts.GetName() == 'global':
                        
                        self._SetJSONDump( shortcuts )
                        
                    
                
            
        
        if version == 383:
            
            existing_shortcut_names = self._GetJSONDumpNames( HydrusSerialisable.SERIALISABLE_TYPE_SHORTCUT_SET )
            
            list_of_shortcuts = ClientDefaults.GetDefaultShortcuts()
            
            for new_name in ( 'media_viewer_media_window', 'preview_media_window' ):
                
                if new_name not in existing_shortcut_names:
                    
                    for shortcuts in list_of_shortcuts:
                        
                        if shortcuts.GetName() == new_name:
                            
                            self._SetJSONDump( shortcuts )
                            
                        
                    
                
            
            if 'media_viewer_browser' in existing_shortcut_names:
                
                try:
                    
                    media_viewer_browser_shortcuts = self._GetJSONDumpNamed( HydrusSerialisable.SERIALISABLE_TYPE_SHORTCUT_SET, dump_name = 'media_viewer_browser' )
                    
                    from hydrus.client.gui import ClientGUIShortcuts
                    
                    right_up = ClientGUIShortcuts.Shortcut( ClientGUIShortcuts.SHORTCUT_TYPE_MOUSE, ClientGUIShortcuts.SHORTCUT_MOUSE_RIGHT, ClientGUIShortcuts.SHORTCUT_PRESS_TYPE_RELEASE, [] )
                    
                    if media_viewer_browser_shortcuts.GetCommand( right_up ) is None:
                        
                        media_viewer_browser_shortcuts.SetCommand( right_up, ClientData.ApplicationCommand( CC.APPLICATION_COMMAND_TYPE_SIMPLE, 'show_menu' ) )
                        
                        self._SetJSONDump( media_viewer_browser_shortcuts )
                        
                    
                except:
                    
                    HydrusData.PrintException( e )
                    
                    message = 'Trying to update the media_viewer_browser shortcuts failed! Please let hydrus dev know!'
                    
                    self.pub_initial_message( message )
                    
                
            
        
        if version == 384:
            
            close_media_viewer = ClientData.ApplicationCommand( CC.APPLICATION_COMMAND_TYPE_SIMPLE, 'close_media_viewer' )
            keep_archive_filter = ClientData.ApplicationCommand( CC.APPLICATION_COMMAND_TYPE_SIMPLE, 'archive_delete_filter_keep' )
            better_dupe_filter = ClientData.ApplicationCommand( CC.APPLICATION_COMMAND_TYPE_SIMPLE, 'duplicate_filter_this_is_better_and_delete_other' )
            
            existing_shortcut_names = self._GetJSONDumpNames( HydrusSerialisable.SERIALISABLE_TYPE_SHORTCUT_SET )
            
            from hydrus.client.gui import ClientGUIShortcuts
            
            updates_to_do = {}
            
            shortcuts_and_commands = []
            
            shortcuts_and_commands.append( ( ClientGUIShortcuts.Shortcut( ClientGUIShortcuts.SHORTCUT_TYPE_KEYBOARD_SPECIAL, ClientGUIShortcuts.SHORTCUT_KEY_SPECIAL_ENTER, ClientGUIShortcuts.SHORTCUT_PRESS_TYPE_PRESS, [] ), close_media_viewer ) )
            shortcuts_and_commands.append( ( ClientGUIShortcuts.Shortcut( ClientGUIShortcuts.SHORTCUT_TYPE_KEYBOARD_SPECIAL, ClientGUIShortcuts.SHORTCUT_KEY_SPECIAL_ENTER, ClientGUIShortcuts.SHORTCUT_PRESS_TYPE_PRESS, [ ClientGUIShortcuts.SHORTCUT_MODIFIER_KEYPAD ] ), close_media_viewer ) )
            shortcuts_and_commands.append( ( ClientGUIShortcuts.Shortcut( ClientGUIShortcuts.SHORTCUT_TYPE_KEYBOARD_SPECIAL, ClientGUIShortcuts.SHORTCUT_KEY_SPECIAL_RETURN, ClientGUIShortcuts.SHORTCUT_PRESS_TYPE_PRESS, [] ), close_media_viewer ) )
            shortcuts_and_commands.append( ( ClientGUIShortcuts.Shortcut( ClientGUIShortcuts.SHORTCUT_TYPE_KEYBOARD_SPECIAL, ClientGUIShortcuts.SHORTCUT_KEY_SPECIAL_RETURN, ClientGUIShortcuts.SHORTCUT_PRESS_TYPE_PRESS, [ ClientGUIShortcuts.SHORTCUT_MODIFIER_KEYPAD ] ), close_media_viewer ) )
            shortcuts_and_commands.append( ( ClientGUIShortcuts.Shortcut( ClientGUIShortcuts.SHORTCUT_TYPE_KEYBOARD_SPECIAL, ClientGUIShortcuts.SHORTCUT_KEY_SPECIAL_ESCAPE, ClientGUIShortcuts.SHORTCUT_PRESS_TYPE_PRESS, [] ), close_media_viewer ) )
            
            updates_to_do[ 'media_viewer' ] = shortcuts_and_commands
            
            shortcuts_and_commands = []
            
            shortcuts_and_commands.append( ( ClientGUIShortcuts.Shortcut( ClientGUIShortcuts.SHORTCUT_TYPE_MOUSE, ClientGUIShortcuts.SHORTCUT_MOUSE_LEFT, ClientGUIShortcuts.SHORTCUT_PRESS_TYPE_DOUBLE_CLICK, [] ), close_media_viewer ) )
            shortcuts_and_commands.append( ( ClientGUIShortcuts.Shortcut( ClientGUIShortcuts.SHORTCUT_TYPE_MOUSE, ClientGUIShortcuts.SHORTCUT_MOUSE_MIDDLE, ClientGUIShortcuts.SHORTCUT_PRESS_TYPE_PRESS, [] ), close_media_viewer ) )
            
            updates_to_do[ 'media_viewer_browser' ] = shortcuts_and_commands
            
            shortcuts_and_commands = []
            
            shortcuts_and_commands.append( ( ClientGUIShortcuts.Shortcut( ClientGUIShortcuts.SHORTCUT_TYPE_MOUSE, ClientGUIShortcuts.SHORTCUT_MOUSE_LEFT, ClientGUIShortcuts.SHORTCUT_PRESS_TYPE_DOUBLE_CLICK, [] ), keep_archive_filter ) )
            
            updates_to_do[ 'archive_delete_filter' ] = shortcuts_and_commands
            
            shortcuts_and_commands = []
            
            shortcuts_and_commands.append( ( ClientGUIShortcuts.Shortcut( ClientGUIShortcuts.SHORTCUT_TYPE_MOUSE, ClientGUIShortcuts.SHORTCUT_MOUSE_LEFT, ClientGUIShortcuts.SHORTCUT_PRESS_TYPE_DOUBLE_CLICK, [] ), better_dupe_filter ) )
            
            updates_to_do[ 'duplicate_filter' ] = shortcuts_and_commands
            
            for ( shortcut_set_name, shortcuts_and_commands ) in updates_to_do.items():
                
                if shortcut_set_name in existing_shortcut_names:
                    
                    try:
                        
                        shortcut_set = self._GetJSONDumpNamed( HydrusSerialisable.SERIALISABLE_TYPE_SHORTCUT_SET, dump_name = shortcut_set_name )
                        
                        for ( s, c ) in shortcuts_and_commands:
                            
                            if shortcut_set.GetCommand( s ) is None:
                                
                                shortcut_set.SetCommand( s, c )
                                
                            
                        
                        self._SetJSONDump( shortcut_set )
                        
                    except:
                        
                        HydrusData.PrintException( e )
                        
                        message = 'Trying to update the "{}" shortcuts failed! Please let hydrus dev know!'.format( shortcut_set_name )
                        
                        self.pub_initial_message( message )
                        
                    
                
            
            #
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ 'danbooru file page parser', 'danbooru file page parser - get webm ugoira' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 386:
            
            try:
                
                status_hook = lambda s: self._controller.pub( 'splash_set_status_subtext', s )
                
                self._RepopulateAndUpdateTagSearchCache( status_hook = status_hook, do_searchable = False, do_integers = False )
                
            except Exception as e:
                
                HydrusData.Print( 'Failed to repopulate fts tag cache:' )
                HydrusData.PrintException( e )
                
                message = 'Trying to update the tag search cache failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultURLClasses( [ 'tvch.moe thread', 'tvch.moe thread json api', 'derpibooru gallery page', 'derpibooru gallery page api' ] )
                
                #
                
                domain_manager.OverwriteDefaultGUGs( [ 'derpibooru tag search', 'derpibooru tag search - no filter' ] )
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ '4chan-style thread api parser', 'derpibooru gallery page api parser' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 387:
            
            result = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_FAVOURITE_SEARCH_MANAGER )
            
            if result is None:
                
                favourite_search_manager = ClientSearch.FavouriteSearchManager()
                
                ClientDefaults.SetDefaultFavouriteSearchManagerData( favourite_search_manager )
                
                self._SetJSONDump( favourite_search_manager )
                
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultURLClasses( [ 'e621 file page', 'e621 gallery page' ] )
                
                #
                
                domain_manager.OverwriteDefaultGUGs( [ 'e621 tag search' ] )
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ 'e621 file page parser', 'e621 gallery page parser' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
                #
                
                login_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_LOGIN_MANAGER )
                
                login_manager.Initialise()
                
                #
                
                login_manager.DeleteLoginScripts( [ 'e-hentai login 2018.11.08', 'e-hentai login 2018.11.12' ] )
                
                #
                
                if not login_manager.DomainHasALoginScript( 'e-hentai.org' ):
                    
                    login_manager.DeleteLoginDomain( 'e-hentai.org' )
                    
                
                #
                
                self._SetJSONDump( login_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 388:
            
            try:
                
                favourite_search_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_FAVOURITE_SEARCH_MANAGER )
                
                folders_to_names = favourite_search_manager.GetFoldersToNames()
                
                do_it = True
                
                if None in folders_to_names:
                    
                    if 'empty page' in folders_to_names[ None ]:
                        
                        do_it = False
                        
                    
                
                if do_it:
                    
                    foldername = None
                    name = 'empty page'
                    
                    tag_search_context = ClientSearch.TagSearchContext()
                    
                    predicates = []
                    
                    file_search_context = ClientSearch.FileSearchContext( file_service_key = CC.LOCAL_FILE_SERVICE_KEY, tag_search_context = tag_search_context, predicates = predicates )
                    
                    synchronised = True
                    media_sort = None
                    media_collect = None
                    
                    new_rows = [ ( foldername, name, file_search_context, synchronised, media_sort, media_collect ) ]
                    
                    #
                    
                    rows = list( favourite_search_manager.GetFavouriteSearchRows() )
                    
                    rows.extend( new_rows )
                    
                    favourite_search_manager.SetFavouriteSearchRows( rows )
                    
                    self._SetJSONDump( favourite_search_manager )
                    
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to add an empty favourite search failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
            try:
                
                script_rows = ClientDefaults.GetDefaultScriptRows()
                
                for script_row in script_rows:
                    
                    dump_type = script_row[0]
                    dump_name = script_row[1]
                    
                    self._c.execute( 'DELETE FROM json_dumps_named WHERE dump_type = ? AND dump_name = ?;', ( dump_type, dump_name ) )
                    
                
                self._c.executemany( 'REPLACE INTO json_dumps_named VALUES ( ?, ?, ?, ?, ? );', script_rows )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to add new file lookup scripts search failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultURLClasses( [ 'deviant art file page', 'deviant art file page api', 'e621 file page (old format)' ] )
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ 'e621 file page parser', 'deviant art file page api parser' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
                #
                
                login_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_LOGIN_MANAGER )
                
                login_manager.Initialise()
                
                #
                
                login_manager.DeleteLoginScripts( [ 'nijie.info login script' ] )
                
                #
                
                if not login_manager.DomainHasALoginScript( 'nijie.info' ):
                    
                    login_manager.DeleteLoginDomain( 'nijie.info' )
                    
                
                #
                
                self._SetJSONDump( login_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 389:
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ 'derpibooru.org file page parser' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 390:
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ 'danbooru file page parser', 'danbooru file page parser - get webm ugoira' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
                #
                
                login_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_LOGIN_MANAGER )
                
                login_manager.Initialise()
                
                #
                
                login_manager.OverwriteDefaultLoginScripts( ( 'e621.net login', ) )
                
                #
                
                login_manager.TryToLinkMissingLoginScripts( ( 'e621.net', ) )
                
                #
                
                self._SetJSONDump( login_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 391:
            
            tag_service_ids = self._GetServiceIds( HC.REAL_TAG_SERVICES )
            
            for tag_service_id in tag_service_ids:
                
                self._CacheTagSiblingsLookupDrop( tag_service_id )
                self._CacheTagSiblingsLookupGenerate( tag_service_id )
                
            
            self._CacheTagSiblingsLookupDrop( self._combined_tag_service_id )
            self._CacheTagSiblingsLookupGenerate( self._combined_tag_service_id )
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ 'e621 file page parser', 'sankaku file page parser' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 392:
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultURLClasses( [ 'deviant art file page extended_fetch api', 'deviant art file page', 'deviant art flash sandbox page' ] )
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ 'deviant art flash sandbox page parser', 'deviant art file extended_fetch parser' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 395:
            
            result = self._c.execute( 'SELECT 1 FROM external_master.sqlite_master WHERE name = ?;', ( 'labels', ) ).fetchone()
            
            if result is None:
                
                try:
                    
                    self._controller.pub( 'splash_set_status_subtext', 'updating notes table' )
                    
                    self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.labels ( label_id INTEGER PRIMARY KEY, label TEXT UNIQUE );' )
                    
                    self._c.execute( 'CREATE TABLE IF NOT EXISTS external_master.notes ( note_id INTEGER PRIMARY KEY, note TEXT UNIQUE );' )
                    self._c.execute( 'CREATE VIRTUAL TABLE IF NOT EXISTS external_caches.notes_fts4 USING fts4( note );' )
                    
                    self._c.execute( 'ALTER TABLE file_notes RENAME TO file_notes_old;' )
                    
                    self._c.execute( 'CREATE TABLE file_notes ( hash_id INTEGER, name_id INTEGER, note_id INTEGER, PRIMARY KEY ( hash_id, name_id ) );' )
                    self._CreateIndex( 'file_notes', [ 'note_id' ] )
                    
                    all_data = self._c.execute( 'SELECT hash_id, notes FROM file_notes_old;' ).fetchall()
                    
                    name_id = self._GetLabelId( 'notes' )
                    
                    for ( hash_id, note ) in all_data:
                        
                        note_id = self._GetNoteId( note )
                        
                        self._c.execute( 'INSERT OR IGNORE INTO file_notes ( hash_id, name_id, note_id ) VALUES ( ?, ?, ? );', ( hash_id, name_id, note_id ) )
                        
                    
                    self._c.execute( 'DROP TABLE file_notes_old;' )
                    
                    self._AnalyzeTable( 'file_notes' )
                    self._AnalyzeTable( 'notes' )
                    self._AnalyzeTable( 'notes_fts4' )
                    self._AnalyzeTable( 'labels' )
                    
                except Exception as e:
                    
                    message = 'Trying to update the notes table failed! Please let hydrus dev know!'
                    
                    HydrusData.Print( message )
                    BlockingSafeShowMessage( message )
                    HydrusData.PrintException( e )
                    
                    raise
                    
                
            
            result = self._c.execute( 'SELECT 1 FROM external_caches.sqlite_master WHERE name = ?;', ( 'subtags_fts4', ) ).fetchone()
            
            try:
                
                if result is None:
                    
                    self._controller.pub( 'splash_set_status_subtext', 'moving fts fast tag search cache' )
                    
                    self._c.execute( 'CREATE VIRTUAL TABLE IF NOT EXISTS external_caches.subtags_fts4 USING fts4( subtag );' )
                    
                    self._c.execute( 'INSERT OR IGNORE INTO external_caches.subtags_fts4 ( docid, subtag ) SELECT docid, subtag FROM external_master.subtags_fts4;' )
                    
                    self._c.execute( 'DROP TABLE external_master.subtags_fts4;' )
                    
                    self._AnalyzeTable( 'subtags_fts4' )
                    
                
            except Exception as e:
                
                message = 'Trying to move tag fast search cache failed! Please let hydrus dev know!'
                
                HydrusData.Print( message )
                BlockingSafeShowMessage( message )
                HydrusData.PrintException( e )
                
                raise
                
            
            result = self._c.execute( 'SELECT 1 FROM external_caches.sqlite_master WHERE name = ?;', ( 'subtags_searchable_map', ) ).fetchone()
            
            try:
                
                if result is None:
                    
                    self._c.execute( 'CREATE TABLE IF NOT EXISTS external_caches.subtags_searchable_map ( subtag_id INTEGER PRIMARY KEY, searchable_subtag_id INTEGER );' )
                    self._CreateIndex( 'external_caches.subtags_searchable_map', [ 'searchable_subtag_id' ] )
                    
                    status_hook = lambda s: self._controller.pub( 'splash_set_status_subtext', s )
                    
                    self._RepopulateAndUpdateTagSearchCache( status_hook = status_hook, do_fts = False, do_integers = False )
                    
                    self._AnalyzeTable( 'subtags_searchable_map' )
                    
                
            except Exception as e:
                
                message = 'Trying to update tag search cache failed! Please let hydrus dev know!'
                
                HydrusData.Print( message )
                BlockingSafeShowMessage( message )
                HydrusData.PrintException( e )
                
                raise
                
            
            
            
        
        if version == 397:
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultGUGs( [ 'newgrounds artist art lookup', 'newgrounds artist games lookup', 'newgrounds artist movies lookup', 'newgrounds artist lookup' ] )
                
                #
                
                domain_manager.OverwriteDefaultURLClasses( [ 'newgrounds movies gallery page', 'newgrounds games gallery page', 'newgrounds file page', 'newgrounds art', 'newgrounds art gallery page' ] )
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ 'gelbooru 0.2.x gallery page parser', 'newgrounds art parser', 'newgrounds file page parser', 'newgrounds gallery page parser' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        if version == 398:
            
            existing_shortcut_names = self._GetJSONDumpNames( HydrusSerialisable.SERIALISABLE_TYPE_SHORTCUT_SET )
            
            if 'media' in existing_shortcut_names:
                
                try:
                    
                    media_shortcuts = self._GetJSONDumpNamed( HydrusSerialisable.SERIALISABLE_TYPE_SHORTCUT_SET, dump_name = 'media' )
                    
                    from hydrus.client.gui import ClientGUIShortcuts
                    
                    delete_command = ClientData.ApplicationCommand( CC.APPLICATION_COMMAND_TYPE_SIMPLE, 'delete_file' )
                    undelete_command = ClientData.ApplicationCommand( CC.APPLICATION_COMMAND_TYPE_SIMPLE, 'undelete_file' )
                    
                    for delete_key in ClientGUIShortcuts.DELETE_KEYS_HYDRUS:
                        
                        shortcut = ClientGUIShortcuts.Shortcut( ClientGUIShortcuts.SHORTCUT_TYPE_KEYBOARD_SPECIAL, delete_key, ClientGUIShortcuts.SHORTCUT_PRESS_TYPE_PRESS, [] )
                        
                        if media_shortcuts.GetCommand( shortcut ) is None:
                            
                            media_shortcuts.SetCommand( shortcut, delete_command )
                            
                        
                        shortcut = ClientGUIShortcuts.Shortcut( ClientGUIShortcuts.SHORTCUT_TYPE_KEYBOARD_SPECIAL, delete_key, ClientGUIShortcuts.SHORTCUT_PRESS_TYPE_PRESS, [ ClientGUIShortcuts.SHORTCUT_MODIFIER_SHIFT ] )
                        
                        if media_shortcuts.GetCommand( shortcut ) is None:
                            
                            media_shortcuts.SetCommand( shortcut, undelete_command )
                            
                        
                    
                    self._SetJSONDump( media_shortcuts )
                    
                except:
                    
                    HydrusData.PrintException( e )
                    
                    message = 'Trying to update the media shortcuts failed! Please let hydrus dev know!'
                    
                    self.pub_initial_message( message )
                    
                
            
        
        if version == 398:
            
            try:
                
                domain_manager = self._GetJSONDump( HydrusSerialisable.SERIALISABLE_TYPE_NETWORK_DOMAIN_MANAGER )
                
                domain_manager.Initialise()
                
                #
                
                domain_manager.OverwriteDefaultURLClasses( [ '8chan.moe thread', '8chan.moe thread json api' ] )
                
                #
                
                domain_manager.OverwriteDefaultParsers( [ '8chan.moe thread api parser' ] )
                
                #
                
                domain_manager.TryToLinkURLClassesAndParsers()
                
                #
                
                self._SetJSONDump( domain_manager )
                
            except Exception as e:
                
                HydrusData.PrintException( e )
                
                message = 'Trying to update some parsers failed! Please let hydrus dev know!'
                
                self.pub_initial_message( message )
                
            
        
        self._controller.pub( 'splash_set_title_text', 'updated db to v{}'.format( HydrusData.ToHumanInt( version + 1 ) ) )
        
        self._c.execute( 'UPDATE version SET version = ?;', ( version + 1, ) )
        
    
    def _UpdateMappings( self, tag_service_id, mappings_ids = None, deleted_mappings_ids = None, pending_mappings_ids = None, pending_rescinded_mappings_ids = None, petitioned_mappings_ids = None, petitioned_rescinded_mappings_ids = None ):
        
        ( current_mappings_table_name, deleted_mappings_table_name, pending_mappings_table_name, petitioned_mappings_table_name ) = GenerateMappingsTableNames( tag_service_id )
        
        if mappings_ids is None: mappings_ids = []
        if deleted_mappings_ids is None: deleted_mappings_ids = []
        if pending_mappings_ids is None: pending_mappings_ids = []
        if pending_rescinded_mappings_ids is None: pending_rescinded_mappings_ids = []
        if petitioned_mappings_ids is None: petitioned_mappings_ids = []
        if petitioned_rescinded_mappings_ids is None: petitioned_rescinded_mappings_ids = []
        
        file_service_ids = self._GetServiceIds( HC.AUTOCOMPLETE_CACHE_SPECIFIC_FILE_SERVICES )
        
        change_in_num_mappings = 0
        change_in_num_deleted_mappings = 0
        change_in_num_pending_mappings = 0
        change_in_num_petitioned_mappings = 0
        change_in_num_tags = 0
        change_in_num_files = 0
        
        all_adds = mappings_ids + pending_mappings_ids
        
        tag_ids_being_added = { tag_id for ( tag_id, hash_ids ) in all_adds }
        
        hash_ids_lists = [ hash_ids for ( tag_id, hash_ids ) in all_adds ]
        hash_ids_being_added = { hash_id for hash_id in itertools.chain.from_iterable( hash_ids_lists ) }
        
        all_removes = deleted_mappings_ids + pending_rescinded_mappings_ids
        
        tag_ids_being_removed = { tag_id for ( tag_id, hash_ids ) in all_removes }
        
        hash_ids_lists = [ hash_ids for ( tag_id, hash_ids ) in all_removes ]
        hash_ids_being_removed = { hash_id for hash_id in itertools.chain.from_iterable( hash_ids_lists ) }
        
        tag_ids_to_search_for = tag_ids_being_added.union( tag_ids_being_removed )
        hash_ids_to_search_for = hash_ids_being_added.union( hash_ids_being_removed )
        
        self._c.execute( 'CREATE TABLE mem.temp_tag_ids ( tag_id INTEGER );' )
        self._c.execute( 'CREATE TABLE mem.temp_hash_ids ( hash_id INTEGER );' )
        
        self._c.executemany( 'INSERT INTO temp_tag_ids ( tag_id ) VALUES ( ? );', ( ( tag_id, ) for tag_id in tag_ids_to_search_for ) )
        self._c.executemany( 'INSERT INTO temp_hash_ids ( hash_id ) VALUES ( ? );', ( ( hash_id, ) for hash_id in hash_ids_to_search_for ) )
        
        pre_existing_tag_ids = self._STS( self._c.execute( 'SELECT tag_id as t FROM temp_tag_ids WHERE EXISTS ( SELECT 1 FROM ' + current_mappings_table_name + ' WHERE tag_id = t );' ) )
        pre_existing_hash_ids = self._STS( self._c.execute( 'SELECT hash_id as h FROM temp_hash_ids WHERE EXISTS ( SELECT 1 FROM ' + current_mappings_table_name + ' WHERE hash_id = h );' ) )
        
        num_tags_added = len( tag_ids_being_added.difference( pre_existing_tag_ids ) )
        num_files_added = len( hash_ids_being_added.difference( pre_existing_hash_ids ) )
        
        change_in_num_tags += num_tags_added
        change_in_num_files += num_files_added
        
        combined_files_current_counter = collections.Counter()
        combined_files_pending_counter = collections.Counter()
        
        if len( mappings_ids ) > 0:
            
            for ( tag_id, hash_ids ) in mappings_ids:
                
                self._c.executemany( 'DELETE FROM ' + deleted_mappings_table_name + ' WHERE tag_id = ? AND hash_id = ?;', ( ( tag_id, hash_id ) for hash_id in hash_ids ) )
                
                num_deleted_deleted = self._GetRowCount()
                
                self._c.executemany( 'DELETE FROM ' + pending_mappings_table_name + ' WHERE tag_id = ? AND hash_id = ?;', ( ( tag_id, hash_id ) for hash_id in hash_ids ) )
                
                num_pending_deleted = self._GetRowCount()
                
                self._c.executemany( 'INSERT OR IGNORE INTO ' + current_mappings_table_name + ' VALUES ( ?, ? );', ( ( tag_id, hash_id ) for hash_id in hash_ids ) )
                
                num_current_inserted = self._GetRowCount()
                
                change_in_num_deleted_mappings -= num_deleted_deleted
                change_in_num_pending_mappings -= num_pending_deleted
                change_in_num_mappings += num_current_inserted
                
                combined_files_pending_counter[ tag_id ] -= num_pending_deleted
                combined_files_current_counter[ tag_id ] += num_current_inserted
                
            
            for file_service_id in file_service_ids:
                
                self._CacheSpecificMappingsAddMappings( file_service_id, tag_service_id, mappings_ids )
                
            
        
        if len( deleted_mappings_ids ) > 0:
            
            for ( tag_id, hash_ids ) in deleted_mappings_ids:
                
                self._c.executemany( 'DELETE FROM ' + current_mappings_table_name + ' WHERE tag_id = ? AND hash_id = ?;', ( ( tag_id, hash_id ) for hash_id in hash_ids ) )
                
                num_current_deleted = self._GetRowCount()
                
                self._c.executemany( 'DELETE FROM ' + petitioned_mappings_table_name + ' WHERE tag_id = ? AND hash_id = ?;', ( ( tag_id, hash_id ) for hash_id in hash_ids ) )
                
                num_petitions_deleted = self._GetRowCount()
                
                self._c.executemany( 'INSERT OR IGNORE INTO ' + deleted_mappings_table_name + ' VALUES ( ?, ? );', ( ( tag_id, hash_id ) for hash_id in hash_ids ) )
                
                num_deleted_inserted = self._GetRowCount()
                
                change_in_num_mappings -= num_current_deleted
                change_in_num_petitioned_mappings -= num_petitions_deleted
                change_in_num_deleted_mappings += num_deleted_inserted
                
                combined_files_current_counter[ tag_id ] -= num_current_deleted
                
            
            for file_service_id in file_service_ids:
                
                self._CacheSpecificMappingsDeleteMappings( file_service_id, tag_service_id, deleted_mappings_ids )
                
            
        
        if len( pending_mappings_ids ) > 0:
            
            culled_pending_mappings_ids = []
            
            for ( tag_id, hash_ids ) in pending_mappings_ids:
                
                select_statement = 'SELECT hash_id FROM ' + current_mappings_table_name + ' WHERE tag_id = ? AND hash_id = ?;'
                select_args_iterator = ( ( tag_id, hash_id ) for hash_id in hash_ids )
                
                existing_current_hash_ids = self._STS( self._ExecuteManySelect( select_statement, select_args_iterator ) )
                
                valid_hash_ids = set( hash_ids ).difference( existing_current_hash_ids )
                
                culled_pending_mappings_ids.append( ( tag_id, valid_hash_ids ) )
                
            
            pending_mappings_ids = culled_pending_mappings_ids
            
            for ( tag_id, hash_ids ) in pending_mappings_ids:
                
                self._c.executemany( 'INSERT OR IGNORE INTO ' + pending_mappings_table_name + ' VALUES ( ?, ? );', ( ( tag_id, hash_id ) for hash_id in hash_ids ) )
                
                num_pending_inserted = self._GetRowCount()
                
                change_in_num_pending_mappings += num_pending_inserted
                
                combined_files_pending_counter[ tag_id ] += num_pending_inserted
                
            
            for file_service_id in file_service_ids:
                
                self._CacheSpecificMappingsPendMappings( file_service_id, tag_service_id, pending_mappings_ids )
                
            
        
        if len( pending_rescinded_mappings_ids ) > 0:
            
            for ( tag_id, hash_ids ) in pending_rescinded_mappings_ids:
                
                self._c.executemany( 'DELETE FROM ' + pending_mappings_table_name + ' WHERE tag_id = ? AND hash_id = ?;', ( ( tag_id, hash_id ) for hash_id in hash_ids ) )
                
                num_pending_deleted = self._GetRowCount()
                
                change_in_num_pending_mappings -= num_pending_deleted
                
                combined_files_pending_counter[ tag_id ] -= num_pending_deleted
                
            
            for file_service_id in file_service_ids:
                
                self._CacheSpecificMappingsRescindPendingMappings( file_service_id, tag_service_id, pending_rescinded_mappings_ids )
                
            
        
        combined_files_seen_ids = set( ( key for ( key, value ) in list( combined_files_current_counter.items() ) if value != 0 ) )
        combined_files_seen_ids.update( ( key for ( key, value ) in list( combined_files_pending_counter.items() ) if value != 0 ) )
        
        combined_files_counts = [ ( tag_id, combined_files_current_counter[ tag_id ], combined_files_pending_counter[ tag_id ] ) for tag_id in combined_files_seen_ids ]
        
        self._CacheCombinedFilesMappingsUpdate( tag_service_id, combined_files_counts )
        
        #
        
        post_existing_tag_ids = self._STS( self._c.execute( 'SELECT tag_id as t FROM temp_tag_ids WHERE EXISTS ( SELECT 1 FROM ' + current_mappings_table_name + ' WHERE tag_id = t );' ) )
        post_existing_hash_ids = self._STS( self._c.execute( 'SELECT hash_id as h FROM temp_hash_ids WHERE EXISTS ( SELECT 1 FROM ' + current_mappings_table_name + ' WHERE hash_id = h );' ) )
        
        self._c.execute( 'DROP TABLE temp_tag_ids;' )
        self._c.execute( 'DROP TABLE temp_hash_ids;' )
        
        num_tags_removed = len( pre_existing_tag_ids.intersection( tag_ids_being_removed ).difference( post_existing_tag_ids ) )
        num_files_removed = len( pre_existing_hash_ids.intersection( hash_ids_being_removed ).difference( post_existing_hash_ids ) )
        
        change_in_num_tags -= num_tags_removed
        change_in_num_files -= num_files_removed
        
        for ( tag_id, hash_ids, reason_id ) in petitioned_mappings_ids:
            
            self._c.executemany( 'INSERT OR IGNORE INTO ' + petitioned_mappings_table_name + ' VALUES ( ?, ?, ? );', [ ( tag_id, hash_id, reason_id ) for hash_id in hash_ids ] )
            
            num_petitions_inserted = self._GetRowCount()
            
            change_in_num_petitioned_mappings += num_petitions_inserted
            
        
        for ( tag_id, hash_ids ) in petitioned_rescinded_mappings_ids:
            
            self._c.executemany( 'DELETE FROM ' + petitioned_mappings_table_name + ' WHERE tag_id = ? AND hash_id = ?;', ( ( tag_id, hash_id ) for hash_id in hash_ids ) )
            
            num_petitions_deleted = self._GetRowCount()
            
            change_in_num_petitioned_mappings -= num_petitions_deleted
            
        
        service_info_updates = []
        
        if change_in_num_mappings != 0: service_info_updates.append( ( change_in_num_mappings, tag_service_id, HC.SERVICE_INFO_NUM_MAPPINGS ) )
        if change_in_num_deleted_mappings != 0: service_info_updates.append( ( change_in_num_deleted_mappings, tag_service_id, HC.SERVICE_INFO_NUM_DELETED_MAPPINGS ) )
        if change_in_num_pending_mappings != 0: service_info_updates.append( ( change_in_num_pending_mappings, tag_service_id, HC.SERVICE_INFO_NUM_PENDING_MAPPINGS ) )
        if change_in_num_petitioned_mappings != 0: service_info_updates.append( ( change_in_num_petitioned_mappings, tag_service_id, HC.SERVICE_INFO_NUM_PETITIONED_MAPPINGS ) )
        if change_in_num_tags != 0: service_info_updates.append( ( change_in_num_tags, tag_service_id, HC.SERVICE_INFO_NUM_TAGS ) )
        if change_in_num_files != 0: service_info_updates.append( ( change_in_num_files, tag_service_id, HC.SERVICE_INFO_NUM_FILES ) )
        
        if len( service_info_updates ) > 0: self._c.executemany( 'UPDATE service_info SET info = info + ? WHERE service_id = ? AND info_type = ?;', service_info_updates )
        
    
    def _UpdateServerServices( self, admin_service_key, serverside_services, service_keys_to_access_keys, deletee_service_keys ):
        
        admin_service_id = self._GetServiceId( admin_service_key )
        
        admin_service = self._GetService( admin_service_id )
        
        admin_credentials = admin_service.GetCredentials()
        
        ( host, admin_port ) = admin_credentials.GetAddress()
        
        #
        
        current_service_keys = { service_key for ( service_key, ) in self._c.execute( 'SELECT service_key FROM services;' ) }
        
        for serverside_service in serverside_services:
            
            service_key = serverside_service.GetServiceKey()
            
            if service_key in current_service_keys:
                
                service_id = self._GetServiceId( service_key )
                
                service = self._GetService( service_id )
                
                credentials = service.GetCredentials()
                
                upnp_port = serverside_service.GetUPnPPort()
                
                if upnp_port is None:
                    
                    port = serverside_service.GetPort()
                    
                    credentials.SetAddress( host, port )
                    
                else:
                    
                    credentials.SetAddress( host, upnp_port )
                    
                
                service.SetCredentials( credentials )
                
                self._UpdateService( service )
                
            else:
                
                if service_key in service_keys_to_access_keys:
                    
                    service_type = serverside_service.GetServiceType()
                    name = serverside_service.GetName()
                    
                    service = ClientServices.GenerateService( service_key, service_type, name )
                    
                    access_key = service_keys_to_access_keys[ service_key ]
                    
                    credentials = service.GetCredentials()
                    
                    upnp_port = serverside_service.GetUPnPPort()
                    
                    if upnp_port is None:
                        
                        port = serverside_service.GetPort()
                        
                        credentials.SetAddress( host, port )
                        
                    else:
                        
                        credentials.SetAddress( host, upnp_port )
                        
                    
                    credentials.SetAccessKey( access_key )
                    
                    service.SetCredentials( credentials )
                    
                    ( service_key, service_type, name, dictionary ) = service.ToTuple()
                    
                    self._AddService( service_key, service_type, name, dictionary )
                    
                
            
        
        for service_key in deletee_service_keys:
            
            try:
                
                self._GetServiceId( service_key )
                
            except HydrusExceptions.DataMissing:
                
                continue
                
            
            self._DeleteService( service_id )
            
        
        self.pub_after_job( 'notify_unknown_accounts' )
        self.pub_after_job( 'notify_new_services_data' )
        self.pub_after_job( 'notify_new_services_gui' )
        self.pub_after_job( 'notify_new_pending' )
        
    
    def _UpdateService( self, service ):
        
        ( service_key, service_type, name, dictionary ) = service.ToTuple()
        
        service_id = self._GetServiceId( service_key )
        
        ( old_dictionary_string, ) = self._c.execute( 'SELECT dictionary_string FROM services WHERE service_id = ?;', ( service_id, ) ).fetchone()
        
        old_dictionary = HydrusSerialisable.CreateFromString( old_dictionary_string )
        
        dictionary_string = dictionary.DumpToString()
        
        self._c.execute( 'UPDATE services SET name = ?, dictionary_string = ? WHERE service_id = ?;', ( name, dictionary_string, service_id ) )
        
        if service_id in self._service_cache:
            
            del self._service_cache[ service_id ]
            
        
    
    def _UpdateServices( self, services ):
        
        self._Commit()
        
        self._c.execute( 'PRAGMA foreign_keys = ON;' )
        
        self._BeginImmediate()
        
        current_service_keys = { service_key for ( service_key, ) in self._c.execute( 'SELECT service_key FROM services;' ) }
        
        future_service_keys = { service.GetServiceKey() for service in services }
        
        for service_key in current_service_keys:
            
            if service_key not in future_service_keys:
                
                service_id = self._GetServiceId( service_key )
                
                self._DeleteService( service_id )
                
            
        
        for service in services:
            
            service_key = service.GetServiceKey()
            
            if service_key in current_service_keys:
                
                self._UpdateService( service )
                
            else:
                
                ( service_key, service_type, name, dictionary ) = service.ToTuple()
                
                self._AddService( service_key, service_type, name, dictionary )
                
            
        
        self.pub_after_job( 'notify_unknown_accounts' )
        self.pub_after_job( 'notify_new_services_data' )
        self.pub_after_job( 'notify_new_services_gui' )
        self.pub_after_job( 'notify_new_pending' )
        
        self._CloseDBCursor()
        
        self._InitDBCursor()
        
    
    def _Vacuum( self, maintenance_mode = HC.MAINTENANCE_FORCED, stop_time = None, force_vacuum = False ):
        
        new_options = self._controller.new_options
        
        existing_names_to_timestamps = dict( self._c.execute( 'SELECT name, timestamp FROM vacuum_timestamps;' ).fetchall() )
        
        db_names = [ name for ( index, name, path ) in self._c.execute( 'PRAGMA database_list;' ) if name not in ( 'mem', 'temp', 'durable_temp' ) ]
        
        if force_vacuum:
            
            due_names = db_names
            
        else:
            
            maintenance_vacuum_period_days = new_options.GetNoneableInteger( 'maintenance_vacuum_period_days' )
            
            if maintenance_vacuum_period_days is None:
                
                return
                
            
            stale_time_delta = maintenance_vacuum_period_days * 86400
            
            due_names = [ name for name in db_names if name in self._db_filenames ]
            
            due_names = [ name for name in due_names if name not in existing_names_to_timestamps or HydrusData.TimeHasPassed( existing_names_to_timestamps[ name ] + stale_time_delta ) ]
            
            SIZE_LIMIT = 1024 * 1024 * 1024
            
            due_names = [ name for name in due_names if os.path.getsize( os.path.join( self._db_dir, self._db_filenames[ name ] ) ) < SIZE_LIMIT ]
            
        
        if len( due_names ) > 0:
            
            job_key_pubbed = False
            
            job_key = ClientThreading.JobKey()
            
            job_key.SetVariable( 'popup_title', 'database maintenance - vacuum' )
            
            self._CloseDBCursor()
            
            try:
                
                time.sleep( 1 )
                
                names_done = []
                
                for name in due_names:
                    
                    if self._controller.ShouldStopThisWork( maintenance_mode, stop_time = stop_time ):
                        
                        break
                        
                    
                    try:
                        
                        db_path = os.path.join( self._db_dir, self._db_filenames[ name ] )
                        
                        try:
                            
                            HydrusDB.CheckCanVacuum( db_path )
                            
                        except Exception as e:
                            
                            if not self._have_printed_a_cannot_vacuum_message:
                                
                                HydrusData.Print( 'Cannot vacuum "{}": {}'.format( db_path, e ) )
                                
                                self._have_printed_a_cannot_vacuum_message = True
                                
                            
                            continue
                            
                        
                        if not job_key_pubbed:
                            
                            self._controller.pub( 'modal_message', job_key )
                            
                            job_key_pubbed = True
                            
                        
                        self._controller.pub( 'splash_set_status_text', 'vacuuming ' + name )
                        job_key.SetVariable( 'popup_text_1', 'vacuuming ' + name )
                        
                        started = HydrusData.GetNowPrecise()
                        
                        HydrusDB.VacuumDB( db_path )
                        
                        time_took = HydrusData.GetNowPrecise() - started
                        
                        HydrusData.Print( 'Vacuumed ' + db_path + ' in ' + HydrusData.TimeDeltaToPrettyTimeDelta( time_took ) )
                        
                        names_done.append( name )
                        
                    except Exception as e:
                        
                        HydrusData.Print( 'vacuum failed:' )
                        
                        HydrusData.ShowException( e )
                        
                        size = os.path.getsize( db_path )
                        
                        text = 'An attempt to vacuum the database failed.'
                        text += os.linesep * 2
                        text += 'For now, automatic vacuuming has been disabled. If the error is not obvious, please contact the hydrus developer.'
                        
                        HydrusData.ShowText( text )
                        
                        self._InitDBCursor()
                        
                        new_options.SetNoneableInteger( 'maintenance_vacuum_period_days', None )
                        
                        self._SaveOptions( HC.options )
                        
                        return
                        
                    
                
                job_key.SetVariable( 'popup_text_1', 'cleaning up' )
                
            finally:
                
                self._InitDBCursor()
                
                self._c.executemany( 'DELETE FROM vacuum_timestamps WHERE name = ?;', ( ( name, ) for name in names_done ) )
                
                self._c.executemany( 'INSERT OR IGNORE INTO vacuum_timestamps ( name, timestamp ) VALUES ( ?, ? );', ( ( name, HydrusData.GetNow() ) for name in names_done ) )
                
                job_key.SetVariable( 'popup_text_1', 'done!' )
                
                job_key.Finish()
                
                job_key.Delete( 10 )
                
            
        
    
    def _Write( self, action, *args, **kwargs ):
        
        result = None
        
        if action == 'analyze': self._AnalyzeDueTables( *args, **kwargs )
        elif action == 'associate_repository_update_hashes': self._AssociateRepositoryUpdateHashes( *args, **kwargs )
        elif action == 'backup': self._Backup( *args, **kwargs )
        elif action == 'clear_false_positive_relations': self._DuplicatesClearAllFalsePositiveRelationsFromHashes( *args, **kwargs )
        elif action == 'clear_false_positive_relations_between_groups': self._DuplicatesClearFalsePositiveRelationsBetweenGroupsFromHashes( *args, **kwargs )
        elif action == 'clear_orphan_file_records': self._ClearOrphanFileRecords( *args, **kwargs )
        elif action == 'clear_orphan_tables': self._ClearOrphanTables( *args, **kwargs )
        elif action == 'content_updates': self._ProcessContentUpdates( *args, **kwargs )
        elif action == 'cull_file_viewing_statistics': self._CullFileViewingStatistics( *args, **kwargs )
        elif action == 'db_integrity': self._CheckDBIntegrity( *args, **kwargs )
        elif action == 'delete_imageboard': self._DeleteYAMLDump( YAML_DUMP_ID_IMAGEBOARD, *args, **kwargs )
        elif action == 'delete_local_booru_share': self._DeleteYAMLDump( YAML_DUMP_ID_LOCAL_BOORU, *args, **kwargs )
        elif action == 'delete_pending': self._DeletePending( *args, **kwargs )
        elif action == 'delete_serialisable_named': self._DeleteJSONDumpNamed( *args, **kwargs )
        elif action == 'delete_service_info': self._DeleteServiceInfo( *args, **kwargs )
        elif action == 'delete_potential_duplicate_pairs': self._DuplicatesDeleteAllPotentialDuplicatePairs( *args, **kwargs )
        elif action == 'dirty_services': self._SaveDirtyServices( *args, **kwargs )
        elif action == 'dissolve_alternates_group': self._DuplicatesDissolveAlternatesGroupIdFromHashes( *args, **kwargs )
        elif action == 'dissolve_duplicates_group': self._DuplicatesDissolveMediaIdFromHashes( *args, **kwargs )
        elif action == 'duplicate_pair_status': self._DuplicatesSetDuplicatePairStatus( *args, **kwargs )
        elif action == 'duplicate_set_king': self._DuplicatesSetKingFromHash( *args, **kwargs )
        elif action == 'file_maintenance_add_jobs': self._FileMaintenanceAddJobs( *args, **kwargs )
        elif action == 'file_maintenance_add_jobs_hashes': self._FileMaintenanceAddJobsHashes( *args, **kwargs )
        elif action == 'file_maintenance_cancel_jobs': self._FileMaintenanceCancelJobs( *args, **kwargs )
        elif action == 'file_maintenance_clear_jobs': self._FileMaintenanceClearJobs( *args, **kwargs )
        elif action == 'imageboard': self._SetYAMLDump( YAML_DUMP_ID_IMAGEBOARD, *args, **kwargs )
        elif action == 'ideal_client_files_locations': self._SetIdealClientFilesLocations( *args, **kwargs )
        elif action == 'import_file': result = self._ImportFile( *args, **kwargs )
        elif action == 'import_update': self._ImportUpdate( *args, **kwargs )
        elif action == 'last_shutdown_work_time': self._SetLastShutdownWorkTime( *args, **kwargs )
        elif action == 'local_booru_share': self._SetYAMLDump( YAML_DUMP_ID_LOCAL_BOORU, *args, **kwargs )
        elif action == 'maintain_similar_files_search_for_potential_duplicates': self._PHashesSearchForPotentialDuplicates( *args, **kwargs )
        elif action == 'maintain_similar_files_tree': self._PHashesMaintainTree( *args, **kwargs )
        elif action == 'migration_clear_job': self._MigrationClearJob( *args, **kwargs )
        elif action == 'migration_start_mappings_job': self._MigrationStartMappingsJob( *args, **kwargs )
        elif action == 'migration_start_pairs_job': self._MigrationStartPairsJob( *args, **kwargs )
        elif action == 'process_repository_content': result = self._ProcessRepositoryContent( *args, **kwargs )
        elif action == 'process_repository_definitions': result = self._ProcessRepositoryDefinitions( *args, **kwargs )
        elif action == 'push_recent_tags': self._PushRecentTags( *args, **kwargs )
        elif action == 'regenerate_similar_files': self._PHashesRegenerateTree( *args, **kwargs )
        elif action == 'regenerate_tag_mappings_cache': self._RegenerateTagMappingsCache( *args, **kwargs )
        elif action == 'regenerate_tag_siblings_cache': self._RegenerateTagSiblingsCache( *args, **kwargs )
        elif action == 'repopulate_tag_search_cache': self._RepopulateAndUpdateTagSearchCache( *args, **kwargs )
        elif action == 'relocate_client_files': self._RelocateClientFiles( *args, **kwargs )
        elif action == 'remove_alternates_member': self._DuplicatesRemoveAlternateMemberFromHashes( *args, **kwargs )
        elif action == 'remove_duplicates_member': self._DuplicatesRemoveMediaIdMemberFromHashes( *args, **kwargs )
        elif action == 'remove_potential_pairs': self._DuplicatesRemovePotentialPairsFromHashes( *args, **kwargs )
        elif action == 'repair_client_files': self._RepairClientFiles( *args, **kwargs )
        elif action == 'reprocess_repository': self._ReprocessRepository( *args, **kwargs )
        elif action == 'reset_repository': self._ResetRepository( *args, **kwargs )
        elif action == 'reset_potential_search_status': self._PHashesResetSearchFromHashes( *args, **kwargs )
        elif action == 'save_options': self._SaveOptions( *args, **kwargs )
        elif action == 'serialisable_simple': self._SetJSONSimple( *args, **kwargs )
        elif action == 'serialisable': self._SetJSONDump( *args, **kwargs )
        elif action == 'serialisables_overwrite': self._OverwriteJSONDumps( *args, **kwargs )
        elif action == 'set_password': self._SetPassword( *args, **kwargs )
        elif action == 'schedule_repository_update_file_maintenance': self._ScheduleRepositoryUpdateFileMaintenanceFromServiceKey( *args, **kwargs )
        elif action == 'update_server_services': self._UpdateServerServices( *args, **kwargs )
        elif action == 'update_services': self._UpdateServices( *args, **kwargs )
        elif action == 'vacuum': self._Vacuum( *args, **kwargs )
        else: raise Exception( 'db received an unknown write command: ' + action )
        
        return result
        
    
    def pub_content_updates_after_commit( self, service_keys_to_content_updates ):
        
        self.pub_after_job( 'content_updates_data', service_keys_to_content_updates )
        self.pub_after_job( 'content_updates_gui', service_keys_to_content_updates )
        
    
    def pub_initial_message( self, message ):
        
        self._initial_messages.append( message )
        
    
    def pub_service_updates_after_commit( self, service_keys_to_service_updates ):
        
        self.pub_after_job( 'service_updates_data', service_keys_to_service_updates )
        self.pub_after_job( 'service_updates_gui', service_keys_to_service_updates )
        
    
    def publish_status_update( self ):
        
        self._controller.pub( 'set_status_bar_dirty' )
        
    
    def GetInitialMessages( self ):
        
        return self._initial_messages
        
    
    def RestoreBackup( self, path ):
        
        for filename in list(self._db_filenames.values()):
            
            source = os.path.join( path, filename )
            dest = os.path.join( self._db_dir, filename )
            
            if os.path.exists( source ):
                
                HydrusPaths.MirrorFile( source, dest )
                
            else:
                
                # if someone backs up with an older version that does not have as many db files as this version, we get conflict
                # don't want to delete just in case, but we will move it out the way
                
                HydrusPaths.MergeFile( dest, dest + '.old' )
                
            
            conf_files = [ 'mpv.conf' ]
            
            for conf_file in conf_files:
                
                source = os.path.join( path, conf_file )
                dest = os.path.join( self._db_dir, conf_file )
                
                if os.path.exists( source ):
                    
                    HydrusPaths.MirrorFile( source, dest )
                    
                
            
        
        client_files_source = os.path.join( path, 'client_files' )
        client_files_default = os.path.join( self._db_dir, 'client_files' )
        
        if os.path.exists( client_files_source ):
            
            HydrusPaths.MirrorTree( client_files_source, client_files_default )
            
        
    
