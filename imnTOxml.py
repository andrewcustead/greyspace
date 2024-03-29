#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

from core import utils
from core.api.grpc.client import CoreGrpcClient
from core.errors import CoreCommandError

if __name__ == "__main__":
    # parse flags
    parser = argparse.ArgumentParser(description="Converts CORE imn files to xml")
    parser.add_argument("-f", "--file", dest="file", help="imn file to convert")
    parser.add_argument(
        "-d", "--dest", dest="dest", default=None, help="destination for xml file, defaults to same location as imn"
    )
    args = parser.parse_args()

    # validate provided file exists
    imn_file = Path(args.file)
    if not imn_file.exists():
        print(f"{args.file} does not exist")
        sys.exit(1)

    # validate destination
    if args.dest is not None:
        dest = Path(args.dest)
        if not dest.exists() or not dest.is_dir():
            print(f"{dest.resolve()} does not exist or is not a directory")
            sys.exit(1)
        xml_file = Path(dest, imn_file.with_suffix(".xml").name)
    else:
        xml_file = Path(imn_file.with_suffix(".xml").name)

    # validate xml file
    if xml_file.exists():
        print(f"{xml_file.resolve()} already exists")
        sys.exit(1)

    # run provided imn using core-gui batch mode
    try:
        print(f"running {imn_file.resolve()} in batch mode")
        output = utils.cmd(f"core-gui --batch {imn_file.resolve()}")
        last_line = output.split("\n")[-1].strip()

        # check for active session
        if last_line == "Another session is active.":
            print("need to restart core-daemon or shutdown previous batch session")
            sys.exit(1)

        # parse session id
        m = re.search(r"Session id is (\d+)\.", last_line)
        if not m:
            print(f"failed to find session id: {output}")
            sys.exit(1)
        session_id = int(m.group(1))
        print(f"created session {session_id}")

        # save xml and delete session
        client = CoreGrpcClient()
        with client.context_connect():
            print(f"saving xml {xml_file.resolve()}")
            client.save_xml(session_id, str(xml_file))

            print(f"deleting session {session_id}")
            client.delete_session(session_id)
    except CoreCommandError as e:
        print(f"core-gui batch failed for {imn_file.resolve()}: {e}")
        sys.exit(1)