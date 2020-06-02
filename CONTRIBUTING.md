## Contributing to Oracle Solaris Discover

## Issues

If you hit an issue or have an enhancement request then file a GitHub issue.
When filing an issue remember that the better written the description is, the more likely it is
to be fixed. Please include:

1. Specific folder of the repository
2. Whether an issue with the Code/Reproducing the sheet
3. Attach a screenshot of the issue

## Code

Pull requests can be made under [The Oracle Contributor Agreement](https://www.oracle.com/technetwork/community/oca-486395.html) (OCA).

This repo is in early and active development. While we welcome contributions from the community, we may defer merging new functionality until the codebase stabilises. We have a list of great things we want to implement.  If you have ideas get in touch directly or via the Oracle Technology Network OKIT discussion forum, so we don't duplicate efforts.

For pull requests to be accepted, the bottom of your commit message must have the following line using your name and e-mail address as it appears in the
OCA Signatories list.

```
Signed-off-by: Your Name <you@example.org>
```

This can be automatically added to pull requests by committing with:

```
  git commit --signoff
```

Only pull requests from committers that can be verified as having
signed the OCA can be accepted.

### Pull request process

1. Sign the [OCA](https://www.oracle.com/technetwork/community/oca-486395.html)
2. Fork this repository
3. Create a branch in your fork to implement the changes. We recommend using the issue number as part of your branch name, e.g. `<username>/1234-fixes`
4. Ensure that any documentation is updated with the changes that are required by your fix.
5. Ensure that any samples are updated if the base image has been changed. 
6. Submit the pull request. *Do not leave the pull request blank*. 
   Explain exactly what your changes are meant to do and provide simple steps on how to validate your changes. 
   Ensure that you reference the issue you created as well. 
   We will assign the pull request to 2-3 people for review before it is merged.