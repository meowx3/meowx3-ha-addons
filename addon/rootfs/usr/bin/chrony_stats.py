import subprocess

def get_tracking():
    return subprocess.getoutput("chronyc tracking")

def get_sources():
    return subprocess.getoutput("chronyc sources")

def get_clients():
    return subprocess.getoutput("chronyc clients"
