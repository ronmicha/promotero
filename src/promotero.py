import os
from shutil import copytree, rmtree

from common.constants import MODULES_ARG_DEFAULT_VALUE, TERRAFORM_DEV_ROLE
from common.logger import Logger
from common.utils import clean_string, is_promoting_qa_to_prod, remove_root_path
from handlers.args_handler import Args
from handlers.file_handler import FileHandler
from handlers.path_handler import PathHandler
from handlers.ssm_handler import SSMHandler


class Promotero:
    def __init__(self, args: Args):
        (
            self.src_env,
            self.dest_envs,
            self.services,
            self.modules,
            self.overwrite,
            self.apply,
        ) = args
        self.path_handler = PathHandler()
        self.ssm_handler = SSMHandler()
        self.file_handler = FileHandler()
        self.new_ssm_params = {}

    @staticmethod
    def log_arg(title: str, arg, newline_prefix: bool = False):
        Logger.info("{0:30} {1}".format(title, arg), newline_prefix)

    def pretty_print_args(self):
        self.log_arg("Source environment", self.src_env, True)
        self.log_arg("Destination environments", self.dest_envs)
        self.log_arg("Services to copy", self.services)
        self.log_arg("Modules to copy", self.modules)
        self.log_arg("Overwrite", self.overwrite)
        self.log_arg("Apply", self.apply)

    def collect_relevant_ssm_files(self, dest_env: str):
        if "ssm" not in self.modules:
            return

        src_managed_ssm_paths = self.path_handler.get_ssm_paths(self.src_env)

        for src_managed_ssm_path in src_managed_ssm_paths:
            dest_managed_ssm_path = self.path_handler.resolve_dest_path(src_managed_ssm_path, self.src_env, dest_env)
            if not os.path.exists(dest_managed_ssm_path):
                Logger.info(f"Destination SSM file does not exist: {dest_managed_ssm_path}, skipping", True)
                continue
            added_ssm_params, _ = self.ssm_handler.get_ssm_params_diff(self.src_env, dest_env, src_managed_ssm_path, dest_managed_ssm_path)

            if added_ssm_params:
                self.new_ssm_params[dest_managed_ssm_path] = added_ssm_params

    def copy_services(self, dest_env: str):
        for service_name in self.services:
            src_service_paths = self.path_handler.get_service_paths(
                self.src_env,
                service_name,
                is_promoting_qa_to_prod(self.src_env, dest_env),
                self.modules,
            )

            for src_service_path in src_service_paths:
                dest_service_path = self.path_handler.resolve_dest_path(src_service_path, self.src_env, dest_env)

                if src_service_path == dest_service_path:
                    continue

                Logger.info(f"Copying  {remove_root_path(src_service_path)}", True)
                Logger.info("{0:8} {1}".format("To", remove_root_path(dest_service_path)))

                if not self.apply:
                    continue

                try:
                    dest_service_path_exists = self.path_handler.is_path_exists(dest_service_path)
                    if self.overwrite and dest_service_path_exists:
                        rmtree(dest_service_path)
                    copytree(src_service_path, dest_service_path)

                    self.update_file_content(dest_service_path, dest_env)
                except Exception as e:
                    Logger.error(f"ERROR: {e}")

    def update_file_content(self, dir_path: str, dest_env: str):
        tg_file_path = os.path.join(dir_path, "terragrunt.hcl")

        if self.path_handler.is_path_exists(tg_file_path):
            self.file_handler.update_terragrunt_file(tg_file_path, self.src_env, dest_env)

    def handle_collected_ssm_files(self):
        if not self.new_ssm_params:
            return

        Logger.info(
            f"The following environments are missing SSM params that exist in '{self.src_env}':",
            True,
        )
        for ssm_file_path, ssm_params in self.new_ssm_params.items():
            Logger.info(f"{remove_root_path(ssm_file_path)}:", True)
            [Logger.info(f"\t{x}") for x in ssm_params]
        Logger.info()

        if not self.apply:
            return

        ans = input("Would you like to edit the above SSM files? (y/n) ")
        if clean_string(ans) != "y":
            return

        self.ssm_handler.assume_aws_role(TERRAFORM_DEV_ROLE)
        self.ssm_handler.sops_ssm_files(list(self.new_ssm_params.keys()))

    def run(self):
        self.pretty_print_args()

        for dest_env in self.dest_envs:
            self.collect_relevant_ssm_files(dest_env)
            self.copy_services(dest_env)

        self.handle_collected_ssm_files()
