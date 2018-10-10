import * as lib from "./lib.js";

let params = (new URL(location)).searchParams;
alert(`${params.get("id")} ${params.get("day")}`);

    // let res = $.get(`/api/flight/${params.get("id")}`, function() {
    //     res = res.responseJSON;
    //     let output = `Id: ${res.id}<br>`;
    //     output += `From: ${res.airport_from}<br>`;
    //     output += `Time From:${res.time_from}<br>`;
    //     output += `To: ${res.airport_to}<br>`;
    //     output += `Time To: ${res.time_to}<br>`;
    //     output += `Day: ${res.day_from}<br>`;
    //     output += `Captain: <span id="first-name">${res.captain.first_name}</span> `;
    //     output += `<span id="last-name">${res.captain.last_name}</span><br>`;
    //     document.getElementById("content").innerHTML = output;
    //
    // }).done(function() {
    //     let res2 = $.get(`/api/get_crews/${params.get("id")}`, function () {
    //         res2 = res2.responseJSON;
    //         let output = `<select id="select">`;
    //         $.each(res2, function (index, e) {
    //             output += `<option value="${e.id}">${e.first_name} ${e.last_name}</option>`
    //         });
    //         output += `</select>`;
    //         document.getElementById("content").innerHTML += output +
    //             `<button id="button">Modify</button>`;
    //
    //         document.getElementById("button").onclick = function () {
    //             let e = document.getElementById("select");
    //             let selected = e.options[e.selectedIndex];
    //             if (selected) {
    //                 modifyCrew(params.get("id"), e.value);
    //             }
    //         };
    //     }).fail(function () {
    //         alert("could not get crews list");
    //     });
    // });



function modifyCrew(flightId, captainId) {
    if (sessionStorage.getItem('synch') !== 'true') {
        alert('Synchronizing...');
        return;
    }

    let csrftoken = getCookie("csrftoken");

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $.ajax({
    type: "POST",
    data: {"flight_id": flightId, "captain_id": captainId},
    url: document.location.origin + `/api/modify_crew`,
    success: function(data) {
        document.getElementById("first-name").innerText = data.first_name;
        document.getElementById("last-name").innerText = data.last_name;
        alert("request successful");
    },
    error: function(xhr) {
       alert("request failed");
       console.log(xhr)
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
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
