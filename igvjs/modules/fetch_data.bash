#!/bin/bash

project_id="$1"
pipeline_name="$2"
workspace="$3"

if [ "${project_id}" = "variant-calling" ]; then
  mkdir -p /usr/local/bin/igv-flask/igvjs/static/data/public/igv-data/variant-calling/bams
  mkdir -p /usr/local/bin/igv-flask/igvjs/static/data/public/igv-data/variant-calling/vcfs
fi

# download sorted bams and their index
cd /usr/local/bin/igv-flask/igvjs/static/data/public/igv-data/variant-calling/bams
gsutil -m cp ${workspace}/analysis/${pipeline_name}/Sam2SortedBam/*/*sorted.ba*

# download vcf files and their index
cd /usr/local/bin/igv-flask/igvjs/static/data/public/igv-data/variant-calling/vcfs
gsutil -m cp ${workspace}/analysis/${pipeline_name}/HaplotypeCaller/*/*vc*

echo "Done!"
