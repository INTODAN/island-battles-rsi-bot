# syntax=docker/dockerfile:1.7
# The Lambda player (hosting/players/README.md): a container image of the
# league's tools, Go, the bots' Go modules and the headless runner built from
# runner.toml's commit. Build it from the repository's root with deploy.sh:
#
#   docker buildx build --platform linux/amd64 -f hosting/players/Dockerfile .
#
# A match's key covers the runner's build, and Go builds another runner for
# another architecture or Go version: the players serve requests from machines
# whose runner has the same hash. ARCH (Lambda's: arm64 or x86_64) and
# GO_VERSION say which.
ARG ARCH=x86_64
FROM public.ecr.aws/lambda/python:3.14-${ARCH}

ARG ARCH
ARG GO_VERSION=1.25.0

RUN dnf install -y git tar gzip && dnf clean all

RUN go_arch=$([ "$ARCH" = x86_64 ] && echo amd64 || echo "$ARCH") \
    && curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-${go_arch}.tar.gz" | tar -C /usr/local -xz
ENV PATH=/usr/local/go/bin:${PATH} \
    GOTOOLCHAIN=local \
    GOFLAGS=-mod=readonly \
    GOPATH=/opt/go \
    GOMODCACHE=/opt/go/pkg/mod

COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /usr/local/bin/uv

WORKDIR ${LAMBDA_TASK_ROOT}

# The league's tools and their dependencies (boto3 too: the store's extra), without the dev tools.
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --extra store --no-emit-project --no-hashes -o /tmp/requirements.txt \
    && uv pip install --python /var/lang/bin/python --target "${LAMBDA_TASK_ROOT}" -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# The one Go module of every bot, and the game's commit. No bot's code: a player builds only code from the store.
COPY go.mod go.sum runner.toml ./
COPY league_tools ./league_tools
COPY hosting/players/lambda_player.py ./

# The SDK and the standard packages a bot may import, compiled once with a
# bot's flags (a player builds bots without cgo) into a build cache that each
# cold start copies to /tmp.
RUN go mod download \
    && CGO_ENABLED=0 GOCACHE=/opt/go-cache go build -trimpath \
        cmp container/heap container/list context encoding/json errors fmt iter math math/bits slices sort \
        strconv strings unicode unicode/utf8 github.com/INTODAN/island-battles-go/clients/island-battles-go/... \
    && chmod -R a+rX /opt/go /opt/go-cache

# The runner, built from runner.toml's commit as every machine of the league builds it.
RUN LEAGUE_SHARED=/opt/league /var/lang/bin/python3 -c "from league_tools import engine; print(engine.build().binary)" \
        > /tmp/runner \
    && cp "$(cat /tmp/runner)" /opt/league/headless-match \
    && rm -rf /opt/league/.runner /tmp/runner

# What a Lambda may write is /tmp alone.
ENV LEAGUE_RUNNER_BINARY=/opt/league/headless-match \
    LEAGUE_SHARED=/tmp/league \
    GOCACHE=/tmp/go-cache \
    HOME=/tmp \
    LEAGUE_PLAYER_ID=lambda

CMD ["lambda_player.handler"]
