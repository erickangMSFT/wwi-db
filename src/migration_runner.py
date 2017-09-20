#!/usr/bin/python

# todo: enable transaction support for database version migration
# do not use this script for non-demo purpose.

import sys
import os
import argparse
import json
import yaml
import pyodbc

__CONFIG_FILE = 'config.yml'

def main(argv):
    """ main function """
    db_version = ''
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', dest='config_file', default=__CONFIG_FILE)
    args = parser.parse_args()

    # load configuration yml file, version change map json file and initialize sql connection object.
    runner_config = RunnerConfig(args.config_file)
    version_control = VersionControl(runner_config.migration_file)
    sql = SQL(runner_config)

    # initialize version control on the target database if not enabled : demo only.
    version_control.init_version_control(sql)
    version_control.print_db_version(sql)

    # build a database version migration plan.
    version_control.build_migration_plan(db_version)
    if version_control.is_up_to_date():
        print('{0}The database is up-to-date.{1}\n'.format(bcolors.OKGREEN, bcolors.ENDC))
    else: 
        # run database version migrations.
        version_control.run_migration_plan(sql)
        version_control.print_db_version(sql)

class VersionControl:
    """ database version control """
    __min_index = -1
    __max_index = -1
    __database_version_index = -1
    __version_map = json.dumps('[]')

    def __init__(self, map_file):
        self.migration_id = ''
        self.migration_data = {}
        self.migration_plan = {}
        self.initial_plan = {}

        self.__version_map = json.loads(self.__load_json_map__(map_file))

        return
    
    # read version-map.json file and load it into a json object.
    def __load_json_map__(self,map_file):
        with open(map_file, "r") as FILE_version_file:
            migrations = json.loads(FILE_version_file.read())
        return json.dumps(migrations)

    def __get_initial_plan__(self):
        self.initial_plan = self.__version_map[0]
        return 

    def init_version_control(self, sql):
        """  initialize version control """
        print('{0}initializing database version control...{1}'.format(bcolors.CYAN, bcolors.ENDC))
        try:
            if sql.check_version_structure():
                print('{0}database versioning is already enabled. skipping...{1}'.format(bcolors.CYAN, bcolors.ENDC))
                return
            self.__get_initial_plan__()
            sql.execute_plan(json.dumps(self.initial_plan))
            sql.set_db_version(json.dumps(self.initial_plan))
        except Exception as ex:
            print('{0}database version initialization failed{1}\n'.format(bcolors.FAIL,bcolors.ENDC))
            print('{0}{1}{2}\n'.format(bcolors.FAIL, str(ex), bcolors.ENDC))
            Util.terminate()        
        return

    # build a migration plan
    def build_migration_plan(self, db_version):
        version_list = []
        print('{0}building migration plan...{1}'
            .format(bcolors.CYAN, bcolors.ENDC))

        for migration in self.__version_map:
            version_list.append(migration['migrationID'])
        
        __max_index = version_list.index(max(version_list))
        
        if __max_index == -1:
            raise ValueError('Detected an invalid migration sequence.')
            
        else:
            self.__max_index = self.__version_map[__max_index]['migrationID']
            print ('{0}target migrationID: {1}{2}\n'.format(bcolors.HEADER, self.__max_index, bcolors.ENDC))
            plan_list =[]
            for i in range(self.__min_index, self.__max_index):
                plan_list.append(self.__version_map[i])
            self.migration_plan = json.dumps(plan_list)
        return

    def run_migration_plan (self, sql):
        print('{0}running migration plans...{1}'.format(bcolors.CYAN, bcolors.ENDC))
        plans = json.loads(self.migration_plan)
        for plan in plans:
            sql.execute_plan(json.dumps(plan))
            sql.set_db_version(json.dumps(plan))
        print('{0}The migration is complete.{1}'.format(bcolors.OKGREEN, bcolors.ENDC))
        return

    def print_db_version(self,sql):
        db_version = json.loads(Util.sqljson_to_pyjson(sql.get_db_version()))
        self.__min_index = db_version['migrationID']
        print ('{0}current database version: {1}.{2}.{3}{4}'.format(bcolors.HEADER, db_version['major_version'], db_version['minor_version'], db_version['revision'], bcolors.ENDC))
        print ('{0}current migrationID: {1}{2}\n'.format(bcolors.HEADER, self.__min_index, bcolors.ENDC))
        return

    def is_up_to_date(self):
        if self.__min_index == self.__max_index:
            return True
        return False

class RunnerConfig:
    def __init__(self,config_file):
        self.migration_file = ''
        self.server = ''
        self.port = ''
        self.database = ''
        self.user = ''
        self.password = ''

        cwd = os.getcwd()
        config_file = cwd + '/' + config_file
        self.__load_config__(config_file)
        return

    # load migration runner configuration from config.yml file.
    def __load_config__(self,config_file):
        with open(config_file, "r") as FILE_config:
            config = yaml.load(FILE_config.read())
            self.migration_file = config['migration_file']
            self.server = config['server']
            self.port = config['port']
            self.database = config['database']
            self.user = config['user']
            self.password = config['password']
        return

class SQL:
    def __init__(self, runner_config):
        self.config = runner_config
        self.__con_str = self.__build_connection_string__()
        return
    
    # internal: build a connection string from config.yml file
    def __build_connection_string__(self):
        con_str = 'DRIVER={ODBC Driver 13 for SQL Server};SERVER=' + self.config.server
        con_str += ',' + str(self.config.port)
        con_str += ';DATABASE=' + self.config.database
        con_str += ';UID=' + self.config.user
        con_str += ';PWD=' + self.config.password
        return con_str

    # check whether db versioning is already enabled in the connected database
    def check_version_structure(self):
        __tsql = 'select case when (object_id(\'dbo.versionMap\', \'U\') is null) then 0 else 1 end'
        result = self.execute(__tsql)
        if int(result[0]) == 1:
            return True
        return False

    def execute_plan(self, plan):
        script_files = {}
        print ('\n{0}executing migration plan...{1}\n'.format(bcolors.CYAN, bcolors.ENDC))
        plan = json.loads(plan)
        script_files = plan['files']
        for script_file in script_files:
            with open(str(script_file['name']), "r") as FILE_sql_script:
                sql_script = FILE_sql_script.read()
                for batch in sql_script.split('GO'):
                    if len(batch) > 0:
                        self.execute_no_query(batch)
        return

    def execute_no_query(self, sql_script):
        try:
            print ('\n{0}Executing:{1} {2}\n'.format(bcolors.CYAN, bcolors.ENDC, sql_script))
            with pyodbc.connect(self.__con_str) as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(sql_script)
        except Exception as ex:
            print('{0}Query Execution Failed:{1}\n'.format(bcolors.FAIL, bcolors.ENDC))
            print('{0}{1}{2}\n'.format(bcolors.FAIL, str(ex), bcolors.ENDC))
            Util.terminate()
        return

    # execute any sql query and return the result to be loaded in json
    def execute(self, sql_script):
        result = []
        try:
            print ('\n{0}Executing:{1} {2}\n'.format(bcolors.CYAN, bcolors.ENDC, sql_script))
            with pyodbc.connect(self.__con_str) as cnxn:
                cursor = cnxn.cursor()
                rows = cursor.execute(sql_script).fetchall()
                for row in rows:
                    result.append(list(row)[0])
        except Exception as ex:
            print('{0}Query Execution Failed:{1}\n'.format(bcolors.FAIL, bcolors.ENDC))
            print('{0}{1}{2}\n'.format(bcolors.FAIL, str(ex), bcolors.ENDC))
            Util.terminate()
        return result

    # after a db migration is successfully complete, set the new version number to the target database.
    def set_db_version(self, version_data):
        json_data = json.loads(version_data)
        __tsql = 'exec dbo.setVersion @version_data = N\'[' + json.dumps(json_data) + ']\''
        return self.execute_no_query(__tsql)
    
    # query the version number of connected database.
    def get_db_version(self):
        __tsql = 'select TOP(1) * from dbo.versionMap order by migrationID desc for json path'
        return self.execute(__tsql)


class Util:

    """ sql server for json option return extra header and footer characters in pyodbc.
    it causes a deserialization failure with python json module. 
    clean up the extra characters. """

    @staticmethod
    def sqljson_to_pyjson(sql_string):
        """ convert sql json data to python json format """
        result_str = str(sql_string).lstrip('[[u\'')
        result_str = result_str.rstrip('\']]')
        return result_str

    @staticmethod
    def terminate():
        """ terminate process """
        print('{0}Terminating migration.{1}\n'.format(bcolors.FAIL, bcolors.ENDC))
        sys.exit()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CYAN = '\033[96m'
    GREY = '\033[90m'

if __name__ == "__main__":
    main(sys.argv[1:])















# Red = '\033[91m'
# Green = '\033[92m'
# Blue = '\033[94m'
# Cyan = '\033[96m'
# White = '\033[97m'
# Yellow = '\033[93m'
# Magenta = '\033[95m'
# Grey = '\033[90m'
# Black = '\033[90m'
# Default = '\033[99m'
