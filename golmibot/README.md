# Golmibot
### Work in progress!
This bot helps building connections to a Golmi server. When a user
joins the bot's room, golmibot checks their Golmi role (which is a type
of permission granted when the user token is created) and communicates
the `room_id` and Golmi role to the user. With this information,
the user client can connect to the correct Golmi room.

Golmibot is also responsible of creating a game room with the desired
settings on the Golmi server.