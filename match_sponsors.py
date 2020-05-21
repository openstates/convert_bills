import requests
import csv


def make_request(state, name):
    resp = requests.get(f"http://localhost:7000/legislators/?state={state}&name={name}")
    if resp.status_code == 500:
        return None
    candidates = resp.json()["data"]
    num = len(candidates)
    if num == 0:
        print("no match for", state, name)
    elif num == 1:
        return candidates[0]
    else:
        print(num, "matches")


with open("covid_sponsors_2.csv") as inf, open("output.csv", "w") as outf:
    total = matches = 0

    outcsv = csv.writer(outf)

    for line in csv.reader(inf):
        total += 1
        match = None

        int_id, sponsor_name, state, os_id, district, chamber, party = line

        if os_id:
            matches += 1

        stripped_name = sponsor_name.strip()
        # match = make_request(state, stripped_name)
        # if not match:
        #     # simple last name only attempt
        #     match = make_request(state, stripped_name.split()[-1])
        if not match:
            match = make_request(state, stripped_name.split(",")[0].strip())

        if match:
            matches += 1
            os_id = match['id']
            district = match["current_role"]["district"]
            chamber = match["current_role"]["chamber"]
            party = match['party']

        outcsv.writerow((int_id, sponsor_name, state, os_id, district, chamber, party))

    print(f"total={total}, matches={matches}, rate={matches/total}")
