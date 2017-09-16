#!/usr/bin/python

import sys
import argparse
import json
import yaml
import pyodbc

__version_map_json = './version-map.json'
__config_file = './config.yml'

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', dest='config_file', default=__config_file)
    args = parser.parse_args()
    
    runner_config = RunnerConfig(args.config_file)
    version_control = VersionControl(runner_config.migration_file)
    sql = SQL(runner_config)
    sql.connect()

    # print(sql.config.server)

    # print (version_control.migration_id)
    # print (version_control.migration_data)
    # print (runner_config.migration_file)
    # print (runner_config.database)
    # print (runner_config.server)
    # print (runner_config.user)
    # print (runner_config.password)

class VersionControl:
# find the current version in the database
# find the target version
# find the diffs

    __min_idex = 0
    __max_index = 0
    __database_version_index = 0
    __version_map = json.dumps('[]')

    def __init__(self, map_file):
        self.migration_id = ''
        self.migration_data = json.dumps('[]')
        self.migration_workload = json.dumps('[]')

        self.__get_database_version()
        self.__version_map = json.loads(self.__load_json_map__(map_file))
        self.__load_map__()
        
        return
    
    def __load_map__(self):
        version_list = []
        for migration in self.__version_map:
            version_list.append(migration['migrationID'])
        __max_index = version_list.index(max(version_list))
        if __max_index == 0:
            raise ValueError('Detected an invalid migration sequence.')
        else:
            self.migration_id = self.__version_map[__max_index]['migrationID']
            self.migration_data = json.dumps(self.__version_map[__max_index])
        return

    def __load_json_map__(self,map_file):
        with open(map_file, "r") as FILE_version_file:
            migrations = json.loads(FILE_version_file.read())
        return json.dumps(migrations)

    def __get_database_version(self):
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

    def connect(self):
        try:
            print ('Connecting SQL Server...')
            connection = pyodbc.connect(self.__con_str)
            cursor = connection.cursor()
            tsql = "select @@version"
            rows = cursor.execute(tsql).fetchall():
                print (rows)
        except Exception, e:
            print(str(e))
            print('connection string: ' + self.__con_str)
        return


    def __build_connection_string__(self):
        con_str = 'DRIVER={ODBC Driver 13 for SQL Server};SERVER=' + self.config.server
        con_str += ';PORT=' + str(self.config.port)
        # con_str += ';DATABASE=' + self.config.database
        con_str += ';UID=' + self.config.user
        con_str += ';PWD=' + self.config.password
        return con_str









class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    main(sys.argv[1:])


# Black        0;30     Dark Gray     1;30
# Red          0;31     Light Red     1;31
# Green        0;32     Light Green   1;32
# Brown/Orange 0;33     Yellow        1;33
# Blue         0;34     Light Blue    1;34
# Purple       0;35     Light Purple  1;35
# Cyan         0;36     Light Cyan    1;36
# Light Gray   0;37     White         1;37
