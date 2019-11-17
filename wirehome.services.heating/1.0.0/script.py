import time

_is_running = False

config = {}

def initialize():
    pass


def start():
    global _is_running
    _is_running = True



def stop():
    global _is_running
    _is_running = False



def get_debug_infomation(_):
    return {
        "is_running": _is_running
    }