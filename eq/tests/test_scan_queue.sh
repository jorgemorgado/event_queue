#!/bin/bash

pushd ../bin > /dev/null

# Test scan-queue scripts
./scan-queue $* ..
RET=$?

popd > /dev/null

exit ${RET}
