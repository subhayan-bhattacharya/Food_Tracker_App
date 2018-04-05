create TABLE log_date(
id INTEGER primary key autoincrement,
entry_date date not NULL
);

create table food (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT    NOT NULL,
  protein       INTEGER NOT NULL,
  carbohydrates INTEGER NOT NULL,
  fat           INTEGER NOT NULL,
  calories      INTEGER NOT NULL
);

CREATE TABLE food_date(
  food_id integer NOT NULL ,
  log_date_id integer not null,
  PRIMARY KEY (food_id,log_date_id)
);

