import re
import requests
from collections import defaultdict
import json
import argparse

def extract_latest_versions_from_url(url: str):
    response = requests.get(url)
    response.raise_for_status()
    text = response.text

    # extract versions from html schema, ignore release candidates
    versions = re.findall(r'\b(\d+\.\d+\.\d+)(?!-rc)\b', text)

    return versions


def parse_version_policy(value: str):
    try:
        major, num_majorminor, num_patch = map(int, value.split(":"))
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Version policy must use the format MAJOR:MINOR_COUNT:PATCH_COUNT"
        )

    if major < 1 or num_majorminor < 1 or num_patch < 1:
        raise argparse.ArgumentTypeError(
            "Major, minor count, and patch count must be greater than zero"
        )

    return major, num_majorminor, num_patch


def select_latest_versions(versions: list, version_policies: dict = None):
    grouped = defaultdict(list)
    for v in versions:
        major_minor = '.'.join(v.split('.')[:2])
        patch = int(v.split('.')[2])
        grouped[major_minor].append(patch)

    sorted_major_minor = sorted(
        grouped.keys(),
        key=lambda x: list(map(int, x.split('.')))
    )

    result = []

    if version_policies:
        for major, policy in sorted(version_policies.items()):
            num_majorminor, num_patch = policy
            major_minor_versions = [
                mm for mm in sorted_major_minor
                if int(mm.split('.')[0]) == major
            ]
            last_major_minor = major_minor_versions[-num_majorminor:]

            for mm in last_major_minor:
                patches = sorted(grouped[mm])[-num_patch:]
                result.extend([f"{mm}.{p}" for p in patches])
    else:
        last_major_minor = sorted_major_minor[-3:]

        for mm in last_major_minor:
            patches = sorted(grouped[mm])[-5:]
            result.extend([f"{mm}.{p}" for p in patches])

    return result


def update_json_with_versions(json_file: str, versions: list):
    # create JSON structure
    data = {
        "openshift_versions": versions
    }

    # write to the file
    with open(json_file, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")  # add trailing newline


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process mirror paths and file path with version info."
    )
    parser.add_argument("file_path", help="The path to the JSON file")
    parser.add_argument(
        "--url",
        type=str,
        default="mirror.openshift.com",
        help="The host to process (default: mirror.openshift.com)"
    )
    parser.add_argument(
        "--path",
        action="append",
        help=(
            "The mirror path to process; may be specified multiple times "
            "(default: /pub/openshift-v4/clients/ocp/)"
        )
    )
    parser.add_argument(
        "--version-policy",
        type=parse_version_policy,
        action="append",
        help=(
            "Version selection policy in MAJOR:MINOR_COUNT:PATCH_COUNT format; "
            "may be specified multiple times. If omitted, the 3 latest "
            "major.minor versions are selected, with up to 5 patches each."
        )
    )
    args = parser.parse_args()

    paths = args.path or ["/pub/openshift-v4/clients/ocp/"]

    version_policies = {}
    for policy in args.version_policy or []:
        major, num_majorminor, num_patch = policy
        if major in version_policies:
            parser.error(f"Version policy for major {major} was specified more than once")
        version_policies[major] = (num_majorminor, num_patch)

    versions = []
    for path in paths:
        url = f"https://{args.url.rstrip('/')}/{path.lstrip('/')}"
        versions.extend(extract_latest_versions_from_url(url))

    versions = list(set(versions))
    versions = select_latest_versions(versions, version_policies)

    json_file = args.file_path
    update_json_with_versions(json_file, versions)

    print(f"Updated {json_file} with the following versions:")
    print("\n".join(f"- {v}" for v in versions))
