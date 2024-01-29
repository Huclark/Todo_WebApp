from flask import Flask, render_template, url_for

# __name__ just references the file
app = Flask(__name__)

# create an index route so that when we browse to the URL we dont get error 404
@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    # debug=True so when there is an error we can get a message to debug
    app.run(debug=True)
