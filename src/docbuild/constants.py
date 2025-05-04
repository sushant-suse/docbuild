import re

DEFAULT_LANGS = ("en-us",)
#: All languages supported by the documentation portal
ALL_LANGUAGES = frozenset(
    "de-de en-us es-es fr-fr ja-jp ko-kr pt-br zh-cn".split(" ")
)

#: The different server roles, including long and short spelling
SERVER_ROLE = ("production", "prod", "p",
               "testing", "test", "t",
               "staging", "stage", "s",
               )

#: The different lifecycle states of a docset
LIFECYCLES = ("supported", "beta", "hidden", "unsupported")


#: All product acronyms and their names
#: - key: /product/@productid
#: - value: /product/name
#
# Use the following command to create the output below:
# xmlstarlet sel -t -v '/product/@productid' -o ' ' -v '/product/name' -nl config.d/[a-z]*.xml
VALID_PRODUCTS = {key.strip(): value.strip()
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


#: Regex for one or more languages, separated by comma:
SINGLE_LANG_REGEX = re.compile(r"[a-z]{2}-[a-z]{2}")
MULTIPLE_LANG_REGEX = re.compile(
    rf"^({SINGLE_LANG_REGEX.pattern},)*"
    rf"{SINGLE_LANG_REGEX.pattern}"
)

#: Regex for splitting a path into its components
LIFECYCLES_STR = "|".join(LIFECYCLES)

PRODUCT_REGEX = re.compile(r"[\w\d_-]+")
DOCSET_REGEX = re.compile(r"[\w\d\._-]+")

HTML_REGEX = r"(?:single-)?html"
DCFILE_REGEX = r"([\w\d_-]+)"


#: Syntax for a single doctype
#:
#: <product-value|*>/<docset-value|*>@<lifecycle-value>/<lang-value1,lang-value2,...|*>
#:
#:
PRODUCT_DOCSET = (
    rf"^/?(?P<product>{PRODUCT_REGEX.pattern}|\*)?"
    rf"/(?P<docset>{DOCSET_REGEX.pattern}|\*)?"
)

SINGLE_DOCTYPE = (
    rf"{PRODUCT_DOCSET}"
    rf"(?:@(?P<lifecycle>{LIFECYCLES_STR}|\*))?"
    rf"(?:/(?P<lang>(?:{SINGLE_LANG_REGEX.pattern}(?:,{SINGLE_LANG_REGEX.pattern})*)|\*))?$"
)



SEPARATORS = r"[ :;]+"
RE_SEPARATORS = re.compile(SEPARATORS)
SINGLE_DOCTYPE_REGEX = re.compile(SINGLE_DOCTYPE)
PRODUCT_DOCSET_REGEX = re.compile(PRODUCT_DOCSET)