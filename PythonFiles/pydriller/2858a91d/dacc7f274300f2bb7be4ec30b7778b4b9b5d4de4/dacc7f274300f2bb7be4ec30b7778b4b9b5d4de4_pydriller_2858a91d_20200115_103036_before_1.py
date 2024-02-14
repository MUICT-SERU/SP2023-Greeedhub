"""
Module that calculates process metrics.
Note: All process metrics are release-duration.
See https://ieeexplore.ieee.org/document/6606589 for more info.
"""

from pathlib import Path
from pydriller.domain.commit import ModificationType
from pydriller.repository_mining import RepositoryMining


class ProcessMetrics:
    """
    This class is responsible to implement the following process metrics:

    * Commit Count: measures the number of commits made to a file
    * Distinct Developers Count: measures the cumulative number of distinct \
      developers that contributed to a file
    * Developers Count Prior Release: counts the number of developer who \
      modified the file during the prior release
    * New Developers Count Prior Release: counts the number of new developer \
      who modified the file during the prior release
    * Normalized Lines Added/Deleted: are the normalized (by the total number \
      of added and deleted lines) added and deleted lines in the file
    """


    def __get_releases(self, path_to_repo: str, from_commit: str = None,
                       to_commit: str  = None):
        """
        Return all releases' sha of a repo between two commits sorted descending from latest.
        :to_commit: the SHA of the commit to stop counting. If None, the
            analysis starts from the latest commit
        :from_commit: the SHA of the commit to start counting. If None, the
            analysis ends to the first commit
        
        :return: set of commit hash
        """
        # Get the sha of all releases in the repo
        releases = set()
        for commit in RepositoryMining(path_to_repo,
                                       from_commit=from_commit,
                                       to_commit=to_commit,
                                       reversed_order=True,
                                       only_releases=True).traverse_commits():
            releases.add(commit.hash)
        
        return releases

    def commits_count(self, path_to_repo: str, filepath: str,
                      from_commit: str = None, to_commit: str = None):
        """
        Return the number of commits made to a file from the first commit to
        the one identified by commit_hash.

        :path_to_repo: path to a single repo
        :to_commit: the SHA of the commit to stop counting. If None, the
            analysis starts from the latest commit
        :from_commit: the SHA of the commit to start counting. If None, the
            analysis ends to the first commit
        :filepath: the path to the file to count for. E.g. 'doc/README.md'

        :return: int number of commits made to the file
        """

        filepath = str(Path(filepath))
        count = 0
        
        #releases = self.__get_releases(path_to_repo, 
        #                               from_commit=from_commit,
        #                               to_commit=to_commit)

        for commit in RepositoryMining(path_to_repo, from_commit=from_commit,
                                       to_commit=to_commit,
                                       reversed_order=True).traverse_commits():
            for modified_file in commit.modifications:
                if filepath in (modified_file.new_path,
                                modified_file.old_path):
                    count += 1

                    if modified_file.change_type == ModificationType.RENAME:
                        filepath = str(Path(modified_file.old_path))

                    break
        return count

    def distinct_dev_count(self, path_to_repo: str, filepath: str,
                           from_commit: str = None, to_commit: str = None):
        """
        Return the cumulative number of distinct developers contributed to
        the file up to the indicated commit.

        :path_to_repo: path to a single repo
        :to_commit: the SHA of the commit to stop counting. If None, the
            analysis starts from the latest commit
        :from_commit: the SHA of the commit to start counting. If None, the
            analysis ends to the first commit
        :filepath: the path to the file to count for. E.g. 'doc/README.md'

        :return: int number of distinct developers contributing to the file
        """
        filepath = str(Path(filepath))
        developers = set()

        for commit in RepositoryMining(path_to_repo, from_commit=from_commit,
                                       to_commit=to_commit,
                                       reversed_order=True).traverse_commits():

            for modified_file in commit.modifications:
                if filepath in (modified_file.new_path,
                                modified_file.old_path):
                    developers.add(commit.author.email.strip())

                    if modified_file.change_type == ModificationType.RENAME:
                        filepath = str(Path(modified_file.old_path))

                    break

        return len(developers)


    def dev_count_prior_release(self, path_to_repo: str, filepath: str,
                                from_commit: str = None, to_commit: str = None):
        """
        Return the number of developers who modified the file during 
        the prior release.

        :path_to_repo: path to a single repo
        :to_commit: the SHA of the commit to stop counting. If None, the
            analysis starts from the latest commit
        :from_commit: the SHA of the commit to start counting. If None, the
            analysis ends to the first commit
        :filepath: the path to the file to count for. E.g. 'doc/README.md'

        :return: int number of developers who contributed to the file during 
            prior release
        """
        developers = set()
        filepath = str(Path(filepath))

        # Get the sha of all releases in the repo
        releases = self.__get_releases(path_to_repo,
                                       from_commit=from_commit,
                                       to_commit=to_commit)
        in_prior_release = False

        for commit in RepositoryMining(path_to_repo, from_commit=from_commit,
                                       to_commit=to_commit,
                                       reversed_order=True).traverse_commits():

            sha = commit.hash
            if sha in releases:
                if not in_prior_release:
                    in_prior_release = True
                    continue # Start count from next iteration
                else:
                    break # Reached another release: stop!

            if not in_prior_release:
                continue

            for modified_file in commit.modifications:

                stop_count = False

                if filepath in (modified_file.new_path,
                                modified_file.old_path):

                    developers.add(commit.author.email.strip())

                    if modified_file.change_type == ModificationType.RENAME:
                        filepath = str(Path(modified_file.old_path))
                    elif modified_file.change_type == ModificationType.ADD:
                        stop_count = True

                    break

                if stop_count:
                    break

        return len(developers)


    def new_dev_count_prior_release(self, path_to_repo: str, filepath: str,
                                    from_commit: str = None, to_commit: str = None):
        """
        Return the number of new developers who modified the file during
        the prior release.

        :path_to_repo: path to a single repo
        :to_commit: the SHA of the commit to stop counting. If None, the
            analysis starts from the latest commit
        :from_commit: the SHA of the commit to start counting. If None, the
            analysis ends to the first commit
        :filepath: the path to the file to count for. E.g. 'doc/README.md'

        :return: int number of new developers who contributed to the file during the prior release
        """

        developers = set()
        duplicates = set()
        filepath = str(Path(filepath))

        # Get the sha of all releases in the repo
        releases = self.__get_releases(path_to_repo,
                                       from_commit=from_commit,
                                       to_commit=to_commit)

        in_prior_release = False
        in_older_release = False

        for commit in RepositoryMining(path_to_repo, from_commit=from_commit, 
                                       to_commit=to_commit,
                                       reversed_order=True).traverse_commits():

            sha = commit.hash
            if sha in releases:
                if not in_prior_release:
                    in_prior_release = True
                    # Start count from next iteration
                    continue
                else:
                    # Reached a release older than the prior
                    in_older_release = True

            if not in_prior_release:
                continue

            for modified_file in commit.modifications:

                stop_count = False

                if filepath in (modified_file.new_path,
                                modified_file.old_path):

                    author = commit.author.email.strip()

                    if in_older_release and author in developers:
                        duplicates.add(author)
                    else:
                        developers.add(author)

                    if modified_file.change_type == ModificationType.RENAME:
                        filepath = str(Path(modified_file.old_path))
                    elif modified_file.change_type == ModificationType.ADD:
                        stop_count = True

                    break

                if stop_count:
                    break

        new_devs = developers - duplicates
        return len(new_devs)


    def normalized_added_lines(self, path_to_repo: str, filepath: str,
                               from_commit: str = None, to_commit: str = None):
        """
        Return the number of normalized (by the total number of added lines)
        added lines in the file.

        :path_to_repo: path to a single repo
        :to_commit: the SHA of the commit to stop counting. If None, the
            analysis starts from the latest commit
        :from_commit: the SHA of the commit to start counting. If None, the
            normalization is given by the total number of added lines from
            the first commit
        :filepath: the path to the file to count for. E.g. 'doc/README.md'

        :return: float number of normalized added lines
        """

        filepath = str(Path(filepath))
        total = 0
        added = 0

        for commit in RepositoryMining(path_to_repo, from_commit=from_commit,
                                       to_commit=to_commit,
                                       reversed_order=True).traverse_commits():

            for modified_file in commit.modifications:
                if filepath in (modified_file.new_path,
                                modified_file.old_path):

                    if commit.hash == to_commit:
                        added = modified_file.added

                    total += modified_file.added
                    if modified_file.change_type == ModificationType.RENAME:
                        filepath = str(Path(modified_file.old_path))

                    break

            if commit.hash == from_commit:
                break

        if total == 0:
            return 0

        return float(added/total)


    def normalized_deleted_lines(self, path_to_repo: str, filepath: str,
                               from_commit: str = None, to_commit: str = None):
        """
        Return the number of normalized (by the total number of deleted lines)
        deleted lines in the file.

        :path_to_repo: path to a single repo
        :to_commit: the SHA of the commit to stop counting. If None, the
            analysis starts from the latest commit
        :from_commit: the SHA of the commit to start counting. If None, the
            normalization is given by the total number of deleted lines from
            the first commit
        :filepath: the path to the file to count for. E.g. 'doc/README.md'

        :return: float number of normalized deleted lines
        """

        filepath = str(Path(filepath))
        total = 0
        deleted = 0

        for commit in RepositoryMining(path_to_repo, from_commit=from_commit,
                                       to_commit=to_commit,
                                       reversed_order=True).traverse_commits():

            for modified_file in commit.modifications:
                if filepath in (modified_file.new_path,
                                modified_file.old_path):

                    if commit.hash == to_commit:
                        deleted = modified_file.removed

                    total += modified_file.removed

                    if modified_file.change_type == ModificationType.RENAME:
                        filepath = str(Path(modified_file.old_path))

                    break

            if commit.hash == from_commit:
                break

        if total == 0:
            return 0

        return float(deleted/total)