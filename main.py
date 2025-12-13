from flask import Flask, render_template, request, jsonify
from pykrx import stock
from pykrx import bond


app = Flask(__name__)

@app.route('/')
def hello():
    return render_template("index.html")


@app.route("/tickers", methods=["POST"])
def tickers():
    date = request.json.get("date")  # JS에서 전달된 날짜 받기
    data = stock.get_market_ticker_list(date)
    return jsonify({"tickers": list(data)})

if __name__ == "__main__":
    app.run(debug=True)

