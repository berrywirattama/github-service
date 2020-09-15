#!/bin/python
from argparse import ArgumentParser
from github import Github
import os

class githubService(object):
    def __init__(self):
        parser = ArgumentParser(
            description="Python for github",
            usage='''githubService <function> <action> [<args>]
Function:
  repo              repository
  collab            collaborator

Action:
  add               Add repo or collaborator

Args:
  -u    --user      Username
        --access    Access Token
  -p    --pass      Password
  -r    --repo      Repository name
        --private   Make repository become private
  -c    --collab    Collaborator name

If you not define the GITHUB_USERNAME and GITHUB_PASSWORD or GITHUB_ACCESSTOKEN in environment you must command like this:
githubService <function> <action>  -u '$USERNAME' -p '$PASSWORD'  [<args>]
githubService <function> <action>  --access '$ACCESS_TOKEN' [<args>]
''')
        parser.add_argument('function', choices=['collab', 'repo'], metavar='Function', type=str)
        parser.add_argument('action', choices=['add'], metavar='Action', type=str)
        parser.add_argument('-u', '--user', dest='username', metavar='Username login', type=str, default=False)
        parser.add_argument('--access', dest='accessToken', metavar='Access token login', type=str, default=False)
        parser.add_argument('-p', '--pass', dest='password', metavar='Password login', type=str, default=False)
        parser.add_argument('-r', '--repo', dest='repository', metavar='Repository for collaborator', type=str, default=False)
        parser.add_argument('--private', dest='privateRepository', action='store_true', default=False)
        parser.add_argument('-c', '--collab', dest='collaborators', metavar='Collaborators', action='append', type=str)
        args = parser.parse_args()

        #LOGIN
        print("LOGIN....")
        if args.username and args.password:
            self.username = args.username
            self.password = args.password
        elif args.accessToken:
            self.accessToken = args.accessToken
        elif os.getenv('GITHUB_USERNAME') and os.getenv('GITHUB_PASSWORD'):
            self.username = os.getenv('GITHUB_USERNAME')
            self.password = os.getenv('GITHUB_PASSWORD')
        elif os.getenv('GITHUB_ACCESSTOKEN'):
            self.accessToken = os.getenv('GITHUB_ACCESSTOKEN')
        if self.username and self.password:
            self.github_login = Github(self.username, self.password)
        elif self.accessToken:
            self.github_login = Github(self.accessToken)
        self.user_github = self.github_login.get_user()

        self.function = args.function
        self.action = args.action
        self.repository = args.repository
        self.privateRepository = args.privateRepository
        self.collaborators = args.collaborators
        getattr(self, self.function)()

    def repo(self):
        if self.action == "add":
            # githubService repo add -r ${REPO_NAME}
            # githubService repo add -r ${REPO_NAME} --private
            listRepo = []
            for repo in self.user_github.get_repos():
                listRepo.append(repo.name)
            if self.repository in listRepo:
                print("The repository already exist")
            else:
                if self.privateRepository:
                    newRepo = self.user_github.create_repo(self.repository, private=self.privateRepository)
                    print("The {} private repository already created".format(self.repository))
                else:
                    newRepo = self.user_github.create_repo(self.repository)
                    print("The {} public repository already created".format(self.repository))

    def collab(self):
        if self.action == "add":
            # githubService collab add -r ${REPO_NAME} -c ${COLLAB_NAME} -c ${COLLAB_NAME}
            listCollaborators = []
            collaborators = []
            repositoryName = self.username + '/' + self.repository
            repository = self.github_login.get_repo(repositoryName)
            getCollaborators = repository.get_collaborators()
            for getCollaborator in getCollaborators:
                listCollaborators.append(getCollaborator.login)
            collaborators = self.collaborators
            for collaborator in collaborators:
                if collaborator in listCollaborators:
                    print("The collaborator {} in {} repository already exist".format(collaborator, self.repository))
                else:
                    repository.add_to_collaborators(collaborator)
                    print("The collaborator {} in {} repository already added please open the email invitations".format(collaborator, self.repository))

if __name__ == '__main__':
    githubService()
