version := `uvx mddj read version`

tag-release:
    git tag -s "{{version}}" -m "v{{version}}"

check-sdist:
    uvx --from='check-sdist==1.3.1' check-sdist --inject-junk
