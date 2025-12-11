#!/bin/bash

#check if .env file exists

FILE=.env

if [[ test -f "$FILE" ]]
then
    echo "$FILE exists."
else
   echo "Copying the .env.example file to .env"
   cp .env.example .env
fi