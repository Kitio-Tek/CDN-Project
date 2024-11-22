from flask import Flask, send_file
import os

app = Flask(__name__)

origin_directory = "files"

@app.route('/<filename>')
def get_file(filename):
    file_path = os.path.join(origin_directory, filename)

    if not os.path.exists(file_path):
        return "File not found", 404

    return send_file(file_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)