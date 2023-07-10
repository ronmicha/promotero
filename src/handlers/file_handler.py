import re
from typing import List, Tuple

from common.utils import get_env_region, is_promoting_qa_to_prod, is_promoting_qa_to_stg


class FileHandler:
    @staticmethod
    def _replace_strings_in_file(file_path: str, replacement_tuples: List[Tuple[str, str, str]]) -> None:
        with open(file_path, "r") as file:
            file_content = file.read()

        for replacement_tuple in replacement_tuples:
            old_str, new_str, replacement_type = replacement_tuple
            if replacement_type == "exact_string":
                file_content = file_content.replace(old_str, new_str)
            elif replacement_type == "regex":
                file_content = re.sub(old_str, new_str, file_content)

        with open(file_path, "w") as file:
            file.write(file_content)

    def update_terragrunt_file(self, tg_file_path: str, src_env: str, dest_env: str) -> None:
        replacement_tuples = []

        replacement_multiline_cloudflare_1 = """
dependency "vpc-cloudflare-ztna" {
  config_path = "${get_parent_terragrunt_dir()}/aws-mgmt/${local.region}/cloudflare-ztna/vpc/cloudflare-ztna"

  mock_outputs = {
    private_subnets_cidr_blocks = "(known after apply-all)"
  }
}
"""

        replacement_multiline_cloudflare_2 = """
    {
      description = "From Cloudflare ZTNA"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = dependency.vpc-cloudflare-ztna.outputs.private_subnets_cidr_blocks
    },"""

        replacement_multiline_binpack = """
    {
      type  = "binpack"
      field = "memory"
    },"""

        src_region = get_env_region(src_env)
        dest_region = get_env_region(dest_env)
        if src_region != dest_region:
            replacement_tuples.append((f'"{src_region}"', f'"{dest_region}"', "exact_string"))  # environments_region constant string

        if is_promoting_qa_to_prod(src_env, dest_env) or is_promoting_qa_to_stg(src_env, dest_env):
            replacement_tuples.extend(
                [
                    ("vizcloud.net", "viz.cloud", "exact_string"),  # viz domain
                    ("Z3HVYAZH6KU37Q", "ZH94J7OJ8WCEI", "exact_string"),  # hosted zone id
                    ("viz-qa-", "viz-", "exact_string"),  # logging bucket
                    ("viz-qacom", "viz-com", "exact_string"),  # logging bucket
                    ("/common/qa/", "/common/prod/", "exact_string"),  # path to tpl file
                    ("/aws-qa-", "/aws-prod-", "exact_string"),  # path to various files
                    (replacement_multiline_cloudflare_1, "", "exact_string"),  # cloudflare ztna access
                    (replacement_multiline_cloudflare_2, "", "exact_string"),  # cloudflare ztna access
                    (replacement_multiline_binpack, "", "exact_string"),  # task_placement_strategy binpack
                    (r"deployment_minimum_healthy_percent\s+=\s+\d+", "deployment_minimum_healthy_percent = 100", "regex"),  # ecs deployment_minimum_healthy_percent
                    (r"deployment_maximum_percent\s+=\s+\d+", "deployment_maximum_percent         = 200", "regex"),  # ecs deployment_maximum_percent
                    (r"desired_count\s+=\s+\d+", "desired_count                      = 0", "regex"),  # ecs-service desired_count
                ]
            )

        if is_promoting_qa_to_stg(src_env, dest_env):
            replacement_tuples.extend(
                [
                    ("aws-${local.environment}-", "aws-prod-", "exact_string"),  # aws account name
                ]
            )

        self._replace_strings_in_file(tg_file_path, replacement_tuples)
