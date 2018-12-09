import boto3
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

@click.group()
def cli():
    """Shotty Manages Snapshot"""

@cli.group("snapshots")
def snapshots():
    """Command for Snapshots"""

@snapshots.command('list')
@click.option('--project', default = None,
help = "Only snapshots for project (tag project:<name>)")
def list_snapshots(project):
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
def create_snapshots(project):
    """Create snapshots for EC2 Instances"""

    instances = filters_instances(project)

    for i in instances:
        i.stop()
        for v in i.volumes.all():
            print("Creating snapshorts of {0}".format(v.id))
            v.create_snapshots(Description="created by snapshotanalyzer-30000")

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
        i.stop()
    return

@instances.command('start')
@click.option('--project', default = None,
help = "Only instances for project")
def list_instances(project):
    "start EC2 Instances"

    instances = filters_instances(project)

    for i in instances:
        print("Startting {0}...".format(i.id))
        i.start()
    return



if __name__ == '__main__':
    cli()
