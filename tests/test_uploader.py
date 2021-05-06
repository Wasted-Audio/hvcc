# Copyright (C) 2014-2018 Enzien Audio, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import requests
import shutil
import sys
import tempfile
import unittest
import urlparse

sys.path.append("../../../hv-uploader")
import hv_uploader

class TestUploader(unittest.TestCase):

    __TEST_TOKEN = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJzdGFydERhdGUiOiAiMjAxNy0wMS0xNlQxOToyNTo1OS41MDIyMjkiLCAibmFtZSI6ICJlbnppZW5fYm90In0=.9nvA3uAsJksYUKLYb4r6T1DKMSoa_wBbqJFN8e_d5cQ="

    # called once before any tests are run
    @classmethod
    def setUpClass(clazz):
        domain = "https://enzienaudio.com"

        # make temporary directory for downloads
        TestUploader.__OUT_DIR = tempfile.mkdtemp(prefix="TestUploader-")

        exit_code, reply_json = hv_uploader.upload(
            input_dir=os.path.join(os.path.dirname(__file__), "uploader"),
            output_dirs=[TestUploader.__OUT_DIR],
            name="heavy",
            generators="c",
            release="dev",
            domain=domain,
            token=TestUploader.__TEST_TOKEN)

        # unittest asserts can only be called on instances
        assert exit_code == 0, "Uploader returned with non-zero exit code: {0}".format(exit_code)
        assert len(reply_json.get("errors",[])) == 0, reply_json["errors"][0]["detail"]

        TestUploader.__JOB_URL = urlparse.urljoin(domain, reply_json["data"]["links"]["html"])

    # called once when all tests are done
    @classmethod
    def tearDownClass(self):
        # when everythign is done, delete the temporary output directory
        shutil.rmtree(TestUploader.__OUT_DIR)

    def check_file_for_generator(self, generator, platform, architecture=None):
        """ Ensure that an asset can be downloaded.
        """

        if platform == "src":
            url = "{0}/{1}/src/archive.zip".format(TestUploader.__JOB_URL, generator)
            out_path = os.path.join(TestUploader.__OUT_DIR, generator, platform, "out.zip")
        else:
            self.assertIsNotNone(architecture)
            url = "{0}/{1}/{2}/{3}/archive.zip".format(TestUploader.__JOB_URL, generator, platform, architecture)
            out_path = os.path.join(TestUploader.__OUT_DIR, generator, platform, architecture, "out.zip")

        try:
            r = requests.get(
                url,
                cookies={"token":TestUploader.__TEST_TOKEN},
                timeout=30.0) # maximum request time of 30 seconds
        except requests.exceptions.Timeout:
            self.fail("Request {0} has timed out. Why is it taking so long?".format(url))

        # assert that the file could be downloaded
        self.assertEqual(
            r.status_code,
            200, # assert that we receive HTTPS status code 200 OK
            "Received HTTPS {0} for {1}. Could not download asset.".format(r.status_code, url))

        # make an output directory and write the asset to disk
        os.makedirs(os.path.dirname(out_path))
        with open(out_path, "wb") as f:
            f.write(r.content)

    def test_unity_src(self):
        self.check_file_for_generator("unity", "src")

    def test_unity_macos_x64(self):
        self.check_file_for_generator("unity", "macos", "x64")

    def test_unity_win_x64(self):
        self.check_file_for_generator("unity", "win", "x64")

    def test_unity_win_x86(self):
        self.check_file_for_generator("unity", "win", "x86")

    def test_unity_linux_x64(self):
        self.check_file_for_generator("unity", "linux", "x64")

    def test_unity_android_armv7a(self):
        self.check_file_for_generator("unity", "android", "armv7a")

    def test_wwise_src(self):
        self.check_file_for_generator("wwise", "src")

    def test_wwise_ios_x64(self):
        self.check_file_for_generator("wwise", "ios", "armv7a")

    def test_wwise_macos_x64(self):
        self.check_file_for_generator("wwise", "macos", "x64")

    def test_wwise_win_x64(self):
        self.check_file_for_generator("wwise", "win", "x64")

    def test_wwise_win_x86(self):
        self.check_file_for_generator("wwise", "win", "x86")

    def test_wwise_linux_x64(self):
        self.check_file_for_generator("wwise", "linux", "x64")

    def test_vst2_src(self):
        self.check_file_for_generator("vst2", "src")

    def test_vst2_macos_x64(self):
        self.check_file_for_generator("vst2", "macos", "x64")

    def test_vst2_win_x86(self):
        self.check_file_for_generator("vst2", "win", "x86")

    def test_vst2_win_x64(self):
        self.check_file_for_generator("vst2", "win", "x64")

    def test_vst2_linux_x64(self):
        self.check_file_for_generator("vst2", "linux", "x64")

    def test_fabric_src(self):
        self.check_file_for_generator("fabric", "src")

    def test_fabric_macos_x64(self):
        self.check_file_for_generator("fabric", "macos", "x64")

    def test_fabric_win_x86(self):
        self.check_file_for_generator("fabric", "win", "x86")

    def test_fabric_win_x64(self):
        self.check_file_for_generator("fabric", "win", "x64")

    def test_fabric_linux_x64(self):
        self.check_file_for_generator("fabric", "linux", "x64")

    def test_fabric_android_armv7a(self):
        self.check_file_for_generator("fabric", "android", "armv7a")

if __name__ == "__main__":
    print("Usage: $ nose2 test_uploader.TestUploader")
