import time

import docker
import pytest
import requests

from ..utils import CONTAINER_NAME, get_config, get_logs, remove_previous_container

client = docker.from_env()


def verify_container(container, response_text):
    config_data = get_config(container)
    assert config_data["host"] == "127.0.0.1"
    assert config_data["port"] == "9000"
    assert config_data["bind"] == "0.0.0.0:8080"
    logs = get_logs(container)
    assert "Checking for script in /app/prestart.sh" in logs
    assert "Running script /app/prestart.sh" in logs
    assert (
        "Running inside /app/prestart.sh, you could add migrations to this file" in logs
    )
    response = requests.get("http://127.0.0.1:8000")
    assert response.text == response_text


@pytest.mark.parametrize(
    "image,response_text",
    [
        (
            "tiangolo/meinheld-gunicorn:python3.6",
            "Hello World from a default Python 3.6 app in a Docker container, with Meinheld and Gunicorn (default)",
        ),
        (
            "tiangolo/meinheld-gunicorn:python3.6-alpine3.8",
            "Hello World from a default Python 3.6 app in a Docker container, with Meinheld and Gunicorn on Alpine (default)",
        ),
        (
            "tiangolo/meinheld-gunicorn:python3.7",
            "Hello World from a default Python 3.7 app in a Docker container, with Meinheld and Gunicorn (default)",
        ),
        (
            "tiangolo/meinheld-gunicorn:python3.7-alpine3.8",
            "Hello World from a default Python 3.7 app in a Docker container, with Meinheld and Gunicorn on Alpine (default)",
        ),
        (
            "tiangolo/meinheld-gunicorn:latest",
            "Hello World from a default Python 3.7 app in a Docker container, with Meinheld and Gunicorn (default)",
        ),
    ],
)
def test_env_bind(image, response_text):
    remove_previous_container(client)
    container = client.containers.run(
        image,
        name=CONTAINER_NAME,
        environment={"BIND": "0.0.0.0:8080", "HOST": "127.0.0.1", "PORT": "9000"},
        ports={"8080": "8000"},
        detach=True,
    )
    time.sleep(1)
    verify_container(container, response_text)
    container.stop()
    # Test that everything works after restarting too
    container.start()
    time.sleep(1)
    verify_container(container, response_text)
    container.stop()
    container.remove()
