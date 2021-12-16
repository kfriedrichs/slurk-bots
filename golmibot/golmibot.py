import argparse
import logging
import os

import requests
import socketio

LOG = logging.getLogger(__name__)


class GolmiBot:
    sio = socketio.Client(logger=True)
    task_id = None

    def __init__(self, token, user, host, port):
        self.token = token
        self.user = user

        self.uri = host
        if port is not None:
            self.uri += f":{port}"
        self.uri += "/slurk/api"

        LOG.info(f"Running golmibot on {self.uri} with token {self.token}")
        # register all event handlers
        self.register_callbacks()

    def run(self):
        # establish a connection to the server
        self.sio.connect(
            self.uri,
            headers={"Authorization": f"Bearer {self.token}", "user": self.user},
            namespaces="/",
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
                    # emit to each user their Golmi connection info
                    for user in users.json():
                        if user["id"] != self.user:
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
    host = {"default": os.environ.get("SLURK_HOST", "http://localhost")}
    port = {"default": os.environ.get("SLURK_PORT")}
    task_id = {"default": os.environ.get("GOLMI_TASK_ID")}

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
    args = parser.parse_args()

    # create bot instance
    golmi_bot = GolmiBot(args.token, args.user, args.host, args.port)
    golmi_bot.task_id = args.task_id
    # connect to chat server
    golmi_bot.run()
