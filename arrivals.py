from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime, timedelta

translation = {
    "beendet":"finished",
    "gelandet": "landed",
    "im Anflug":"approach",
    "Gepäck":"baggage",
    "Check-In":"check-in",
    "gestartet": "departed",
    "geplant":"planned",
    "verspätet":"delayed"
}

def get_time(flight_number):
    flight_number = flight_number.split(" ")
    prefix = flight_number[0]
    code = flight_number[1]
    url = f"https://www.flightstats.com/v2/flight-tracker/{prefix}/{code}"
    req = Request(url, headers={"Accept-Language": "en-US;q=0.7,en;q=0.3", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0"})
    html_page = urlopen(req).read()
    soup = BeautifulSoup(html_page, 'html.parser')
    estimate = soup.find_all("div", {"class": "ticket__TicketCard-sc-1rrbl5o-7 WlxJD"})[1]
    return estimate.text.split("Estimated")[1].split(" ")[0]

def get_all_arivals(from_=datetime.now(), per_page=400):
    from_string = from_.strftime("%Y-%m-%dT%H:%M:%S")
    url = f"https://www.munich-airport.com/flightsearch/arrivals?from={from_string}&allow_scroll_back=1&per_page={per_page}&allow_pagination=1&page=0&_=1660396277000"
    req = Request(url, headers={"Accept-Language": "en-US;q=0.7,en;q=0.3", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0"})
    html_page = urlopen(req).read()
    soup = BeautifulSoup(html_page, 'html.parser')
    flights = soup.find_all("tr", {"class": "fp-flight-item"})
    flights_parsed = []
    for flight in flights:
        try:
            flight_data = {
                "flight_number" : flight.find("td", {"class": "fp-flight-number"}).text.strip(),
                "status" : translation[flight.find("td", {"class": "fp-flight-status"}).text.strip()],
                "from" : flight.find("td", {"class": "fp-flight-airport"}).text.strip(),
                "url" : "https://www.munich-airport.com" + flight.find("td", {"class": "fp-flight-number"}).a["href"]
            }
            flights_parsed.append(flight_data)
        except Exception as e:
            continue
    return flights_parsed

def get_plane_image(url):
    req = Request(url, headers={"Accept-Language": "en-US;q=0.7,en;q=0.3", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0"})
    html_page = urlopen(req).read()
    soup = BeautifulSoup(html_page, 'html.parser')
    info = soup.find("div", {"class": "detail-info"})
    return info.find("a")["href"]

def get_next_arrival():
    arrivals = get_all_arivals(from_=(datetime.now() - timedelta(hours=2)))
    earliest_time = 2400
    approaching = []
    for arrival in arrivals:
        if arrival["status"] == "approach":
            arrival["arrives_at"] = get_time(" ".join(arrival["flight_number"].split(" ")[0:2]))
            approaching.append(arrival)
    earliest_time = 99999
    ep = None
    for plane in approaching:
        if int(plane['arrives_at'].replace(":", "")) < earliest_time:
            ep = plane
            earliest_time = int(plane['arrives_at'].replace(":", ""))
    return {
        "from" : ep["from"],
        "to" : "Munich (MUC)",
        "time" : ep["arrives_at"],
        "image" : get_plane_image(ep["url"])
    }

