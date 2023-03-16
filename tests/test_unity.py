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
import subprocess
import sys
import tempfile
import unittest
import zipfile

# sys.path.append("../")
# import hvcc

raise unittest.SkipTest()

sys.path.append("../../../royal/tools")
import uploader  # noqa


SCRIPT_DIR = os.path.dirname(__file__)
UNITY_TEST_DIR = os.path.join(os.path.dirname(__file__), "unity", "test")


class TestUnityPlugins(unittest.TestCase):

    __TEST_TOKEN = "VPwuY6XUCvPKbyjYK3OZ1z01nUbDg1lv"

    # called once before any tests are run
    @classmethod
    def setUpClass(clazz):
        # make temporary directory for downloads
        TestUnityPlugins.__OUT_DIR = tempfile.mkdtemp(prefix="TestUnity-")

        exit_code, reply_json = uploader.upload(
            input_dir=os.path.join(UNITY_TEST_DIR, "Assets", "Patch"),
            output_dirs=[TestUnityPlugins.__OUT_DIR],
            name="heavy",
            generators="c",
            release="dev",
            token=TestUnityPlugins.__TEST_TOKEN,
            x=False)

        # unittest asserts can only be called on instances
        assert exit_code == 0, f"Uploader returned with non-zero exit code: {exit_code}"
        assert len(reply_json.get("errors", [])) == 0, reply_json["errors"][0]["detail"]

        TestUnityPlugins.__JOB_URL = reply_json["data"]["links"]["files"]["self"]

    # called once when all tests are done
    @classmethod
    def tearDownClass(self):
        # when everythign is done, delete the temporary output directory
        shutil.rmtree(TestUnityPlugins.__OUT_DIR)

    def generate_plugin(self, generator, platform, architecture=None):
        """ Ensure that an asset can be downloaded.
        """

        if platform == "src":
            url = f"{TestUnityPlugins.__JOB_URL}/{generator}/src/archive.zip"
            out_path = os.path.join(TestUnityPlugins.__OUT_DIR, generator, platform, "out.zip")
        else:
            self.assertIsNotNone(architecture)
            url = f"{TestUnityPlugins.__JOB_URL}/{generator}/{platform}/{architecture}/archive.zip"
            out_path = os.path.join(TestUnityPlugins.__OUT_DIR, generator, platform, architecture, "out.zip")

        try:
            r = requests.get(
                url,
                cookies={"token": TestUnityPlugins.__TEST_TOKEN},
                timeout=30.0)  # maximum request time of 30 seconds
        except requests.exceptions.Timeout:
            self.fail(f"Request {url} has timed out. Why is it taking so long?")

        # assert that the file could be downloaded
        self.assertEqual(
            r.status_code,
            200,  # assert that we receive HTTPS status code 200 OK
            f"Received HTTPS {r.status_code} for {url}. Could not download asset.")

        # make an output directory and write the asset to disk
        os.makedirs(os.path.dirname(out_path))
        with open(out_path, "wb") as f:
            f.write(r.content)

        return out_path

    def check_unity_log(self, log_file):
        """ Checks for and prints certain compiler output messages from a unity generated build log file (-logFile)
        """
        with open(log_file, "r") as f:
            should_print = False
            for line in f.readlines():
                if line.startswith("-----CompilerOutput:"):
                    should_print = True

                if should_print:
                    print(line),

                if line.startswith("-----EndCompilerOutput"):
                    break

    def test_unity(self):
        # set up output directory
        out_dir = os.path.join(UNITY_TEST_DIR, "Assets", "Plugins")
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)

        # compile patch and extract build results
        platform = sys.platform
        if platform in ["darwin", "Darwin"]:
            unity_app_path = "/Applications/Unity/Unity.app/Contents/MacOS/Unity"
            zip_path = self.generate_plugin("unity", "osx", "x86_64")
        elif platform in ["windows", "Windows"]:
            unity_app_path = "unknown"
            zip_path = self.generate_plugin("unity", "win", "x86_64")
        else:
            self.fail(f"Unsupported test platform ({platform})")

        with (zipfile.ZipFile(zip_path, "r")) as z:
            z.extractall(out_dir)
            z.close()

        # build unity project
        log_file = os.path.join(out_dir, "unity_test_build.log")
        cmd = [
            unity_app_path,
            "-quit",
            "-batchmode",
            "-logFile", log_file,
            "-projectPath", UNITY_TEST_DIR,
            "-executeMethod", "HeavyTestScript.Perform",
            "-buildOSXUniversalPlayer", os.path.join(UNITY_TEST_DIR, "build")
        ]
        try:
            subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            self.check_unity_log(log_file)
            self.fail(f"Unity Build failed: ExitCode={e.returncode}, check {log_file} for more info.")


if __name__ == "__main__":
    print("Usage: $ nose2 test_unity.TestUnityPlugins")
