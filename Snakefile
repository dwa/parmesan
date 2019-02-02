

from pathlib import Path
samples = [('parquets'/x.relative_to('QVDs').parent / (x.stem + '.pq')).as_posix() for x in Path('QVDs').glob('**/*.qvd')]


rule all:
    input: samples

# rule prune:

rule convert_qvds:
    input:
        "QVDs/{table}.qvd"
    output:
        "parquets/{table}.pq"
    # conda:
    #     "envs/qvds.yaml"
    # threads: 8
    # benchmark:
    #     "benchmarks/{table}.benchmark"
    # log: "logs/{table}.log"
    shell:
#        "bash -c 'mkdir -p $(dirname {output}); touch {output}'"
        "bash -c 'mkdir -p $(dirname {output}); convert-qvd-to-parquet \"{input}\" --out \"{output}\"  --overwrite'"
