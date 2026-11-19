# Scripts

This directory contains utility scripts for managing and processing actions related to the Ansible collection for OpenShift. These scripts can be used to extract version information, update configuration files, and perform other maintenance tasks.

## versions-extract.py

This script extracts the latest OpenShift versions from a specified URL and updates a JSON file with this information. It allows customization of the number of major/minor and patch versions to extract.

Arguments:

- `file_path`: The path to the JSON file to update.
- `--url`: (Optional) The URL to process for version extraction (default is `mirror.openshift.com`).
- `--path`: (Optional) The mirror path to process; may be specified multiple times (default is `/pub/openshift-v4/clients/ocp/`).
- `--version-policy`: (Optional) The version selection policy in `MAJOR:MINOR_COUNT:PATCH_COUNT` format; may be specified multiple times. If omitted, the 3 latest major/minor versions are selected, with up to 5 patches for each.

Example usage:

```bash
python3 versions-extract.py .github/openshift-versions.json
```

### Execution

This script is typically executed as part of a GitHub Actions workflow to keep the OpenShift version matrix up to date automatically. See the `.github/workflows/update-version-matrix.yaml` file for an example of how this script is integrated into a CI/CD pipeline.
