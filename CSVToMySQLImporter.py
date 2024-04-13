import sys
import csv
import time
import mysql.connector as mysql

class CSVToMySQLImporter:
    def __init__(self):
        if len(sys.argv) < 2 or sys.argv[1] == '--help':
            self.show_help()
        else:
            try:
                args = self.parse_args(sys.argv[1:])
                self.connect_to_mysql(args)

                file_info = input("Alright, tell me about the CSV file (file=yourfile.csv columns=0 delimiter=, table=yourtable): ")

                file_args = self.parse_args(file_info.split())
                filename = file_args.get('file')
                columns = int(file_args.get('columns', 0))
                delimiter = file_args.get('delimiter', ',')
                table = file_args.get('table', filename.split('.')[0])

                self.import_csv(filename, delimiter, columns, table)

            except Exception as e:
                print(f"Yikes! Something went wrong: {e}")
                sys.exit(1)

    def parse_args(self, args):
        """Parse arguments and return them as a dictionary."""
        return dict(arg.split('=') for arg in args)

    def show_help(self):
        print("""
        ******************************************
        Super Easy CSV to MySQL Importer (Casual Edition)
        ******************************************

        How to use this cool tool:

        1. Open your terminal or command prompt.
        2. Type `python CSVToMySQLImporter.py host=your_mysql_host un=your_username pw=your_password db=your_database`
           (Replace those placeholders with your actual MySQL info.)
        3. When prompted, tell me about your CSV file using this format:
           `file=yourfile.csv columns=0 delimiter=, table=yourtable`

        Here's what those things mean:
          - file: The path to your awesome CSV file.
          - columns (optional): The line number with column headings (defaults to 0, the first line).
          - delimiter (optional): The character that separates values in your CSV (defaults to comma ',').
          - table: The name of the table you want to create and fill with data.

        That's it! Let the data flow!
        """)

    def connect_to_mysql(self, args):
        """Connect to the MySQL database using provided credentials."""
        try:
            self.db = mysql.connect(
                host=args.get('host'),
                user=args.get('un'),
                password=args.get('pw'),
                database=args.get('db')
            )
            self.cursor = self.db.cursor()
            print("Connected to MySQL database!")
        except mysql.Error as e:
            print(f"Unable to connect to MySQL: {e}")
            sys.exit(1)

    def import_csv(self, filename, delimiter, columns, table):
        """Import CSV file to MySQL database."""
        try:
            with open(filename, 'r', newline='') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=delimiter)

                for _ in range(columns):
                    next(csv_reader)
                column_headers = next(csv_reader)
                column_definitions = ', '.join(f"{col} VARCHAR(255)" for col in column_headers)

                table_name = table.replace('-', '_')
                create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INT AUTO_INCREMENT, {column_definitions}, PRIMARY KEY (id))"
                self.cursor.execute(create_table_query)

                insert_query = f"INSERT INTO {table_name} ({', '.join(column_headers)}) VALUES ({', '.join(['%s'] * len(column_headers))})"

                start_time = time.time()
                for row in csv_reader:
                    cleaned_row = [self.clean_value(value) for value in row]
                    self.cursor.execute(insert_query, cleaned_row)

                self.db.commit()

                end_time = time.time()
                print("\nData import successful!")
                print(f"Time taken: {end_time - start_time:.2f} seconds")

        except Exception as e:
            print(f"Error during import: {e}")
            self.db.rollback()

        finally:
            self.cursor.close()
            self.db.close()

    @staticmethod
    def clean_value(value):
        """Clean and strip values."""
        return value.strip().replace('"', '')


if __name__ == "__main__":
    CSVToMySQLImporter()
