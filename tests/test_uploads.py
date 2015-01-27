# -*- coding: utf8 -*-

"""Tests for uploading of files in to MongoDB GridFS.

:license: AGPL v3, see LICENSE for more details
:copyright: 2014-2015 Joe Doherty

"""

import io
from os import listdir
from os.path import isfile, join

from pjuu.lib import get_uuid
from pjuu.lib.uploads import process_upload, get_upload

from tests import FrontendTestCase


class PagesTests(FrontendTestCase):

    def test_uploads(self):
        """Simply tests the backend functions in `lib.uploads`.

        Also tests `posts.get_upload` since this is only a simple wrapper
        around the backend function.

        """
        test_upload_dir = 'tests/upload_test_files/'
        test_upload_files = [
            join(test_upload_dir, f) for f in listdir(test_upload_dir)
            if isfile(join(test_upload_dir, f))
        ]

        # Test each file in the upload directory
        for f in test_upload_files:
            print 'Testing:', f
            uuid = get_uuid()
            image = io.BytesIO(
                open(f).read()
            )
            filename = process_upload(uuid, image)

            self.assertEqual(filename, '{}.png'.format(uuid))

            # Get the upload these are designed for being served directly by
            # Flask. This is a Flask/Werkzeug response object
            image = get_upload(filename)

            self.assertEqual(image.headers['Content-Type'], 'image/png')

        # Ensure that if we load a non-image file a None value is returned
        uuid = get_uuid()
        image = io.BytesIO()
        self.assertIsNone(process_upload(uuid, image))
