$("#searchBtn").click(function () {
    const date = $("#query").val();
    $.ajax({
        url: "/tickers",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ date: date }),

        success: function (response) {
            console.log(response);

            $("#result").empty();
            response.tickers.forEach(t => {
                $("#result").append(`<li>${t}</li>`);
            });
        },

        error: function (err) {
            console.error("에러 발생:", err);
        }
    });
});