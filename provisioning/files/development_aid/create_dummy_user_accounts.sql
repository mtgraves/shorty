-- set up flare db for dev work

insert into athena.user_table (
        username,
        lastname,
        firstname,
        email,
        phone,
        user_status
    )  values 
    (
        'sbilly99',
        'Billy',
        'Squid',
        'squid.billy@gmail.com',
        '999-999-9999',
        1
    ), 
    (
        'picklerick',
        'Sanchez',
        'Rick',
        'rick.sanchez@gmail.com',
        '888-888-8888',
        1
    ),
	(
        'Mortyyyyy',
        'Smith',
        'Morty',
        'morty.smith@gmail.com',
        '777-777-7777',
        1
    )
    
    ;