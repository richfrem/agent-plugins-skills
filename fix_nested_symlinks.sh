#!/bin/bash
find plugins -type l -name "resources" | grep "resources/resources" | while read -r symlink; do
    dir=$(dirname "$symlink")
    rm "$symlink"
    if [ -z "$(ls -A "$dir")" ]; then
        rmdir "$dir"
        ln -s ../../resources "$dir"
    fi
done

find plugins -type l -name "references" | grep "references/references" | while read -r symlink; do
    dir=$(dirname "$symlink")
    rm "$symlink"
    if [ -z "$(ls -A "$dir")" ]; then
        rmdir "$dir"
        ln -s ../../references "$dir"
    fi
done
