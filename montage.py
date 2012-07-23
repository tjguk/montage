import os, sys
import datetime
import itertools

import jinja2
import pyexiv2
from PIL import Image
from winsys import fs

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

    return copy_from.copy(copy_to)

def copy_images(from_dir, images_dir, from_date, to_date):
    for jpg in from_dir.flat("*.jpg"):
        print jpg.relative_to(from_dir)
        metadata = pyexiv2.ImageMetadata(jpg)
        metadata.read()
        timestamp_metadata = metadata.get('Exif.Image.DateTime', None)
        if timestamp_metadata is None:
            timestamp = jpg.written_at
        else:
            timestamp = timestamp_metadata.value
        if from_date <= timestamp.date() <= to_date:
            to_filepath = images_dir + "%s.jpg" % timestamp.strftime("%Y%m%d-%H%M%S")
            target = copy_with_rename(jpg, to_filepath)
            if target: print "=>", target.filename

def generate_thumbnails(images_dir):
    """From each of the images in the images directory, extract
    the largest square section from its centre and generate a
    thumbnail of that square.
    """
    thumbnails_dirpath = fs.Dir(images_dir + "thumbnails").create()
    for jpg in images_dir.files("*.jpg"):
        image = Image.open(jpg)
        width, height = image.size
        short_edge = min((width, height))
        crop_box = (
            (width - short_edge) / 2,
            (height - short_edge) / 2,
            width - (width - short_edge) / 2,
            height - (height - short_edge) / 2
        )
        image = image.crop(crop_box)
        image.thumbnail((THUMBNAIL_EDGE, THUMBNAIL_EDGE), Image.ANTIALIAS)
        print thumbnails_dirpath + jpg.filename
        image.save(thumbnails_dirpath + jpg.filename, "JPEG")

def generate_html(root_dir):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates/"))
    gallery_template = env.get_template("gallery.html")
    picture_template = env.get_template("picture.html")
    montage_filepath = root_dir + "montage.html"

    images = []
    for jpg in sorted(root_dir.dir("images").files("*.jpg")):
        with open(root_dir.file("%s.html" % jpg.base), "wb") as picture_file:
            picture_file.write(picture_template.render(image=jpg))
        name = jpg.name
        jpg_date = datetime.date(int(name[:4]), int(name[4:6]), int(name[6:8]))
        images.append(dict(month=jpg_date.strftime("%b %Y"), image=jpg))

    gallery_html = gallery_template.render(
        title="Westpark Through the Year",
        images=images
    )
    with open(montage_filepath, "wb") as html_file:
        html_file.write(gallery_html)

FROM_DIRPATH = r"\\handel\public\westpark-club\images\2011\2011-Nov Garden"
IMAGES_RELPATH = "images"
FROM_DATE = datetime.date(2011, 9, 1)
TO_DATE = datetime.date(2012, 7, 31)
THUMBNAIL_EDGE = 140
def main(from_dirpath=FROM_DIRPATH, root_dirpath="web"):
    from_dir = fs.dir(from_dirpath)
    root_dir = fs.Dir(root_dirpath).create()
    images_dir = root_dir.dir(IMAGES_RELPATH).create()

    copy_images(from_dir, images_dir, FROM_DATE, TO_DATE)
    generate_thumbnails(images_dir)
    generate_html(root_dir)

if __name__ == '__main__':
  main(*sys.argv[1:])
