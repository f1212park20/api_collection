from flask import Flask, render_template, request, jsonify
from pykrx import stock
from pykrx import bond
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import date
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import psutil
import logging

logging.basicConfig(filename='server_metrics.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

def log_server_metrics(action_name=""):
    cpu = psutil.cpu_percent(interval=0)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    logging.info(f"[{action_name}] CPU:{cpu}%, Memory:{memory}%, Disk:{disk}%")

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template("index.html")

@app.route("/tickers", methods=["POST"])
def tickers():
    log_server_metrics("tickers_request")  # 조회 시 서버 상태 기록

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


# 특정 종목 예측 및 수익률 계산
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    start_date = data["start_date"]
    end_date = data["end_date"]
    ticker = data["search"]

    df = stock.get_market_ohlcv_by_date(
        fromdate=start_date.replace("-", ""),
        todate=end_date.replace("-", ""),
        ticker=ticker
    )

    if df.empty:
        return jsonify({"error": "데이터 없음"}), 400

    # 종가 데이터
    prices = df["종가"].values
    X = np.arange(len(prices)).reshape(-1, 1)

    # 선형 회귀 모델
    model = LinearRegression()
    model.fit(X, prices)
    pred_price = model.predict([[len(prices)]])[0]

    # 수익률 계산
    df['일간수익률'] = df['종가'].pct_change()
    df['누적수익률'] = (1 + df['일간수익률']).cumprod() - 1

    return jsonify({
        "ticker": ticker,
        "last_price": int(prices[-1]),
        "predicted_price": round(float(pred_price), 2),
        "latest_daily_return": round(df['일간수익률'].iloc[-1]*100, 2),
        "cumulative_return": round(df['누적수익률'].iloc[-1]*100, 2)
    })

# 관리자 페이지
@app.route('/admin')
def admin():
    today = date.today()
    today_str = today.strftime("%Y%m%d")
    print(type(today_str))

    df=stock.get_market_ohlcv(today_str)

    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace('\n', '', regex=False)

    data = df.reset_index().to_dict(orient="records")
    print(df.index.name)

    return render_template("admin.html", rows=data)


# 테스트용 벡터화 및 모델
sample_texts = ["주식 상승", "주가 폭락"]
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(sample_texts)

# 간단한 학습
model = MultinomialNB()
model.fit(X, ["긍정", "부정"])


@app.route('/news')
def index():
    return render_template("news.html")

#뉴스 예측
@app.route("/news_searh", methods=["POST"])
def news():
    log_server_metrics("tickers_request")  # 조회 시 서버 상태 기록

    data = request.get_json()
    print(data)
    query = data.get("query", "경제")  # JS에서 보낸 query 사용

    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        "X-Naver-Client-Id": "",
        "X-Naver-Client-Secret": ""
    }
    params = {
        "query": query,
        "display": 5,
        "start": 1,
        "sort": "date"
    }

    response = requests.get(url, headers=headers, params=params)
    news_items = response.json().get('items', [])
    print(news_items)

    news_list = []
    for news in news_items:
        title=news['title']
        link=news['link']
        # 벡터화 후 예측
        X_news = vectorizer.transform([title])
        prediction = model.predict(X_news)[0]
        print(prediction)

        news_list.append({
            "title": title,
            "link": link,
            "prediction": prediction
        })

    return jsonify(news_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

