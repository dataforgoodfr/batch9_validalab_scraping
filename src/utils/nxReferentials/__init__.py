import karmahutils as kut
import nxDSSAutomatization as nxauto
from dataiku.core.sql import SQLExecutor2
import pandas as pd

version_number = '1.1'
version_type = 'library'


def format_column_name(column_name):
    name_parts = [X.replace('ID', 'id') for X in column_name.split('_')]
    first_part = name_parts[0][0].lower() + name_parts[0][1:]
    other_parts = [X[0].upper() + X[1:] for X in name_parts[1:]]
    return ''.join([first_part] + other_parts)


def dwh_to_di_renaming_rule(dataframe):
    return {X: format_column_name(X) for X in dataframe.columns}


def rename_columns(dataframe, input_format='DWH', output_format='DI'):
    print('conversion',input_format,'to',output_format)
    return dataframe.rename(columns=dwh_to_di_renaming_rule(dataframe=dataframe))


def format_client_name(dataframe, client_name_column='client'):
    """takes a dataframe containing client Name in DWH format :
    the client name column must *not* be called clientName
    * add the clientName column using refactoring rules from DI
    * rename the former client name column to clientNameDWH"""
    dataframe['clientName'] = dataframe[client_name_column].apply(
        lambda client_name: client_name.replace(' ', '').split('(')[0][:12])
    dataframe.rename(columns={client_name_column: 'clientNameDWH'}, inplace=True)
    return dataframe


def convert_to_server_id(sales_unit):
    sales_unit_in_str = str(sales_unit)
    sales_unit_no_platform = sales_unit_in_str[1:]
    return int(sales_unit_no_platform)


def get_ref_table(referential_name):
    return nxauto.get_sql_table(referential_name=referential_name)


def store_name_of_views(view_ids=None, silent_mode=True):
    env = nxauto.get_project_variables(scope='local')['env']
    table_name = '_'.join([env, 'DIReferential', 'referentialstorename'])
    query = 'SELECT * FROM ' + table_name
    connection = SQLExecutor2(connection='dataiku_workspace')
    store_referential = connection.query_to_df(query)
    store_referential = store_referential[['storeName', 'viewId']]
    store_referential = store_referential[~pd.isnull(store_referential.viewId)]
    if view_ids is not None:
        store_referential = kut.filter_on_values(
            df=store_referential,
            value_list=view_ids,
            column_name='viewId'
        )
    store_referential['viewId'] = store_referential.viewId.astype(int)
    store_name_dic = store_referential.set_index('viewId')['storeName'].to_dict()
    if not silent_mode:
        print(store_referential)
        print(store_referential.dtypes)
        print(store_name_dic)

    return store_name_dic


print("loaded nxReferential version", version_type,version_number)
