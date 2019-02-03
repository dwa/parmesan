from pathlib import Path

SRC = 'qvd'
TGT = 'pq'

convert_to = [(TGT/x.relative_to(SRC).parent / (x.stem + '.pq')).as_posix()
              for x in Path(SRC).glob('**/*.qvd')]

rule all:
    input: convert_to

rule sync_convert:
    input:
        f"{SRC}/{{table}}.qvd"
    output:
        f"{TGT}/{{table}}.pq"
    # conda:
    #     "envs/qvds.yaml"
    # threads: 8
    # benchmark:
    #     "benchmarks/{table}.benchmark"
    # log: "logs/{table}.log"
    shell:
        "bash -c 'mkdir -p $(dirname {output}); convert-qvd-to-parquet \"{input}\" --out \"{output}\"  --overwrite'"
