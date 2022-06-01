#!/bin/bash

pushd ../lib/db > /dev/null

python -m db $*
RET=$?

popd > /dev/null

exit ${RET}
