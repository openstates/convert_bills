import csv
from django.contrib.postgres.search import SearchQuery
from utils import init_django


def search_term(term):
    from opencivicdata.legislative.models import Bill
    bills = Bill.objects.all().order_by("legislative_session__jurisdiction")
    bills = bills.filter(
        searchable__search_vector=SearchQuery(term, search_type="phrase", config="english")
    )
    bills = bills.select_related("legislative_session", "legislative_session__jurisdiction",
                                 "searchable")
    print(term, len(bills))
    fieldnames = ["state", "session", "identifier", "uuid", "title", "sponsors", "text_url"]
    with open("output/" + term.replace(" ", "_") + ".csv", "w") as f:
        out = csv.DictWriter(f, fieldnames)
        out.writeheader()
        for b in bills:
            try:
                link_url = b.searchable.version_link.url
            except Exception:
                link_url = ""
            out.writerow({
                "state": b.legislative_session.jurisdiction,
                "session": b.legislative_session.name,
                "identifier": b.identifier,
                "uuid": b.id,
                "title": b.title,
                "sponsors": "; ".join(s.name for s in b.sponsorships.all()),
                "text_url": link_url,
            })
            with open(b.id.replace("ocd-bill/", "output/"), "w") as tf:
                tf.write(b.searchable.raw_text)


def main():
    init_django()
    search_term("prescription drug monitoring program")
    search_term("prescription drug abuse")
    search_term("prescription analgesics")
    search_term("controlled substance")
    search_term("opiates")


if __name__ == "__main__":
    main()
