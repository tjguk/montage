import os, sys
import itertools

import pyexiv2
from PIL import Image

from winsys import fs

def copy_with_rename(copy_from, copy_to):
  if copy_to:
    if copy_from.equal_contents (copy_to):
      return
    for i in itertools.count(1):
      new_copy_to = copy_to.changed(base="%s.%d" % (copy_to.base, i))
      print "Trying", new_copy_to
      if not new_copy_to:
        copy_to = new_copy_to
        break

  print copy_from.copy(copy_to)

def main(from_dirpath="originals", to_dirpath="renamed"):
  print from_dirpath
  print to_dirpath
  from_dir = fs.dir(from_dirpath)
  to_dir = fs.Dir(to_dirpath).create()

  for jpg in from_dir.flat("*.jpg"):
    print jpg
    metadata = pyexiv2.ImageMetadata(jpg)
    metadata.read()
    timestamp_metadata = metadata.get('Exif.Image.DateTime', None)
    if timestamp_metadata is None:
      timestamp = jpg.written_at
    else:
      timestamp = timestamp_metadata.value
    to_filepath = to_dir + "%s.jpg" % timestamp.strftime("%Y%m%d-%H%M%S")
    copy_with_rename(jpg, to_filepath)

if __name__ == '__main__':
  main(*sys.argv[1:])
