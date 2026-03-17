# Workflow Summary

This summary is derived from the latest workflow export stored in the repository.

## Start-node inputs
- `raw_scripts`
  - Label in export: transcript input
  - Type: `file-list`
  - Allowed file type: `document`
  - Upload method in export: `local_file`
  - Required: `false`
- `photos`
  - Label in export: image input
  - Type: `file-list`
  - Allowed file type: `image`
  - Upload method in export: `local_file`
  - Required: `false`
- `scene`
  - Label: `scene`
  - Type: `text-input`
  - Required: `false`

## End-node output
- The latest export exposes exactly one workflow output:
  - `full_info_with_image_des`
  - Type: `array[file]`

## What the skill should assume
- Either or both inputs may be provided.
- The workflow contains both a document extraction path and an image-processing path, so the script should support multiple files for each input.
- The `scene` text input should be passed through when the user provides a research scene.
- The latest workflow should expose its main result under `data.outputs.full_info_with_image_des`.
- That value is currently expected to be an `array[file]`.
- If the start node or end node changes again in Dify, update the skill scripts and this file together.

## Maintenance rule
- If the user replaces the Dify workflow export with a newer version, re-check the start node before changing the script or the trigger description.
