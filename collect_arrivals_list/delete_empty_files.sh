#!/bin/bash

echo "Dry‑run: Listing empty files under $(pwd)"
echo "-----------------------------------------"
find . -type f -empty -print

echo
read -p "Proceed with deletion? (y/N) " confirm

if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    echo "Deleting empty files..."
    find . -type f -empty -delete
    echo "Done."
else
    echo "Aborted. No files were deleted."
fi
