copy (
  select ve.*,
  (SELECT value FROM opencivicdata_votecount WHERE vote_event_id=ve.id AND option='yes') AS yes_count,
  (SELECT value FROM opencivicdata_votecount WHERE vote_event_id=ve.id AND option='no') AS no_count,
  (SELECT SUM(value) FROM opencivicdata_votecount WHERE vote_event_id=ve.id AND option != 'yes' AND option != 'no') AS other_count
  from opencivicdata_voteevent ve
  join opencivicdata_organization o on ve.organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/votes.csv' with CSV HEADER;

copy (SELECT pv.* 
  from opencivicdata_personvote pv
  JOIN opencivicdata_voteevent ve ON pv.vote_event_id=ve.id
  join opencivicdata_organization o on ve.organization_id=o.id 
  join opencivicdata_jurisdiction j on o.jurisdiction_id=j.id
  where j.name='North Carolina'
) to '/tmp/vote_person.csv' with CSV HEADER;
