# wwi-db

1. Get the list of changes from version-map.json
2. Connect to a target database and get its version number from dbo.version-map table.
    * if version-map table does not exist raise error.
    * if exists proceed.
3. Build a migration scripts execution queue
4. Execute in transaction and update the version number in dbo.version-map table.


### version-map table

```json
    {
        "description": "Version 1.0.1 fix for Website.InsertCustomerOrders",
        "version": {
            "major": 1,
            "minor": 1,
            "revision": 0
        },
        "files": [
            {
                "executionOrder": 1,
                "name": "migrations/wwi_db_changes_1_0_1.sql"
            }
        ]
    }

```