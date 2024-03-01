import os
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from .main import resize_and_crop


def resized_image_file(
    image_field,
    format,
    dimensions,
    crop_origin="middle"
):
    # create the resized image file
    # **NOTE** This will resize smaller images and, while it respects aspect ratios, make the resoution worse.
    image_file = resize_and_crop(
        image_field.file,
        dimensions,
        crop_origin,
    )
    # create a memory backed image file
    image_bytes = BytesIO()
    image_file.save(image_bytes, format)
    image_bytes.seek(0)
    # create the new thumbnail filename
    image_basename = os.path.basename(image_field.name)
    image_basename_bits = image_basename.split(".")
    image_filename_prefix = "_".join(image_basename_bits[:-1])
    image_filename = "{}_{}x{}.{}".format(
        image_filename_prefix,
        dimensions[0],
        dimensions[1],
        format,
    )
    # save the thumbnail file to the model field
    return SimpleUploadedFile(
        image_filename,
        image_bytes.read(),
        content_type="image/{}".format(format),
    )
