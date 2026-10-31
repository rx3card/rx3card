#!/usr/bin/env bash
# Rebuilds assets/plates from the original downloads listed in ASSET_SOURCES.md.
# Run by hand only when a plate changes: the Actions workflow reuses the output.
# usage: scripts/build_plates.sh <folder with the originals>
set -euo pipefail
SRC=$1; OUT="$(dirname "$0")/../assets/plates"; mkdir -p "$OUT"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

# the dish, at dusk: sky extended left by mirroring so the plate has no edge
magick "$SRC/a-radio-telescope.jpg" -colorspace Gray -gravity north -crop 1888x1500+0+0 +repage -resize 980x \
  -level 8%,96%,0.62 -attenuate 0.18 +noise Gaussian "$tmp/dish.png"
magick \( "$tmp/dish.png" -flop \) "$tmp/dish.png" +append -gravity east -crop 1400x766+0+0 +repage "$tmp/wide.png"
# the phone keeps the whole dish and the figure on the lift; words sit on the black below
magick "$tmp/dish.png" -resize 720x -gravity north -background black -extent 720x930 "$tmp/tall.png"

for theme in halloween:'#ff9a3c' dark:'#c9c9d6'; do
  name=${theme%%:*}; ink=${theme#*:}
  clut() { magick "$1" -colorspace sRGB \( -size 1x256 gradient:black-"$ink" \) -clut "$2"; }
  clut "$tmp/wide.png" "$tmp/c.png"
  # neutral scrim under the headline, the one gradient allowed
  magick "$tmp/c.png" \( -size 766x1400 gradient:black-white -rotate -90 -level 6%,60% \) -compose Multiply -composite \
    -resize 1280x -quality 62 "$OUT/dish-$name.jpg"
  clut "$tmp/tall.png" "$tmp/t.png"
  magick "$tmp/t.png" \( -size 720x930 gradient:white-black -level 38%,58% \) -compose Multiply -composite \
    -quality 60 "$OUT/dish-$name-phone.jpg"
  # the array, summer sky printed backwards: steel lit against black, forest gone
  magick "$SRC/duga-radar-array-near-chernobyl-ukraine-2014.jpg" -colorspace Gray -negate -gravity northwest \
    -crop 1600x470+300+290 +repage -resize 1280x -level 50%,86%,1.0 \
    \( -size 1280x376 gradient:white-black -level 8%,16% \) -compose Multiply -composite -compose Over \
    -colorspace sRGB \( -size 1x256 gradient:black-"$ink" \) -clut -quality 62 "$OUT/array-$name.jpg"
done
