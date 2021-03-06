#!/usr/bin/env python2
import sys
import os
from argparse import ArgumentParser
from launchpadlib.credentials import UnencryptedFileCredentialStore
from launchpadlib.launchpad import Launchpad

HERE = os.path.dirname(os.path.abspath(__file__))


def parse_args():
    """
    Parse the command line arguments
    """
    parser = ArgumentParser()
    parser.add_argument('-p', '--merge-proposal', required=True,
                        help='The main part of the URL to the merge proposal, without the hostname.')
    parser.add_argument('-m', '--message', required=True,
                        help='The comment to add to the merge proposal')
    parser.add_argument('-s', '--subject', default=None, help='The subject for the comment')
    return parser.parse_args()


def get_merge_proposal(merge_proposal_url):
    """
    Get the merge proposal for the ``merge_proposal_url``
    """
    lp = Launchpad.login_with('OpenLP CI', 'production', version='devel',
                              credential_store=UnencryptedFileCredentialStore(os.path.join(HERE, 'launchpadcreds.txt')))
    openlp_project = lp.projects['openlp']
    merge_proposals = openlp_project.getMergeProposals()
    for merge_proposal in merge_proposals:
        if str(merge_proposal).endswith(merge_proposal_url):
            return merge_proposal
    return None


def create_comment(merge_proposal, comment, subject):
    """
    Create a comment on the merge proposal
    """
    if not subject:
        subject = 'Jenkins test update'
    merge_proposal.createComment(subject=subject, content=comment)


def main():
    """
    Run the thing
    """
    args = parse_args()
    merge_proposal = get_merge_proposal(args.merge_proposal)
    if not merge_proposal:
        print('No merge proposal with that URL found')
        sys.exit(1)
    else:
        create_comment(merge_proposal, args.message, args.subject)


if __name__ == '__main__':
    main()
