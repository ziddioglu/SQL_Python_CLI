import sys
import click
try:
    import pyodbc
except Exception as e:
    pyodbc = None

@click.command()
@click.version_option('0.01', prog_name='Backup Lister')
@click.option('--hostname', '-H', help='SQL Server host (use "." for localhost)', type=str, default='.', show_default=True)
@click.option('--instance', '-i', help='Instance name (leave empty for default instance)', type=str, default='', show_default=True)
@click.option('--database', '-d', help='Database you want to see backups for', type=str, default='master', show_default=True)
def main(hostname, instance, database):
    """Show backups for a given database by querying msdb.dbo.backupset / backupmediafamily"""
    if pyodbc is None:
        click.echo("pyodbc is not installed. Install with: pip install pyodbc", err=True)
        sys.exit(1)

    server = hostname if not instance else r"{}\{}".format(hostname, instance)
    # pick a reasonable ODBC driver available on the system
    drivers = pyodbc.drivers()
    if not drivers:
        click.echo("No ODBC drivers found. Install 'ODBC Driver 17 for SQL Server' or similar.", err=True)
        sys.exit(1)
    driver = next((d for d in drivers if 'ODBC Driver' in d or 'SQL Server' in d), drivers[0])

    conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE=msdb;Trusted_Connection=yes;"
    query = """
    SELECT
      b.database_name,
      b.backup_start_date,
      b.backup_finish_date,
      b.backup_size,
      CASE b.[type]
        WHEN 'D' THEN 'Full'
        WHEN 'I' THEN 'Differential'
        WHEN 'L' THEN 'Log'
      END as backup_type,
      b.is_copy_only,
      m.physical_device_name
    FROM
      dbo.backupset b
    INNER JOIN
      dbo.backupmediafamily m ON b.media_set_id = m.media_set_id
    WHERE
      b.database_name = ?
    ORDER BY
      b.backup_start_date DESC;
    """

    try:
        with pyodbc.connect(conn_str, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(query, database)
            cols = [col[0] for col in cur.description] if cur.description else []
            rows = cur.fetchall()
            # print header
            click.echo("\t".join(cols))
            for row in rows:
                # convert row -> string values safely
                click.echo("\t".join("" if v is None else str(v) for v in row))
    except pyodbc.Error as ex:
        click.echo(f"Database error: {ex}", err=True)
        sys.exit(2)
    except Exception as ex:
        click.echo(f"Unexpected error: {ex}", err=True)
        sys.exit(3)

if __name__ == '__main__':
    main()