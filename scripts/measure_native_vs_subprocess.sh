$ hyperfine --warmup 1 --runs 3 --parameter-list metric pylinecount,linecount --parameter-list workers 1,4 'pyrepositoryminer branch ~/bare-repos/Cockpit.git | pyrepositoryminer commits ~/bare-repos/Cockpit.git | pyrepositoryminer analyze --workers {workers} ~/bare-repos/Cockpit.git - {metric}'

Benchmark #1: pyrepositoryminer branch ~/bare-repos/Cockpit.git | pyrepositoryminer commits ~/bare-repos/Cockpit.git | pyrepositoryminer analyze --workers 1 ~/bare-repos/Cockpit.git - pylinecount
  Time (mean ± σ):     11.889 s ±  0.016 s    [User: 11.254 s, System: 1.048 s]
  Range (min … max):   11.880 s … 11.907 s    3 runs

Benchmark #2: pyrepositoryminer branch ~/bare-repos/Cockpit.git | pyrepositoryminer commits ~/bare-repos/Cockpit.git | pyrepositoryminer analyze --workers 1 ~/bare-repos/Cockpit.git - linecount
  Time (mean ± σ):     31.852 s ±  0.142 s    [User: 18.537 s, System: 17.080 s]
  Range (min … max):   31.764 s … 32.016 s    3 runs

Benchmark #3: pyrepositoryminer branch ~/bare-repos/Cockpit.git | pyrepositoryminer commits ~/bare-repos/Cockpit.git | pyrepositoryminer analyze --workers 4 ~/bare-repos/Cockpit.git - pylinecount
  Time (mean ± σ):      4.316 s ±  0.019 s    [User: 15.534 s, System: 1.295 s]
  Range (min … max):    4.296 s …  4.334 s    3 runs

Benchmark #4: pyrepositoryminer branch ~/bare-repos/Cockpit.git | pyrepositoryminer commits ~/bare-repos/Cockpit.git | pyrepositoryminer analyze --workers 4 ~/bare-repos/Cockpit.git - linecount
  Time (mean ± σ):     28.004 s ±  0.769 s    [User: 47.573 s, System: 80.543 s]
  Range (min … max):   27.404 s … 28.871 s    3 runs

Summary
  'pyrepositoryminer branch ~/bare-repos/Cockpit.git | pyrepositoryminer commits ~/bare-repos/Cockpit.git | pyrepositoryminer analyze --workers 4 ~/bare-repos/Cockpit.git - pylinecount' ran
    2.75 ± 0.01 times faster than 'pyrepositoryminer branch ~/bare-repos/Cockpit.git | pyrepositoryminer commits ~/bare-repos/Cockpit.git | pyrepositoryminer analyze --workers 1 ~/bare-repos/Cockpit.git - pylinecount'
    6.49 ± 0.18 times faster than 'pyrepositoryminer branch ~/bare-repos/Cockpit.git | pyrepositoryminer commits ~/bare-repos/Cockpit.git | pyrepositoryminer analyze --workers 4 ~/bare-repos/Cockpit.git - linecount'
    7.38 ± 0.05 times faster than 'pyrepositoryminer branch ~/bare-repos/Cockpit.git | pyrepositoryminer commits ~/bare-repos/Cockpit.git | pyrepositoryminer analyze --workers 1 ~/bare-repos/Cockpit.git - linecount'