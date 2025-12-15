from flask import Flask, render_template, request, jsonify
from pykrx import stock
from pykrx import bond
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template("index.html")


@app.route("/tickers", methods=["POST"])
def tickers():
    date = request.json.get("date")  # JS에서 전달된 날짜 받기
    start=request.json.get("start")
    end=request.json.get("end")

    start = start.replace("-", "")
    end=end.replace("-", "")

    df = stock.get_market_ohlcv(f"{start}", f"{end}", f"{date}", adjusted=False)
    print(df.head())

    df = df[df['거래량'] > 0]
    df = df.sort_index()

    # 2) 딕셔너리 리스트로 변환
    df_reset = df.reset_index()
    df_reset['날짜'] = df_reset['날짜'].dt.strftime('%Y-%m-%d')  # 날짜 포맷
    df_json = df_reset.to_dict(orient="records")

    # 예시: 단순히 받은 날짜를 다시 반환
    return jsonify({"status": "ok", "date": df_json})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    start_date = data["start_date"]
    end_date = data["end_date"]
    ticker=data["search"]

    df = stock.get_market_ohlcv_by_date(
        fromdate=start_date.replace("-", ""),
        todate=end_date.replace("-", ""),
        ticker=ticker
    )

    if df.empty:
        return jsonify({"error": "데이터 없음"}), 400

    prices = df["종가"].values
    X = np.arange(len(prices)).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, prices)

    pred_price = model.predict([[len(prices)]])[0]

    return jsonify({
        "ticker": ticker,
        "predicted_price": int(pred_price)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

