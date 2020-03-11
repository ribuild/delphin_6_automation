# Add a new user in Robo T3

Create a new database. 

Open the shell in for that database by right-clicking on the database.
In the command line write: 

```
db.createUser( { user: "myuser",
                 pwd: "mypw",
                 roles: [ { role: "readWrite", db: "mydb" }] },
               { w: "majority" , wtimeout: 5000 } 
              )
```