#!/bin/sh

set -e

host="$ES_HOST:$ES_PORT"
shift
cmd="$@"


until $(curl --output /dev/null --silent --head --fail "$host"); do
    printf '.'
    sleep 1
done

# First wait for ES to start...
response=$(curl $host)

until [ "$response" = "200" ]; do
    response=$(curl --write-out %{http_code} --silent --output /dev/null "$host")
    >&2 echo "Elastic Search is unavailable - sleeping"
    sleep 1
done


# next wait for ES status to turn to Green
health="$(curl -fsSL "$host/_cat/health?h=status")"
health="$(echo "$health" | sed -r 's/^[[:space:]]+|[[:space:]]+$//g')" # trim whitespace (otherwise we'll have "green ")

until [ "$health" = 'green' ]; do
    health="$(curl -fsSL "$host/_cat/health?h=status")"
    health="$(echo "$health" | sed -r 's/^[[:space:]]+|[[:space:]]+$//g')" # trim whitespace (otherwise we'll have "green ")
    >&2 echo "Elastic Search is unavailable - sleeping"
    sleep 1
done

echo "Elastic Search is ready"

# тут надо вызвать скрипты в таком порядке:
# etl/app/etl/init/make_index.sh
# etl/app/etl/init/make_index2.sh
# etl/app/etl/init/make_index3.sh

exec "$@"