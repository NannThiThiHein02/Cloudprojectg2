from flask import Flask, render_template, request
import redis

app = Flask(__name__)

def get_redis_connection():
    try:
        r = redis.Redis(
            host='redis-service',
            port=6379,
            db=0,
            socket_timeout=5,
            socket_connect_timeout=5
        )
        r.ping()  # Test the connection
        return r
    except redis.RedisError:
        # Fallback to local Redis for development
        try:
            r = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            r.ping()
            return r
        except redis.RedisError:
            return None

r = get_redis_connection()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        color = request.form.get('color', '#ff0000')
        if r:
            try:
                r.zincrby('color_votes', 1, color)
            except redis.RedisError as e:
                app.logger.error(f"Redis error: {str(e)}")

    votes = []
    if r:
        try:
            votes = r.zrange('color_votes', 0, -1, desc=True, withscores=True)
        except redis.RedisError as e:
            app.logger.error(f"Redis error: {str(e)}")

    total_votes = sum(score for _, score in votes) if votes else 0
    return render_template('index.html', votes=votes, total_votes=total_votes)

@app.route('/health')
def health():
    if r:
        try:
            r.ping()
            return 'OK', 200
        except redis.RedisError as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return 'Redis unavailable', 503
    else:
        return 'Redis unavailable', 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)