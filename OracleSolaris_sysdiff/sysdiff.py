#!/usr/bin/python3.7
#
# Copyright (c) 2020, 2022, Oracle and/or its affiliates.
#
"""sysdiff script"""

__version__ = "20220614"

import sys
import os
import stat
import fileinput
import subprocess
import time
import argparse
import configparser


class ContentsEntry:
    """contents file entry"""

    def __init__(self):
        self.ftype = None
        self.major = None
        self.minor = None
        self.mode = None
        self.owner = None
        self.group = None
        self.size = None
        self.cksum = None
        self.modtime = None
        self.target = None
        self.inode = None
        self.list = None
        self.pkglist = None


class FileDesc:
    """File description for the IPS packaging"""

    #
    # path is the path to file, si is stat_result for the file
    #
    def __init__(self, si, entry):
        self.type = "unknown"
        self.mode = stat.S_IMODE(si.st_mode)
        self.owner = None
        self.group = None
        self.modtime = int(si.st_mtime)
        self.nlink = si.st_nlink
        self.inode = (si.st_dev, si.st_ino)
        self.target = None
        self.comment = ""
        self.preserve = None

        self.owner = get_user(si.st_uid)
        if self.owner is None:
            self.comment += f" Unmatched uid: {si.st_uid}"

        self.group = get_group(si.st_gid)
        if self.group is None:
            self.comment += f" Unmatched gid: {si.st_gid}"

        #
        # We cannot distinguish between file and hardlink for 'new' files -
        # all hardlinks for given file are identical from the OS
        # point of view - so we initially set every regular file as 'file',
        # process the contents to take advantage of known links, and,
        # after the directory scan is complete, we'll re-work the 'new'
        # files assuming first encountered file for given inode is 'file'
        # and the remaining ones are 'hardlink'
        # IPS does not deal with packaging block or character device files
        # nor pipes or doors - all of them have to be handled by the app or
        # driver itself. Note that /dev/ entries can be delivered, but these
        # are plain symlinks into /devices/, not special files. All of these
        # files will end up as the 'unhandled' type, as we cannot package them.
        #
        if stat.S_ISLNK(si.st_mode):
            self.type = "link"
            self.target = os.readlink(entry.path)
        elif stat.S_ISDIR(si.st_mode):
            self.type = "dir"
        elif stat.S_ISREG(si.st_mode):
            self.type = "file"
            if self.nlink > 1:
                self.type = "hardlink"
                if self.inode in hardlinks:
                    self.target = hardlinks[self.inode]
        elif stat.S_ISFIFO(si.st_mode):
            self.type = "unhandled"
            self.comment += "file type: FIFO"
        elif stat.S_ISCHR(si.st_mode):
            self.type = "unhandled"
            self.comment += "file type: character device"
        elif stat.S_ISBLK(si.st_mode):
            self.type = "unhandled"
            self.comment += "file type: block device"
        elif stat.S_ISSOCK(si.st_mode):
            self.type = "unhandled"
            self.comment += "file type: socket"
        elif stat.S_ISDOOR(si.st_mode):
            self.type = "unhandled"
            self.comment += "file type: door"
        elif stat.S_ISPORT(si.st_mode):
            self.type = "unhandled"
            self.comment += "file type: event port"


zone_name = ""
zone_root = ""
tstamp = time.strftime("%Y%m%d%H%M%S")
output_dir = "/var/tmp"
new_files_fname = "new_files"
mod_files_fname = "mod_files"
mod_vol_files_fname = "mod_vol_files"
matched_files_fname = "matched_files"
pkg_fname = "pkg"
param_fname = "params"
param_section = "params"
params_read = False
pkg_file = None
defcache = "cache"
volTypes = {"v", "e"}
fileTypes = {"f"} | volTypes
devTypes = {"b", "c"}
dirTypes = {"d", "x"}
linkTypes = {"s", "l"}
excludeDirs = set()
excludeDirsPath = os.path.join(sys.path[0], "excludeDirs")
knownNewFiles = set()
knownModFiles = set()
pkglist = set()
newpkgs = set()
contents = {}
passwd = {}
group = {}
new_files = {}
mod_files = {}
mod_vol_files = {}
matched_files = {}
hardlinks = {}
enable_checksums = False
plain_output = False
quiet = False
preserve_age = 5
now = time.time()
pkg_fmri = "testpackage@1.0"
pkg_summary = "test package"
pkg_desc = None


def parse_group():
    """Parse the group file from the target zone to populate cache"""
    for line in fileinput.input(zone_root + "/etc/group"):
        s = line.split(":")
        if s[2] in group:
            print("Duplicate entry in /etc/group|" + line + "|\n")
            continue
        group[s[2]] = s[0]


def parse_passwd():
    """Parse the  psswd file from the target zone to populate cache"""
    for line in fileinput.input(zone_root + "/etc/passwd"):
        s = line.split(":")
        if s[2] in passwd:
            print("Duplicate entry in /etc/passwd|" + line + "|\n")
            continue
        passwd[s[2]] = s[0]


def get_group(gid):
    """Convert the gid to group name. The group cache is consulted first, then
    a call to the naming service is done. If a match is found the result is
    cached"""
    if str(gid) in group:
        return group[str(gid)]

    command = ["getent", "group", str(gid)]
    sp = subprocess.run(command, capture_output=True, text=True, check=False)
    if sp.returncode != 0:
        if not quiet:
            print("command\n", " ".join(command), "\nfailed")
        return None

    s = sp.stdout.split(":")
    if len(s) == 4:
        group[str(gid)] = s[0]
        return s[0]

    return None


def get_user(uid):
    """Convert the uid to user name. The passwd cache is consulted first, then
    a call to the naming service is done. If a match is found the result is
    cached"""
    if str(uid) in passwd:
        return passwd[str(uid)]

    command = ["getent", "passwd", str(uid)]
    sp = subprocess.run(command, capture_output=True, text=True, check=False)
    if sp.returncode != 0:
        if not quiet:
            print("command\n", " ".join(command), "\nfailed")
        return None

    s = sp.stdout.split(":")
    if len(s) == 7:
        passwd[str(uid)] = s[0]
        return s[0]

    return None


def get_cksum(path):
    """Calculate the checksum of the file"""
    sp = subprocess.run(
        ("/usr/bin/sum", path), capture_output=True, text=True, check=False
    )

    if sp.returncode != 0:
        sys.stdout.flush()
        sys.stderr.write("sum " + path + " failed\n")
        sys.stderr.write(sp.stderr)
        sys.exit(1)

    s = sp.stdout.split(" ")

    return s[0]


def parse_contents(cpath):
    """Parse the 'contents' file from the target zone"""
    for line in fileinput.input(cpath):
        line = line.rstrip("\n")
        #
        # Skip comments
        #
        if line[0] == "#":
            continue
        #
        # New style entries always start with /
        #
        if line[0] == "/":
            #
            # We split the entry into path, type, class and remainder,
            # which will be further split depending on type
            #
            s = line.split(" ", 3)
            path = s[0]
            entry = ContentsEntry()
            entry.ftype = s[1]
            if entry.ftype in fileTypes:
                s = s[3].split(" ", 6)
                entry.mode = int(s[0], 8)
                entry.owner = s[1]
                entry.group = s[2]
                entry.size = int(s[3])
                entry.cksum = s[4]
                entry.modtime = int(s[5])
                entry.pkglist = s[6].split(" ")
            elif entry.ftype in dirTypes:
                s = s[3].split(" ", 3)
                entry.mode = int(s[0], 8)
                entry.owner = s[1]
                entry.group = s[2]
                entry.pkglist = s[3].split(" ")
            elif entry.ftype in devTypes:
                s = s[3].split(" ", 5)
                entry.major = s[0]
                entry.minor = s[1]
                entry.mode = int(s[2], 8)
                entry.owner = s[3]
                entry.group = s[4]
                entry.pkglist = s[5].split(" ")
            elif entry.ftype in linkTypes:
                entry.pkglist = s[3].split(" ")
                # if (entry.ftype == "l"):
                #    print(entry.__dict__)
                #    sys.exit()
        else:
            #
            # Parse old style entries
            #
            if not quiet:
                print("Parsing old style entry |" + line + "|\n")
            s = line.split(" ", 3)
            entry = ContentsEntry()
            entry.ftype = s[0]
            path = s[2]
            entry.pkglist = s[3].split(" ")

        if entry.ftype in linkTypes:
            #
            # Link entries have path in format path=rpath - we need to split
            # them for easier matching
            #
            s = path.split("=")
            if len(s) != 2:
                sys.stdout.flush()
                print("Invalid link entry |" + path + "|\n", file=sys.stderr)
                sys.exit(1)
            path = s[0]
            entry.target = s[1]

        #
        # This should never happen - there can be only single entry for each
        # path
        #
        if path in contents:
            sys.stdout.flush()
            print("Duplicate entry for |" + path + "|\n", file=sys.stderr)
            print(entry.__dict__, file=sys.stderr)
            print(contents[path].__dict__, file=sys.stderr)
            sys.exit(1)
        #
        # We check the pkglist for given entry against the 'clean' list
        # to find non-Solaris pkgs installed
        #
        if len(pkglist) != 0:
            for d in entry.pkglist:
                if d.split(":")[0].lstrip("*") not in pkglist:
                    newpkgs.add(d)

        contents[path] = entry


def walk_and_compare(dir_path):
    """Walk the target zone root and match the files against the manifest"""
    try:
        with os.scandir(dir_path) as it:
            for entry in it:
                #
                # We walk the tree from 'outside' of the zone, but the
                # contents list 'internal' paths, so we need to cut off
                # the zone_root at the beginning of the path. The '/' needs
                # to be left in place.
                #
                path = entry.path[len(zone_root):]
                #
                # We skip the excluded dirs first - no point processing them
                # any further
                #
                if entry.is_dir(follow_symlinks=False):
                    if path in excludeDirs:
                        if not quiet:
                            print("Skipping directory |" + path + "|")
                        continue

                si = entry.stat(follow_symlinks=False)
                f = FileDesc(si, entry)
                #
                # If the entry is not matched against the contents database
                # we just record it as 'new'. For directories we do a simple
                # traversal, just adding the contents to new files as well.
                #
                if path not in contents:
                    new_files[path] = f
                    if entry.is_dir(follow_symlinks=False):
                        walk_and_compare(entry.path)
                        continue
                    continue
                #
                # Symlinks are a special case - they don't have their own
                # attributes, only the target. We can handle them ahead of
                # anything else
                #
                if entry.is_symlink():
                    if contents[path].ftype != "s":
                        f.comment += " S " + " file replaced by link"
                        mod_files[path] = f
                        continue
                    if os.readlink(entry.path) == contents[path].target:
                        matched_files[path] = f
                        continue
                    f.comment += (
                        " S |"
                        + os.readlink(entry.path)
                        + "| vs |"
                        + contents[path].target
                        + "|\n"
                    )
                    mod_files[path] = f
                    continue

                #
                # We need to differentiate between regular files which got
                # modified, which is unexpected, and the volatile files, which
                # are expected to change.
                #
                if contents[path].ftype in volTypes:
                    modified_files = mod_vol_files
                    f.preserve = "true"
                else:
                    modified_files = mod_files
                #
                # We need to treat 'link' file entries in a special way
                # since they represent hardlinks, which from the FS point of
                # view are regular files, but 'contents' lists just target
                # for them.
                # On first passage we'll preserve the (fs, inode) tuple and
                # the list where the target entry belongs, and use it for
                # subsequent hardlinks.
                #
                if contents[path].ftype == "l":
                    first_pass = False
                    ldir = dir_path[len(zone_root):]
                    rpath = os.path.normpath(
                        os.path.join(ldir, contents[path].target)
                    )
                    #
                    # If the link target is not in contents, or it's not a file
                    # it's a fatal error because the database is corrupted.
                    #
                    if rpath not in contents:
                        sys.stdout.flush()
                        print(
                            rpath + " not found in contents.", file=sys.stderr
                        )
                        sys.exit(1)

                    if contents[rpath].ftype not in fileTypes:
                        sys.stdout.flush()
                        print(
                            path
                            + " target path "
                            + rpath
                            + " is not a file, type: "
                            + contents[rpath].ftype,
                            file=sys.stderr,
                        )
                        sys.exit(1)

                    if f.nlink == 1:
                        f.comment += (
                            " plain file replaced a hardlink to "
                            + contents[path].target
                        )
                        modified_files[path] = f
                        continue

                    if contents[rpath].inode is None:
                        tsi = os.stat(zone_root + rpath)
                        contents[rpath].inode = (tsi.st_dev, tsi.st_ino)
                        if contents[rpath].inode not in hardlinks:
                            hardlinks[contents[rpath].inode] = rpath
                        elif hardlinks[contents[rpath].inode] != rpath:
                            sys.stdout.flush()
                            print(
                                "hardlinks table contains different entry for"
                                + rpath
                                + " : "
                                + hardlinks[contents[rpath].inode],
                                file=sys.stderr,
                            )
                            sys.exit(1)
                        #
                        # We'll adjust this later if the file does match
                        #
                        first_pass = True
                        contents[rpath].list = modified_files

                    if f.inode == contents[rpath].inode:
                        f.type = "hardlink"
                        f.target = contents[path].target
                        if not first_pass:
                            contents[rpath].list[path] = f
                            continue
                    else:
                        f.type = "hardlink"
                        f.comment += " hardlink pointing to different target"
                        modified_files[path] = f
                        continue
                else:
                    rpath = path
                #
                # Directories are handled in 2 parts - first we handle
                # the recursion, then pass through the attributes matching
                # and handle the directory entry itself
                #
                if entry.is_dir(follow_symlinks=False):
                    walk_and_compare(entry.path)
                    #
                    # It might happen that a directory has replaced a regular
                    # file registered in contents - hopefully it should not
                    # happen often.
                    #
                    if contents[rpath].ftype not in dirTypes:
                        modified_files[path] = f
                        continue
                #
                # We'll test parameters common to all entries first
                #
                # volatile and editable files probably need to be treated
                # more leniently - we expect them to not match.
                #
                if f.owner is not None:
                    if f.owner != contents[rpath].owner:
                        f.comment += (
                            " owner differs "
                            + contents[rpath].owner
                            + " vs "
                            + f.owner
                        )
                        modified_files[path] = f
                        continue
                else:
                    #
                    # The comment already states the uid is not matched, so
                    # by definition the file cannot match a known one
                    #
                    modified_files[path] = f
                    continue
                if f.group is not None:
                    if f.group != contents[rpath].group:
                        f.comment += (
                            " group differs "
                            + contents[rpath].group
                            + " vs "
                            + f.group
                        )
                        modified_files[path] = f
                        continue
                else:
                    #
                    # The comment already states the gid is not matched, so
                    # by definition the file cannot match a known one
                    #
                    modified_files[path] = f
                    continue
                if f.mode != contents[rpath].mode:
                    f.comment += (
                        f" mode differs {contents[rpath].mode:04o} vs"
                        f" {f.mode:04o}"
                    )
                    modified_files[path] = f
                    continue
                if entry.is_dir(follow_symlinks=False):
                    matched_files[path] = f
                    continue
                if stat.S_ISCHR(si.st_mode):
                    if contents[rpath].ftype != "c":
                        f.comment += (
                            " file type mismatch char device vs "
                            + contents[rpath].ftype
                        )
                        modified_files[path] = f
                        continue
                    if os.major(si.rdev) != contents[rpath].major:
                        f.comment += (
                            " device major mismatch "
                            f" {contents[rpath].major:d}"
                            f" vs {os.major(si.rdev):d}"
                        )
                        modified_files[path] = f
                        continue
                    if os.minor(si.rdev) != contents[rpath].minor:
                        f.comment += (
                            " device minor mismatch "
                            f" {contents[rpath].minor:d}"
                            f" vs {os.minor(si.rdev):d}"
                        )
                        modified_files[path] = f
                        continue
                    matched_files[path] = f
                    continue
                if stat.S_ISBLK(si.st_mode):
                    if contents[rpath].ftype != "b":
                        f.comment += (
                            " file type mismatch block device vs "
                            + contents[rpath].ftype
                        )
                        modified_files[path] = f
                        continue
                    if os.major(si.rdev) != contents[rpath].major:
                        f.comment += (
                            " device major mismatch "
                            f" {contents[rpath].major:d}"
                            f" vs {os.major(si.rdev):d}"
                        )
                        modified_files[path] = f
                        continue
                    if os.minor(si.rdev) != contents[rpath].minor:
                        f.comment += (
                            " device minor mismatch "
                            f" {contents[rpath].minor:d}"
                            f" vs {os.minor(si.rdev):d}"
                        )
                        modified_files[path] = f
                        continue
                    matched_files[path] = f
                    continue
                if stat.S_ISREG(si.st_mode):
                    if si.st_size != contents[rpath].size:
                        f.comment += (
                            f" size mismatch {contents[rpath].size:d} vs"
                            f" {si.st_size:d}"
                        )
                        modified_files[path] = f
                        continue
                    if f.modtime != contents[rpath].modtime:
                        f.comment += (
                            " timestamp mismatch"
                            f" {contents[rpath].modtime}"
                            f" vs {f.modtime}"
                        )
                        modified_files[path] = f
                        continue
                    if enable_checksums or contents[path].ftype in volTypes:
                        cksum = get_cksum(entry.path)
                        if cksum != contents[rpath].cksum:
                            f.comment += (
                                f" checksum differs {contents[rpath].cksum} vs"
                                f" {cksum}"
                            )
                            modified_files[path] = f
                            continue
                    contents[rpath].list = matched_files
                    matched_files[path] = f
                    continue
                #
                # All files should have been handled above
                #
                sys.stdout.flush()
                print(
                    "Reached the end of checks: |" + path + "|\n",
                    file=sys.stderr,
                )
                sys.exit(1)

    except OSError as error:
        sys.stdout.flush()
        print(error, file=sys.stderr)


def handle_hardlinks():
    """Walk files lists to match the hardlinks which
    so far weren't matched with targets. Since the hardlink is not
    possible to distinguish from 'target file', we simply assume that
    the first encountered entry for given inode will be 'file', and all
    the remaining ones will be 'hardlinks'"""
    for files in (matched_files, mod_files, mod_vol_files, new_files):
        for path in list(files):
            e = files[path]
            if (e.type == "hardlink") and (e.target is None):
                if e.inode in hardlinks:
                    e.target = os.path.relpath(
                        hardlinks[e.inode], os.path.split(path)[0]
                    )
                else:
                    e.type = "file"
                    hardlinks[e.inode] = path


def print_out_files(filename, filelist, known_list=None):
    """Print out the file list in the requested format"""
    if preserve_age > 0:
        cutoff = now - (preserve_age * 86400)
    else:
        cutoff = 0

    try:
        with open(filename, "a", encoding="utf-8") as f:
            for path in sorted(list(filelist)):
                if known_list is not None:
                    if path in known_list:
                        continue
                if plain_output:
                    f.write(f"{path}\n")
                    continue
                e = filelist[path]
                if e.comment:
                    f.write(f"# {e.comment}\n")
                if e.type == "unhandled":
                    f.write("# ")
                f.write(e.type)
                f.write(f' path="{path[1:]}"')
                if e.type == "link":
                    f.write(f' target="{e.target}"')
                elif e.type == "hardlink":
                    f.write(f' target="{e.target}"')
                else:
                    f.write(f" mode={e.mode:04o}")
                    if e.owner is not None:
                        f.write(f" owner={e.owner}")
                    if e.group is not None:
                        f.write(f" group={e.group}")
                    if e.preserve == "true":
                        f.write(" preserve=true")
                    elif cutoff > 0:
                        if e.modtime > cutoff:
                            f.write(" preserve=true")

                f.write("\n")

    except OSError as error:
        sys.stdout.flush()
        print(error, file=sys.stderr)


def emit_results():
    """Handle the processing of results"""
    if plain_output:
        ext = "out"
        filename = f"{output_dir}/{new_files_fname}.{ext}"
    else:
        ext = "p5m"
        filename = f"{output_dir}/{pkg_fname}.{ext}"

    manifest_filename = filename
    config = configparser.ConfigParser()
    config[param_section] = {
        "plain_output": plain_output,
        "zone_root": zone_root,
        "pkg_fmri": pkg_fmri,
        "pkg_file": filename,
    }

    try:
        if not plain_output:
            with open(filename, "x", encoding="utf-8") as f:
                f.write(f"set name=pkg.fmri value={pkg_fmri}\n")
                f.write(f'set name=pkg.summary value="{pkg_summary}"\n')
                if pkg_desc is not None:
                    f.write(f'set name=pkg.description value="{pkg_desc}"\n')
    except OSError as error:
        sys.stdout.flush()
        print(error, file=sys.stderr)

    if not quiet:
        print(f"Writing {filename}")
    print_out_files(filename, new_files, knownNewFiles)
    filename = f"{output_dir}/{mod_files_fname}.{ext}"
    if not quiet:
        print(f"Writing {filename}")
    print_out_files(filename, mod_files, knownModFiles)
    filename = f"{output_dir}/{mod_vol_files_fname}.{ext}"
    if not quiet:
        print(f"Writing {filename}")
    print_out_files(filename, mod_vol_files)
    filename = f"{output_dir}/{matched_files_fname}.{ext}"
    if not quiet:
        print(f"Writing {filename}")
    print_out_files(filename, matched_files)
    try:
        filename = f"{output_dir}/{param_fname}.ini"
        with open(filename, "x", encoding="utf-8") as f:
            config.write(f)
    except OSError as error:
        sys.stdout.flush()
        print(error, file=sys.stderr)

    if plain_output:
        print(f"File lists generated in: {output_dir}")
    else:
        print(
            "IPS package manifest generated:\n"
            + f"{manifest_filename}\n\n"
            + "Please review and adjust it as needed before running "
            + "the next step.\n\n"
            + "Please provide the following directory as results-dir for the "
            + "next steps:\n\n"
            + output_dir
        )
        print("\nThe next step should be 'sysdiff depresolve'")


def parse_ignore(ignore):
    """Parse the ignore file"""
    for p in ignore.split(","):
        p = p.strip().rstrip("/")
        if p[0] != "/":
            sys.stdout.flush()
            print(
                "excluded dir\n" + p + "\nis not an absolute path",
                file=sys.stderr,
            )
            sys.exit(1)
        excludeDirs.add(p)


def load_excludeDirs(path):
    """Load the excludeDirs file"""
    if path is None:
        path = excludeDirsPath

    if not quiet:
        print(f"Loading excluded dirs list from file:\n{path}")

    try:
        for p in fileinput.input(path):
            p = p.strip().rstrip("/")
            if p[0] != "/":
                sys.stdout.flush()
                print(
                    f"In file\n{path}\n"
                    + f"excluded dir\n{p}\nis not an absolute path",
                    file=sys.stderr,
                )
                sys.exit(1)
            excludeDirs.add(p)
    except OSError as error:
        sys.stdout.flush()
        print(
            "Unable to load excluded dirs from file",
            path,
            "error:\n",
            error,
            file=sys.stderr,
        )


def load_known_files():
    """Load the known_files lists"""
    path = os.path.join(sys.path[0], "known_mod_files." + os.uname().machine)
    try:
        for line in fileinput.input(path):
            knownModFiles.add(line.rstrip("\n"))
    except OSError as error:
        sys.stdout.flush()
        print(
            "Unable to load known mod file list from file",
            path,
            "error:\n",
            error,
            file=sys.stderr,
        )
    path = os.path.join(sys.path[0], "known_new_files." + os.uname().machine)
    try:
        for line in fileinput.input(path):
            knownNewFiles.add(line.rstrip("\n"))
    except OSError as error:
        sys.stdout.flush()
        print(
            "Unable to load known new file list from file\n",
            path,
            "\nerror:\n",
            error,
            file=sys.stderr,
        )


def load_pkglist():
    """Load the baseline package list for current architecture"""
    path = os.path.join(sys.path[0], "pkglist." + os.uname().machine)
    try:
        for line in fileinput.input(path):
            pkglist.add(line.rstrip("\n"))
    except OSError as error:
        sys.stdout.flush()
        print(
            "Unable to load pkg list from file\n",
            path,
            "\nerror:\n",
            error,
            file=sys.stderr,
        )


def do_sysdiff(args):
    """Handler for the diff subcommand, executed via args.func(args) in main"""
    global zone_name, zone_root, enable_checksums, plain_output, preserve_age
    global output_dir, pkg_fmri, pkg_summary, pkg_desc, pkg_fname

    zone_name = args.zonename
    enable_checksums = args.chksum
    plain_output = args.plain_output
    if args.preserve_age is not None:
        preserve_age = args.preserve_age

    load_excludeDirs(args.exclude_dirs)

    if args.ignore:
        parse_ignore(args.ignore)

    if args.output_dir is not None:
        output_dir = args.output_dir

    if output_dir[0] != "/":
        sys.stdout.flush()
        print("results dir parent must be an absolute path", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(output_dir):
        sys.stdout.flush()
        print("results dir parent must be a directory", file=sys.stderr)
        sys.exit(1)

    output_dir = f"{output_dir}/{zone_name}-{tstamp}"

    sp = subprocess.run(
        ("/usr/sbin/zoneadm", "-z", zone_name, "list", "-p"),
        capture_output=True,
        text=True,
        check=False,
    )

    if sp.returncode != 0:
        sys.stdout.flush()
        sys.stderr.write("zoneadm failed\n")
        sys.stderr.write(sp.stderr)
        sys.exit(1)

    zi = sp.stdout.split(":")

    if zi[5] != "solaris10":
        sys.stdout.flush()
        sys.stderr.write("zone brand must be solaris10\n")
        sys.exit(1)

    if zi[2] != "installed":
        sys.stdout.flush()
        sys.stderr.write('zone must be in the "installed" state.\n')
        sys.exit(1)

    zone_root = zi[3] + "/root"

    if args.pkg_name is not None:
        pkg_fmri = args.pkg_name
        if "@" in pkg_fmri:
            sys.stdout.flush()
            print("Please don't use '@' in pkg_name", file=sys.stderr)
            sys.exit(1)
    else:
        pkg_fmri = zone_name

    #
    # We don't want the @... part in the filename - it messes up pkgdepend
    #
    pkg_fname = pkg_fmri

    if args.pkg_version is not None:
        pkg_fmri = pkg_fmri + "@" + args.pkg_version
    else:
        pkg_fmri = pkg_fmri + "@1.0"

    if args.pkg_summary is not None:
        pkg_summary = args.pkg_summary
    else:
        pkg_summary = "package generated from " + zone_name

    if args.pkg_desc is not None:
        pkg_desc = args.pkg_desc

    try:
        os.mkdir(output_dir)
    except OSError as error:
        sys.stdout.flush()
        print("Unable to create target dir: " + output_dir, file=sys.stderr)
        print(error, file=sys.stderr)
        sys.exit(1)

    parse_passwd()
    if not quiet:
        print(f"passwd entries: {len(passwd)}")
    parse_group()
    if not quiet:
        print(f"group entries: {len(group)}")
    if not args.full_scan:
        load_known_files()
        if not quiet:
            print(f"known new files loaded: {len(knownNewFiles)}")
            print(f"known mod files loaded: {len(knownModFiles)}")
    else:
        if not quiet:
            print("skipping known new/modified files lists")
    load_pkglist()
    if not quiet:
        print(f"pkgs loaded: {len(pkglist)}")
    parse_contents(zone_root + "/var/sadm/install/contents")
    if not quiet:
        print(f"contents entries: {len(contents)}")
    if len(newpkgs) != 0:
        print(f"{len(newpkgs)} non-Solaris pkgs found:")
        for p in sorted(newpkgs):
            print(p)
    else:
        if not quiet:
            print("no non-Solaris pkgs found")
    walk_and_compare(zone_root)
    if not quiet:
        print(f"new_files: {len(new_files)}")
        print(f"matched_files: {len(matched_files)}")
        print(f"mod_files: {len(mod_files)}")
        print(f"mod_vol_files: {len(mod_vol_files)}")
    handle_hardlinks()
    emit_results()


def read_params():
    """Read and parse the params file to initialize the internal state"""
    global zone_root, plain_output, pkg_file, params_read, pkg_fmri

    config = configparser.ConfigParser()
    try:
        filename = f"{output_dir}/{param_fname}.ini"
        with open(filename, "r", encoding="utf-8") as f:
            config.read_file(f)
    except OSError as error:
        sys.stdout.flush()
        print(f"Unable to open params file: {filename}", file=sys.stderr)
        print(error, file=sys.stderr)
        sys.exit(1)

    if param_section not in config.sections():
        sys.stdout.flush()
        print(
            f"Invalid parameters file - no {param_section} section",
            file=sys.stderr,
        )
        sys.exit(1)

    if "zone_root" in config[param_section]:
        zone_root = config[param_section]["zone_root"]
    else:
        sys.stdout.flush()
        print(
            "Invalid parameters file - 'zone_root' key is missing",
            file=sys.stderr,
        )
        sys.exit(1)
    if "pkg_file" in config[param_section]:
        pkg_file = config[param_section]["pkg_file"]
    else:
        sys.stdout.flush()
        print(
            "Invalid parameters file - 'pkg_file' key is missing",
            file=sys.stderr,
        )
        sys.exit(1)
    if "plain_output" in config[param_section]:
        plain_output = config[param_section].getboolean("plain_output")
    else:
        sys.stdout.flush()
        print(
            "Invalid parameters file - 'plain_output' key is missing",
            file=sys.stderr,
        )
        sys.exit(1)
    #
    # pkg_fmri is used only for the archive subcommand, and it can work without
    # it - we don't have to bail out if it's missing
    #
    if "pkg_fmri" in config[param_section]:
        pkg_fmri = config[param_section]["pkg_fmri"]
    else:
        pkg_fmri = None

    if plain_output:
        sys.stdout.flush()
        print(
            "IPS manifest is needed for IPS package generation.",
            file=sys.stderr,
        )
        print(
            "Please run the 'sysdiff diff' without '-l' flag", file=sys.stderr
        )
        sys.exit(1)

    if not pkg_file.startswith(output_dir):
        sys.stdout.flush()
        print(
            "Corrupt params: path to the manifest does not match results dir",
            file=sys.stderr,
        )
        print(f"pkg: {pkg_file}\ndir: {output_dir}", file=sys.stderr)
        sys.exit(1)

    params_read = True


def do_depresolve(args):
    """Handler for the depresolve subcommand, executed via args.func(args)
    in main"""
    global output_dir

    if not params_read:
        output_dir = args.results_dir
        if output_dir[0] != "/":
            sys.stdout.flush()
            print("results_dir must be an absolute path", file=sys.stderr)
            sys.exit(1)

        if not os.path.isdir(output_dir):
            sys.stdout.flush()
            print("results_dir must be a directory", file=sys.stderr)
            sys.exit(1)
        read_params()

    command = ["pkgdepend", "generate", "-md", zone_root, pkg_file]
    oname = pkg_file + ".dep"
    try:
        with open(oname, "w", encoding="utf-8") as outfile:
            if not quiet:
                print("running command:\n", " ".join(command), "\n")
            sp = subprocess.run(
                command,
                stdout=outfile,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
    except OSError as error:
        sys.stdout.flush()
        print(
            f"Unable to open dependencies file for writing: {oname}",
            file=sys.stderr,
        )
        print(error, file=sys.stderr)
        sys.exit(1)

    if sp.returncode != 0:
        sys.stdout.flush()
        print("command\n", " ".join(command), "\nfailed", file=sys.stderr)
        print(sp.stderr, file=sys.stderr)
        sys.exit(1)

    command = ["pkgdepend", "resolve", "-m", oname]
    if not quiet:
        print("running command:\n", " ".join(command), "\n")

    sp = subprocess.run(command, capture_output=True, text=True, check=False)

    if sp.returncode != 0:
        sys.stdout.flush()
        print("command\n", " ".join(command), "\nfailed", file=sys.stderr)
        print(sp.stderr, file=sys.stderr)
        sys.exit(1)

    print("'sysdiff depresolve' successful, next step is 'sysdiff lint'")


def do_lint(args):
    """Handler for the lint subcommand, executed via args.func(args)
    in main"""
    global output_dir

    if not params_read:
        output_dir = args.results_dir
        if output_dir[0] != "/":
            sys.stdout.flush()
            print("results_dir must be an absolute path", file=sys.stderr)
            sys.exit(1)

        if not os.path.isdir(output_dir):
            sys.stdout.flush()
            print("results_dir must be a directory", file=sys.stderr)
            sys.exit(1)
        read_params()

    if args.cache_dir is not None:
        cache_dir = args.cache_dir
        if cache_dir[0] != "/":
            sys.stdout.flush()
            print("cache_dir must be an absolute path", file=sys.stderr)
            sys.exit(1)
    else:
        cache_dir = f"{output_dir}.{defcache}"

    if not os.path.isdir(cache_dir):
        try:
            os.mkdir(cache_dir)
        except OSError as error:
            sys.stdout.flush()
            print("Unable to create cache dir: " + cache_dir, file=sys.stderr)
            print(error, file=sys.stderr)
            sys.exit(1)

    command = [
        "pkglint",
        "-c",
        cache_dir,
        "-r",
        args.repo,
        pkg_file + ".dep.res",
    ]

    if not quiet:
        print("running command:\n", " ".join(command), "\n")

    sp = subprocess.run(command, capture_output=True, text=True, check=False)

    if sp.returncode != 0:
        sys.stdout.flush()
        print("command\n", " ".join(command), "\nfailed", file=sys.stderr)
        print(sp.stderr, file=sys.stderr)
        sys.exit(1)

    print("'sysdiff lint' successful, next step is 'sysdiff publish'")


def do_publish(args):
    """Handler for the publish subcommand, executed via args.func(args)
    in main"""
    global output_dir

    if not params_read:
        output_dir = args.results_dir
        if output_dir[0] != "/":
            sys.stdout.flush()
            print("results_dir must be an absolute path", file=sys.stderr)
            sys.exit(1)

        if not os.path.isdir(output_dir):
            sys.stdout.flush()
            print("results_dir must be a directory", file=sys.stderr)
            sys.exit(1)
        read_params()

    if args.create:
        if args.publisher is None:
            sys.stdout.flush()
            print(
                "publisher prefix is mandatory for repo creation, "
                + "use --publisher option to provide it",
                file=sys.stderr,
            )
            sys.exit(1)
        command = ["pkgrepo", "create", args.repo]
        if not quiet:
            print("running command:\n", " ".join(command), "\n")

        sp = subprocess.run(
            command, capture_output=True, text=True, check=False
        )

        if sp.returncode != 0:
            sys.stdout.flush()
            print("command\n", " ".join(command), "\nfailed", file=sys.stderr)
            print(sp.stderr, file=sys.stderr)
            sys.exit(1)
        command = [
            "pkgrepo",
            "-s",
            args.repo,
            "set",
            f"publisher/prefix={args.publisher}",
        ]
        if not quiet:
            print("running command:\n", " ".join(command), "\n")

        sp = subprocess.run(
            command, capture_output=True, text=True, check=False
        )

        if sp.returncode != 0:
            sys.stdout.flush()
            print("command\n", " ".join(command), "\nfailed", file=sys.stderr)
            print(sp.stderr, file=sys.stderr)
            sys.exit(1)
    command = [
        "pkgsend",
        "-s",
        args.repo,
        "publish",
        "-d",
        zone_root,
        pkg_file + ".dep.res",
    ]
    if not quiet:
        print("running command:\n", " ".join(command), "\n")

    sp = subprocess.run(command, capture_output=True, text=True, check=False)

    if sp.returncode != 0:
        sys.stdout.flush()
        print("command\n", " ".join(command), "\nfailed", file=sys.stderr)
        print(sp.stderr, file=sys.stderr)
        sys.exit(1)

    print(
        "'sysdiff publish' successful, the package can be converted to"
        + " an archive using 'sysdiff archive'"
    )


def do_archive(args):
    """Handler for the archive subcommand, executed via args.func(args)
    in main"""
    global output_dir, pkg_fmri

    if not params_read:
        output_dir = args.results_dir
        if output_dir[0] != "/":
            sys.stdout.flush()
            print("results_dir must be an absolute path", file=sys.stderr)
            sys.exit(1)

        if not os.path.isdir(output_dir):
            sys.stdout.flush()
            print("results_dir must be a directory", file=sys.stderr)
            sys.exit(1)
        read_params()

    if args.archive is None:
        archive = pkg_file.rstrip("p5m") + "p5p"
    else:
        archive = args.archive

    command = ["pkgrecv", "-s", args.repo, "-a", "-d", archive]
    if args.pkg_fmri is not None:
        pkg_fmri = args.pkg_fmri

    if pkg_fmri is not None:
        command.append(pkg_fmri)

    if not quiet:
        print("running command:\n", " ".join(command), "\n")

    sp = subprocess.run(command, capture_output=True, text=True, check=False)

    if sp.returncode != 0:
        sys.stdout.flush()
        print("command\n", " ".join(command), "\nfailed", file=sys.stderr)
        print(sp.stderr, file=sys.stderr)
        sys.exit(1)

    print(f"{archive} created successfully")


def main():
    """main function handling the argument processing and calling the
    appropriate subcommands handlers"""
    global quiet

    desc = "Produce a diff between current Solaris 10 branded zone "
    desc += "contents and the state based on the SVR4 packaging data "
    desc += "and optionally package them in an IPS package."
    epg = "The first step to analyze a new Solaris 10 branded zone is "
    epg += '"sysdiff diff"'
    parser = argparse.ArgumentParser(description=desc, epilog=epg)
    parser.add_argument(
        "-q",
        default=False,
        dest="quiet",
        action="store_true",
        help="suppress informational output",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=__version__
    )

    subparsers = parser.add_subparsers(dest="cmd", required=True)

    desc = "Produce a diff between current Solaris 10 branded zone "
    desc += "contents and the state based on the SVR4 packaging data."
    parser_diff = subparsers.add_parser("diff", description=desc)
    parser_diff.set_defaults(func=do_sysdiff)
    parser_diff.add_argument(
        "-c",
        default=False,
        dest="chksum",
        action="store_true",
        help="enable checksums for all files (slow)",
    )
    parser_diff.add_argument(
        "-f",
        default=False,
        dest="full_scan",
        action="store_true",
        help="ignore the known new/modified files",
    )
    parser_diff.add_argument(
        "-l",
        default=False,
        dest="plain_output",
        action="store_true",
        help="output plain file list, not IPS manifest",
    )
    parser_diff.add_argument(
        "--exclude-dirs-path",
        dest="exclude_dirs",
        help="location of the file from which the directories to be "
        + "excluded from search are to be read. "
        + f"By default {excludeDirsPath}",
    )
    parser_diff.add_argument(
        "--extra-ignore-dirs",
        type=str,
        dest="ignore",
        help="comma separated list of directories to be ignored during scan "
        + 'appended to the list read from "excludeDirs"',
    )
    parser_diff.add_argument(
        "--results-dir-parent",
        type=str,
        dest="output_dir",
        help="directory where the results directory will be created, "
        + f'by default "{output_dir}" will be used',
    )
    parser_diff.add_argument(
        "--pkg-name",
        type=str,
        dest="pkg_name",
        help="name of the generated package",
    )
    parser_diff.add_argument(
        "--pkg-version",
        type=str,
        dest="pkg_version",
        help="version of the generated package",
    )
    parser_diff.add_argument(
        "--pkg-summary",
        type=str,
        dest="pkg_summary",
        help="short info about the generated package",
    )
    parser_diff.add_argument(
        "--pkg-desc",
        type=str,
        dest="pkg_desc",
        help="long description of the generated package",
    )
    parser_diff.add_argument(
        "--preserve-age",
        type=int,
        dest="preserve_age",
        help=(
            'number of days to be used as threshold for the "preserve"'
            ' heuristic. "0" disables the mechanism, default is '
        )
        + format(preserve_age),
    )
    parser_diff.add_argument(
        "zonename",
        type=str,
        help="name of the target zone (must be Solaris 10 branded zone)",
    )

    desc = "Resolve the dependencies for the package manifest.\n"
    desc += "Wrapper for the 'pkgdepend' command"
    parser_depresolve = subparsers.add_parser(
        "depresolve",
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_depresolve.set_defaults(func=do_depresolve)
    parser_depresolve.add_argument(
        "results_dir",
        metavar="results-dir",
        help="directory where results of 'sysdiff diff' were stored",
    )

    desc = "Validate the manifest before packaging.\n"
    desc += "Wrapper for the 'pkglint' command"
    parser_lint = subparsers.add_parser(
        "lint",
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_lint.set_defaults(func=do_lint)
    parser_lint.add_argument(
        "--s11.4-repo",
        type=str,
        required=True,
        dest="repo",
        help="Solaris 11.4 repo URI",
    )
    parser_lint.add_argument(
        "--cache-dir", type=str, dest="cache_dir", help="cache dir location"
    )
    parser_lint.add_argument(
        "results_dir",
        metavar="results-dir",
        help="directory where results of 'sysdiff diff' were stored",
    )

    desc = "Publish the package based on the prepared manifest.\n"
    desc += "Wrapper for the 'pkgsend publish' command"
    parser_pub = subparsers.add_parser(
        "publish",
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_pub.set_defaults(func=do_publish)
    parser_pub.add_argument(
        "-c",
        default=False,
        dest="create",
        action="store_true",
        help="create a file system based repository for the package",
    )
    parser_pub.add_argument(
        "--target-repo",
        type=str,
        required=True,
        dest="repo",
        help="target repo URI",
    )
    parser_pub.add_argument(
        "--publisher", type=str, help="publisher prefix for the repo"
    )
    parser_pub.add_argument(
        "results_dir",
        metavar="results-dir",
        help="directory where results of 'sysdiff diff' were stored",
    )

    desc = "Generate an archive from the published package.\n"
    desc += "Wrapper for the 'pkgrecv -a' command"
    parser_arch = subparsers.add_parser(
        "archive",
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_arch.set_defaults(func=do_archive)
    parser_arch.add_argument(
        "--source-repo",
        type=str,
        required=True,
        dest="repo",
        help="pkg repo URI (the same as used for the publish command)",
    )
    parser_arch.add_argument("--archive", type=str, help="archive name")
    parser_arch.add_argument(
        "--pkg-fmri",
        type=str,
        dest="pkg_fmri",
        help="FMRI of the package to be archived",
    )
    parser_arch.add_argument(
        "results_dir",
        metavar="results-dir",
        help="directory where results of 'sysdiff diff' were stored",
    )

    args = parser.parse_args()
    quiet = args.quiet

    args.func(args)


if __name__ == "__main__":
    main()
