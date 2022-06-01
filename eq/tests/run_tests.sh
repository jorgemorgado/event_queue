#!/bin/bash

# Disable verbose mode
VERBOSE=""

function usage() {
    echo "Usage: ${0} [-h] [-v]

    -h          Show usage information
    -v          Verbose mode" 1>&2
    exit 1;
}

while getopts "vh" OPTION; do
    case ${OPTION} in
        v)
            VERBOSE="-v"
            shift
            ;;
        h)
            usage
            ;;
    esac
done

RET=0
BASEDIR=`dirname ${0}`
pushd ${BASEDIR} > /dev/null

echo "Testing Python Db module"
./test_module_db.sh ${VERBOSE} || RET=1

echo "Testing Python DbEvent module"
./test_module_dbevent.sh ${VERBOSE} || RET=1

echo "Testing generic q script(s)"
./test_scripts.sh ${VERBOSE} || RET=1

echo "Testing scan-queue"
./test_scan_queue.sh ${VERBOSE} || RET=1

if [ ${RET} -eq 0 ]; then
    echo "All tests passed successfully."
else
    echo "Some tests have failed. Use '-v' for verbose testing."
fi

popd > /dev/null
exit ${RET}
