from configs import *

from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
from platform import system

VERSION = "b0.0"

if __name__ == "__main__":
    if system() == "Windows": set_event_loop_policy(WindowsSelectorEventLoopPolicy())