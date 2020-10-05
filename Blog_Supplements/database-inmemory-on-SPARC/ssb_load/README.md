```fixed
benchmark/export.csv.     Parameters used by jmeter to generate the queries
          load-cfg.jmx    Benchmark configuration file to be opened with jmeter
          query.sql       One example query used in 'load-cfg.jmx'
          
scripts/prep-db.sql       Script to prepare the database for the benchmark
        mv-inmemory.sql   Moves all tables under inmemory control
        no-inmemory.sql   Resets tables back to default treatment
        dump-im.sql       Dumps data related population of inmemory area
        
sqlldr                    All control file sneeded to load *.tbl files into database
```

