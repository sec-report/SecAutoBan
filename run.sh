#!/usr/bin/env zsh

createPassword(){
    if [ ! -f ".env" ]; then
        echo -n "clickhouse_password=" > .env
        echo $(uuidgen |sed 's/-//g') >> .env
    fi
}

run(){
    createPassword
    docker compose up -d
}

stop(){
    docker compose down
}

update(){
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
