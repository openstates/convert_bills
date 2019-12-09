import csv
from django.contrib.postgres.search import SearchQuery
from utils import init_django


def search_term(term):
    from opencivicdata.legislative.models import Bill
    bills = Bill.objects.all()
    bills = bills.filter(
        searchable__search_vector=SearchQuery(term, search_type="phrase")
    )
    fieldnames = ["state", "session", "identifier", "uuid", "title", "sponsors", "text_url"]
    with open("output/" + term.replace(" ", "_") + ".csv", "w") as f:
        out = csv.DictWriter(f, fieldnames)
        out.writeheader()
        for b in bills:
            out.writerow({
                "state": b.legislative_session.jurisdiction,
                "session": b.legislative_session.name,
                "identifier": b.identifier,
                "uuid": b.id,
                "title": b.title,
                "sponsors": "; ".join(s.name for s in b.sponsorships.all()),
                "text_url": b.searchable.version_link.url,
            })
            with open(b.id.replace("ocd-bill/", "output/"), "w") as tf:
                tf.write(b.searchable.raw_text)

def main():
    init_django()
    search_term("prescription drug monitoring program")


if __name__ == "__main__":
    main()
