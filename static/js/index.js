$(document).ready(function () {

    // 검색 버튼 클릭 이벤트
    $("#searchBtn").click(function () {
        const date = $("#date").val();
        const start = $("#start").val();
        const end = $("#end").val();

        console.log("검색 버튼 클릭됨:", date, start, end);

        $.ajax({
            url: "/tickers",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ date: date, start: start, end: end }),
            success: function (response) {
                console.log("응답 데이터:", response);

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

            // 차트 그리기
            drawCharts(response.date, date);
            },
            error: function (err) {
                console.error("서버 오류:", err);
                alert("데이터 요청 실패");
            }
        });
    });

    function drawCharts(dataRows, dateStr) {
        if (!dataRows || dataRows.length === 0) return;

        const volumeData = [['날짜', '거래량']];
        const rateData = [['날짜', '등락률']];

        dataRows.forEach(row => {
            volumeData.push([row['날짜'], row['거래량']]);
            rateData.push([row['날짜'], row['등락률']]);
        });

        google.charts.setOnLoadCallback(function () {
            const vData = google.visualization.arrayToDataTable(volumeData);
            const vOptions = {
                title: `${dateStr} 거래량 추세선`,
                curveType: 'function',
                legend: { position: 'bottom' },
                hAxis: { title: '날짜' },
                vAxis: { title: '거래량' },
                pointSize: 5
            };
            const vChart = new google.visualization.LineChart(document.getElementById('chart_div'));
            vChart.draw(vData, vOptions);

            const rData = google.visualization.arrayToDataTable(rateData);
            const rOptions = {
                title: `${dateStr} 등락률 추세선`,
                curveType: 'function',
                legend: { position: 'bottom' },
                hAxis: { title: '날짜' },
                vAxis: { title: '등락률' },
                pointSize: 5
            };
            const rChart = new google.visualization.LineChart(document.getElementById('chart_div1'));
            rChart.draw(rData, rOptions);
        });
    }

});

//수익률 에측
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
            console.log(res);
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
