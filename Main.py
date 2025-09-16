from flask import Flask, render_template


data = [
    {"Id": 1001, "Name": "Talha", "Pharmacy": "Clinton Pharmacy", "Status": "Plan Exclusion", "DOB": "2/5/1999"},
    {"Id": 1002, "Name": "Talha", "Pharmacy": "Clinton Pharmacy", "Status": "Plan Exclusion", "DOB": "2/5/1999"},
]

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("table.html", data=data)

if __name__ == '__main__':
    app.run(debug=True)
