export PATH="$PATH:$HOME/go/bin"
. "$HOME/.cargo/env"


# Colima Docker socket
export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"
export TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock
