$("#searchBtn").click(function () {
    const date = $("#date").val();
    const start=$("#start").val();
    const end=$("#end").val();
    console.log(typeof date, date);

    $.ajax({
        url: "/tickers",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ date: date, start: start, end: end }),

        success: function (response) {
            console.log(response);

            $("#resultBody").empty();
            if(!response.date || !Array.isArray(response.date) || response.date.length === 0){
                $("#resultBody").append("<tr><td>데이터 없음</td></tr>");
                return;
            }

            response.date.forEach(row => {
                $("#resultBody").append(`<tr><td>${row['날짜']}</td>
                <td>${row['종가']}</td>
                <td>${row['고가']}</td>
                <td>${row['저가']}</td>
                <td>${row['종가']}</td>
                <td>${row['거래량']}</td>
                <td>${row['거래대금']}</td>
                <td>${row['등락률']}</td>
                </tr>`);
            });
             // 거래량 데이터
            var chartData = [['날짜', '거래량']];
            response.date.forEach(row => {
                chartData.push([row['날짜'], row['거래량']]);
            });

            // 차트 그리기
            google.charts.setOnLoadCallback(function () {
                var data = google.visualization.arrayToDataTable(chartData);
                var options = {
                    title: `${date} 거래량 추세선`,
                    curveType: 'function',
                    legend: { position: 'bottom' },
                    hAxis: { title: '날짜' },
                    vAxis: { title: '거래량'},
                    pointSize: 5
                };
                var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
                chart.draw(data, options);
            });

            // 등락률 데이터
            var chartData = [['날짜', '등락률']];
            response.date.forEach(row => {
                chartData.push([row['날짜'], row['등락률']]);
            });

            //  등락률 그리기
            google.charts.setOnLoadCallback(function () {
                var data = google.visualization.arrayToDataTable(chartData);
                var options = {
                    title: `${date} 등락률 추세선`,
                    curveType: 'function',
                    legend: { position: 'bottom' },
                    hAxis: { title: '날짜' },
                    vAxis: { title: '등락률'},
                    pointSize: 5
                };
                var chart = new google.visualization.LineChart(document.getElementById('chart_div1'));
                chart.draw(data, options);
            });

        },

        error: function (err) {
            console.error("에러 발생:", err);
        }
    });
});

$("#searchBtn1").click(function () {
    const search=$("#search").val();
    const startDate=$("#start1").val();
    const endDate=$("#end1").val();


    $.ajax({
        url: "/predict",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            search: search,
            start_date: startDate,
            end_date: endDate
        }),
        success: function (res) {
//            console.log(res);
//            alert("예측 종가: " + res.predicted_price);
              $("#resultTicker").text(res.predicted_price);

              // 결과창 보이기
             $("#resultBox").show();

        },
        error: function (err) {
            console.error(err);
            alert("서버 오류");
        }
    });

});
