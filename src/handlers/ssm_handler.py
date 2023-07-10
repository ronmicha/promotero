import json
import os
import re
import subprocess
from typing import List

from common.constants import ROLE_SESSION_NAME
from common.logger import Logger
from common.utils import remove_root_path


class SSMHandler:
    @staticmethod
    def _get_ssm_params(env: str, ssm_file_path: str) -> List[str]:
        ssm_params = []

        with open(ssm_file_path) as file:
            for line in file:
                # remove the '/<env>' prefix, the '_unencrypted| suffix, and the value after ':'
                ssm_param = re.sub(rf"^/{env}|_unencrypted|: ?.*", "", line.strip())
                if ssm_param.startswith("#"):
                    continue
                if ssm_param == "sops":
                    # done with SSM keys and reached sops metadata
                    break
                ssm_params.append(ssm_param)

        return ssm_params

    def get_ssm_params_diff(
        self,
        src_env: str,
        dest_env: str,
        src_ssm_file_path: str,
        dest_ssm_file_path: str,
    ):
        if not (src_ssm_file_path and dest_ssm_file_path):
            return set(), set()

        src_ssm_params = set(self._get_ssm_params(src_env, src_ssm_file_path))
        dest_ssm_params = set(self._get_ssm_params(dest_env, dest_ssm_file_path))

        added_ssm_params = src_ssm_params - dest_ssm_params
        deleted_ssm_params = dest_ssm_params - src_ssm_params

        return added_ssm_params, deleted_ssm_params

    @staticmethod
    def assume_aws_role(role_arn: str) -> None:
        os.environ.pop("AWS_ACCESS_KEY_ID", None)
        os.environ.pop("AWS_SECRET_ACCESS_KEY", None)
        os.environ.pop("AWS_SESSION_TOKEN", None)

        token_code = input("Enter AWS MFA code: ")

        Logger.info(f"Assuming AWS role: {role_arn}")
        serial_number = os.environ.get("SERIAL_NUMBER")

        bash_command = f"aws sts assume-role --role-arn {role_arn} --role-session-name {ROLE_SESSION_NAME} --serial-number {serial_number} --token-code {token_code} --duration-seconds 3600"

        output_bytes = subprocess.check_output(bash_command, shell=True)
        output_str = output_bytes.decode("utf-8")
        output = json.loads(output_str)
        credentials = output["Credentials"]

        os.environ["AWS_ACCESS_KEY_ID"] = credentials["AccessKeyId"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = credentials["SecretAccessKey"]
        os.environ["AWS_SESSION_TOKEN"] = credentials["SessionToken"]

        Logger.info("Assumed role successfully!", newline_suffix=True)

    @staticmethod
    def sops_ssm_files(ssm_paths: List[str]) -> None:
        if not os.environ["EDITOR"]:
            Logger.info("WARNING: environment variable 'EDITOR' was not found. SSM files will be opened in vim editor")

        for ssm_path in ssm_paths:
            Logger.info(f'Opening "{remove_root_path(ssm_path)}"...')
            subprocess.Popen(f"sops {ssm_path}", shell=True)
