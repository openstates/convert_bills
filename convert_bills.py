import os
import sys
import glob
import json
import functools
import django
from django.db import transaction
import dj_database_url


action_types = {
    "bill:filed": "filing",
    "bill:introduced": "introduction",
    "bill:reading:1": "reading-1",
    "bill:reading:2": "reading-2",
    "bill:reading:3": "reading-3",
    "bill:passed": "passage",
    "bill:failed": "failure",
    "bill:withdrawn": "withdrawal",
    "bill:substituted": "substitution",
    "committee:referred": "committee-referral",
    "committee:passed": "committee-passage",
    "committee:passed:favorable": "committee-passage-favorable",
    "committee:passed:unfavorable": "committee-passage-unfavorable",
    "committee:failed": "committee-failure",
    "governor:received": "executive-received",
    "governor:signed": "executive-signature",
    "governor:vetoed": "executive-veto",
    "governor:vetoed:line-item": "executive-veto-line-item",
    "amendment:introduced": "amendment-introduction",
    "amendment:passed": "amendment-passage",
    "amendment:withdrawn": "amendment-withdrawal",
    "amendment:failed": "amendment-failure",
    "amendment:tabled": "amendment-failure",
    "amendment:amended": "amendment-amended",
    "bill:veto_override:passed": "veto-override-passage",
    "bill:veto_override:failed": "veto-override-failure",
}


def abbr_to_jid(abbr):
    if abbr == "pr":
        return "ocd-jurisdiction/country:us/territory:pr/government"
    elif abbr == "dc":
        return "ocd-jurisdiction/country:us/district:dc/government"
    else:
        return f"ocd-jurisdiction/country:us/state:{abbr}/government"


def init_django():
    from django.conf import settings

    DATABASE_URL = os.environ.get("DATABASE_URL", "postgis://localhost/openstatesorg")
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
    settings.configure(
        DATABASES=DATABASES,
        INSTALLED_APPS=("opencivicdata.core", "opencivicdata.legislative"),
    )
    django.setup()


def convert_state(directory, state):
    from opencivicdata.legislative.models import Bill

    jid = abbr_to_jid(state)
    sessions = glob.glob(os.path.join(directory, state, "bills", state, "*"))
    delete = True

    for session_dir in sorted(sessions):
        # check if session is OK to import
        session = os.path.basename(session_dir)
        count = Bill.objects.filter(
            legislative_session__jurisdiction_id=jid,
            legislative_session__identifier=session,
        ).count()
        session_files = glob.glob(os.path.join(session_dir, "*/*"))
        if count:
            print(
                f"already have {count} bills for {session} in database, {len(session_files)} in JSON data"
            )
            if delete:
                count = Bill.objects.filter(
                    legislative_session__jurisdiction_id=jid,
                    legislative_session__identifier=session,
                ).delete()
            else:
                continue

        with transaction.atomic():
            print(f"importing {len(session_files)} for {session}...")
            for file in session_files:
                with open(file) as f:
                    old = json.load(f)
                    import_bill(jid, old)
            raise Exception()


def convert_classification(classification, state):
    # ca weirdness
    if 'fiscal committee' in classification:
        classification.remove('fiscal committee')
    if 'urgency' in classification:
        classification.remove('urgency')
    if 'local program' in classification:
        classification.remove('local program')
    if 'tax levy' in classification:
        classification.remove('tax levy')

    # if classification[0] in ['miscellaneous', 'jres', 'cres']:
    #     return

    if classification == ['memorial resolution'] and state == 'ar':
        classification = ['memorial']
    if classification == ['concurrent memorial resolution'] and state == 'ar':
        classification = ['concurrent memorial']
    if classification == ['joint session resolution'] and state == 'il':
        classification = ['joint resolution']
    if classification == ['legislative resolution'] and state == 'ny':
        classification = ['resolution']
    if classification == ['address'] and state == 'nh':
        classification = ['resolution']

    return classification


@functools.lru_cache(20)
def get_session(jid, session):
    from opencivicdata.legislative.models import LegislativeSession
    return LegislativeSession.objects.get(identifier=session, jurisdiction_id=jid)


@functools.lru_cache(20)
def get_chamber(jid, chamber):
    from opencivicdata.core.models import Organization
    # if state in ('ne', 'dc'):
    #     chamber = 'legislature'
    # elif chamber in ('joint', 'conference'):
    #     chamber = 'legislature'
    return Organization.objects.get(classification=chamber, jurisdiction_id=jid)


@functools.lru_cache(500)
def get_person(pid, name):
    from opencivicdata.core.models import Person
    if pid:
        try:
            return Person.objects.get(identifiers__identifier=pid)
        except Person.DoesNotExist:
            # do more?
            print("no such person", pid, name)


def import_bill(jid, old):
    from opencivicdata.legislative.models import Bill

    # not needed
    not_needed = [
        "level", "country", "_current_term", "+bill_type", "+subject", "+scraped_subjects",
        "subjects", "_type", "_term", "action_dates", "_current_session", "_all_ids",
    ]
    for f in not_needed:
        old.pop(f, None)

    billy_id = old.pop('_id')
    bill_id = old.pop("bill_id")
    chamber = old.pop("chamber")
    state = old.pop('state')
    created_at = old.pop('created_at')
    updated_at = old.pop('updated_at')
    session = old.pop("session")
    title = old.pop("title")
    classification = convert_classification(old.pop("type"), state)
    sources = old.pop("sources")
    actions = old.pop("actions")
    votes = old.pop("votes")
    documents = old.pop("documents")
    versions = old.pop("versions")
    sponsors = old.pop("sponsors")
    alternate_titles = old.pop("alternate_titles", [])
    scraped_subjects = old.pop("scraped_subjects", [])
    companions = old.pop("companions", [])

    if old.keys():
        print(old.keys())
        raise ValueError("left over keys")

    b = Bill.objects.create(
        identifier=bill_id,
        classification=classification,
        title=title,
        legislative_session=get_session(jid, session),
        from_organization=get_chamber(jid, chamber),
        subject=scraped_subjects,
        updated_at=updated_at,
        created_at=created_at,
    )
    # b.legacy_bill_mapping.create(legacy_id=billy_id)

    for title in alternate_titles:
        b.alternate_titles.create(title=title)
    for source in sources:
        source.pop('retrieved', None)
        b.sources.create(**source)
    for doc in documents:
        d, _ = b.documents.get_or_create(note=doc['name'])
        d.links.create(url=doc["url"], media_type=doc.pop("mimetype"))
    for doc in versions:
        d, _ = b.versions.get_or_create(note=doc['name'])
        d.links.create(url=doc["url"], media_type=doc.pop("mimetype"))
    for spon in sponsors:
        if spon.get('committee_id') is not None:
            entity_type = 'organization'
        elif spon.get('leg_id') is not None:
            entity_type = 'person'
        else:
            entity_type = ''
        b.sponsorships.create(
            classification=spon['type'],
            primary=(spon['type'] == 'primary'),
            name=spon['name'],
            entity_type=entity_type,
            person_id=get_person(spon.get('leg_id'), spon['name']),
        )
    for comp in companions:
        if state in ('nj', 'ny', 'mn'):
            rtype = 'companion'
        b.related_bills.create(identifier=comp['bill_id'],
                               legislative_session=comp['session'],
                               relation_type=rtype)


    # if not old['title'] and self.state == 'me':
    #     old['title'] = '(unknown)'

    # for act in old.pop('actions'):
    #     actor = act['actor']
    #     if actor.lower() in ('governor', 'mayor', 'secretary of state'):
    #         actor = 'executive'
    #     elif actor.lower() == 'house' or (actor.lower().startswith('lower (') and self.state == 'ca'):
    #         actor = 'lower'
    #     elif actor.lower() in ('senate', 'upper`') or (actor.lower().startswith('upper (') and self.state == 'ca'):
    #         actor = 'upper'
    #     elif actor in ('joint', 'other', 'Data Systems', 'Speaker', 'clerk',
    #                    'Office of the Legislative Fiscal Analyst', 'Became Law w',
    #                    'conference') or (actor.lower().startswith('legislature (') and self.state == 'ca'):
    #         actor = 'legislature'

    #     if actor in ('committee', 'sponsor') and self.state == 'pr':
    #         actor = 'legislature'

    #     # nebraska & DC
    #     if actor in ('upper','council') and self.state in ('ne', 'dc'):
    #         actor = 'legislature'

    #     if act['action']:
    #         newact = new.add_action(act['action'], act['date'][:10], chamber=actor,
    #                                 classification=[action_types[c] for c in act['type'] if c != 'other'])
    #         for re in act.get('related_entities', []):
    #             if re['type'] == 'committee':
    #                 re['type'] = 'organization'
    #             elif re['type'] == 'legislator':
    #                 re['type'] = 'person'
    #             newact.add_related_entity(re['name'], re['type'])

    # for abid in old.pop('alternate_bill_ids', []) + old.pop('+alternate_bill_ids', []):
    #     new.add_identifier(abid)

    # ext_title = old.pop('+extended_title', None)
    # if ext_title:
    #     new.add_title(ext_title, note='Extended Title')
    # official_title = old.pop('+official_title', None)
    # if official_title:
    #     new.add_title(official_title, note='Official Title')

    # to_extras = ['+status', '+final_disposition', '+volume_chapter', '+ld_number', '+referral',
    #              '+companion', '+description', '+fiscal_note_probable:',
    #              '+preintroduction_required:', '+drafter', '+category:', '+chapter',
    #              '+requester', '+transmittal_date:', '+by_request_of', '+bill_draft_number:',
    #              '+bill_lr', '+bill_url', '+rcs_num', '+fiscal_note', '+impact_clause', '+fiscal_notes',
    #              '+short_title', '+type_', '+conference_committee', 'conference_committee',
    #              '+companion_bill_ids', '+additional_information']
    # for k in to_extras:
    #     v = old.pop(k, None)
    #     if v:
    #         new.extras[k.replace('+', '')] = v

    # # votes
    # vote_no = 1
    # for vote in old.pop('votes'):
    #     vote.pop('id')
    #     vote.pop('state')
    #     vote.pop('bill_id')
    #     vote.pop('bill_chamber', None)
    #     vote.pop('+state', None)
    #     vote.pop('+country', None)
    #     vote.pop('+level', None)
    #     vote.pop('+vacant', None)
    #     vote.pop('+not_voting', None)
    #     vote.pop('+amended', None)
    #     vote.pop('+excused', None)
    #     vote.pop('+NV', None)
    #     vote.pop('+AB', None)
    #     vote.pop('+P', None)
    #     vote.pop('+V', None)
    #     vote.pop('+E', None)
    #     vote.pop('+EXC', None)
    #     vote.pop('+EMER', None)
    #     vote.pop('+present', None)
    #     vote.pop('+absent', None)
    #     vote.pop('+seconded', None)
    #     vote.pop('+moved', None)
    #     vote.pop('+vote_type', None)
    #     vote.pop('+actual_vote', None)
    #     vote.pop('+skip_votes', None)
    #     vote.pop('vote_id')
    #     vote.pop('+bill_chamber', None)
    #     vote.pop('+session', None)
    #     vote.pop('+bill_id', None)
    #     vote.pop('+bill_session', None)
    #     vote.pop('committee', None)
    #     vote.pop('committee_id', None)
    #     vtype = vote.pop('type', 'passage')

    #     if vtype == 'veto_override':
    #         vtype = ['veto-override']
    #     elif vtype == 'amendment':
    #         vtype = ['amendment-passage']
    #     elif vtype == 'other':
    #         vtype = ''
    #     else:
    #         vtype = ['bill-passage']

    #     # most states need identifiers for uniqueness, just do it everywhere
    #     identifier = vote['date'] + '-' + str(vote_no)
    #     vote_no += 1

    #     chamber = vote.pop('chamber')
    #     if chamber == 'upper' and self.state in ('ne', 'dc'):
    #         chamber = 'legislature'
    #     elif chamber == 'joint':
    #         chamber = 'legislature'

    #     newvote = VoteEvent(legislative_session=vote.pop('session'),
    #                    motion_text=vote.pop('motion'),
    #                    result='pass' if vote.pop('passed') else 'fail',
    #                    chamber=chamber,
    #                    start_date=vote.pop('date'),
    #                    classification=vtype,
    #                    bill=new,
    #                    identifier=identifier)
    #     for vt in ('yes', 'no', 'other'):
    #         newvote.set_count(vt, vote.pop(vt + '_count'))
    #         for name in vote.pop(vt + '_votes'):
    #             newvote.vote(vt, name['name'])

    #     for source in vote.pop('sources'):
    #         source.pop('retrieved', None)
    #         newvote.add_source(**source)

    #     if not newvote.sources:
    #         newvote.sources = new.sources

    #     to_extras = ['+record', '+method', 'method', '+filename', 'record', '+action',
    #                  '+location', '+rcs_num', '+type_', '+threshold', '+other_vote_detail',
    #                  '+voice_vote']
    #     for k in to_extras:
    #         v = vote.pop(k, None)
    #         if v:
    #             newvote.extras[k.replace('+', '')] = v

    #     assert not vote, vote.keys()
    #     yield newvote

    # yield new


def main():
    dirname = sys.argv[1]
    state = sys.argv[2]
    init_django()
    convert_state(dirname, state)


if __name__ == "__main__":
    main()
