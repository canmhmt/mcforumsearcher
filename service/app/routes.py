from flask import redirect, url_for, render_template, jsonify

def routes(app):
    @app.route("/main/welcome")
    def welcome_page():
        return render_template("app/templates/main.html")

