from flask import Flask
import threading

app1 = Flask(__name__)
app2 = Flask(__name__)

def run_app1():
    app1.run(port=5000)

def run_app2():
    app2.run(port=5001)

if __name__ == '__main__':
    t1 = threading.Thread(target=run_app1)
    t2 = threading.Thread(target=run_app2)
    t1.start()
    t2.start()