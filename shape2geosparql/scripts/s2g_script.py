import click

from shape2geosparql import convert


@click.command()
@click.argument('infile', type=click.Path(exists=True))
@click.option('--outfile', '-o', type=click.Path(), help='If not provided, output is stdout')
@click.option('--format', '-f', 'outformat', default='nt', help="'xml', 'n3', 'turtle', 'nt', etc.")
def main(infile, outfile, outformat):
    converter = convert(infile)

    if outfile is None:
        print(converter.write(outformat=outformat).decode())
    else:
        converter.write(outfile, outformat=outformat)


if __name__ == '__main__':
    main()
