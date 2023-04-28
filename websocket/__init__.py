from flask_socketio import SocketIO

wss = SocketIO()

from .dms import *
from .chat import *