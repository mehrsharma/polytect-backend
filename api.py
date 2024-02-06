from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World 0!'

@app.route('/input_taker', methods=['POST'])
def say_my_name():
    data = request.get_json()
    name = data.get('name', '')
    return f"Hello, {name}!"

@app.route('/hello_world_1')
def hello_world_1():
    return 'Hello, World 1!'

if __name__ == '__main__':
    app.run(debug=True)
