from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.get_json()
    token = data['token']
    text = data['text']
    output_file = data['output_file']

    # Выполнение команды синтеза речи
    command = f'python3 synthesize.py --token "{token}" --file "{output_file}" --text "{text}"'
    subprocess.run(command, shell=True)

    # Возвращение результата
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run()
