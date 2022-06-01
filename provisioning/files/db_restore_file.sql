-- ===============================================================
-- flare initial database creation script
--
-- This should only be run by ansible (via vagrant), where
-- the flare_db_default_name gets replaced with whatever db
-- name is specified at the time of provisioning.
-- ===============================================================

drop database if exists flare_db_default_name;
create database flare_db_default_name;


-- ==============================================================
-- CATEGORY TABLE - USER STATUS
-- ==============================================================
drop table if exists flare_db_default_name.user_status_table;
create table flare_db_default_name.user_status_table (
	id INT4 NOT NULL AUTO_INCREMENT,
	status_name VARCHAR(16) NOT NULL,
	PRIMARY KEY (id)
);
-- populate roles table
insert into flare_db_default_name.user_status_table (status_name)  values
	('Requested'), -- 1 
    ('Active'), -- 2
    ('Disabled')  -- 3
;


-- ==============================================================
-- USER TABLE
-- ==============================================================
drop table if exists flare_db_default_name.user_table;
CREATE TABLE flare_db_default_name.user_table (
    id INT4 NOT NULL AUTO_INCREMENT,
    username VARCHAR(64) NOT NULL,
    lastname VARCHAR(64) NOT NULL,
    firstname VARCHAR(64) NOT NULL,
    email VARCHAR(64) NOT NULL,
    phone VARCHAR(32) NOT NULL,
    user_status INT4 NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_status) REFERENCES flare_db_default_name.user_status_table(id)
);


-- ==============================================================
-- CATEGORY TABLE - ROLES
-- ==============================================================
drop table if exists flare_db_default_name.roles_table;
create table flare_db_default_name.roles_table (
	id INT4 NOT NULL AUTO_INCREMENT,
	role_name VARCHAR(64) NOT NULL,
	PRIMARY KEY (id)
);
-- populate roles table
insert into flare_db_default_name.roles_table (role_name)  values
    ('Admin')  -- 3
;


-- ==============================================================
-- ASSOCIATION TABLE - USER ROLES
-- ==============================================================
drop table if exists flare_db_default_name.user_roles_table;
create table flare_db_default_name.user_roles_table (
	id INT4 NOT NULL AUTO_INCREMENT,
	user_id INT4 NOT NULL,
    role_id INT4 NOT NULL,
	PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES flare_db_default_name.user_table(id),
    FOREIGN KEY (role_id) REFERENCES flare_db_default_name.roles_table(id)
);
