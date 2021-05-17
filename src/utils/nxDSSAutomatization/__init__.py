import json
import numpy as np
import dataiku
import pandas as pd
from dataiku.scenario import Scenario
import karmahutils as kut
from dataiku.customrecipe import *
from dataiku.core.sql import SQLExecutor2

version_number = 'v1.6.1'
version_type = 'validalab-scraping'


def substitute_log_entry(log_entry, runlog, allowed_addition=True):
    if len(runlog) == 0:
        print('empty runlog, filling the new log entry')
        return [log_entry]
    return kut.substitute_entry(
        dict_list=runlog,
        new_entry=log_entry,
        criteria='clientName',
        allowed_addition=allowed_addition
    )


def get_sql_table(referential_name, project_key='DIReferential'):
    env = get_project_variables(scope='local')['env']
    project_key = dataiku.default_project_key() if not project_key or project_key == 'self' else project_key
    table_name = '_'.join([env, project_key, referential_name.lower()])
    query = 'SELECT * FROM ' + table_name
    connection = SQLExecutor2(connection='dataiku_workspace')
    return connection.query_to_df(query)


def get_project_variables(scope=None, project_key=None):
    project_key = dataiku.default_project_key() if not project_key else project_key
    project = dataiku.api_client().get_project(project_key)
    return project.get_variables()[scope] if scope else project.get_variables()


def add_project_variable(variable, key, scope='local', list_shaped=True, project_key=None, unique=False):
    project_key = dataiku.default_project_key() if not project_key else project_key
    project = dataiku.api_client().get_project(project_key)
    variables = project.get_variables()
    value = \
        kut.unique_values_as_string(array=variable, list_shaped=list_shaped, unique=unique) if type(variable) == list \
            else variable
    variables[scope][key] = value
    project.set_variables(variables)
    return variables


def flatten_sql_path(path):
    return '_'.join(path.split('_')[:-1] + [path.split('_')[-1].lower()])


# noinspection PyPep8Naming
def add_ECRM_context(variables, connection='dataiku_workspace'):
    print('adding ecrm context')
    project_name = dataiku.default_project_key()
    project = dataiku.api_client().get_project(project_name)
    local_variables = project.get_variables()['local']
    env = local_variables['env']
    executor = SQLExecutor2(connection=connection)
    sql_query_client_ecrm = "SELECT * FROM " + env + "_DIReferential_referentialECRMOperation"
    client_ecrm = executor.query_to_df(sql_query_client_ecrm)
    ecrm_info = client_ecrm[client_ecrm.clientName == variables['local']['clientName']]
    print('found', len(ecrm_info), 'relevant entries')
    variables['local']['ecrmOperations'] = {}
    for i, operation_row in ecrm_info.iterrows():
        operation_dict = operation_row.to_dict()
        operation_type = operation_dict['operationType']
        del (operation_dict['operationType'])
        variables['local']['ecrmOperations'][operation_type] = operation_dict
    return variables


def build_scenario(
        build_plan,
        filter_on='ready',
        connection='dataiku_workspace',
        ref_table='referentialclient',
        ref_project='DIReferential',
        add_ecrm_context=True,
        finish_on_client=None,
        single_client=None
        ):
    scenario = Scenario()
    if not isinstance(filter_on, list):
        filter_on = [filter_on]
    project_name = dataiku.default_project_key()
    project_key = dataiku.api_client().get_project(project_name)
    local_variables = project_key.get_variables()['local']
    env = local_variables['env']
    kut.display_message('reading client context referential')

    executor = SQLExecutor2(connection=connection)
    sql_query_referential_client = "SELECT * FROM " + '_'.join([env, ref_project, ref_table])
    client_ref = executor.query_to_df(sql_query_referential_client)
    filter_query = ' & '.join(filter_on)
    client_ref = client_ref.query(filter_query) if filter_query else client_ref
    kut.display_message('Client ready for automation  : ' + client_ref.clientName.unique())

    kut.display_message('run configuration')
    print(build_plan)

    if not pd.isnull(finish_on_client):
        finish_client = client_ref[client_ref.clientName == finish_on_client]
        if len(finish_client) == 0:
            kut.display_message(
                'finish client not found in plan ' + finish_on_client + ' is the client name valid ?')  # Example: load a DSS dataset as a Pandas dataframe
        other_clients = client_ref[client_ref.clientName != finish_on_client]
        client_ref = pd.concat([other_clients, finish_client], ignore_index=True)
    success = []
    if single_client is not None:
        requested_client = client_ref[client_ref.clientName == single_client]
        if not len(single_client):
            kut.display_message('requested single client is not found,building all allowed clients')
        else:
            client_ref = requested_client
    for index, client_row in client_ref.iterrows():
        variables = set_client_context(client_row=client_row, add_ecrm_context=add_ecrm_context, connection=connection)
        client_name = variables['local']['clientName']
        kut.display_message('starting builds on ' + client_name)

        run_scenario(table_plan=build_plan, scenario=scenario)
        success.append(client_name)
        scenario.set_global_variables(successfullRun=success)
        print('done_________________' + client_name)
    return success


def run_scenario(table_plan, scenario):
    for table in table_plan:
        if 'mode' not in table.keys():
            table['mode'] = 'RECURSIVE_BUILD'
        if 'fail_fatal' not in table.keys():
            table["fail_fatal"] = True
        scenario.build_dataset(table['name'], build_mode=table['mode'], fail_fatal=table['fail_fatal'])
    return 1


def set_client_context(client_row, project_key=None, add_ecrm_context=True, connection='dataiku_workspace'):
    kut.display_message('setting context', secondary=True)
    if not project_key:
        project_name = dataiku.default_project_key()
        project_key = dataiku.api_client().get_project(project_name)
        print('inferring project key:', project_key)
    new_vars = serialize_variables(new_vars=client_row.to_dict(), project=project_key, context='local')
    if add_ecrm_context:
        new_vars = add_ECRM_context(new_vars, connection=connection)
    project_key.set_variables(new_vars)
    variables = project_key.get_variables()
    local_variables = project_key.get_variables()['local']
    client_name = local_variables['clientName']
    print('client name:', client_name)
    print(local_variables)
    return variables


def is_json_serializable(x):
    try:
        json.dumps(x)
        return True
    except TypeError:
        return False


def serialize_project_variables(new_vars, project, context='local'):
    variables = project.get_variables()
    for var in new_vars.keys():
        new_var = new_vars[var]
        variables[context][var] = json_serialize(new_var)
    return variables


def json_serialize_dict(dictionary):
    return {json_serialize(X): json_serialize(dictionary[X]) for X in dictionary.keys()}


def json_serialize(value, silence_mode=True):
    if isinstance(value, (int, np.integer, np.int64)):
        return int(value)
    if isinstance(value, (bool, np.bool, np.bool_)):
        if not silence_mode:
            print('np.bool to serialize:', value)
        return bool(value)
    if not is_json_serializable(value):
        print('warning', value, 'is not serializable and no correction have been done')
        print(value, type(value))
    return value


##############################
# Back compatibility section #
#################################################################################################################

# noinspection PyPep8Naming
def serialize_variables(new_vars, project, context='local'):
    return serialize_project_variables(new_vars=new_vars, project=project, context=context)


print('loaded nxDSSAutomation', version_type, version_number)
