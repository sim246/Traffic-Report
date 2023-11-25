from flask import Flask
from flask import Flask, render_template
from threading import Thread
from subscriber import connect, get_weather, get_motion_collision
global start, weather, motion_collision

app = Flask(__name__)
start = False
weather = ""
motion_collision = ""

@app.route('/')
def TraficReport():
    global start, weather, motion_collision
    conn = Thread(target=connect, args=(), daemon=False)
    if start == False:
        conn.start()
        start = True
    weather = get_weather()
    motion_collision = get_motion_collision()
    return render_template('index.html', weather=weather, motion_collision=motion_collision)
