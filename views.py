from flask import Blueprint, render_template

views = Blueprint(__name__,"views")

@views.route("/")  #this is to go to different types of pages url
def home():
    return render_template("index.html")  #will render the html templete to the route

