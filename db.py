'''
Database connectivity file for Benford's law validator webapp
'''
import sqlalchemy as sql
from sqlalchemy import create_engine


# Define a class to interact with database
class Db:
    def __init__(self):
        self.engine = sql.create_engine("sqlite:///benford.sqlite")
        # connection = self.engine.connect()
        metadata = sql.MetaData()
        self.benfordTable = sql.Table(
            "benford",
            metadata,
            sql.Column("Id", sql.Integer(), primary_key=True),
            sql.Column("filename", sql.String, nullable=False),
            sql.Column("column", sql.String, nullable=False),
            sql.Column("mad", sql.Float(), nullable=False),
            sql.Column("array", sql.String, nullable=False),
            sql.Column(
                "timestamp",
                sql.DateTime(timezone=False),
                nullable=False,
                server_default=sql.func.now(),
            ),
        )
        #metadata.drop_all(self.engine) # Can uncomment to start with a fresh database
        metadata.create_all(self.engine)

# Method to insert a new dataset into database
    def insertDataset(self, f1d, data, value, f1dmad):
        with self.engine.connect() as con:
            jsonString = f1d["Found"].to_json()
            query = sql.insert(self.benfordTable).values(
                filename=data["filename"], column=value, mad=f1dmad, array=jsonString
            )
            con.execute(query)

# Method to get values of a dataset from the database
    def getDataset(self, value):
        with self.engine.connect() as con:
            result = con.execute(
                sql.select([self.benfordTable]).where(self.benfordTable.columns.Id == value + 1)
            ).fetchone()
        id, filename, value, f1dmad, array, timestamp = result
        return array, value, f1dmad

# Method to get info for all of the datasets in database
    def getDatasetList(self):
        with self.engine.connect() as con:
            optionslist = con.execute(
                sql.select(
                    [
                        self.benfordTable.columns.filename,
                        self.benfordTable.columns.column,
                        self.benfordTable.columns.timestamp,
                    ]
                )
            ).fetchall()
        return optionslist