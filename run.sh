#!/usr/bin/env bash


downloadDockerCompose(){
     if [ ! -f "docker-compose.yml" ]; then
         wget https://raw.githubusercontent.com/sec-report/SecAutoBan/main/docker-compose.yml
     fi
}

createPassword(){
    if [ ! -f ".env" ]; then
        echo "clickhouse_password=$(uuidgen |sed 's/-//g')" > .env
    fi
}

run(){
    downloadDockerCompose
    createPassword
    docker compose up -d
}

stop(){
    docker compose down
}

update(){
    if [ -f "docker-compose.yml" ]; then
         rm docker-compose.yml
         downloadDockerCompose
    fi
    docker compose pull
}

if [ "$1" = "stop" ]
then
    stop
    exit
elif [ "$1" = "update" ]
then
    update
    exit
fi

run
