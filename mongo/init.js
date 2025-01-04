/**
 * this file is used to initialize the database with some data
 * this file will be executed when the container is created
 * creating an admin user and app user
 * creating a database and a collection
 * inserting some data
 **/


// create a new database
db = db.getSiblingDB('admin');

// create an admin user
db.createUser({
    user: "admin",
    pwd: "root",
    roles: [ { role: "userAdminAnyDatabase" , db: "admin" }, "readWriteAnyDatabase" ]
});


// Switch to the application database
db = db.getSiblingDB('app');

// Create an application user
db.createUser({
    user: "app",
    pwd: "root",
    roles: [{ role: "readWrite", db: "app" }]
});

// Create collections
db.createCollection('users');
db.createCollection('items');
db.createCollection('reccomendations');
