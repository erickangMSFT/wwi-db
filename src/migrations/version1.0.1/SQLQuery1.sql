-- Create a new table called 'MyTable1' in schema 'dbo'
-- Drop the table if it already exists
IF OBJECT_ID('dbo.MyTable1', 'U') IS NOT NULL
DROP TABLE dbo.MyTable1
GO
-- Create the table in the specified schema
CREATE TABLE dbo.MyTable1
(
    MyTable1Id INT NOT NULL PRIMARY KEY, -- primary key column
    Column1 [NVARCHAR](50) NOT NULL,
    Column2 [NVARCHAR](50) NOT NULL
    -- specify more columns here
);
GO