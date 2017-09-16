
IF (OBJECT_ID('dbo.versionMap', 'U') IS NULL)
BEGIN
    CREATE TABLE [dbo].[versionMap]
    (
        migrationID int NOT NULL PRIMARY KEY,
        description nvarchar(400) NOT NULL,
        version nvarchar(100) NOT NULL,
        migrationFiles nvarchar(max) NULL
    );

    -- Setting WideWorldImporters database to version 1 just for a demo pupose.

    DECLARE @json NVARCHAR(MAX)
    SET @json =  N'[
        {
            "migrationID": 2,
            "description": "Version 1.0.1 fix for Website.InsertCustomerOrders",
            "version": {
                "major": 1,
                "minor": 1,
                "revision": 0
            },
            "files": [
                {
                    "executionOrder": 1,
                    "name": "migrations/version1.0.1/wwi_db_changes_1.0.1.sql"
                }
            ]
        }
    ]'

    SELECT *
    FROM OPENJSON(@json)  
    WITH (
       migrationId int '$.migrationID',  
       description nvarchar(400) '$.description', 
        version nvarchar(max) '$.version',  
       files nvarchar(max) '$.files'
    )
    
    -- INSERT INTO dbo.versionMap
    -- values
    --     (1, 'test', 'test json', 'test json')
END

select *
from dbo.versionMap
drop table dbo.versionMap