#!/bin/bash

fdupes -Srd --noprompt $1 && find $1 -type d -empty && find $1 -type d -empty -delete
