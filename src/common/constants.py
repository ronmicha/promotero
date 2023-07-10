from os import path
from typing import Dict, List

ROOT_PATH: str = path.abspath(path.join(__file__, "..", "..", "..", "..", ".."))

BASE_DIR: str = path.join("environments", "aws")

MANAGED_SSM_FILENAME: str = "managed.yaml"

TERRAFORM_DEV_ROLE: str = "arn:aws:iam::899829144201:role/VizMgmtTerraformDevelopers"

ROLE_SESSION_NAME: str = "promotero_script_assume_role_session"

QA_ENV_REGIONS: Dict[str, str] = {
    "qa-aidna-1": "eu-west-1",
    "qa-aidna-2": "eu-west-1",
    "qa-atlas-1": "eu-west-1",
    "qa-atlas-2": "eu-west-1",
    "qa-devops-1": "eu-west-1",
    "qa-dna-1": "eu-west-1",
    "qa-europa-1": "eu-west-1",
    "qa-hyperion-1": "eu-west-1",
    "qa-neptune-1": "eu-west-1",
    "qa-nova-1": "eu-west-1",
    "qa-planetx-1": "eu-west-1",
    "qa-sanity-1": "eu-west-1",
    "qa-sanity-2": "eu-west-1",
    "qa-solaris-1": "eu-west-1",
    "qa-titan-1": "eu-west-1",
    "qa-web-1": "eu-west-1",
    "qa-demo-1": "us-east-2",
}

PROD_ENV_REGIONS: Dict[str, str] = {
    "prod-ohio-1": "us-east-2",
    "prod-upmc-1": "us-east-2",
    "prod-frankfurt-1": "eu-central-1",
}

STG_ENV_REGIONS: Dict[str, str] = {
    "stg-performance-1": "us-west-2",
}

QA_ENVS: List[str] = list(QA_ENV_REGIONS.keys())

PROD_ENVS: List[str] = list(PROD_ENV_REGIONS.keys())

STG_ENVS: List[str] = list(STG_ENV_REGIONS.keys())

ALL_ENVS: List[str] = QA_ENVS + PROD_ENVS + STG_ENVS

MODULES_ARG_DEFAULT_VALUE = "all"
