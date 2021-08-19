:: Note: this script does not return an error code because it's meant for manual use only.
@echo off

SETLOCAL

IF %1 == local CALL :lint_func & CALL :test_func

IF %1 == lint CALL :lint_func

IF %1 == test CALL :test_func

EXIT /B 0

:: define function to run linter
:lint_func
echo pylint osducli
pylint osducli --msg-template="{path}({line}): [{msg_id}{obj}] {msg}" --load-plugins=scripts.license_verify_pylint --rcfile=pylintrc -r n
echo pylint licenses
pylint scripts/license_verify_pylint.py --msg-template="{path}({line}): [{msg_id}{obj}] {msg}" --load-plugins=scripts.license_verify_pylint --rcfile=pylintrc -r n
pylint scripts/license_verify.py --msg-template="{path}({line}): [{msg_id}{obj}] {msg}" --load-plugins=scripts.license_verify_pylint --rcfile=pylintrc -r n
echo flake8 osducli
flake8 --statistics --append-config=.flake8 osducli
:: pylint ./osducli --msg-template="{path}({line}): [{msg_id}{obj}] {msg}" --load-plugins=pylintcheckersfolder
:: pylint ./checkers --msg-template="{path}({line}): [{msg_id}{obj}] {msg}" --load-plugins=pylintcheckersfolder
EXIT /B 0

:: define function to launch tests
:test_func
echo testing
nose2 -v --with-coverage --coverage osducli
EXIT /B 0

ENDLOCAL

@echo on



