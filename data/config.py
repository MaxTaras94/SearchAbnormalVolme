from environs import Env
import os


env = Env()
env.read_env()

ADMINS = env.list("ADMINS")

LOGINMT5 = env.int("LOGINMT5")
PASSMT5 = env.str("PASSMT5")
SERVERMT5 = env.str("SERVERMT5")
path_to_terminal = env.str("path_to_terminal") 
TOKEN = env.str("TOKEN")
channel_id = env.str("channel_id")
THCU_MM_1_BOT = env.str("THCU_MM_1_BOT")
api_key = env.str("api_key")
secret_key = env.str("secret_key")

DATA_DIR = os.path.dirname(__file__)
APP_DIR = os.path.dirname(DATA_DIR)

if __name__ == '__main__':
    print(DATA_DIR)
    print(APP_DIR)
