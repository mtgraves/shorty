-- ==============================================================
-- LINK TABLE
-- ==============================================================
drop table if exists shorty.random_link_table;
CREATE TABLE shorty.random_link_table (
    id INT4 NOT NULL AUTO_INCREMENT,
    user_id INT4 NOT NULL,
    original_url VARCHAR(512) NOT NULL,
    new_url VARCHAR(512) NOT NULL,
	new_url_suffix VARCHAR(256) BINARY NOT NULL,
	date_created DATETIME,
    PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES shorty.user_table(id)
);

drop table if exists shorty.requested_link_table;
CREATE TABLE shorty.requested_link_table (
    id INT4 NOT NULL AUTO_INCREMENT,
    user_id INT4 NOT NULL,
    original_url VARCHAR(512) NOT NULL,
    new_url VARCHAR(512) NOT NULL,
	new_url_suffix VARCHAR(256) BINARY NOT NULL,
	date_created DATETIME,
    PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES shorty.user_table(id)
);
