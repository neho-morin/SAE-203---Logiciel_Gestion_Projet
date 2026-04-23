import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_PATH = os.path.join(BASE_DIR, "nudge.db")

APP_NAME = "Nudge"
APP_VERSION = "0.1.0"
