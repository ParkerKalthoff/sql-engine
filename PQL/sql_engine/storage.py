from typing import Union

class Database:

    def __init__(self):
        self.tables: dict[str, Table] = {}

    def create_table(self, table_name : str, columns : dict[str, str]):
        
        table_name = table_name.upper()
        
        if not table_name:
            raise ValueError("Need to pass in a table name")

        if table_name in self.tables.keys():
            raise ValueError(f"Attempted to create table {table_name} that alreadys exists")

        if not columns:
            raise ValueError(f"Attempted to create table {table_name} with no columns")
        
        self.tables[table_name] = Table(table_name, columns)
    
    def get_table(self, table_name: str):

        table_name = table_name.upper()

        if not table_name:
            raise ValueError("Need to pass in a table name")

        if table_name not in self.tables.keys():
            raise ValueError(f"Attempted to query table that doesn't exist")
        
        return self.tables[table_name]


class Table:

    def __init__(self, table_name: str, columns: dict[str, str]):
        
        # TODO create custom datatypes class
        
        columns = {k.upper(): v for k, v in columns.items()}

        self.table_name = table_name

        # COLUMNS : {column_name : datatype}
        self.columns = columns
        
        # DATA : {column_name : list[vals]}
        self.data : dict[str, list[str]] = {k: [] for k in columns.keys()} 

    def insert(self, values: dict[str, list[str]]):
        
        values = {k.upper(): v for k, v in values.items()}

        for col in values:
            if col not in self.columns:
                raise ValueError(f"Column '{col}' does not exist in table '{self.table_name}'")

        lengths = [len(v) for v in values.values()]
        if len(set(lengths)) != 1:
            raise ValueError(f"All inserted columns must have the same number of rows, got lengths {lengths}")

        num_rows = lengths[0]
        for col in self.columns:
            if col in values:
                self.data[col].extend(values[col])
            else:
                self.data[col].extend([None] * num_rows) # type: ignore

    def __getitem__(self, key: Union[str, list[str], tuple[str]]) -> dict[str, list[str]]:

        if isinstance(key, str):
            col = key.upper()
            if col not in self.data:
                raise KeyError(f"Column '{col}' does not exist in table '{self.table_name}'")
            return {col: self.data[col]}

        elif isinstance(key, (list, tuple)): # type: ignore

            if not key:
                raise ValueError('Passed in no arguments in iterable')
            else:
                for col in key:
                    if not isinstance(col, str): # type: ignore
                        raise ValueError('Passed in non string type into __getitem__')

            cols = [k.upper() for k in key]
            for col in cols:
                if col not in self.data:
                    raise KeyError(f"Column '{col}' does not exist in table '{self.table_name}'")
            return {k: v for k, v in self.data.items() if k in cols}

        else:
            raise TypeError(f"Invalid key type {type(key)}; must be str or list/tuple of str")
        
    def select(self, key: Union[str, list[str], tuple[str]]) -> dict[str, list[str]]:
        """
            Uses getitem
        """
        return self.__getitem__(key)

    def where(self, *conditions: str):
        pass


    def _generate_filter_mask(self, value1: str, value1_type: str, operator: str, value2: str, value2_type: str, negate: bool = False):
        """
            Generates a filter mask,

            value1 and value2 must either be a column or a text literal
        """
        
        if not value1.startswith("'") and not value1.endswith("'") and (value1 not in self.columns.keys()):
            raise ValueError(f"{value1} is not a column in {self.table_name}")
        
        if not value2.startswith("'") and not value2.endswith("'") and (value2 not in self.columns.keys()):
            raise ValueError(f"{value2} is not a column in {self.table_name}")
        
        if value1_type != value2_type:
            raise ValueError(f"Data types {value1_type} and {value2_type} are not comparable")

        length = len(self.data.values()[0]) # type: ignore
        value1_is_col = value1.startswith("'")
        value2_is_col = value2.startswith("'")

        if operator == '=':
            pass
        elif operator in ('<>', '!='):
            pass

        if value1_type not in ('numeric', 'time'):
            raise ValueError(f'Invalid Operator: {operator} for {value1_type}')

        if operator == '>':
            pass
        elif operator == '>=':
            pass
        elif operator == '<':
            pass
        elif operator == '<=':
            pass