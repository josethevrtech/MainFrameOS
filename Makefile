.PHONY: check bootstrap package-support package-canary kernel-dtb
check:
	python3 scripts/check.py
	python3 -m unittest discover -s tests -v
	python3 -m py_compile scripts/*.py packages/mainframeos-support/mainframeos-support
	bash -n packages/mainframeos-support/PKGBUILD packages/compat-json-c/PKGBUILD
bootstrap:
	python3 scripts/build.py bootstrap
package-support:
	python3 scripts/build.py package mainframeos-support
package-canary:
	python3 scripts/build.py package compat-json-c
kernel-dtb:
	python3 scripts/kernel.py
