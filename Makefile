VERSION=$(shell grep '^version' pyproject.toml | cut -d '"' -f2)

.PHONY: tag-release
tag-release:
	git tag -s "$(VERSION)" -m "v$(VERSION)"
