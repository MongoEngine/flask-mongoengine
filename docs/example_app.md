# Example app

A simple multi file app - to help get you started.

Completely located in docker container. Require ports 8000, 27015 on host
system to be opened (for development needs).

Usage:

1. From flask-mongoengine root folder just run `docker-compose up`.
2. Wait until dependencies downloaded and containers up and running.
3. Open `http://localhost:8000/` to check the app.
4. Hit `ctrl+c` in terminal window to stop docker-compose.
5. You can use this app for live flask-mongoengine development and testing.

```{note}
Example app files located in ``example_app`` directory.
```
