import csv
import glob
from collections import defaultdict


def vote_transform(state):
    # keep a list of which bills are in which session, chamber
    session_bills = defaultdict(set)
    bill_votes = dict()
    with open(f"{state}_bill_legislator_votes.csv") as f:
        leg_votes = list(csv.DictReader(f))
    with open(f"{state}_bill_votes.csv") as f:
        for v in csv.DictReader(f):
            bill_votes[v["vote_id"]] = v
            session_bills[(v["session"], v["chamber"])].add(v["vote_id"])

    for (session, chamber), vote_ids in session_bills.items():
        print(session, chamber, len(vote_ids))
        unique_legislators = set()
        votes_by_leg = defaultdict(dict)
        for lv in leg_votes:
            if lv["vote_id"] in vote_ids:
                unique_legislators.add(lv["name"])
                votes_by_leg[lv["name"]][lv["vote_id"]] = lv["vote"]

        with open(f"output/{state}_{session}_{chamber}_vote_grid.csv", "w") as f:
            fields = ["state", "session", "chamber", "legislator_name"]
            fields += list(vote_ids)
            out = csv.DictWriter(f, fields)
            out.writeheader()
            for leg in unique_legislators:
                data = {
                    "state": state,
                    "session": session,
                    "legislator_name": leg,
                    "chamber": chamber,
                }
                for vid in vote_ids:
                    data[vid] = votes_by_leg[leg].get(vid, "")
                out.writerow(data)

        with open(f"output/{state}_{session}_{chamber}_vote_detail.csv", "w") as f:
            fields = [
                "state",
                "session",
                "chamber",
                "vote_id",
                "bill_id",
                "motion",
            ]
            out = csv.DictWriter(f, fields)
            out.writeheader()

            for vote_id in vote_ids:
                out.writerow(
                    {
                        "state": state,
                        "session": session,
                        "chamber": chamber,
                        "vote_id": vote_id,
                        "bill_id": bill_votes[vote_id]["bill_id"],
                        "motion": bill_votes[vote_id]["motion"].replace("\n", " "),
                    }
                )

for file in glob.glob("*_bills.csv"):
    state = file.split("_")[0]
    vote_transform(state)
