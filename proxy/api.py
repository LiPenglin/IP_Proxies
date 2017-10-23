from flask import Flask, g
from .db import RedisClient

__all__ = ['app']

# __name__ 程序主模块或包的名字，Flask用这个参数决定程序的根目录
app = Flask(__name__)

def get_conn():
    if not hasattr(g, 'redis_client'):
        g.redis_client = RedisClient()
    return g.redis_client

@app.route('/')
def index():
    return '<h2>This is Proxy Pool System</h2>'

@app.route('/get')
def get_proxy():
    conn = get_conn()
    return conn.pop()

@app.route('/count')
def get_counts():
    conn = get_conn()
    return str(conn.queue_len)

if __name__ == '__main__':
    app.run()