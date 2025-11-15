import click

@click.command()
@click.version_option('0.01',prog_name='Backup Lister')
@click.option('--hostname', '-h', help='Specify hostname the SQL Server instance is running on', type=str,default='.')
@click.option('--database', '-d', help='Specify database you want to see backups for', type=str, default='master')
def main(hostname,database):
    """A simple CLI that will show all the backups taken for all the database sytems running an host"""
    click.echo("My first CLi command!")
    click.echo("hostname is {}".format(hostname))
    click.echo("database is {}".format(database))

if __name__ == '__main__':
    main()