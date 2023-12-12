import getpass
import sys

import mysql.connector
from mysql.connector import errorcode


DB_NAME = 'Empresa'

TABLES = [
    (
        True,
        'Pessoa',
        '''
CREATE TABLE Pessoa (
  nome VARCHAR(100) NOT NULL,
  morada VARCHAR(100) NOT NULL,
  numSegurancaSocial INTEGER PRIMARY KEY
)''',
    ),
    (
        True,
        'Empregado',
        '''
CREATE TABLE Empregado (
  refPessoa INTEGER PRIMARY KEY,
  numMecanografico INTEGER UNIQUE KEY,
  salario FLOAT NOT NULL,
  genero ENUM ('FEMININO', 'MASCULINO') NOT NULL,
  dataDeNascimento DATE NOT NULL,
  supervisor INTEGER NULL DEFAULT NULL,
  FOREIGN KEY (refPessoa)
    REFERENCES Pessoa (numSegurancaSocial)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (supervisor)
    REFERENCES Empregado (refPessoa)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)''',
    ),
    (
        True,
        'Dependente',
        '''
CREATE TABLE Dependente (
  refPessoa INTEGER PRIMARY KEY,
  FOREIGN KEY (refPessoa)
    REFERENCES Pessoa (numSegurancaSocial)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)''',
    ),
    (
        True,
        'Dependencia',
        '''
CREATE TABLE Dependencia (
  refDependente INTEGER NOT NULL,
  relacao ENUM ('FILHO', 'FILHA', 'PAI', 'MÃE') NOT NULL,
  refEmpregado INTEGER NOT NULL,
  PRIMARY KEY (refDependente, refEmpregado),
  FOREIGN KEY (refDependente)
    REFERENCES Dependente (refPessoa)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (refEmpregado)
    REFERENCES Empregado (refPessoa)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)''',
    ),
    (
        True,
        'Departamento',
        '''
CREATE TABLE Departamento (
  nome VARCHAR(100) NOT NULL,
  numero INTEGER PRIMARY KEY,
  diretor INTEGER NOT NULL,
  dataNomeacao DATE NOT NULL DEFAULT (current_date ()),
  FOREIGN KEY (diretor)
    REFERENCES Empregado (refPessoa)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)''',
    ),
    (
        False,
        'Empregado',
        '''
ALTER TABLE Empregado
  ADD COLUMN (pertence INTEGER NULL),
  ADD CONSTRAINT FOREIGN KEY (pertence)
    REFERENCES Departamento (numero)
    ON DELETE CASCADE
    ON UPDATE CASCADE
'''
    ),
]


def main ():
    connection = connect_mysql ()
    cursor = connection.cursor ()
    create_database (cursor)
    connection.database = DB_NAME
    setup_tables (cursor)
    connection.close ()

    try:
        cursor.execute ("USE {}".format(DB_NAME))
        print ('Using database {}'.format (DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DB_NAME))
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)
    cnx.close()


def connect_mysql ():
    mysql_root_password = getpass.getpass ('MySQL root password? ')
    try:
        return mysql.connector.connect(
            user='root',
            password=mysql_root_password,
            host='127.0.0.1')
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print ('Something is wrong with the MySQL root user or password')
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print ('Database does not exist')
        else:
            print(err)
        sys.exit (1)


def create_database (cursor):
    try:
        cursor.execute (
            'CREATE DATABASE {} DEFAULT CHARACTER SET "utf8"'.format (DB_NAME))
    except mysql.connector.Error as err:
        print ('Failed creating database: {}'.format (err))
        print ('Trying dropping...')
        try:
            cursor.execute (
                'DROP DATABASE {}'.format (DB_NAME)
            )
        except mysql.connector.Error as err:
            print ('Failed dropping database: {}.\nQuiting!'.format (err))
            sys.exit (1)
        try:
            cursor.execute (
                'CREATE DATABASE {} DEFAULT CHARACTER SET "utf8"'.format (DB_NAME))
            print ('Database {} created successfully.'.format (DB_NAME))
        except mysql.connector.Error as err:
            print ('Second creation attempt also failed: {}'.format (err))
            print ('Quiting!')
            sys.exit (1)
    return


def setup_tables (cursor):
    print ('Setuping tables...')
    steps = len (TABLES)
    for index, (create_flag, table_name, sql_instruction) in enumerate (TABLES):
        print ('{} {} {}/{}'.format (
            'Creating table' if create_flag else 'Altering table',
            table_name,
            index + 1,
            steps
        ))
        try:
            cursor.execute (sql_instruction)
        except mysql.connector.Error as err:
            print ('An error has occurrede: {}'.format (err))
            print ('Quiting!')
            sys.exit (1)
    return


if not main ():
    sys.exit (1)
