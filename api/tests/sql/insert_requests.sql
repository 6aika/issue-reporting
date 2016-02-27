INSERT INTO feedbacks (id, service_request_id, service_code, description, requested_datetime, updated_datetime, status,
                      status_notes, agency_responsible, service_name, address_string, location, title, detailed_status,
                      service_object_id, service_object_type, vote_counter, synchronized)
VALUES (1, '1982hglaqe8pdnpophff', 171, '111adsfasdf', '2015-06-23T15:50:11', '2015-07-24T12:00:44',
        'closed', 'Kiitos', '1234', 'Potholes', 'Helsinki', ST_GeomFromText('POINT(24.9364543 60.1852955)', 4326),
        'Helsingissä monesti pyöräti...', 'IN_PROCESS', '10844', 'http://www.hel.fi/servicemap/v2', 0, True),
       (2, '2981hglaqe8pdnpoiuyt', 171, '111adsfasdf', '2015-06-23T15:52:11', '2015-07-24T12:02:44',
        'closed', 'Kiitos', '1234', 'Potholes', 'Helsinki', ST_GeomFromText('POINT(24.949235 60.186585)', 4326),
        'Helsingissä monesti pyöräti...', 'IN_PROCESS', '', '', 0, True),
       (3, 'o231kdfksdfhsdfkjlf', 171, 'some testing text', '2015-06-24T15:50:11', '2015-07-25T12:00:44',
        'open', 'Kiitos', '1234', 'Potholes', 'SPb', ST_GeomFromText('POINT(24.940712 60.183301)', 4326),
        'Helsingissä monesti pyöräti...', 'IN_PROCESS', '', '', 0, True),
       (4, '9374kdfksdfhsdfasdf', 173, '111adsfasdf', '2015-06-25T15:50:11', '2015-07-25T12:00:44',
        'open', 'Kiitos', '1234', 'Potholes', 'SPb', ST_GeomFromText('POINT(24.769625 60.192005)', 4326),
        'Helsingissä monesti pyöräti...', 'IN_PROCESS', '', '', 0, True);

insert into media_urls(feedback_id, media_url) values(1, 'https://asiointi.hel.fi/palautews/rest/v1/attachment/13timm1nle0m4cvi6ocf.jpg');

insert into tasks(feedback_id, task_state, task_type, owner_name, task_modified, task_created)
values(1, 're_assigned', 'assigned', 'Rakennusvirasto', '2015-06-18T12:31:41+03:00', '2015-06-17T19:55:09+03:00'),
  (1, 'completed', 'wait_for_answer', 'Rakennusvirasto', '2015-06-18T12:32:19+03:00', '2015-06-18T12:31:41+03:00'),
  (1, 'open', 'wait_for_answer', 'Kaupunkisuunnitteluvirasto', '2015-06-18T14:12:48+03:00', '2015-06-18T14:12:48+03:00'),
  (1, 'completed', 'informed', 'Kaupunkisuunnitteluvirasto', '2015-06-18T14:59:42+03:00', '2015-06-18T14:13:02+03:00');