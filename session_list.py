import csv
from opencivicdata.legislative.models import LegislativeSession


with open("sessions.csv", "w") as f:
    of = csv.writer(f)

    for s in LegislativeSession.objects.all().order_by("jurisdiction_id", "identifier"):
        count = s.bills.count()
        if count:
            first_action_date = s.bills.order_by("billstatus__first_action_date")[
                0
            ].billstatus.first_action_date
            last_action_date = s.bills.order_by("-billstatus__latest_action_date")[
                0
            ].billstatus.latest_action_date
        else:
            last_action_date = first_action_date = ""
        of.writerow((
            s.jurisdiction.name,
            s.identifier,
            s.name,
            s.start_date,
            s.end_date,
            count,
            first_action_date,
            last_action_date,
        ))
