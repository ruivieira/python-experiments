"""The wax effemeral board"""
from flask import Flask, render_template_string
from libwax import templates

app = Flask(__name__)

# @app.route('/')
# def helloIndex():
#     return 'Hello World from Python Flask!'


@app.route("/")
def template_test():
    """Return a test template"""
    return render_template_string(
        templates.TEMPLATE, my_string="Wheeeee!", my_list=[0, 1, 2, 3, 4, 5]
    )


app.run(host="0.0.0.0", port=5000)
