#!/usr/bin/env bash

downloadSelf(){
    if [ ! -f "run.sh" ]; then
        wget https://raw.githubusercontent.com/sec-report/SecAutoBan/main/run.sh -O run.sh
        chmod +x run.sh
    fi
}

downloadDockerCompose(){
    if [ ! -f "docker-compose.yml" ]; then
        wget https://raw.githubusercontent.com/sec-report/SecAutoBan/main/docker-compose.yml -O docker-compose.yml
    fi
}

createPassword(){
    if [ ! -f ".env" ]; then
        echo "mysql_password=$(uuidgen |sed 's/-//g')" > .env
    fi
}

exec() {
    if [ "$1" = "changeUserPassword" ]
    then
        docker compose exec sec-report /sec_report $1 $2 $3 $4 $5
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
    if [ -f "run.sh" ]; then
         rm run.sh
         downloadSelf
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
elif [ "$1" = "exec" ]
then
    exec $2 $3 $4 $5 $6
    exit
fi

run
