#!/bin/bash

pushd ../lib/dbevent > /dev/null

python -m dbevent $*
RET=$?

popd > /dev/null

exit ${RET}
