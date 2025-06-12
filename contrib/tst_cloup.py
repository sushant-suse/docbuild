from pprint import pprint

import cloup
from cloup import option, option_group


@cloup.command()
@cloup.argument('input_path', help="Input path")
@cloup.argument('out_path', help="Output path")
@option_group(
    'An option group',
    option('-o', '--one', help='a 1st cool option'),
    option('-t', '--two', help='a 2nd cool option'),
    option('--three', help='a 3rd cool option'),
)
def main(**kwargs):
    """A test program for cloup."""
    pprint(kwargs, indent=3)

main()

