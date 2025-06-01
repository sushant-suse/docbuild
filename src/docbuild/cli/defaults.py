"""Defaults for the CLI and environment configuration.

* `DEFAULT_APP_CONFIG`: Default configuration for the application.
* `DEFAULT_ENV_CONFIG`: Default configuration for the environment.
"""

from ..constants import APP_NAME

DEFAULT_APP_CONFIG = {
    "debug": False,
    "role": "production",
    "paths": {
        "config_dir": "/etc/docbuild",
        "repo_dir": "/data/docserv/repos/permanent-full/",
        "temp_repo_dir": "/data/docserv/repos/temporary-branches/",
    },
    "paths.tmp": {
        "tmp_base_path": "/tmp",
        "tmp_path": "{tmp_base_path}/doc-example-com",
    },
}

DEFAULT_ENV_CONFIG = {
    "role": "production",
    "paths": {
        "config_dir": "/etc/docbuild",
        "repo_dir": "/data/docserv/repos/permanent-full/",
        "temp_repo_dir": "/data/docserv/repos/temporary-branches/",
    },
    "paths.tmp": {
        "tmp_base_path": f"/var/tmp/{APP_NAME}",
        "tmp_path": "{tmp_base_path}/doc-example-com",
    },
}
