import re

APP_NAME = "docbuild"

DEFAULT_LANGS = ("en-us",)
#: All languages supported by the documentation portal
ALLOWED_LANGUAGES = frozenset("de-de en-us es-es fr-fr ja-jp ko-kr pt-br zh-cn".split(" "))

#: The different server roles, including long and short spelling
SERVER_ROLE = ("production", "prod", "p",
               "testing", "test", "t",
               "staging", "stage", "s",
               )

#: The different lifecycle states of a docset
ALLOWED_LIFECYCLES = ("supported", "beta", "hidden", "unsupported")
DEFAULT_LIFECYCLE = "supported"

#: All product acronyms and their names
#: - key: /product/@productid
#: - value: /product/name
#
# Use the following command to create the output below:
# xmlstarlet sel -t -v '/product/@productid' -o ' ' -v '/product/name' -nl config.d/[a-z]*.xml
VALID_PRODUCTS: dict[str, str] = {
    key.strip(): value.strip()
    for key, value in (line.split(" ", 1)
    for line in """appliance Appliance building
cloudnative Cloud Native
compliance Compliance Documentation
container Container Documentation
liberty SUSE Multi-Linux Support
sbp SUSE Best Practices
ses SUSE Enterprise Storage
sled SUSE Linux Enterprise Desktop
sle-ha SUSE Linux Enterprise High Availability (incl. SLE HA GEO)
sle-hpc SUSE Linux Enterprise High-Performance Computing
sle-micro SUSE Linux Micro
sle-public-cloud SUSE Linux Enterprise in Public Clouds
sle-rt SUSE Linux Enterprise Real Time
sles-sap SUSE Linux Enterprise Server for SAP applications
sles SUSE Linux Enterprise Server
sle-vmdp SUSE Linux Enterprise Virtual Machine Driver Pack
smart SUSE Smart Docs
smt SUSE Linux Enterprise Subscription Management Tool
soc SUSE OpenStack Cloud
style SUSE Documentation Style Guide
subscription Subscription Management
suma-retail SUSE Multi-Linux Manager for Retail
suma SUSE Multi-Linux Manager
suse-ai SUSE AI
suse-caasp SUSE CaaS Platform
suse-cap SUSE Cloud Application Platform
suse-distribution-migration-system SUSE Distribution Migration System
suse-edge SUSE Edge
trd Technical Reference Documentation""".strip().splitlines()
)
}
ALLOWED_PRODUCTS = tuple([item for item in VALID_PRODUCTS])


#: Regex for one or more languages, separated by comma:
SINGLE_LANG_REGEX = re.compile(r"[a-z]{2}-[a-z]{2}")
MULTIPLE_LANG_REGEX = re.compile(
    rf"^({SINGLE_LANG_REGEX.pattern},)*"
    rf"{SINGLE_LANG_REGEX.pattern}"
)

#: Regex for splitting a path into its components
LIFECYCLES_STR = "|".join(ALLOWED_LIFECYCLES)



#: Syntax for a single doctype
#:
#: <product-value|*>/<docset-value|*>@<lifecycle-value>/<lang-value1,lang-value2,...|*>
#:
#:

SEPARATORS = r"[ :;]+"
RE_SEPARATORS = re.compile(SEPARATORS)

#: Paths to the app's config
APP_CONFIG_PATHS = (f"/etc/{APP_NAME}", f"~/.config/{APP_NAME}", "./")
#: The filename of the app's config file without any paths
APP_CONFIG_FILENAME = "config.toml"