export class Flight {
    constructor(json: string) {
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

    id: number;
    airport_from: string;
    airport_to: string;
    day_from: string;
    day_to: string;
    time_from: string;
    time_to: string;
    captain: Captain;

    stringify(): string {
        console.log(JSON.stringify(this));
        console.log(JSON.stringify(
            {"id": this.id, "aiport_from": this.airport_from, "airport_to": this.airport_to,
            "day_from": this.day_from, "day_to": this.day_to, "time_from": this.time_from,
            "time_to": this.time_to, "captain": this.captain}));
        return JSON.stringify(
            {"id": this.id, "aiport_from": this.airport_from, "airport_to": this.airport_to,
            "day_from": this.day_from, "day_to": this.day_to, "time_from": this.time_from,
            "time_to": this.time_to, "captain": this.captain});
    }

    static stringifyArray(array: Flight[]): string {
        return JSON.stringify(array);
    }

    static stringToArray(json: string): Flight[] {
        let flights_data: any = JSON.parse(json);
        let flights: Flight[] = [];
        for (let id in flights_data) {
            if (flights_data.hasOwnProperty(id)) {
                let flight: Flight = new Flight(JSON.stringify(flights_data[id]));
                flights.push(flight);
            }
        }
        return flights;
    }
}

export class Captain {
    constructor(id: number, first_name: string, last_name: string) {
        this.id = id;
        this.first_name = first_name;
        this.last_name = last_name;
    }

    id: number;
    first_name: string;
    last_name: string;

    static stringifyArray(array: Captain[]): string {
        return JSON.stringify(array);
    }

    static stringToArray(json: string): Captain[] {
        let captains_data: any = JSON.parse(json);
        let captains: Captain[] = [];
        for (let id in captains_data) {
            if (captains_data.hasOwnProperty(id)) {
                let captain: Captain = new Captain(parseInt(id), captains_data[id].first_name, captains_data[id].last_name);
                captains.push(captain);
            }
        }
        return captains;
    }

    stringify(): string {
        return JSON.stringify({
            "id": this.id,
            "first_name": this.first_name,
            "last_name": this.last_name
        });
    }
}

export function saveData(json: string): void {
    let data: any = JSON.parse(json);
    let flights_data: any = data.flights;
    let captains_data: any = data.captains;

    for (let day in flights_data) {
        if (flights_data.hasOwnProperty(day)) {
            let flights_of_day: any = flights_data[day];
            localStorage.setItem(day, JSON.stringify(flights_of_day));
        }
    }

    for (let id in captains_data) {
        if (captains_data.hasOwnProperty(id)) {
            let c: any = captains_data[id];
            localStorage.setItem(id, JSON.stringify(c));
        }
    }
}

export function parseModified(json: string): [number, number][] {
    let data: any = JSON.parse(json);
    let result: [number, number][] = [];
    for (let flight_id in data) {
        if (data.hasOwnProperty(flight_id)) {
            let ids: any = data[flight_id];
            result.push([ids[0], ids[1]]);
        }
    }
    return result;
}

function stringifyModified(flights_captains: [number, number][]): string {
    return JSON.stringify(flights_captains);
}

export function modifiedToJSON(flights_captains: [number, number][]): any {
    let dict = {};
    for (let id in flights_captains) {
        dict[flights_captains[id][0].toString()] = flights_captains[id][1].toString();
    }
    return dict;
}

function modifyCrew(flight_id: number, captain_id: number): void {
    if (sessionStorage.getItem('sync') === 'true') {
        alert("Synchronizing...");
        return;
    }

    let flights_captains: [number, number][] = [];
    if (localStorage.getItem('modified') === 'true') {
        let modified_data: any = localStorage.getItem('modified_data');
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

export function showFlight(id: number, day: string): void {
    let flights: Flight[] = Flight.stringToArray(localStorage.getItem(day));
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


    let captain: Captain[] = Captain.stringToArray(localStorage.getItem(id.toString()));

    output = `<select id="select">`;

    $.each(captain, function (index, e) {
        output += `<option value="${e.id}">${e.first_name} ${e.last_name}</option>`
    });
    output += `</select>`;
    document.getElementById("modification").innerHTML += output +
        `<button id="modification-button">Modify</button>`;

    document.getElementById("modification-button").onclick = function () {
        let e = document.getElementById("select") as HTMLSelectElement;
        let selected = e.options[e.selectedIndex];
        if (selected) {
            modifyCrew(id, parseInt(e.value));
        }
    };
    window.scrollTo(0, document.body.scrollHeight);
}


export function showFlights(): void {
    let day: string = String($("#date-field").val());
    let flights: Flight[] = Flight.stringToArray(localStorage.getItem(day));

    let output = '<table><tr><th>From</th><th>Time From</th><th>To</th><th>Time To</th>';
    output += '<th>Captain</th>';
    output += '</tr>';
    $.each(flights, function(index, element) {
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
        showFlight(parseInt(this.id), day)
    });
}
