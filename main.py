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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

