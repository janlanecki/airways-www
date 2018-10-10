export class Flight {
    constructor(json) {
        let data = JSON.parse(json);
        this.id = data.id;
        this.airport_from = data.airport_from;
        this.airport_to = data.airport_to;
        this.day_from = data.day_from;
        this.day_to = data.day_to;
        this.time_from = data.time_from;
        this.time_to = data.time_to;
        this.captain = new Captain(data.captain.id, data.captain.first_name, data.captain.last_name);
    }
    stringify() {
        console.log(JSON.stringify(this));
        console.log(JSON.stringify({ "id": this.id, "aiport_from": this.airport_from, "airport_to": this.airport_to,
            "day_from": this.day_from, "day_to": this.day_to, "time_from": this.time_from,
            "time_to": this.time_to, "captain": this.captain }));
        return JSON.stringify({ "id": this.id, "aiport_from": this.airport_from, "airport_to": this.airport_to,
            "day_from": this.day_from, "day_to": this.day_to, "time_from": this.time_from,
            "time_to": this.time_to, "captain": this.captain });
    }
    static stringifyArray(array) {
        return JSON.stringify(array);
    }
    static stringToArray(json) {
        let flights_data = JSON.parse(json);
        let flights = [];
        for (let id in flights_data) {
            if (flights_data.hasOwnProperty(id)) {
                let flight = new Flight(JSON.stringify(flights_data[id]));
                flights.push(flight);
            }
        }
        return flights;
    }
}
export class Captain {
    constructor(id, first_name, last_name) {
        this.id = id;
        this.first_name = first_name;
        this.last_name = last_name;
    }
    static stringifyArray(array) {
        return JSON.stringify(array);
    }
    static stringToArray(json) {
        let captains_data = JSON.parse(json);
        let captains = [];
        for (let id in captains_data) {
            if (captains_data.hasOwnProperty(id)) {
                let captain = new Captain(parseInt(id), captains_data[id].first_name, captains_data[id].last_name);
                captains.push(captain);
            }
        }
        return captains;
    }
    stringify() {
        return JSON.stringify({
            "id": this.id,
            "first_name": this.first_name,
            "last_name": this.last_name
        });
    }
}
export function saveData(json) {
    let data = JSON.parse(json);
    let flights_data = data.flights;
    let captains_data = data.captains;
    for (let day in flights_data) {
        if (flights_data.hasOwnProperty(day)) {
            let flights_of_day = flights_data[day];
            localStorage.setItem(day, JSON.stringify(flights_of_day));
        }
    }
    for (let id in captains_data) {
        if (captains_data.hasOwnProperty(id)) {
            let c = captains_data[id];
            localStorage.setItem(id, JSON.stringify(c));
        }
    }
}
export function parseModified(json) {
    let data = JSON.parse(json);
    let result = [];
    for (let flight_id in data) {
        if (data.hasOwnProperty(flight_id)) {
            let ids = data[flight_id];
            result.push([ids[0], ids[1]]);
        }
    }
    return result;
}
function stringifyModified(flights_captains) {
    return JSON.stringify(flights_captains);
}
export function modifiedToJSON(flights_captains) {
    let dict = {};
    for (let id in flights_captains) {
        dict[flights_captains[id][0].toString()] = flights_captains[id][1].toString();
    }
    return dict;
}
function modifyCrew(flight_id, captain_id) {
    if (sessionStorage.getItem('sync') === 'true') {
        alert("Synchronizing...");
        return;
    }
    let flights_captains = [];
    if (localStorage.getItem('modified') === 'true') {
        let modified_data = localStorage.getItem('modified_data');
        if (modified_data !== null) {
            flights_captains = parseModified(modified_data);
        }
    }
    for (let id in flights_captains) {
        if (flights_captains[id][0] == flight_id) {
            flights_captains.splice(parseInt(id), 1);
            break;
        }
    }
    flights_captains.push([flight_id, captain_id]);
    console.log(JSON.stringify(modifiedToJSON(flights_captains)));
    localStorage.setItem('modified_data', stringifyModified(flights_captains));
    localStorage.setItem('modified', 'true');
}
export function showFlight(id, day) {
    let flights = Flight.stringToArray(localStorage.getItem(day));
    let flight = null;
    for (let f in flights) {
        if (flights[f].id == id) {
            flight = flights[f];
            break;
        }
    }
    let output = `<h1>Modification:</h1>`;
    output += `Id: ${flight.id}<br>`;
    output += `From: ${flight.airport_from}<br>`;
    output += `Time From:${flight.time_from}<br>`;
    output += `To: ${flight.airport_to}<br>`;
    output += `Time To: ${flight.time_to}<br>`;
    output += `Day: ${flight.day_from}<br>`;
    output += `Captain: <span id="first-name">${flight.captain.first_name}</span> `;
    output += `<span id="last-name">${flight.captain.last_name}</span><br>`;
    document.getElementById("modification").innerHTML = output;
    let captain = Captain.stringToArray(localStorage.getItem(id.toString()));
    output = `<select id="select">`;
    $.each(captain, function (index, e) {
        output += `<option value="${e.id}">${e.first_name} ${e.last_name}</option>`;
    });
    output += `</select>`;
    document.getElementById("modification").innerHTML += output +
        `<button id="modification-button">Modify</button>`;
    document.getElementById("modification-button").onclick = function () {
        let e = document.getElementById("select");
        let selected = e.options[e.selectedIndex];
        if (selected) {
            modifyCrew(id, parseInt(e.value));
        }
    };
    window.scrollTo(0, document.body.scrollHeight);
}
export function showFlights() {
    let day = String($("#date-field").val());
    let flights = Flight.stringToArray(localStorage.getItem(day));
    let output = '<table><tr><th>From</th><th>Time From</th><th>To</th><th>Time To</th>';
    output += '<th>Captain</th>';
    output += '</tr>';
    $.each(flights, function (index, element) {
        output += `<tr>`;
        output += `<td>${element.airport_from}</td>`;
        output += `<td>${element.time_from}</td>`;
        output += `<td>${element.airport_to}</td>`;
        output += `<td>${element.time_to}</td>`;
        output += `<td id=${element.id}>`;
        output += `${element.captain.first_name} ${element.captain.last_name}</td>`;
        output += `<td><button type="button" class="modify-button" id="${element.id}">Modify</button>`;
        output += `</td>`;
        output += `</tr>`;
    });
    output += '</table>';
    document.getElementById('content').innerHTML = output;
    $('.modify-button').on('click', function () {
        showFlight(parseInt(this.id), day);
    });
}
