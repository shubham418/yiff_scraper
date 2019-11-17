#!/bin/bash

for d in *
do
  if [ -d "$d" ]; then
    echo "Cleaning duplicates in $d..."
    # while read link; do megadl "$link"; done < "$d/mega.nz.txt" && rm "$d/mega.nz.txt"
    #fdupes -Sr ./$d # show
    fdupes -Srd --noprompt ./$d # delete
    find $d -type d -empty # show
    find $d -type d -empty -delete # delete
  fi
done
