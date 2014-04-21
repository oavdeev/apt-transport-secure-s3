apt-transport-secure-s3
=======================

APT transport for S3 with authentication and HTTPS support.

Why
-----------------------
To host private debian repositories on S3 and use Amazon IAM for access control. There is already a project called `apt-transport-s3` which does the same thing, but it does not support HTTPS.

Installation
-----------------------

Just rename python file to `s3`, add executable permissions (+x) and drop it off under` /usr/lib/apt/methods/`.

It requires Python >= 2.7.3 and boto >= 2.6.0. It will actually work with earlier versions as well but it won't be secure as SSL certificates will not be properly verified.

Usage
-----------------------

Just as any other method, add url to your repo to the sources.list file, with url like that:

```
deb s3://<aws-key-id>:<aws-key-secret>@<bucket>/some/path/ squeeze main
```
