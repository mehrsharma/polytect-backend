from flask import Flask, request

application = Flask(__name__)

@application.route('/')
def hello_world():
    return 'Hello, World 0!'

@application.route('/input_taker', methods=['POST'])
def say_my_name():
    data = request.get_json()
    name = data.get('name', '')
    return f"Hello, {name}!"

@application.route('/hello_world_1')
def hello_world_1():
    return 'Hello, World 1!'

if __name__ == '__main__':
    application.run(debug=True)
