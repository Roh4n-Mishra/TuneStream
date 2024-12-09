from flask import Flask, render_template, request

app = Flask(__name__)




@app.route("/", methods=["GET", "POST"])
def home():
    output = None
    if request.method == "POST":
        # Get the input from the form
        user_input = request.form.get("user_input")
        
        # Process the input using the Python script
        if user_input:
            output = process_input(user_input)

    # Render the template with the output (if any)
    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)
