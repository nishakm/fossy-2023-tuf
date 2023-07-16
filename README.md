# fossy-2023-tuf

These are instructions to get the demo presented at [FOSSY 2023](https://2023.fossy.us/) to work. My OS is Ubuntu 22.04 wthich comes with Python 3.10. Additionally, I installed Docker which you can do using [these instructions](https://docs.docker.com/engine/install/ubuntu/). This should be enough to get started, but if not, please file an issue.

## Setting up the demo

WARNING: repository-service-tuf is still a work in progress. It's possible that the source code and docker images have changed since this demo. Reach out to the project maintainers if you want to set up a production instance of the service.

### Setting up the rstuf client
```
$ git clone <this repo>
$ python3 -m venv rstuf
$ source rstuf/bin/activate
$ (rstuf) pip install repository-service-tuf # repository-service-tuf==0.3.0a1
$ rstuf -h
```

### Setting up the RSTUF service

Make sure you have generated a `root` key pair and an `online` key pair using `rstuf key generate` first. You will need the online key password when setting up the service. In the demo, I do the key-pair generation in a folder called `bootstrap` which I will reference here.
```
$ mkdir keyvault
$ cp bootstrap/online keyvault/online
$ docker swarm init
$ printf "online,<your online password>" | docker secret create SECRETS_RSTUF_ONLINE_KEY -
$ docker stack deploy -c docker-compose.yml rstuf
```
My laptop is slow and maybe yours is as well. So you may want to check the status of your services by running `docker service list`. For me, the `rstuf_rstuf-worker` spins up a little earlier than the `rstuf_postgres` service and doesn't have a chance to create the metadata table. I usually restart this service by running `docker ps` to find the running container, and then restarting it.

```
$ docker ps
CONTAINER ID   IMAGE                                                                 COMMAND                  CREATED       STATUS                 PORTS                                                                  NAMES
588ff793a96a   ghcr.io/repository-service-tuf/repository-service-tuf-worker:latest   "bash entrypoint.sh"     3 hours ago   Up 3 hours (healthy)                                                                          rstuf_rstuf-worker.1.jm7on97z8v8dn3wvu2dq4352t
dfa6259aa44e   postgres:15.1                                                         "docker-entrypoint.s…"   3 hours ago   Up 3 hours (healthy)   5432/tcp                                                               rstuf_postgres.1.m01g08aq2ec4pu58t9lldbx5r
487afd58e7fb   redis:4.0                                                             "docker-entrypoint.s…"   3 hours ago   Up 3 hours (healthy)   6379/tcp                                                               rstuf_redis.1.x90odj77z6y5jbh1ax0jy556a
7932789fea19   rabbitmq:3-management-alpine                                          "docker-entrypoint.s…"   3 hours ago   Up 3 hours (healthy)   4369/tcp, 5671-5672/tcp, 15671-15672/tcp, 15691-15692/tcp, 25672/tcp   rstuf_rabbitmq.1.proni7bbfrtcbxfclz3z5q2hf
6bfed24b128f   ghcr.io/repository-service-tuf/repository-service-tuf-api:latest      "bash entrypoint.sh"     3 hours ago   Up 3 hours                                                                                    rstuf_rstuf-api.1.tor2ezdpq4adtk5hrdxka9yln
a2a861d42fa6   python:3.10-slim-buster                                               "python -m http.serv…"   3 hours ago   Up 3 hours                                                                                    rstuf_web-server.1.odmp7gv1vfna50atq3xnk5nkk

$ docker restart 6bfed24b128f

```
Where `6bfed24b128f` is the docker container id.

### The "repo"

This is just a filesystem in which I created a file and added a line to it. This is the "target". I had to manually create the metadata for the target. You will find this in the `add_target.json` file. I needed to find the size of the file and it's blake2b-256 hash which you can do using `b2sum -l 256 myfile.txt`. This demo uses the API directly to add a target rather than using a CLI client to upload the target. Hosting the repo is just a matter of running `python -m http.server`.
