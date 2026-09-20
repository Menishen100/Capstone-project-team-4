# Paired Dataset Generation Protocol

## Purpose

This Week 5 workflow is Menishen's integration layer between Arthur's clean
image validation and Exzavier's LSB embedder. It produces exactly one
lossless PNG stego counterpart for every validated clean source and writes the
metadata needed to reproduce later experiments.

The workflow does not alter the clean source image and does not implement an
embedding algorithm. It calls the team-owned src.lsb_embedder.embed_lsb
function after the clean collection has passed src.evaluation.validate_dataset.

## Required clean-source conditions

Before generation, the clean collection must contain exactly 100 legally
usable PNG or BMP files in mode L or RGB. The inventory file
data/clean_metadata.csv must have one truthful row for each clean image:

~~~
source_id,filename,source_license_note
~~~

The generator fails rather than fabricating a source or license note. This
protects the project requirement that every paired image is traceable to a
legally usable clean source.

## Output metadata

The generator writes data/metadata.csv using this schema:

~~~
source_id,clean_filename,stego_filename,payload_rate,random_seed,color_mode,width,height,split,format,source_license_note,generation_status,payload_bytes,capacity_bits,embedded_bits,changed_values
~~~

Each row represents one clean/stego pair. It stores the required source
identifier, payload rate, color mode, dimensions, random seed, and split,
along with the source/license note and embedder diagnostics.

## Split rule

The workflow assigns a split by source_id before generating stego output.
Both members of a pair use that one row and therefore cannot be placed in
different splits.

| Split | Clean images | Stego images | Pairs |
| --- | ---: | ---: | ---: |
| Development | 60 | 60 | 60 |
| Validation | 20 | 20 | 20 |
| Held-out test | 20 | 20 | 20 |

## Reproducible generation

Run the following command from the repository root after the clean inventory
has been completed with real source and license information:

~~~powershell
python -m src.evaluation.generate_dataset dataset/clean data/clean_metadata.csv dataset/stego data/metadata.csv --payload-rate 0.25 --seed 20260920
~~~

The master seed is deterministically combined with each source_id, so the
same clean files, inventory, payload rate, and master seed produce the same
per-image seeds, metadata, and stego pixel output. The command protects
existing stego files. Use --overwrite only after reviewing any earlier output
that is being replaced.

## Integrity checks

The workflow validates that every required metadata field is populated, source
IDs and filenames are unique, every clean filename maps to the expected stego
filename, both files exist, all split totals are 60/20/20, and the collection
contains exactly 100 pairs. Tests also verify generation on a complete
100-pair fixture, deterministic reproduction, invalid pair mappings, and
rejection of an incomplete clean inventory.
