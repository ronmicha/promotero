import os
import re
from glob import glob
from typing import List

from common.constants import (
    BASE_DIR,
    MANAGED_SSM_FILENAME,
    MODULES_ARG_DEFAULT_VALUE,
    ROOT_PATH,
)
from common.utils import get_env_region, is_qa_env

sep = os.path.sep


def wrap(string: str, wrapper: str = sep) -> str:
    return f"{wrapper}{string}{wrapper}"


class PathHandler:
    def __init__(self):
        self.commercial_dir_regex = rf"{wrap('aws-(qa|prod)-commercial')}"
        self.processing_dir_regex = rf"{wrap('aws-(qa|prod)-processing')}"
        self.common_dir_regex = rf"{wrap(f'common{sep}(qa|prod)')}"

        self.relevant_dir_pattern = "|".join(
            [
                wrap("aws-ops"),
                self.commercial_dir_regex,
                self.processing_dir_regex,
                self.common_dir_regex,
            ]
        )

    def _is_relevant_path(self, path: str, modules: List[str] = None) -> bool:
        dir_match = re.search(self.relevant_dir_pattern, path)
        is_dir_match = bool(dir_match)

        if not is_dir_match:
            return False

        is_module_match = True
        if modules and modules != MODULES_ARG_DEFAULT_VALUE:
            is_module_match = any(wrap(module) in dir_match.string for module in modules)

        return is_module_match

    def _get_paths(self, path_parts: List[str], modules: List[str] = None) -> List[str]:
        paths = glob(os.path.join(ROOT_PATH, BASE_DIR, "*", *path_parts), recursive=True)
        relevant_paths = [path for path in paths if self._is_relevant_path(path, modules)]
        return sorted(relevant_paths)

    def get_ssm_paths(self, env: str, filename: str = MANAGED_SSM_FILENAME) -> List[str]:
        return self._get_paths(["*", env, "**", filename])

    def get_service_paths(self, env: str, service_name: str, include_common_dir: bool, modules: List[str]) -> List[str]:
        paths = self._get_paths(["*", env, "*", service_name], modules)
        if include_common_dir:
            paths += self._get_paths(["qa", "*", service_name], modules)
        return paths

    def resolve_dest_path(self, path: str, src_env: str, dest_env: str) -> str:
        root_dest_env = "qa" if is_qa_env(dest_env) else "prod"

        dest_path = re.sub(self.commercial_dir_regex, wrap(f"aws-{root_dest_env}-commercial"), path)
        dest_path = re.sub(
            self.processing_dir_regex,
            wrap(f"aws-{root_dest_env}-processing"),
            dest_path,
        )
        dest_path = re.sub(self.common_dir_regex, wrap(f"common{sep}{root_dest_env}"), dest_path)
        dest_path = re.sub(
            rf"{wrap(get_env_region(src_env))}",
            wrap(get_env_region(dest_env)),
            dest_path,
        )
        dest_path = re.sub(rf"{wrap(src_env)}", wrap(dest_env), dest_path)

        return dest_path

    @staticmethod
    def is_path_exists(path: str) -> bool:
        return os.path.exists(path)
