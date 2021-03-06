#!/bin/bash

test=`curl -X POST http://localhost:5000/create \
    -d '{"number":"2"}' \
    -H "Content-Type: application/json" \
    -s \
| jq -r '.data.task_id'`

# get status
check=`curl http://localhost:5000/status/${test} -s | jq -r '.status'`

while [ "$check" != "SUCCESS" ]
do
  check=`curl http://localhost:5000/status/${test} -s | jq -r '.status'`
  echo $(curl http://localhost:5000/status/${test} -s)
done