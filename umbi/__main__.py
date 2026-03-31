import logging

import click

import umbi
import umbi.umb

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    show_default=True,
    required=False,
    help="logging level",
)
@click.option("--import-umb", type=click.Path(), required=False, help=".umb filepath to import as ExplicitUmb")
@click.option("--import-ats", type=click.Path(), required=False, help=".umb filepath to import as SimpleAts")
@click.option("--export", type=click.Path(), required=False, help=".umb filepath to export")
def main(log_level, import_umb, import_ats, export):
    umbi.setup_logging(level=log_level)
    logger.info(f"this is {umbi.__toolname__} v.{umbi.__version__}")

    umb = None
    ats = None
    if import_umb is not None:
        umb = umbi.umb.read(import_umb)
        logger.info(f"imported: {umb}")
    if import_ats is not None:
        ats = umbi.ats.read(import_ats)
        logger.info(f"imported: {ats}")
    if export is not None:
        if umb is None and ats is None:
            raise ValueError("--export specified, but nothing to export")
        if umb is not None and ats is not None:
            raise ValueError("cannot specify both --import-umb and --import-ats when using --export")
        if umb is not None:
            umbi.umb.write(umb, export)
        if ats is not None:
            umbi.ats.write(ats, export)


if __name__ == "__main__":
    main()
