#!/bin/bash

pushd ../bin > /dev/null

# Test the factorial script
CMD=`./q ../examples/factorial.q`
RET=$?

if [ ${RET} -eq 0 ]; then
    if [ ${CMD} -ne 120 ]; then
        echo "Error: expected 120, but got ${CMD}"
        RET=1
    fi
fi

popd > /dev/null

exit ${RET}
