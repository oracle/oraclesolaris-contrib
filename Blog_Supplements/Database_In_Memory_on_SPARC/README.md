# Database Load Generation and Software in Silicon

The Oracle SPARC CPUs all offer specific circuitry to accelerate certain Oracle database functionality, esp. with regard to the inmemory option. (SPARC M8 also adds acceleration for al NUMBER related operations inside the Oracle database ontop of the aforementioned inmemory acceleration. These will not be covered here)

The existence of these Software-in-Silicon technologies of course pose the question what are they good for in real life, or how could they their benefit be demonstrated? This articlewill describe a setup of a benchmark scenario to demontrate the benefit of Software in Silicon, esp. in a side-by-side comparison with systems without Software-in-Silicon like technology. Of course it can also serve as a testbed for various performance monitoring tools since it has multiple software layers and can generate considerable load on the CPU cores, memory backend, and I/O subsystem.

The basic idea is to use the Star-Schema-Benchmark data to load a database with a scalable amount of data, and that dataset is derived from the well-known TPC-H standard benchmark. This article will not explain how to run an actual TPC benchmark, but it will give a better understanding how the TPC-H benchmark works.  The big difference between TPC-H and the scenario I will describe is the query, we will only use one query which is a fairly simple join statement. This already suffices to put some load on SPARC's software in silicon infrastructure, and at the same time generate load on CPU, memory, and disks.

First and morefmost one has to install an Oracle database, we will look at a 19c installation, the whole scenario only requires at least a database release 12.1.0.2 with certain patches. Older database releases lack the support and hooks for software in silicon

I will briefly touch on the actual contents of the various SQL scripts used or configuration scripts. A knowledgable reader will be able build and adapt them to his specific needs, and a set of scripts that I have been successfully using will be made available on https://github.com/oraclesolaris-contrib/ in the area containing supplemental material to Oracle Solaris blogs

## Installing and Preparing the Database

The installation of the database runs along the usual lines, one downloads the tarball from the [Oracle website](https://www.oracle.com/uk/database/technologies/oracle-database-software-downloads.html) and unpacks it in $ORACLE_HOME. Next I assume one creates a tablespace that can grow large enough, a scale 100 benchmark requires around 200GB for the tablespace itself and TEMP etc. Running it on ASM or a filesystem is not relevant for *our* scenario. ASM would of course deliver a better performance than running it on-top of a filesystem. But the whole point is to load the inmemory subsystem, so disk performance is mostly impacting the ramp-up phase of the benchmark. 

Once the database software is installed,  create a database and a tablespace called `SSB` (this makes maintenance and monitoring easier later when all data ends up in a tablespace on its own) , a few tables inside this tablespace and a user `ssb` to be used to run the actual tests. The github repo will contain a script that does all that on a filesystem, but all steps are straightforward Oracle database admin steps. But I will cite the `create table` statements so one knwows how the tables must look like to work with the datagenerator used later to fill them

1. `lineorder` table, this will become the facts table and it controls the disk footprint of the benchmark

   ```sql
   create table lineorder
   (LO_ORDERKEY number,
   LO_LINENUMBER number,
   LO_CUSTKEY number,
   LO_PARTKEY number,
   LO_SUPPKEY number,
   LO_ORDERDATE number,
   LO_ORDERPRIORITY char(15),
   LO_SHIPPRIORITY char(1),
   LO_QUANTITY number,
   LO_EXTENDEDPRICE number,
   LO_ORDTOTALPRICE number,
   LO_DISCOUNT number,
   LO_REVENUE number,
   LO_SUPPLYCOST number,
   LO_TAX number,
   LO_COMMITDATE number,
   LO_SHIPMODE char(10)
   )
   ;
   
   ```

2. `part` and `supplier` table, the benchmark will later cycle through values from a csv file `category` and `region` within these tables. From the database side these operations will look like many different queries, this is imperative to not let the database cache the result of the first query and only return the cached result set

   ```sql
   create table part (
   P_PARTKEY number,
   P_NAME varchar(22),
   P_MFGR char(6),
   P_CATEGORY char(7),
   P_BRAND1 char(9),
   P_COLOR varchar(11),
   P_TYPE varchar(25),
   P_SIZE number,
   P_CONTAINER char(10)
   )
   ;
   create table supplier (
   S_SUPPKEY number,
   S_NAME char(25),
   S_ADDRESS varchar(25),
   S_CITY char(10),
   S_NATION char(15),
   S_REGION char(12),
   S_PHONE char(15)
   )
   ;
   ```

3. `customer` and `date_dim` two additional dimension tables

   ```sql
   create table customer (
   C_CUSTKEY number,
   C_NAME varchar(25),
   C_ADDRESS varchar(25),
   C_CITY char(10),
   C_NATION char(15),
   C_REGION char(12),
   C_PHONE char(15),
   C_MKTSEGMENT char(10)
   )
   ;
   create table date_dim (
   D_DATEKEY number,
   D_DATE char(18),
   D_DAYOFWEEK char(10),
   D_MONTH char(9),
   D_YEAR number,
   D_YEARMONTHNUM number,
   D_YEARMONTH char(7),
   D_DAYNUMINWEEK number,
   D_DAYNUMINMONTH number,
   D_DAYNUMINYEAR number,
   D_MONTHNUMINYEAR number,
   D_WEEKNUMINYEAR number,
   D_SELLINGSEASON char(12),
   D_LASTDAYINWEEKFL char(1),
   D_LASTDAYINMONTHFL char(1),
   D_HOLIDAYFL char(1),
   D_WEEKDAYFL char(1)
   )
   ;
   ```

With these tables in place we are ready to fill them. This is covered in the next section.

## Generating and Loading Test Data

The Transaction Performance Council has defined a set of standard database benchmarks which all run against a simple dataset which can be generated algorithmically. The structure of this data is modeled after real-life examples and so it is well suited to model real-life systems in a controlled fashion.

There are some simplifications to this dataset available, I have chosen to use the Star-Schema-Benchmark data generator `ssb-dbgen` which is freely available from [github](https://github.com/electrum/ssb-dbgen). `clone/download` it as a zip file, unpack it, make sure you have a compiler installed (it compiles/makes straightforward with either `gcc` or Solaris DeveloperStudio `cc` ) 

Now you're ready to generate the actual data which will be loaded into the database in the next step. We already briefly touched on diskspace in the previous section when the tablespace for the benchmark data was created, to create the loaddata you need roughly the same amount of disk space, so to create a scale 100 setup one needs another 100GB or so and some headroom. The `dbgen` binary is the actual tool to create the test data, and the majority of the data lies in the `lineorder` table (*fact* table), scale 100 means about 600 million rows of data in `lineorder`. (To get an idea of the added value of the inmemory option it is important to use it on a large enough dataset, if you test it against say only a thousand rows in the fact table it might even slow things down)

Creating the data requires 5 invocations of `dbgen`:

```bash
./dbgen –T c –s 100 
./dbgen –T d –s 100 
./dbgen –T p –s 100 
./dbgen –T s –s 100 
./dbgen –T l –C 32 –s 100 
```

These can all run in concurrency, the last command creates the content for the lineorder table in 32 parallel threads. Leveraging the built-in parallelization features of `dbgen` makes a lot of sense for lineorder because of its size, it doesn't really pay off for the smaller dimension tables (creating data in parallel threads also results in as many files to be loaded later into the database)

`dbgen` creates files ending on .tbl, the example above these would be 36 files, 32 for the lineorder table, and one file for each of the dimension tables "customer", "supplier", "parts", and "date_dim". Loading the database is performed using the `sqlldr` tool:

```bash
sqlldr userid=ssb/ssb \
	direct=true skip_index_maintenance=true \
	data=<name of dbgen output file> \
	control=<name of control file>
```

An example control file for the customer table would look like this, the other control files of course would need to be adapted to match the table definition given in the previous section:

```bash
load data
into table customer
append 
fields terminated by '|'
(c_custkey, c_name, c_address, c_city, c_nation, c_region, c_phone, c_mktsegment)
```

(The lineorder table of course requires 32 invocations for the 32 different files with load data, `sqlldr` keeps appending data to a table when called more than once)

## Running the Benchmark

With the database loaded we are ready to perform queries, but to run a benchmark one should have a load generator ready. I will be using [Apache jmeter](https://jmeter.apache.org), and the `oraclesolaris-contrib` repo on github will have `*.jmx` file ready to execute the benchmark against the database. This file assumes that both the database and the jmeter loadgenerator run on the system. One can of course separate the loadgeneration from the database part by means of processor sets or split them on two different systems.

The query should contain a `join` statement to best utilize the software in silicon infrastructure, an example (that I usually use) could be

```sql
select sum(lo_revenue), d_year, p_brand1
from lineorder, date_dim, part, supplier
where lo_orderdate = d_datekey
and lo_partkey = p_partkey
and lo_suppkey = s_suppkey
and p_category = 'MFGR#12'
and s_region = 'AFRICA'
group by d_year, p_brand1
order by d_year, p_brand1;
```

`jmeter` would change`'MFGR#12'` and `'AFRICA'` for each query issued. 

The main purpsoe of this load generation scenario was to demonstrate the effect of the inmemory option, to do so you first have to set the `inmemory_size` parameter to a value different from zero (keep in mind that the SGA is reduced by that amount of memory) Something in the area of 10% of the SGA size should already have a notcieable effect.

Next step is to move all tables under inmemory control (I only quote the actual command for one table)

```sql
alter table ssb.part inmemory memcompress for query high priority critical;
...
```

(replacing the last part of this command with `no inmeory` would move the tables bcak into the row store)

You should see a huge difference in throughput and execution time between execution using the inmemory option and running it in the old fashioned way. In parallel you will notice a large load on the storage infrastructure when executing without the inmemory option

Copyright (c) 2020, Oracle and/or its affiliates. Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.