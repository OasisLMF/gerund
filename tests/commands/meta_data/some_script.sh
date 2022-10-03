#!/usr/bin/env bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd $SCRIPTPATH

ls
echo $ONE

if [ -d "/path/to/dir" ]
then
    echo "Directory /path/to/dir exists"
else
    echo "Directory /path/to/dir does not exist"
fi

