# PostgreSQL: The Accelerated Guide to Near-Expertise

A concise, command-centric guide for mastering PostgreSQL on Linux, inspired by `postgresql.org/docs/current/`.

## 1. Core Concepts

-   **Cluster**: A collection of databases managed by a single PostgreSQL server instance.
-   **Database**: A named collection of SQL objects (tables, schemas, etc.).
-   **Schema**: A namespace within a database; organizes objects like tables, functions. `public` is the default.
-   **Role**: Identity that can own database objects and have privileges. Can be a user (login role) or a group.
-   **SQL (Structured Query Language)**: The standard language for interacting with relational databases.
    -   **DDL (Data Definition Language)**: Defines data structures (e.g., `CREATE TABLE`, `ALTER TABLE`).
    -   **DML (Data Manipulation Language)**: Manipulates data (e.g., `SELECT`, `INSERT`, `UPDATE`, `DELETE`).
    -   **DCL (Data Control Language)**: Manages access and permissions (e.g., `GRANT`, `REVOKE`).
    -   **TCL (Transaction Control Language)**: Manages transactions (e.g., `BEGIN`, `COMMIT`, `ROLLBACK`).

## 2. Installation (Ubuntu/Debian Example)

```bash
# Update package list
sudo apt update
```
# Install PostgreSQL server and client tools, plus contrib package for utilities
sudo apt install postgresql postgresql-contrib
Installs PostgreSQL, creates a postgres Linux user, and usually initializes a default cluster.Service is typically named postgresql or postgresql@[version]-main (e.g., postgresql@16-main).3. Initial Setup & Service Management3.1. Service Control (systemd)Replace [version] with your PostgreSQL major version (e.g., 16).sudo systemctl status postgresql # Check status (or postgresql@[version]-main)
sudo systemctl start postgresql  # Start
sudo systemctl stop postgresql   # Stop
sudo systemctl restart postgresql# Restart
sudo systemctl reload postgresql # Reload configuration without full restart
sudo systemctl enable postgresql # Enable auto-start on boot
3.2. Default Superuser (postgres)The postgres database superuser is typically set up with peer authentication for local connections.Connect as postgres OS user to become postgres DB user:sudo -u postgres psql
# You are now in the psql shell, connected to the 'postgres' database.
# Prompt: postgres=#
3.3. Cluster Informationpg_lsclusters # List all PostgreSQL clusters, versions, ports, data directories
Data directory (default): /var/lib/postgresql/[version]/main/Config files (default): /etc/postgresql/[version]/main/4. psql: The Interactive TerminalLaunch psql:psql # Tries to connect as current OS user to database with same name
psql -U dbuser -d dbname -h host -p port # Full connection string
sudo -u postgres psql mydatabase # Connect as 'postgres' to 'mydatabase'
4.1. Essential psql Meta-Commands (run within psql)\q: Quit.\c dbname [username]: Connect to a new database (optionally as a different user).\l or \list: List databases.\l+: List databases with more details.\dn[S+] [pattern]: List schemas. S for system schemas, + for details.\dt[S+] [pattern]: List tables (e.g., \dt public.*).\dv[S+] [pattern]: List views.\di[S+] [pattern]: List indexes.\ds[S+] [pattern]: List sequences.\df[S+] [pattern]: List functions.\dg[S+] [pattern] or \du[S+] [pattern]: List roles (users/groups).\d table_name: Describe a table (columns, indexes, constraints).\d+ table_name: More detailed description.\dp table_name or \z table_name: Show table privileges.\timing [on|off]: Toggle query execution time display.\x [on|off|auto]: Toggle expanded display for query results.\h [SQL_COMMAND]: Help on SQL commands (e.g., \h CREATE TABLE).\?: Help on psql backslash commands.\i filename.sql: Execute commands from a file.\e: Edit current query buffer in an external editor (uses EDITOR env var).\ef [function_name]: Edit function source in external editor.\password [username]: Change a user's password.\conninfo: Display current connection information.\set [name [value]]: Set psql variable (e.g., \set PROMPT1 '%n@%/%R%# ').\! [command]: Execute shell command.5. Role and Permission Management (DCL)5.1. Roles (Users and Groups)-- Create a login role (user)
CREATE ROLE username WITH LOGIN PASSWORD 'strong_password' VALID UNTIL '2026-01-01';
CREATE USER another_user WITH PASSWORD 'pass123'; -- Alias for CREATE ROLE ... LOGIN

-- Create a role that can create databases
CREATE ROLE db_creator LOGIN CREATEDB PASSWORD 'creator_pass';

-- Create a group role (no login)
CREATE ROLE app_readonly NOLOGIN;

-- Modify roles
ALTER ROLE username NOCREATEDB;
ALTER ROLE username RENAME TO new_username;
ALTER ROLE app_readonly ADD MEMBER user1, user2;
ALTER ROLE app_readonly DROP MEMBER user1;
ALTER ROLE username SET search_path = myschema, public; -- Set default search_path for user

-- Delete a role (must not own objects or have privileges)
DROP ROLE old_username;
-- To drop role with objects: REASSIGN OWNED BY old_username TO new_owner; DROP OWNED BY old_username; DROP ROLE old_username;
5.2. PrivilegesGrant minimum necessary privileges.-- Database-level privileges
GRANT CONNECT ON DATABASE mydatabase TO username;
GRANT CREATE ON DATABASE mydatabase TO db_creator; -- Allows creating schemas in mydatabase
GRANT TEMPORARY ON DATABASE mydatabase TO report_user; -- Allows creating temporary tables

-- Schema-level privileges
GRANT USAGE ON SCHEMA public TO username; -- Allows access to objects in schema
GRANT CREATE ON SCHEMA public TO username; -- Allows creating objects in schema

-- Table-level privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE my_table TO username;
GRANT ALL PRIVILEGES ON TABLE my_table TO admin_user;
GRANT SELECT (col1, col2), UPDATE (col1) ON my_table TO specific_user; -- Column-level
GRANT TRUNCATE ON TABLE large_log_table TO maint_user;

-- Grant on all existing tables/sequences/functions in a schema
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO writer_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA app_logic TO app_user;
GRANT EXECUTE ON ALL ROUTINES IN SCHEMA app_logic TO app_user; -- Includes procedures

-- Default privileges for future objects (CRITICAL for roles creating tables)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;
ALTER DEFAULT PRIVILEGES FOR ROLE app_owner IN SCHEMA app_schema GRANT INSERT, UPDATE ON TABLES TO app_writer;

-- Sequence privileges
GRANT USAGE, SELECT ON SEQUENCE my_sequence TO username; -- USAGE for nextval/currval

-- Function/Procedure privileges
GRANT EXECUTE ON FUNCTION my_function(int) TO username;
GRANT EXECUTE ON PROCEDURE my_procedure(int) TO username;

-- Type privileges
GRANT USAGE ON TYPE my_custom_type TO some_user;

-- Revoke privileges
REVOKE INSERT ON my_table FROM username;
REVOKE ALL PRIVILEGES ON DATABASE mydatabase FROM public; -- Revoke from the pseudo-role 'public'
6. Database and Schema Management (DDL)6.1. DatabasesCREATE DATABASE my_app_db
    WITH
    OWNER = db_owner_role
    TEMPLATE = template0  -- Clean template, no locale-specific objects
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8' -- Sort order
    LC_CTYPE = 'en_US.UTF-8'   -- Character classification
    TABLESPACE = my_tablespace -- Optional: specify default tablespace
    ALLOW_CONNECTIONS = true
    CONNECTION LIMIT = 50
    IS_TEMPLATE = false;

ALTER DATABASE my_app_db RENAME TO production_db;
ALTER DATABASE production_db OWNER TO new_owner;
ALTER DATABASE production_db SET search_path = app_schema, public; -- Set default search_path
ALTER DATABASE production_db CONNECTION LIMIT 100;
ALTER DATABASE template_db IS_TEMPLATE true;

DROP DATABASE old_db; -- Fails if there are active connections
DROP DATABASE IF EXISTS temp_db WITH (FORCE); -- PostgreSQL 13+ (terminates connections)
6.2. SchemasCREATE SCHEMA IF NOT EXISTS app_specific_schema AUTHORIZATION app_user;
ALTER SCHEMA old_schema_name RENAME TO new_schema_name;
ALTER SCHEMA new_schema_name OWNER TO new_owner_role;
DROP SCHEMA app_specific_schema; -- Fails if not empty
DROP SCHEMA IF EXISTS old_schema CASCADE; -- Drops schema and all its objects
Current schema search path: SHOW search_path;Set for session: SET search_path TO my_schema, public, "$user"; ("$user" refers to a schema with the same name as the current user)7. Table Management (DDL)7.1. Common Data TypesNumeric: SMALLINT (2b), INTEGER (or INT, 4b), BIGINT (8b), DECIMAL(precision, scale) (or NUMERIC), REAL (4b float), DOUBLE PRECISION (8b float). SERIAL (4b auto-inc), BIGSERIAL (8b auto-inc).Character: VARCHAR(n) (variable-length with limit), CHAR(n) (fixed-length), TEXT (variable unlimited).Binary: BYTEA.Date/Time: DATE, TIME [WITHOUT TIME ZONE], TIME WITH TIME ZONE (or TIMETZ), TIMESTAMP [WITHOUT TIME ZONE], TIMESTAMP WITH TIME ZONE (or TIMESTAMPTZ), INTERVAL [fields] [ (p) ].Boolean: BOOLEAN (TRUE, FALSE, NULL).UUID: UUID (use gen_random_uuid() from pgcrypto or uuid_generate_v4() from uuid-ossp).JSON: JSON (text), JSONB (binary, indexed, preferred).Array: datatype[] (e.g., INTEGER[], TEXT[][]).Range Types: INT4RANGE, INT8RANGE, NUMRANGE, DATERANGE, TSRANGE, TSTZRANGE.Geometric: POINT, LINE, LSEG, BOX, PATH, POLYGON, CIRCLE.Network Address: CIDR, INET, MACADDR, MACADDR8.Text Search: TSVECTOR, TSQUERY.Enumerated: CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');Composite: CREATE TYPE complex AS (r DOUBLE PRECISION, i DOUBLE PRECISION);Special: XML, MONEY (locale-sensitive currency, NUMERIC often preferred). OID (object identifier, legacy).7.2. Creating Tables & ConstraintsCREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    location TEXT
);

CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY, -- Auto-incrementing integer, NOT NULL, UNIQUE
    employee_code VARCHAR(10) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    hire_date DATE DEFAULT CURRENT_DATE,
    salary NUMERIC(10, 2) CHECK (salary > 0),
    department_id INTEGER REFERENCES departments(department_id) ON DELETE SET NULL ON UPDATE CASCADE,
    manager_id INTEGER REFERENCES employees(employee_id) ON DELETE RESTRICT, -- Disallow deleting manager if they have reports
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp(), -- Or CURRENT_TIMESTAMP (transaction start)
    updated_at TIMESTAMPTZ DEFAULT clock_timestamp()
);

-- Table with composite primary key
-- CREATE TABLE order_items (
--     order_id INT REFERENCES orders(order_id),
--     product_id INT REFERENCES products(product_id),
--     quantity INT,
--     PRIMARY KEY (order_id, product_id)
-- );

-- Table Partitioning (Declarative, PostgreSQL 10+)
-- CREATE TABLE measurement (logdate DATE NOT NULL, city_id INT, peaktemp INT) PARTITION BY RANGE (logdate);
-- CREATE TABLE measurement_y2025m05 PARTITION OF measurement FOR VALUES FROM ('2025-05-01') TO ('2025-06-01') PARTITION BY LIST (city_id);
-- CREATE TABLE measurement_y2025m05_sf PARTITION OF measurement_y2025m05 FOR VALUES IN (1);
Constraint Types: PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK, NOT NULL, EXCLUDE (generalized exclusion constraint).DEFERRABLE INITIALLY DEFERRED constraints can be checked at transaction end.7.3. Altering Tables-- Add/Drop Columns
ALTER TABLE employees ADD COLUMN phone_number VARCHAR(20);
ALTER TABLE employees DROP COLUMN is_active;
ALTER TABLE employees ADD COLUMN termination_date DATE; -- Add column

-- Modify Column Type (data must be convertible, may require USING clause)
ALTER TABLE employees ALTER COLUMN phone_number TYPE TEXT;
-- ALTER TABLE employees ALTER COLUMN salary TYPE INTEGER USING salary::INTEGER; -- Explicit cast

-- Add/Drop Constraints
ALTER TABLE employees ADD CONSTRAINT check_salary_positive CHECK (salary > 0 AND salary < 1000000);
ALTER TABLE employees DROP CONSTRAINT check_salary_positive;
-- ALTER TABLE employees ADD UNIQUE (employee_code); -- Creates unique index
-- ALTER TABLE employees ADD FOREIGN KEY (office_id) REFERENCES offices(office_id);
ALTER TABLE employees VALIDATE CONSTRAINT fk_department; -- If added with NOT VALID

-- Set/Drop Default
ALTER TABLE employees ALTER COLUMN termination_date SET DEFAULT NULL;
ALTER TABLE employees ALTER COLUMN hire_date DROP DEFAULT;

-- Set/Drop Not Null
ALTER TABLE employees ALTER COLUMN phone_number SET NOT NULL;
ALTER TABLE employees ALTER COLUMN phone_number DROP NOT NULL;

-- Rename Column/Table
ALTER TABLE employees RENAME COLUMN phone_number TO contact_number;
ALTER TABLE employees RENAME TO staff;

-- Change table owner or schema
ALTER TABLE staff OWNER TO new_owner;
ALTER TABLE staff SET SCHEMA new_schema;

-- Attach/Detach Partition
-- ALTER TABLE measurement ATTACH PARTITION measurement_y2025m06 FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
-- ALTER TABLE measurement DETACH PARTITION measurement_y2025m05;
7.4. Dropping and Truncating TablesDROP TABLE IF EXISTS old_staff;
DROP TABLE staff CASCADE; -- Drops dependent objects (views, FKs referencing it) - CAUTION!

TRUNCATE TABLE large_log_table; -- Removes all rows, fast, keeps structure
TRUNCATE TABLE parent_table RESTART IDENTITY CASCADE; -- Resets sequences, cascades to FK-referencing tables
8. Data Manipulation (DML)8.1. INSERTINSERT INTO departments (name, location) VALUES ('Engineering', 'Building A'), ('Sales', 'Building B'), ('HR', 'Main Office');

INSERT INTO employees (employee_code, first_name, last_name, email, department_id, salary)
VALUES ('EMP001', 'Alice', 'Wonder', 'alice@example.com', 1, 75000),
       ('EMP002', 'Bob', 'Builder', 'bob@example.com', 1, 80000);

-- Insert from SELECT
INSERT INTO archive_employees (employee_id, first_name, last_name, salary)
SELECT employee_id, first_name, last_name, salary FROM employees WHERE hire_date < '2020-01-01';

-- Return generated values
INSERT INTO departments (name) VALUES ('Marketing') RETURNING department_id, name;

-- Upsert (Insert or Update on conflict) - requires unique constraint for conflict target
INSERT INTO customer_stats (customer_id, last_purchase_date, total_spent)
VALUES (123, CURRENT_DATE, 50.00)
ON CONFLICT (customer_id) DO UPDATE -- (customer_id) is the conflict target (column with unique index)
  SET last_purchase_date = EXCLUDED.last_purchase_date, -- EXCLUDED refers to values proposed for insertion
      total_spent = customer_stats.total_spent + EXCLUDED.total_spent,
      update_count = COALESCE(customer_stats.update_count, 0) + 1
  WHERE customer_stats.is_active = TRUE; -- Optional: condition for DO UPDATE
8.2. SELECT (Querying Data)-- Basic SELECT
SELECT first_name, last_name, salary FROM employees;
SELECT * FROM employees WHERE department_id = 1 AND salary > 70000;

-- Aliases
SELECT e.first_name AS "First Name", d.name AS "Department"
FROM employees e JOIN departments d ON e.department_id = d.department_id;

-- Ordering
SELECT * FROM employees ORDER BY last_name ASC NULLS FIRST, first_name DESC NULLS LAST;

-- Limiting results (pagination)
SELECT * FROM employees ORDER BY salary DESC LIMIT 10 OFFSET 20; -- Rows 21-30
-- FETCH FIRST 10 ROWS ONLY; -- SQL standard alternative to LIMIT

-- DISTINCT values
SELECT DISTINCT department_id FROM employees;
SELECT DISTINCT ON (department_id) * FROM employees ORDER BY department_id, hire_date DESC; -- Get latest hire per dept

-- Operators: =, <, >, <=, >=, <>, !=, AND, OR, NOT, BETWEEN, IN, LIKE, ILIKE (case-insensitive LIKE), SIMILAR TO, IS NULL, IS NOT NULL, IS DISTINCT FROM, IS NOT DISTINCT FROM.
-- LIKE patterns: '%' (any sequence), '_' (any single char). Use `ESCAPE 'char'` for literal % or _.
SELECT * FROM employees WHERE first_name LIKE 'A%';
SELECT * FROM employees WHERE email ILIKE '%.com';

-- Array operators: ANY, ALL, @> (contains), <@ (is contained by), && (overlap)
-- SELECT * FROM products WHERE 'electronics' = ANY(tags); -- tags is an array column
-- SELECT * FROM products WHERE tags @> ARRAY['electronics', 'portable'];

-- JSON/JSONB operators (for JSONB): ?, ?&, ?|, @>, <@, -> (get obj field/array elem), ->> (get as text), #> (path), #>> (path as text)
-- SELECT * FROM events WHERE event_data ->> 'type' = 'conference'; (->> gets text)
-- SELECT * FROM events WHERE event_data @> '{"location": "Berlin"}'; (jsonb_contains)
-- SELECT * FROM events WHERE event_data -> 'attendees' ->> 0 = 'Alice'; -- First attendee name
8.3. UPDATECAUTION: Always use WHERE unless you intend to update all rows.UPDATE employees
SET salary = salary * 1.10, updated_at = clock_timestamp()
WHERE department_id = (SELECT department_id FROM departments WHERE name = 'Engineering');

-- Update using FROM clause (join)
UPDATE employees e
SET manager_id = s.manager_id_new, salary = e.salary * s.raise_multiplier
FROM staff_hierarchy_updates s -- staff_hierarchy_updates is another table
WHERE e.employee_code = s.employee_code AND e.department_id = 2;

-- Update and return changed rows
UPDATE employees SET is_active = FALSE WHERE hire_date < '2010-01-01' RETURNING employee_id, first_name, email;
8.4. DELETECAUTION: Always use WHERE unless you intend to delete all rows.DELETE FROM employees WHERE employee_id = 105;

-- Delete using a subquery or JOIN (USING clause)
DELETE FROM employees
WHERE department_id IN (SELECT department_id FROM departments WHERE name LIKE 'Obsolete%');

DELETE FROM employees e
USING departments d
WHERE e.department_id = d.department_id AND d.name = 'Redundant';

-- Delete and return deleted rows
DELETE FROM old_logs WHERE log_date < CURRENT_DATE - INTERVAL '1 year' RETURNING *;
9. Advanced Querying9.1. JoinsINNER JOIN (or JOIN): Only matching rows from both tables.LEFT [OUTER] JOIN: All rows from left table, matching from right (or NULLs).RIGHT [OUTER] JOIN: All rows from right table, matching from left (or NULLs).FULL [OUTER] JOIN: All rows from both tables, NULLs where no match.CROSS JOIN: Cartesian product (all combinations).NATURAL JOIN: Joins on columns with the same name (use with caution, implicit).USING (column_list): Shorthand for ON t1.col = t2.col AND ... when join columns have same names.LATERAL JOIN: Allows right-hand side of join to reference columns from left-hand side (like a correlated

