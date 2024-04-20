from flask import Flask

app = Flask(__name__)


app.config["secret_key"] = 'p26b5LZUEGuPkvekv6ZzkwInufEDyjfT'
app.config["mongo_uri"] = 'mongodb+srv://rameshbhopale2021:Ramesh@3691@cluster0.bzoxmna.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
# client = Mong
# client = MongoClient("mongodb+srv://rameshbhopale2021:Ramesh@3691@cluster0.bzoxmna.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

@app.route('/')
def hello_world():
	return 'Hello World'

# main driver function
if __name__ == '__main__':
	app.run()
