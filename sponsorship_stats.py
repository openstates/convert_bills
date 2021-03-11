from openstates.data.models import BillSponsorship
from openstates.metadata import STATES_BY_NAME
import csv

out = csv.writer(open("sponsorships.csv", "w"))

for state in STATES_BY_NAME.values():
    qs = BillSponsorship.objects.filter(bill__legislative_session__jurisdiction_id=state.jurisdiction_id)
    total_sponsorships = qs.count()
    unmatched_sponsorships = qs.filter(person_id=None).count()
    distinct = qs.distinct("name").count()
    out.writerow((state.name, total_sponsorships, unmatched_sponsorships, (total_sponsorships-unmatched_sponsorships)/total_sponsorships*100, distinct))
    print(state.name)

out.close()
