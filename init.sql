
CREATE USER "pythonhttp"@"localhost" IDENTIFIED BY 'qwerty123'

CREATE DATABASE matlista CHARACTER SET = "utf8mb4";

USE matlista;

CREATE TABLE users(
    userid int NOT NULL AUTO_INCREMENT, 
    email text, 
    name text, 
    password text, 
    verified tinyint(4) DEFAULT 0, 
    admin tinyint(4) NOT NULL DEFAULT 0, 
    primary key(userid)
);

CREATE TABLE vertokens(email text, token text);
CREATE TABLE loginsessions(email text, secret text);
CREATE TABLE passwordreset(email text, secret text);
CREATE TABLE menues(year int, weeknumber int, day text, menu JSON);
CREATE TABLE admintokens(email text, token text);
CREATE TABLE orders(userid int, year int , weeknumber int, day text, foodorder JSON);

GRANT UPDATE, INSERT, SELECT ON users TO pythonhttp@localhost;
GRANT INSERT, SELECT, DELETE ON vertokens TO pythonhttp@localhost;
GRANT INSERT, SELECT, DELETE ON loginsessions TO pythonhttp@localhost;
GRANT INSERT, SELECT, DELETE ON passwordreset TO pythonhttp@localhost;
GRANT INSERT, SELECT, UPDATE ON menues TO pythonhttp@localhost;
GRANT INSERT, SELECT, DELETE ON admintokens TO pythonhttp@localhost;
GRANT UPDATE, INSERT, SELECT, DELETE ON orders TO pythonhttp@localhost;
