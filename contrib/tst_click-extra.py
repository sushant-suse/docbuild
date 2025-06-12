from click import echo
from click_extra import config_option
from cloup import command, option, option_group
from cloup.constraints import RequireAtLeast


@command()
@option("--count", default=1, help="Number of greetings.")
@option("--name", prompt="Your name", help="The person to greet.")
@option_group(
    "Cool options",
    option("--foo", help="The option that starts it all."),
    option("--bar", help="Another important option."),
    config_option("--hello-conf", metavar="CONF_FILE", help="Loads CLI config."),
    constraint=RequireAtLeast(1),
)
def hello(count, name, foo, bar, hello_conf):
    """Simple program that greets NAME for a total of COUNT times."""
    for _ in range(count):
        echo(f"Hello, {name}!")


if __name__ == "__main__":
   hello()

