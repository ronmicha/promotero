import os
import unittest

from common.constants import (
    ALL_ENVS,
    MANAGED_SSM_FILENAME,
    PROD_ENVS,
    QA_ENVS,
    ROOT_PATH,
)
from common.utils import is_qa_env
from handlers.path_handler import PathHandler


class TestUtils(unittest.TestCase):
    path_handler = PathHandler()

    def test_root_path(self):
        last_dir_in_root_path = ROOT_PATH.split(os.sep)[-1]
        self.assertEqual(last_dir_in_root_path, "terraform-live")

    def test_is_qa_env(self):
        self.assertTrue(is_qa_env(QA_ENVS))
        for env in QA_ENVS:
            self.assertTrue(is_qa_env(env))

        self.assertFalse(is_qa_env(PROD_ENVS))
        for env in PROD_ENVS:
            self.assertFalse(is_qa_env(env))

    def test_get_ssm_paths(self):
        for env in ALL_ENVS:
            ssm_paths = self.path_handler.get_ssm_paths(env)
            self.assertEqual(len(ssm_paths), 2)

            for path in ssm_paths:
                filename = path.split(os.sep)[-1]
                self.assertEqual(filename, MANAGED_SSM_FILENAME)
                self.assertIn(env, path)

    def test_get_service_paths(self):
        pass

    def test_resolve_dest_path(self):
        pass


if __name__ == "__main__":
    unittest.main()
