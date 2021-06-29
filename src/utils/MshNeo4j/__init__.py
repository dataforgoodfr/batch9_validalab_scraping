import os
from subprocess import check_output
import pandas as pd
from py2neo import Graph, Node, Relationship
import karmahutils as kut


version_info = "v0.1"
version_type = 'moonshade library'
authors = ['Yann Girard']
contact = 'yann.girard@gmail.com'
lib_name = 'MshNeo4j'
purpose = """QoL tools for interacting and maintaining neo4j db."""


def get_graph(key, ip, user, database="validalabdev"):
    """create a Graph object connecting to the database.
    The function is there to provide space to handle connection failure"""
    try:
        return Graph('bolt://' + ip, auth=(user, key), name="validalabdev")
    except Exception as e:
        kut.display_message('can not connect to', database, 'with user', user, 'on ip', ip)
        print(e)


def cypher_command(cypher_string, user, key, in_db=None):
    command = 'cypher-shell'
    if in_db is not None:
        command += f' -d {in_db}'
    return command + f' -u {user} -p {key} "{cypher_string}"'


def execute_cypher(cypher_string, user, key, silent_mode=True, in_db=None):
    command = cypher_command(cypher_string=cypher_string, user=user, key=key, in_db=in_db)
    if not silent_mode:
        print(command)
    return check_output(command, shell=True)


def show_databases():
    show_database = execute_cypher("show databases;")
    show_array = [X.split(',') for X in show_database.decode("unicode_escape").split('\n')]
    db_printing = pd.DataFrame(data=show_array[1:], columns=show_array[0])
    print(db_printing)
    return db_printing


def backup_database(database, backup_dir="/data/backup-data/"):
    # read the backup
    content_dir = os.listdir(backup_dir)
    content_dir.sort()
    latest_dump = content_dir[-1]
    print('restoring from:', latest_dump)

    # shutdown the dev db
    shut_cypher = f"stop database {database};"
    print('shutting down database')
    execute_cypher(shut_cypher, silent_mode=False)
    print('done')

    # load data
    load_command = "neo4j-admin load --force --from=" + backup_dir + latest_dump + " --database=" + database
    print("loading through:", load_command)
    check_output(load_command, shell=True)

    # restart the dev db
    restart_cypher = f"start database {database};"
    print('restarting  database')
    execute_cypher(restart_cypher, in_db='neo4j', silent_mode=False)
    print("done")
    return show_databases()
