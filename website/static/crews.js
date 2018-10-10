import * as lib from "./lib.js";

function formatDate(date) {
    let d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;

    return [year, month, day].join('-');
}

$(document).ready(function () {
    document.getElementById('date-field').value = formatDate(new Date());
    document.getElementById('search-button').addEventListener('click', lib.showFlights);
    let syncButton = $('#sync-button');
    if (sessionStorage.getItem('sync') === 'true') {
        syncButton.off('click').on('click', function() {
        syncButton.css('background', "#808080");
            alert("Synchronizing...");
        });
    } else {
        syncButton.off('click').on('click', synchronize);
    }
});

function get_server_data() {
    let req = $.get("/api/server_data", function() {
        lib.saveData(JSON.stringify(req.responseJSON));
    }).fail(function() {
        alert("Could not download data from server")
    });
}

function sendModified() {
    let csrftoken = getCookie("csrftoken");
    console.log('In send');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $.ajax({
    type: "POST",
    data: lib.modifiedToJSON(lib.parseModified(localStorage.getItem('modified_data'))),
    url: document.location.origin + `/api/modify_data`,
    success: function() {
        localStorage.setItem('modified', 'false');
        alert("Data sent successfully");
        get_server_data();
    },
    error: function(xhr) {
       alert("Could not send data");
       console.log(xhr);
    }
  });
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        let cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function synchronize() {
    sessionStorage.setItem('sync', 'true');
    console.log('Synchronize');
    let syncButton = $('#sync-button');
    syncButton.css('background', "#808080");
    syncButton.off('click').on('click', function() {
        alert("Synchronizing...");
    });

    $(document).ajaxStop(function() {
        syncButton.css('background', "#00BFFF");
        syncButton.off('click').on('click', synchronize);
        sessionStorage.setItem('sync', 'false');
    });

    if (localStorage.getItem('modified') === 'true') {
        console.log('Sending modified data');
        sendModified();
    } else {
        get_server_data();
    }
}