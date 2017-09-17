#!/usr/bin/python

import sys
import argparse
import json
import yaml
import pyodbc

__version_map_json = './version-map.json'
__config_file = './config.yml'

def main(argv):
    db_version = ''
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', dest='config_file', default=__config_file)
    args = parser.parse_args()

    runner_config = RunnerConfig(args.config_file)
    version_control = VersionControl(runner_config.migration_file)
    sql = SQL(runner_config)

    version_control.init_version_control(sql)
    db_version = json.loads(Util.sqljson_to_pyjson(sql.get_db_version()))
    print ('{0}current database version: {1}.{2}.{3}{4}\n'
        .format(bcolors.HEADER, 
                db_version['major_version'], 
                db_version['minor_version'], 
                db_version['revision'], 
                bcolors.ENDC))
    version_control.build_migration_plan(db_version)
    version_control.run_migration_plan(sql)

class VersionControl:
    __min_idex = -1
    __max_index = -1
    __database_version_index = -1
    __version_map = json.dumps('[]')

    def __init__(self, map_file):
        self.migration_id = ''
        self.migration_data = json.dumps('[]')
        self.migration_workload = json.dumps('[]')

        self.__version_map = json.loads(self.__load_json_map__(map_file))
        return
    
    # read version-map.json file and load it into a json object.
    def __load_json_map__(self,map_file):
        with open(map_file, "r") as FILE_version_file:
            migrations = json.loads(FILE_version_file.read())
        return json.dumps(migrations)

    # initialize version control
    def init_version_control(self, sql):
        print('{0}initializing database version control...{1}'
            .format(bcolors.CYAN, bcolors.ENDC))
        try:
            sql.init_db_versioning()
        
        except Exception as e:
            print('{0}database version initialization failed{1}\n'
                .format(bcolors.FAIL,bcolors.ENDC))
            print('{0}{1}{2}\n'
                .format(bcolors.FAIL, str(e), bcolors.ENDC))
            Util.terminate        
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
            self.migration_id = self.__version_map[__max_index]['migrationID']
            self.migration_data = json.dumps(self.__version_map[__max_index])
        return

    def run_migration_plan (self,sql):
        print('{0}running migrations{1}'
            .format(bcolors.CYAN, bcolors.ENDC))
        return

class RunnerConfig:
    def __init__(self,config_file):
        self.migration_file = ''
        self.server = ''
        self.port = ''
        self.database = ''
        self.user = ''
        self.password = ''

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

    # internal: initialize versioning on the connected database
    def init_db_versioning(self):
        if self.__check_versioning__():
            return
        self.__create_version_structure__()
        return

    # check whether db versioning is already enabled in the connected database
    def __check_versioning__(self):
        __tsql = 'select case when (object_id(\'dbo.versionMap\', \'U\') is null) then 0 else 1 end'
        result = self.execute(__tsql)
        if result[0] == 1:
            return True
        return False

    # create necessary schedule objects to record versioning on the connected database: demo purpose only.
    # in a non-demo scenario, operation should fail out if a database does not have a versioning mechanism enabled.
    def __create_version_structure__(self):
        print ('\n{0}creating database versioning schema...{1}\n'
            .format(bcolors.CYAN, bcolors.ENDC))
        self.run_migration_workload()
        return
    
    # execute any sql query and return the result to be loaded in json
    def execute(self,sql_script):
        result = []
        try:
            print ('\n{0}Executing:{1} {2}\n'
                .format(bcolors.CYAN, bcolors.ENDC, sql_script))
            
            with pyodbc.connect(self.__con_str) as cnxn:
            	cursor = cnxn.cursor()
            	rows = cursor.execute(sql_script).fetchall()
                for row in rows:
                     result.append(list(row))
            
            print ('{0}Done!{1}\n'
                .format(bcolors.CYAN, bcolors.ENDC))

        except Exception as e:
            print('{0}Query Execution Failed:{1}\n'
                .format(bcolors.FAIL,bcolors.ENDC))
            print('{0}{1}{2}\n'
                .format(bcolors.FAIL, str(e), bcolors.ENDC))
            Util.terminate()            
        return result
    
    # after a db migration is successfully complete, set the new version number to the target database.
    def set_db_version(self, version_data):
        json_data = json.loads(version_data)
        __tsql = 'exec dbo.setVersion @json = N\'[' + json.dumps(json_data) + ']\''
        return self.execute(__tsql)
    
    # query the version number of connected database.
    def get_db_version(self):
        __tsql = 'select TOP(1) * from dbo.versionMap order by migrationID desc for json path'
        return self.execute(__tsql)

    # run migration workloads in SQL.
    def run_migration_workload(self, migration_plan):
        return

class Util:

    # sql server for json option return extra header and footer characters in pyodbc.
    # it causes a deserialization failure with python json module. 
    # clean up the extra characters.
    @staticmethod
    def sqljson_to_pyjson(sql_string):
        result_str = str(sql_string).lstrip('[[u\'')
        result_str =  result_str.rstrip('\']]')
        return result_str

    @staticmethod
    def terminate():
        print('{0}Terminating migration.{1}\n'
                .format(bcolors.FAIL, bcolors.ENDC))
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