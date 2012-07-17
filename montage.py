import os, sys
import itertools

import pyexiv2
from winsys import fs

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

def copy_with_rename(copy_from, copy_to):
    if copy_to:
        if copy_from.equal_contents(copy_to):
            return
        for i in itertools.count(1):
            new_copy_to = copy_to.changed(base="%s.%d" % (copy_to.base, i))
            print "Trying", new_copy_to
            if not new_copy_to:
                copy_to = new_copy_to
                break

    copy_from.copy(copy_to)

def copy_images(from_dir, images_dir):
    for jpg in from_dir.flat("*.jpg"):
        print jpg
        metadata = pyexiv2.ImageMetadata(jpg)
        metadata.read()
        timestamp_metadata = metadata.get('Exif.Image.DateTime', None)
        if timestamp_metadata is None:
            timestamp = jpg.written_at
        else:
            timestamp = timestamp_metadata.value
        to_filepath = images_dir + "%s.jpg" % timestamp.strftime("%Y%m%d-%H%M%S")
        print copy_with_rename(jpg, to_filepath)

def generate_thumbnails(images_dir):
    raise NotImplementedError

def generate_html(images_dir, to_html):
    raise NotImplementedError

def main(from_dirpath, to_htmlpath="montage.html", images_dirpath="images"):
    from_dir = fs.dir(from_dirpath)
    to_html = fs.file(to_htmlpath)
    images_dir = fs.Dir(images_dirpath).create()

    copy_images(from_dir, images_dir)
    generate_thumbnails(images_dir)
    generate_html(images_dir, to_html)

if __name__ == '__main__':
  main(*sys.argv[1:])
