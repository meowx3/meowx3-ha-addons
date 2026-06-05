from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/gps")
def gps():
    return subprocess.getoutput("gpspipe -w -n 10")

@app.get("/chrony")
def chrony():
    return subprocess.getoutput("chronyc tracking")

@app.get("/clients")
def clients():
    return subprocess.getoutput("chronyc clients")
