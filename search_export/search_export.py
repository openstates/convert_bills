import json
from django.contrib.postgres.search import SearchQuery
from utils import init_django


class WebSearchQuery(SearchQuery):
    SEARCH_TYPES = {
        "plain": "plainto_tsquery",
        "phrase": "phraseto_tsquery",
        "raw": "to_tsquery",
        "web": "websearch_to_tsquery",
    }


def vote_to_dict(v):
    return {
        "date": v.start_date,
        "identifier": v.identifier,
        "motion_text": v.motion_text,
        "result": v.result,
        "counts": [{"option": c.option, "value": c.value} for c in v.counts.all()],
        "votes": [{"option": v.option, "voter_name": v.voter_name} for v in v.votes.all()],
    }


def search_term(term, filename):
    from opencivicdata.legislative.models import Bill
    bills = Bill.objects.all().order_by("legislative_session__jurisdiction")
    bills = bills.filter(
        searchable__search_vector=WebSearchQuery(term, search_type="web", config="english")
    )
    bills = bills.select_related("legislative_session", "legislative_session__jurisdiction",
                                 "searchable")
    print(term, len(bills))
    with open("output/" + filename + ".csv", "w") as f:
        for b in bills:
            try:
                link_url = b.searchable.version_link.url
            except Exception:
                link_url = ""
            bill = {
                "state": b.legislative_session.jurisdiction.name,
                "session": b.legislative_session.name,
                "identifier": b.identifier,
                "uuid": b.id,
                "title": b.title,
                "sponsors": [s.name for s in b.sponsorships.all()],
                "actions": [{"date": a.date, "description": a.description} for a in b.actions.all()],
                "votes": [vote_to_dict(v) for v in b.votes.all()],
                "text_url": link_url,
                "text": b.searchable.raw_text,
            }
            with open(f"output/{b.id.replace('ocd-bill/', '')}.json", "w") as f:
                json.dump(bill, f)


def main():
    init_django()
    # query = "epidemic OR pandemic OR flu OR cold OR health OR influenza OR swine flu OR covid OR coronavirus"
    # # query = "flood reduce OR flood risk"
    # # search_term("flood reduce", "reduce")
    # # search_term("flood risk", "risk")
    for word in ["epidemic", "pandemic", "flu", "cold", "influenza", "swine flu", "covid", "coronavirus"]:
        search_term(word, word)


if __name__ == "__main__":
    main()
