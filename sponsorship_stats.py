from openstates.data.models import BillSponsorship, LegislativeSession
from openstates.metadata import STATES_BY_NAME
import csv

out = csv.writer(open("sponsorships.csv", "w"))

out.writerow(("state", "session", "total", "unmatched", "percent_matched", "distinct"))

for state in STATES_BY_NAME.values():
    session = (
        LegislativeSession.objects.filter(jurisdiction_id=state.jurisdiction_id).exclude(classification="special")
        .order_by("start_date")
        .last()
    )
    print(state.name, session)
    qs = BillSponsorship.objects.filter(bill__legislative_session=session)
    total_sponsorships = qs.count()
    unmatched_sponsorships = qs.filter(person_id=None).count()
    distinct = qs.filter(person_id=None).distinct("name").count()
    if total_sponsorships:
        percent = (
            (total_sponsorships - unmatched_sponsorships) / total_sponsorships * 100
        )
    else:
        percent = 100
    out.writerow(
        (
            state.name,
            session.name,
            total_sponsorships,
            unmatched_sponsorships,
            percent,
            distinct,
        )
    )
