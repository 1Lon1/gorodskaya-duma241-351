FROM docker:27-cli AS client

FROM debian:trixie-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server python3 \
    && rm -rf /var/lib/apt/lists/* /etc/ssh/ssh_host_* \
    && install -d -m 0755 /run/sshd

COPY --from=client /usr/local/bin/docker /usr/local/bin/docker
COPY --from=client /usr/local/libexec/docker/cli-plugins/docker-compose /usr/local/libexec/docker/cli-plugins/docker-compose

ARG DEPLOY_UID=1001
ARG DOCKER_GID=104
RUN useradd --create-home --uid "$DEPLOY_UID" --shell /bin/bash duma-deploy \
    && usermod -p '*' duma-deploy \
    && groupadd -o -g "$DOCKER_GID" docker-host \
    && usermod -aG docker-host duma-deploy

COPY sshd_config /etc/ssh/sshd_config

CMD ["/usr/sbin/sshd", "-De"]
