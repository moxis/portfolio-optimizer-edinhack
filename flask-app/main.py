from geneticalgo import GA
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        stocks = request.form["list"].replace(" ", "").split(",")
        capital = float(request.form["capital"])
        ga = GA(stocks)
        result = ga.natural_selection()

        returns = ga.get_returns(result, capital)
        portfolio = ga.get_portfolio(result)
        performance = ga.get_performance(result, capital)

        return render_template("report.html", returns=returns, portfolio=portfolio, performance = performance)

    return render_template("index.html")

if __name__=='__main__':
    app.run(debug=True)
