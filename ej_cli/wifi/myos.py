import platform
import sys


PLATFORM = platform.system().lower()
ARCHITECTURE = '64' if sys.maxsize > 2**32 else '32'
