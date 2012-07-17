import os, sys
import datetime

from PIL import Image

from winsys import fs

def main(from_dirpath="renamed"):
  from_dir = fs.dir(from_dirpath)
  assert from_dir
  last_month = None
  for jpg in sorted(from_dir.files("*.jpg")):
    date8, _, time6 = jpg.base.partition("-")
    date = datetime.date(int(date8[:4]), int(date8[4:6]), int(date8[6:8]))
    month = date.strftime("%b %Y")
    if month != last_month:
      last_month = month
      print month
    print "  ", jpg.base


if __name__ == '__main__':
  main(*sys.argv[1:])
