import csv
from django.contrib.postgres.search import SearchQuery
from utils import init_django


class WebSearchQuery(SearchQuery):
    SEARCH_TYPES = {
        "plain": "plainto_tsquery",
        "phrase": "phraseto_tsquery",
        "raw": "to_tsquery",
        "web": "websearch_to_tsquery",
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
    fieldnames = ["state", "session", "identifier", "uuid", "title", "sponsors", "text_url"]
    with open("output/" + filename + ".csv", "w") as f:
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
    query = """flood reduce OR flood risk OR flood program OR flood damage OR flood measures OR flood development OR flood mitigation OR flood fund OR flood communities OR storm reduce OR storm risk OR storm program OR storm damage OR storm measures OR storm development OR storm mitigation OR storm fund OR storm communities OR disaster reduce OR disaster risk OR disaster program OR disaster damage OR disaster measures OR disaster development OR disaster mitigation OR disaster fund OR disaster communities OR flooding reduce OR flooding risk OR flooding program OR flooding damage OR flooding measures OR flooding development OR flooding mitigation OR flooding fund OR flooding communities OR nature reduce OR nature risk OR nature program OR nature damage OR nature measures OR nature development OR nature mitigation OR nature fund OR nature communities OR natural reduce OR natural risk OR natural program OR natural damage OR natural measures OR natural development OR natural mitigation OR natural fund OR natural communities OR wetlands reduce OR wetlands risk OR wetlands program OR wetlands damage OR wetlands measures OR wetlands development OR wetlands mitigation OR wetlands fund OR wetlands communities OR storms reduce OR storms risk OR storms program OR storms damage OR storms measures OR storms development OR storms mitigation OR storms fund OR storms communities"""
    # query = "flood reduce OR flood risk"
    # search_term("flood reduce", "reduce")
    # search_term("flood risk", "risk")
    search_term(query, "disasters")


if __name__ == "__main__":
    main()
