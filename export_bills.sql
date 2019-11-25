copy (
  select *
  from opencivicdata_bill b
  join opencivicdata_organization o on b.from_organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/bills.csv' with CSV HEADER;

copy (
  select *
  from opencivicdata_billabstract x 
  join opencivicdata_bill b ON x.bill_id = b.id
  join opencivicdata_organization o on b.from_organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/bill_abstracts.csv' with CSV HEADER;

copy (
  select *
  from opencivicdata_billtitle x 
  join opencivicdata_bill b ON x.bill_id = b.id
  join opencivicdata_organization o on b.from_organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/bill_titles.csv' with CSV HEADER;


copy (
  select *
  from opencivicdata_billaction x 
  join opencivicdata_bill b ON x.bill_id = b.id
  join opencivicdata_organization o on b.from_organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/bill_actions.csv' with CSV HEADER;

copy (
  select *
  from opencivicdata_billidentifier x 
  join opencivicdata_bill b ON x.bill_id = b.id
  join opencivicdata_organization o on b.from_organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/bill_identifiers.csv' with CSV HEADER;

copy (
  select *
  from opencivicdata_billsource x 
  join opencivicdata_bill b ON x.bill_id = b.id
  join opencivicdata_organization o on b.from_organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/bill_sources.csv' with CSV HEADER;

copy (
  select *
  from opencivicdata_billsponsorship x 
  join opencivicdata_bill b ON x.bill_id = b.id
  join opencivicdata_organization o on b.from_organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/bill_sponsorships.csv' with CSV HEADER;

copy (
  select *
  from opencivicdata_billdocument x 
  join opencivicdata_bill b ON x.bill_id = b.id
  join opencivicdata_organization o on b.from_organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/bill_documents.csv' with CSV HEADER;

copy (
  select *
  from opencivicdata_billversion x 
  join opencivicdata_bill b ON x.bill_id = b.id
  join opencivicdata_organization o on b.from_organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/bill_versions.csv' with CSV HEADER;

copy (
  select *
  from opencivicdata_billversionlink x 
  join opencivicdata_billversion bv ON x.version_id = bv.id
  join opencivicdata_bill b ON bv.bill_id = b.id
  join opencivicdata_organization o on b.from_organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/bill_version_links.csv' with CSV HEADER;

copy (
  select *
  from opencivicdata_billdocumentlink x 
  join opencivicdata_billdocument bd ON x.document_id = bd.id
  join opencivicdata_bill b ON bd.bill_id = b.id
  join opencivicdata_organization o on b.from_organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/bill_document_links.csv' with CSV HEADER;


-- votes

