let searchWord = "";
let canSearch = true;
let delay = (function () {
    var timer = 0;
    return function (callback, ms, that) {
        clearTimeout(timer);
        timer = setTimeout(callback.bind(that), ms);
    };
})();

function search() {
    console.log("searching");
    while (document.getElementById("searchresults").hasChildNodes()) {
        document.getElementById("searchresults").removeChild(document.getElementById("searchresults").lastChild);
    }
    $.get("/query/" + searchWord, function (data) {
        if (data.length == 0) {
            canSearch = true;
        }
        data.forEach(d => createOption(d), () => canSearch = true);
    });
}

function createOption(d) {
    let option = document.createElement("option");
    option.value = d;
    document.getElementById("searchresults").appendChild(option);
}

$(document).ready(function () {
    $('#searchbar').keyup(function () {
        let inputText = $(this).val();
        delay(function () {
            if (canSearch) {
                canSearch = false;
                searchWord = inputText;
                search();
            }
        }, 1000);

    });
});