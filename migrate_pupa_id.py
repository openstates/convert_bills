from openstates.data.models import VoteEvent
from openstates.reports.models import Identifier

OLD = 64
NEW = 111

num = Identifier.objects.filter(content_type_id=OLD).count()

# fix old
for i, ident in enumerate(Identifier.objects.filter(content_type_id=OLD).all()):
    if i % 500 == 0:
        print(f'Old Identifier {i}/{num}')
    ident.content_type_id = NEW
    if ident.content_object:
        ident.content_object.dedupe_key = ident.identifier
    ident.delete()

# fix new
num = Identifier.objects.filter(content_type_id=NEW).count()
for i, ident in enumerate(Identifier.objects.filter(content_type_id=NEW).all()):
    if i % 500 == 0:
        print(f'New Identifier {i}/{num}')
    if ident.content_object:
        ident.content_object.dedupe_key = ident.identifier
    ident.delete()
