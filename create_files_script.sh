#!/bin/bash

DIR="$HOME/sftp_test/upload"

for i in {1..5}; do
    echo "Test file $i content" > "$DIR/file_$i.txt"
    sleep 10
done