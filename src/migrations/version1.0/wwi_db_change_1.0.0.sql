IF (OBJECT_ID('dbo.versionMap', N'U') IS NULL)
BEGIN
    CREATE TABLE [dbo].[versionMap]
    (
        migrationID int NOT NULL PRIMARY KEY,
        description nvarchar(400) NOT NULL,
        major_version int NOT NULL,
        minor_version int NOT NULL,
        revision int NOT NULL,
        deployment_date datetime2(7) NOT NULL
    )
END
GO

IF(OBJECT_ID('dbo.setVersion', N'P') IS NOT NULL )
    DROP PROCEDURE dbo.setVersion 
GO

CREATE PROCEDURE dbo.setVersion @version_data nvarchar(max)
AS 
BEGIN
    INSERT dbo.versionMap(migrationID, description, major_version, minor_version, revision, deployment_date)
        SELECT migrationId,description, major_version, minor_version,revision, sysdatetime() FROM OPENJSON(@version_data)  
        WITH (
            migrationId int '$.migrationID',  
            description nvarchar(400) '$.description', 
            major_version int '$.version.major',
            minor_version int '$.version.minor',
            revision int '$.version.revision'  
        )
END
GO

IF(OBJECT_ID('dbo.getVersion', N'P') IS NOT NULL )
    DROP PROCEDURE dbo.getVersion 
GO

CREATE PROCEDURE dbo.getVersion
AS 
BEGIN
    SELECT TOP(1) migrationID, description,
        major_version,
        minor_version,
        revision,
        deployment_date
    FROM dbo.versionMap
    ORDER BY migrationID DESC
END
GO