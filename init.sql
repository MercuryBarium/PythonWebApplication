
CREATE USER "dbUSER"@"localhost" IDENTIFIED BY 'dbPWD'

CREATE DATABASE matlista CHARACTER SET = "utf8mb4";

USE matlista;

CREATE TABLE users(userid text, email text, name text, password text, verified tinyint(4), orders JSON DEFAULT "[]");
CREATE TABLE vertokens(email text, token text);
CREATE TABLE loginsessions(email text, secret text);
CREATE TABLE passwordreset(email text, secret text);

GRANT UPDATE, INSERT, SELECT ON users TO pythonhttp@localhost;
GRANT INSERT, SELECT, DELETE ON vertokens TO pythonhttp@localhost;
GRANT INSERT, SELECT, DELETE ON loginsessions TO pythonhttp@localhost;
GRANT INSERT, SELECT, DELETE ON passwordreset TO pythonhttp@localhost;
