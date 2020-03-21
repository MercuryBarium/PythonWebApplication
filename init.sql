
CREATE USER "dbUSER"@"localhost" IDENTIFIED BY 'dbPWD'

CREATE DATABASE matlista CHARACTER SET = "utf8mb4";

USE matlista;

<<<<<<< HEAD
CREATE TABLE users(userid text, email text, name text, password text, verified tinyint(4), orders JSON DEFAULT "[]");
=======
CREATE TABLE users(
    userid int NOT NULL AUTO_INCREMENT, 
    email text, 
    name text, 
    password text, 
    verified tinyint(4) DEFAULT 0, 
    orders JSON, 
    admin tinyint(4) NOT NULL DEFAULT 0, 
    primary key(userid)
);

>>>>>>> bbe3450e0c52eedcea0400ac7008dd68239332c5
CREATE TABLE vertokens(email text, token text);
CREATE TABLE loginsessions(email text, secret text);
CREATE TABLE passwordreset(email text, secret text);
CREATE TABLE menues(weeknumber int, weekday text, menu JSON);
CREATE TABLE admintokens(email text, token text);

GRANT UPDATE, INSERT, SELECT ON users TO pythonhttp@localhost;
GRANT INSERT, SELECT, DELETE ON vertokens TO pythonhttp@localhost;
GRANT INSERT, SELECT, DELETE ON loginsessions TO pythonhttp@localhost;
GRANT INSERT, SELECT, DELETE ON passwordreset TO pythonhttp@localhost;
GRANT INSERT, SELECT, UPDATE ON menues TO pythonhttp@localhost;
GRANT INSERT, SELECT, DELETE ON admintokens TO pythonhttp@localhost;
