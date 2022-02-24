# Golmibot
### Work in progress!
This bot helps building connections to a Golmi server. When a user
joins the bot's room, golmibot checks their Golmi role (which is a type
of permission granted when the user token is created) and communicates
the `room_id` and Golmi role to the user. With this information,
the user client can connect to the correct Golmi room.

Golmibot is also responsible of creating a game room with the desired
settings on the Golmi server.

# Setup
0. Download *slurk*, *slurk-bots*, and *golmi* to the same directory and navigate into the slurk directory:
```
cd slurk
```
1. Build the slurk docker image (make sure docker is running!):
```sh
docker build --tag "slurk/server" -f Dockerfile .
```
2. Set the environment variables SLURK_DOCKER, SLURK_GOLMI_PORT and SLURK_GOLMI_PORT:
```sh
export SLURK_DOCKER=slurk
export SLURK_GOLMI_URL=http://127.0.0.1
export SLURK_GOLMI_PORT=2000
```
3. Start the slurk server:
```sh
./scripts/start_server.sh
``` 
4. In a new terminal tab, navigate into the golmi directory. **! Make sure you are
using the `game` branch!** Create an environment for golmi:
```sh
cd ../golmi
conda create --name golmi python=3.9
conda activate golmi
pip install -r requirements.txt
``` 

Or, alternatively, using venv (assuming python3.9 is installed on your system):
```sh
cd ../golmi
python3.9 -m venv golmi
. golmi/bin/activate
pip install -r requirements.txt
``` 

5. Start the golmi server:
```sh
python run.py --port 2000
``` 
6. Return to your slurk terminal.
7. Create the golmi layout:
```sh
GOLMI_ROOM_LAYOUT_ID=$(scripts/create_layout.sh examples/golmi_layout.json | jq .id)
echo $GOLMI_ROOM_LAYOUT_ID
``` 
8. Create a waiting room layout and room id:
```sh
WAITING_ROOM_LAYOUT_ID=$(scripts/create_layout.sh waiting_room_layout.json | jq .id)
echo $WAITING_ROOM_LAYOUT_ID
WAITING_ROOM_ID=$(scripts/create_room.sh $WAITING_ROOM_LAYOUT_ID | jq .id)
```

9. Create a task:
```sh
TASK_LAYOUT_ID=$(scripts/create_layout.sh examples/golmi_layout.json | jq .id)
TASK_ID=$(scripts/create_task.sh  "Bot Task" 2 $TASK_LAYOUT_ID | jq .id)
```

10. Create the concierge bot user:
```sh
CONCIERGE_TOKEN=$(scripts/create_room_token.sh $WAITING_ROOM_ID concierge_bot_permissions.json | jq -r .id)
echo $CONCIERGE_TOKEN
CONCIERGE_USER=$(scripts/create_user.sh "ConciergeBot" $CONCIERGE_TOKEN | jq .id)
echo $CONCIERGE_USER
```
10. Create the golmibot user:
```sh
GOLMIBOT_TOKEN=$(scripts/create_room_token.sh $WAITING_ROOM_ID ../slurk-bots/golmibot/golmi_bot_permissions.json | jq -r .id)
echo $GOLMIBOT_TOKEN
GOLMIBOT_USER=$(scripts/create_user.sh "GolmiBot" $GOLMIBOT_TOKEN | jq .id)
echo $GOLMIBOT_USER
```

9. Create tokens for two players (here: one instruction follower, one
instruction giver):
```sh
IF_TOKEN=$(scripts/create_room_token.sh $WAITING_ROOM_ID ../slurk-bots/golmibot/golmi_if_permissions.json | jq -r .id)
echo $IF_TOKEN
IG_TOKEN=$(scripts/create_room_token.sh $WAITING_ROOM_ID ../slurk-bots/golmibot/golmi_ig_permissions.json | jq -r .id)
echo $IG_TOKEN
``` 

10. Start the bots. Copy the TOKEN und USER into a new terminal
for each bot, then start the bot. Golmibot has some python requirements.
### TODO: Change this to use docker!
```sh
CONCIERGE_TOKEN=""
CONCIERGE_USER=
cd ../slurk-bots/concierge
python concierge.py -t $CONCIERGE_TOKEN -u $CONCIERGE_USER -p 5000
```
```sh
GOLMIBOT_TOKEN=""
GOLMIBOT_USER=
cd ../slurk-bots/golmibot
python3.9 -m venv golmibot
. golmibot/bin/activate
pip install -r requirements.txt
python golmibot.py -t $GOLMIBOT_TOKEN -u $GOLMIBOT_USER -p 5000 -G http://127.0.0.1 -g 2000
```

11. Navigate to `localhost:5000` (if you are using the default host and port for
slurk) in a browser and enter a user name and IF_TOKEN.
In a private window or from another browser, repeat this step, using the IG_TOKEN.
**NOTE: Game does NOT yet work as intended. See golmibot.py for a description of the main issue.**

