#!/usr/bin/env python3

from subprocess import call
from datetime import datetime

VERSION_FILE = "./root/contants/VERSION.py"
UPDATE_GIT = "git add -A && git commit -m 'updated version v%s'"


def main():
    with open(VERSION_FILE, "r") as vfile:
        updated = False
        version = vfile.read()
        version = version.replace('"', "")
        version = version.split("=")[1]
        version = [int(v) for v in version.split(".")]
        if version[-1] != 9:
            version[-1] += 1
            updated = True
        else:
            version[-1] = 0
        if version[1] != 9 and updated != True:
            version[1] += 1
            updated = True
        elif updated != True:
            version[-1] += 1
        if updated != True:
            version[0] += 1
    version = ".".join([str(v) for v in version])

    with open(VERSION_FILE, "w") as vfile:
        print(f"* Creating version {version}")
        cmd = UPDATE_GIT % version
        date = str(datetime.now().strftime("%d/%m/%Y"))
        version = f'VERSION="{version}"\nLAST_UPDATE="{date}"'
        vfile.write(f"#\!/usr/bin/env python3\n{version}")

    call(cmd, shell=True)


if __name__ == "__main__":
    main()