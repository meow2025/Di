drop table if exists user;
create table user (
    user_id integer primary key autoincrement,
    username text unique not null,
    salted_pwd text not null,
    email text unique not null
);

drop table if exists thread;
create table thread (
    thread_id integer primary key autoincrement,
    user_id integer not null,
    title text not null,
    text text not null,
    click integer not null default (0),
    reply integer not null default (0),
    pub_date integer not null,
    last_update integer not null
);

drop table if exists reply;
create table reply (
    reply_id integer primary key autoincrement,
    thread_id integer not null,
    user_id integer not null,
    text text not null,
    pub_date integer not null
);

drop table if exists tag;
create table tag (
    tag_id integer primary key autoincrement,
    tag_name text not null unique
);

drop table if exists thread_tag;
create table thread_tag (
    thread_id integer not null,
    tag_id integer not null
);

drop table if exists mark;
create table mark (
    user_id integer not null,
    thread_id integer not null,
    mark_time integer not null,
    notify integer not null
);

drop table if exists notification;
create table notification (
    user_id integer not null,
    thread_id integer not null,
    type integer not null,
    other_user_id integer not null,
    time integer not null,
    is_read integer not null default (0)
);

drop table if exists section;
create table section (
    user_id integer not null,
    thread_id integer not null,
    type integer not null,
    other_user_id integer not null,
    time integer not null,
    is_read integer not null default (0)
);