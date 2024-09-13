#!/usr/bin/python3
# -*- Coding : UTF-8 -*-

"""
A little helper to check for newer releases on github
"""


__author__ = 'Benjamin Schubert, ben.c.schubert@gmail.com'

__version__ = "0.1.0"


import json
from urllib.request import urlopen


class InexistentReleaseTagError(BaseException):
    """
    An Exception class when a Release Tag is not found in the list of releases
    """
    def __init__(self, release_tag: str="given") -> None:
        self.release_tag = release_tag

    def __str__(self) -> str:
        return "The release tag '{}' does not exists".format(self.release_tag)


def current_version_id(current_version: str, versions: list) -> dict:
    """
    Retrieves the current version based on the tag name from a list of versions
    :param current_version: the current version tag
    :param versions: a list of all versions
    :return: a dictionary containing all information about the current version
    """
    for version in versions:
        if version["tag_name"] == current_version:
            return version
    raise InexistentReleaseTagError(current_version)


def get_releases(user: str, repository: str) -> list:
    """
    Gets all releases from the github api for the given user's repository
    :param user: the user who owns the repository
    :param repository: the repository
    :return: a list of releases
    """
    url = "https://api.github.com/repos/{user}/{repository}/releases".format(user=user, repository=repository)
    binary_data = urlopen(url).read()
    data = json.loads(binary_data.decode("UTF-8"))
    return data


def get_latest_version(current_version: str, versions: list) -> str:
    """
    Checks in a list of version if any of them is newer than the first.
    :param current_version: the current version of the program, with all information
    :param versions: all program versions as returned by github
    :return: the latest version
    """
    latest_version = current_version_id(current_version, versions)
    for version in versions:
        if latest_version["id"] < version["id"]:
            latest_version = version

        return latest_version["tag_name"]


def check_updates(version: str, user: str, repository: str) -> (bool, str):
    """
    Checks if a newer version exists for a program at the given version, on github
    :param version: current program version
    :param user: the user who owns the repository
    :param repository: the repository where the code is hosted
    :return: True and the latest version if a new version exists, False and the current version if not
    """
    versions = get_releases(user, repository)
    latest_version = get_latest_version(version, versions)
    if latest_version != version:
        return True, latest_version
    return False, latest_version