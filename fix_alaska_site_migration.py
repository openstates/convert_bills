from utils import init_django
from urllib.parse import urlparse, parse_qs


def convert_url(url):
    parsed = urlparse(url)
    if parsed.netloc == "www.legis.state.ak.us":
        args = parse_qs(parsed.query)
        session = args["session"][0]
        if parsed.path == "/basis/get_bill.asp":
            bill_id = args["bill"][0]
            return f'https://www.akleg.gov/basis/Bill/Detail/{session}?Root={bill_id}'
        elif parsed.path == "/basis/get_bill_text.asp":
            hsid = args["hsid"][0]
            return f"https://www.akleg.gov/basis/Bill/Text/{session}?hsid={hsid}"
        elif parsed.path == "/basis/get_documents.asp":
            if 'docid' in args:
                docid = args["docid"][0]
                return f'http://www.akleg.gov/basis/get_documents.asp?session={session}&docid={docid}'
            else:
                bill_id = args["bill"][0]
                return f'https://www.akleg.gov/basis/Bill/Detail/{session}?Root={bill_id}#tab5_4'
        elif parsed.path == "/basis/get_fulltext.asp":
            bill_id = args["bill"][0]
            return f'https://www.akleg.gov/basis/Bill/Detail/{session}?Root={bill_id}#tab1_4'
        else:
            raise Exception(parsed.path)


def update_url(obj):
    new = convert_url(obj.url)
    if new:
        print(f"{obj.url} => {new}")
    else:
        raise Exception(obj.url)


def main():
    init_django()
    from opencivicdata.legislative.models import Bill
    bills = Bill.objects.filter(from_organization__jurisdiction__name="Alaska")
    print(f"{len(bills)} alaska bills")
    for b in bills:
        for s in b.sources.all():
            update_url(s)
        for doc in b.documents.all():
            for link in doc.links.all():
                update_url(link)
        for doc in b.versions.all():
            for link in doc.links.all():
                update_url(link)


main()
