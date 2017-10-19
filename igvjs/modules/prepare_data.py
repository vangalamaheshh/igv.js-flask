#!/usr/bin/env python
#vim: syntax=python tabstop=2 expandtab

import json
import subprocess

def prepare_data(data):
  if data["pipeline_name"] == "variant-calling":
    return prepare_variant_calling_data(data)
  else:
    return "Currently only supports variant-calling data"

def prepare_variant_calling_data(data):
  err = download_variant_calling_data(data)
  if err:
    return err
  if data["organism"] == "human":
    with open("/usr/local/bin/igv-flask/igvjs/static/data/public/igv-data/config/ref/human.config.json") as fh:
      json_data = json.load(fh)
    json_data = prepare_variant_json(json_data, data)
    with open("/usr/local/bin/igv-flask/igvjs/static/data/public/igv-data/config/" + data["pipeline_name"] +
                "/" + data["project_id"] + ".json", "w") as ofh:
      json.dump(json_data, ofh)
  else:
    return "Currently only supports human data"
  return None

def prepare_variant_json(json_data, data):
  track_number = 1
  for index in range(0, len(data["sample_ids"])):
    sample_id = data["sample_ids"][index]
    sample_name = data["sample_names"][index]
    bam_track = {
      "url": "static/data/public/igv-data/variant-calling/bams/" + sample_id + ".sorted.bam",
      "name": sample_name,
      "height": 200,
      "order": track_number,
      "type": "alignment"
    }
    track_number += 1
    vcf_track = {
      "url": "static/data/public/igv-data/variant-calling/vcfs/" + sample_id + ".vcf",
      "name": sample_name,
      "height": 200,
      "order": track_number,
      "type": "variant"
    }
    track_number += 1
    json_data["tracks"].extend([bam_track, vcf_track])
  
  return json_data
     

def download_variant_calling_data(data):
  try:
    command = "bash /usr/local/bin/igv-flask/igvjs/modules/fetch_data.bash"
    args = '"' + data["project_id"] + '"' + " " + '"' + data["pipeline_name"] + '"' + " " + '"' + data["workspace"] + '"'
    command_out = subprocess.check_output(command + " " + args, shell = True, stderr = subprocess.STDOUT).decode('utf-8').strip()
  except subprocess.CalledProcessError:
    return "Error in preparing data with gsutil."
  return None 
