import click
from tennis_new.fetch.tennis_explorer.combiner import get_joined


@click.command()
@click.option('--rewrite-match-file', default=True)
def _get_joined(rewrite_match_file):
    get_joined(rewrite_match_file=rewrite_match_file)


if __name__ == '__main__':
    _get_joined()