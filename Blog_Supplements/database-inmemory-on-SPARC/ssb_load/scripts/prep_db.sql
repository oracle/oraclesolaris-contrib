create bigfile tablespace ssb datafile 'ts_ssb' size 100G  autoextend on next 1G;
grant connect, resource to ssb identified by ssb;
alter user ssb default tablespace ssb;
conn ssb/ssb

drop table lineorder;
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
drop table part;
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
drop table supplier;
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
drop table customer;
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
drop table date_dim;
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

