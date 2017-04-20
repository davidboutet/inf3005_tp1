create table article (
  id integer primary key,
  titre varchar(100),
  identifiant varchar(50),
  auteur varchar(100),
  date_publication text,
  paragraphe varchar(500)
);

create table users (
  id integer primary key,
  utilisateur varchar(25),
  email varchar(100),
  salt varchar(32),
  hash varchar(128),
  validated integer,
  token varchar(128)
);

create table sessions (
  id integer primary key,
  id_session varchar(32),
  utilisateur varchar(25)
);


INSERT INTO users (id, utilisateur, email, salt, hash, validated, token)
VALUES ('10000', 'correcteur', 'correcteur@correcteur.com', '91569610822d41149431c9abb41662f7', '8ff047dd86f67e85616dc491bf4d171dbd1294ff81073150bc5d8ce9e4170c43d091f539bd2b37d0331d2ee8715a85592ef7502e8150f7991427093d8b21480b', 'true', '188966850992407b88d1324ae7dcb91f');