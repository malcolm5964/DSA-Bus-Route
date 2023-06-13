from flask import Flask
from views import views

app = Flask(__name__)
app.register_blueprint(views, url_prefix="/index") #this will enable to go the the specific pages example /views/home to go to home page or in this case /index to go to index page


if __name__ == '__main__':
    app.run(debug=True, port=8000)  #to run the website in the port, debug=true is if any changes will automatically refresh and no need to rerun the script
