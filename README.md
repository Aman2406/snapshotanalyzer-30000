# snapshotanalyzer-30000
Demo project to manage AWS EC2 instance snapshort

## About

This project is a demo, and uses boto3 module to manage a AWS EC2 instance snapshots.

## configure

shotty uses configuration file created by the AWS ClI that is

'aws configure --profile shotty'

## Executing
"pipenv run python shotty/shotty.py <command> <sub-command> <--project=PROJECT_NAME>"
eg: pipenv run python shotty/shotty.py instances snapshots list
*command* is instances, volumes, snapshots.
*subcommand* depends on command
*Project* is optional, as it s only used for filtering using tags. If you don't use projects, it will apply on all the instances owned by the user.
