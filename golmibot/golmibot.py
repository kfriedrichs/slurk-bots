import argparse
import logging
import os

import requests
import socketio

LOG = logging.getLogger(__name__)

#TODO: need to delete rooms again


class GolmiBot:
    """
    Helps set up a Golmi game within slurk.
    """
    sio = socketio.Client(logger=True)
    golmi_sio = socketio.Client(logger=True)
    task_id = None

    def __init__(self, token, user, host, port, golmi_host, golmi_port):
        self.token = token
        self.user = user

        self.uri = host
        if port is not None:
            self.uri += f":{port}"
        self.uri += "/slurk/api"
        LOG.info(f"Running golmibot on {self.uri} with token {self.token}")

        self.golmi_uri = f"{golmi_host}:{golmi_port}"
        self.golmi_uri += "/pentomino_game"

        # register all event handlers
        self.register_callbacks()

    def run(self):
        # establish a connection to the server
        self.sio.connect(
            self.uri,
            headers={"Authorization": f"Bearer {self.token}", "user": self.user},
            namespaces="/",
        )
        #TODO where to put pw?
        print(self.golmi_uri)
        self.golmi_sio.connect(
            self.golmi_uri,
            auth={"password": "GiveMeTheBigBluePasswordOnTheLeft"}
        )
        # wait until the connection with the server ends
        self.sio.wait()

    def register_callbacks(self):
        @self.sio.event
        def joined_room(data):
            self.user = data["user"]

        @self.sio.event
        def new_task_room(data):
            room_id = data["room"]
            task_id = data["task"]
            # do I need to join the room?
            if self.task_id is None or task_id == self.task_id:
                response = requests.post(
                    f"{self.uri}/users/{self.user}/rooms/{room_id}",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                if not response.ok:
                    LOG.error(f"Could not let golmi bot join room: {response.status_code}")
                    response.raise_for_status()
                LOG.debug("Golmi bot joins new task room", data)
                # get the users
                users = requests.get(
                    f"{self.uri}/rooms/{room_id}/users",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                if users.ok:
                    # create a new Golmi task room
                    # TODO: Here, Golmibot should set parameters for the Golmi
                    # game that is being created, e.g., a room_id, a game config,
                    # (once implemented on Golmi) a game goal, etc.
                    #self.golmi_sio.emit("add_game_room", {"room_id": room_id})
                    # emit to each user their Golmi connection info
                    users = users.json()
                    for user in users:
                        if user["id"] != self.user:
                            # TODO: permission_id != user_id.
                            # To get permissions of a specific user, the
                            # token is needed. The user knows their token, but
                            # golmibot does not. The user does not have API
                            # permissions so they can't query their permissions
                            # themselves.
                            # The user does not know Golmibot's user id, so they
                            # can't send the token to Golmibot for the bot to
                            # do the query.

                            # Solutions:
                            # a) 3-way conversation between bot and
                            # clients: Golmibot sends its own session id, clients
                            # send their token, Golmibot queries permissions and
                            # sends role to clients
                            # b) Kill golmibot. Update slurk code for the server
                            # to send the role. The room number can be inferred
                            # by clients from the "status" event

                            permissions = requests.get(
                                f"{self.uri}/permissions/{user['id']}",
                                headers={"Authorization": f"Bearer {self.token}"}
                            )
                            permissions = permissions.json()

                            credentials = {"room_id": room_id,
                                           "role": permissions["golmi_role"]}
                            self.sio.emit(
                                "forward_private_data",
                                {"session_id": user["session_id"], "data": credentials}
                            )

                else:
                    LOG.error(f"Could not get users in room {room_id}: {response.status_code}")


if __name__ == "__main__":
    # set up logging configuration
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(message)s")

    # create commandline parser
    parser = argparse.ArgumentParser(description="Run Golmi Bot.")

    # collect environment variables as defaults
    if "SLURK_TOKEN" in os.environ:
        token = {"default": os.environ["SLURK_TOKEN"]}
    else:
        token = {"required": True}
    if "SLURK_USER" in os.environ:
        user = {"default": os.environ["SLURK_USER"]}
    else:
        user = {"required": True}
    if "SLURK_GOLMI_PORT" in os.environ:
        golmi_port = {"default": os.environ["SLURK_GOLMI_PORT"]}
    else:
        golmi_port = {"required": True}
    host = {"default": os.environ.get("SLURK_HOST", "http://localhost")}
    port = {"default": os.environ.get("SLURK_PORT")}
    task_id = {"default": os.environ.get("GOLMI_TASK_ID")}
    golmi_host = {"default": os.environ.get("SLURK_GOLMI_URL", "http://localhost")}

    # register commandline arguments
    parser.add_argument(
        "-t", "--token", help="token for logging in as bot", **token
    )
    parser.add_argument("-u", "--user", help="user id for the bot", **user)
    parser.add_argument(
        "-c", "--host", help="full URL (protocol, hostname) of chat server", **host
    )
    parser.add_argument("-p", "--port", type=int, help="port of chat server", **port)
    parser.add_argument("--task_id", type=int, help="task to join", **task_id)
    parser.add_argument(
        "-G", "--golmi_host", help="full URL (protocol, hostname) of Golmi server, "
                                   "can be same as chat server", **golmi_host
    )
    parser.add_argument(
        "-g", "--golmi_port", type=int, help="port of Golmi server",**golmi_port
    )
    args = parser.parse_args()

    # create bot instance
    golmi_bot = GolmiBot(
        args.token, args.user, args.host, args.port, args.golmi_host, args.golmi_port
    )
    golmi_bot.task_id = args.task_id
    # connect to chat server
    golmi_bot.run()
