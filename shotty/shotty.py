import boto3
import botocore
import click
session = boto3.Session(profile_name = 'shotty')
ec2 = session.resource('ec2')

def filters_instances(project):
    instances = []
    if project:
        filters = [{'Name':'tag:Project','Values':[project]}]
        instances = ec2.instances.filter(Filter=filters)
    else:
        instances = ec2.instances.all()

    return instances

def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'

@click.group()
def cli():
    """Shotty Manages Snapshot"""

@cli.group("snapshots")
def snapshots():
    """Command for Snapshots"""

@snapshots.command('list')
@click.option('--project', default = None,
help = "Only snapshots for project (tag project:<name>)")
@click.option('--all','list_all', default=False, is_flag=True,
help = "List all snaphots from all volumes, not just the recent one")
def list_snapshots(project, list_all):
    "List EC2 snapshots"

    instances = filters_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(','.join((
                s.id,
                i.id,
                v.id,
                s.state,
                s.progress,
                s.start_time.strftime('%c')
                )))

                if s.state == "completed" and not list_all:
                    break
    return

@cli.group('volumes')
def volumes():
    '''Command for Volumes'''

@volumes.command('list')
@click.option('--project', default = None,
help = "Only Volumes for project (tag project:<name>)")
def list_volumes(project):
    "List EC2 volumes"

    instances = filters_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(",".join((
            v.id,
            i.id,
            v.state,
            str(v.size) + "GiB",
            v.encrypted and "Encrypted" or "Not Encrypted"
            )))
    return

@cli.group('instances')
def instances():
    """Commands for instances """

@instances.command('snapshot',
help = "Create Snapshots for all volumes")
@click.option('--project', default = None,
help = "Only instances for project (tag project:<name>)")
def create_snapshot(project):
    """Create snapshots for EC2 Instances"""

    instances = filters_instances(project)

    for i in instances:

        print("Stopping {0}....".format(i.id))
        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print("Skipping {0}, snapshot already in progress".format(v.id))
                continue
            print("   Creating snapshots of {0}".format(v.id))
            v.create_snapshot(Description = "created by snapshotanalyzer 30000")

        print("Starting {0}....".format(i.id))

        i.start()
        i.wait_until_running()

    print("Job Completed")
    return

@instances.command('list')
@click.option('--project', default = None,
help = "Only instances for project (tag project:<name>)")
def list_instances(project):
    "List EC2 Instances"

    instances = filters_instances(project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or []}
        print (','.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<noproject>')
            )))
    return


@instances.command('stop')
@click.option('--project', default = None,
help = "Only instances for project")
def list_instances(project):
    "Stop EC2 Instances"

    instances = filters_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not Stop {0} ".format(i.id) + str(e))
            continue
    return

@instances.command('start')
@click.option('--project', default = None,
help = "Only instances for project")
def list_instances(project):
    "start EC2 Instances"

    instances = filters_instances(project)

    for i in instances:
        print("Startting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not Stop {0} ".format(i.id) + str(e))
            continue
    return



if __name__ == '__main__':
    cli()
