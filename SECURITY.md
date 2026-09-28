# Source and credentials

The default `SOURCE_MODE=demo` publishes two bundled synthetic messages once,
then exits. It never creates a MongoDB source client. Restarting the retriever
publishes them again; downstream deduplication is a future STREAM-01 task.
Labels exist only to exercise both routes and make no claim about people.

`python -m common.demo_source` previews the fixture completely offline.
The Compose pipeline still requires local Kafka/MongoDB. Use
`docker compose --env-file config/.env ...` after copying the template.
Host ports bind to loopback. The unauthenticated stack is for local demos only.
OpenShift manifests default to demo source; they are examples, not a secured
production deployment.

To opt into a database you own, set `SOURCE_MODE=mongo`, `ATLAS_URI`, `ATLAS_DB`
and `ATLAS_COLLECTION` in your private environment. `ATLAS_URI` is mandatory in
mongo mode; missing/blank values fail before creating a client. On OpenShift,
set the URI through your own Secret reference and explicitly change SOURCE_MODE.
Never reuse the previously embedded URI. It remains in Git history: the service
owner must revoke/rotate the exposed credential. Validity and rotation have not
been verified. No external DB was accessed, and history was not rewritten.

Run `python -m unittest discover -s tests -v` after installing the retriever's
requirements. Tests block network access and verify fixture publication and
missing-configuration behavior. Gitleaks CI scans the tree and new commits with
full redaction. End-to-end Kafka/Mongo and container execution are not claimed
by these offline tests.
