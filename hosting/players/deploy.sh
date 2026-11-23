#!/usr/bin/env bash
# Builds the Lambda player's image, pushes it to its ECR repository and points
# the function at it. Run by a person with the league's AWS credentials, once
# the resources of hosting/players/README.md exist; an agent never runs it.
#
#   hosting/players/deploy.sh
#
# Environment (all optional):
#   AWS_REGION   eu-central-1
#   REPOSITORY   island-battles-league-player   (the ECR repository)
#   FUNCTION     island-battles-league-player   (the Lambda function)
#   ARCH         arm64, or x86_64: the function's architecture, and the runner's
#   GO_VERSION   the Go that builds the runner: by default .go-version's, which the workflows use too, for one runner build
set -euo pipefail
cd "$(dirname "$0")/../.."

region="${AWS_REGION:-eu-central-1}"
repository="${REPOSITORY:-island-battles-league-player}"
function="${FUNCTION:-island-battles-league-player}"
arch="${ARCH:-x86_64}"
go_version="${GO_VERSION:-$(cat "$(dirname "$0")/../../.go-version")}"
case "$arch" in
  arm64) platform=linux/arm64 ;;
  x86_64) platform=linux/amd64 ;;
  *) echo "ARCH is arm64 or x86_64, not $arch" >&2; exit 1 ;;
esac

account=$(aws sts get-caller-identity --query Account --output text)
registry="$account.dkr.ecr.$region.amazonaws.com"
tag="$(git rev-parse --short=12 HEAD)-$arch"
image="$registry/$repository:$tag"

aws ecr get-login-password --region "$region" | docker login --username AWS --password-stdin "$registry"
# Lambda takes a plain image manifest: no provenance attestation.
docker buildx build --platform "$platform" --provenance=false \
  --build-arg ARCH="$arch" --build-arg GO_VERSION="$go_version" \
  -f hosting/players/Dockerfile -t "$image" --push .

aws lambda update-function-code --region "$region" --function-name "$function" \
  --image-uri "$image" --architectures "$arch" > /dev/null
aws lambda wait function-updated --region "$region" --function-name "$function"
echo "$function now runs $image"
