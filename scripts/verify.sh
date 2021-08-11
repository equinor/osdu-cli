#!/bin/bash

# Basic script used by Travis and local to verify all tests

function launch_pylint()
{
    $(which pylint) $1 --msg-template='{path}({line}): [{msg_id}{obj}] {msg}' --load-plugins=scripts.license_verify_pylint
}

function launch_unit_tests()
{
    nose2 -v --with-coverage --coverage osducli
}

if [[ $1 == "local" ]]
    then
        launch_unit_tests && launch_pylint ./osducli && launch_pylint ./scripts/license_verify_pylint
elif [[ $1 == "test" ]]
    then
        launch_unit_tests
elif [[ $1 == "lint" ]]
    then
        echo "Linting CLI..."
        launch_pylint ./osducli
        r1=$?
        echo "Linting Checker..."
        launch_pylint ./scripts/license_verify_pylint
        r2=$?
        exit $((r1 + r2))
fi
