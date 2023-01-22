import click


@click.group()
def main():
    """Enduro"""
    pass


@main.command()
@click.argument("config_path")
def run(config_path):
    from enduro.run import run

    run(config_path)
