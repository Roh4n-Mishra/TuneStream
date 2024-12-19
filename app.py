from flask import Flask, render_template, request,url_for,redirect
from temp1 import out

app = Flask(__name__)



@app.route("/", methods=["GET", "POST"])
def home():
    output = None
    if request.method=="POST":
        user_input = request.form["user_input"]
        output = out(user_input)
    
    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)
