#!/usr/bin/env python
"""Update citation data only after a complete, successful Scholar response."""

from datetime import datetime
from pathlib import Path
import os
import sys
import tempfile

import yaml


def load_scholar_user_id() -> str:
    with open('_data/socials.yml') as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict) or not config.get('scholar_userid'):
        raise ValueError('Configure scholar_userid in _data/socials.yml')
    return config['scholar_userid']


def get_scholar_citations(client=None, output_file='_data/citations.yml') -> bool:
    """Return whether data changed; preserve the existing file on any failure."""
    output = Path(output_file)
    today = datetime.now().strftime('%Y-%m-%d')
    existing_data = None
    if output.exists():
        existing_data = yaml.safe_load(output.read_text())
        if not isinstance(existing_data, dict) or not isinstance(existing_data.get('papers'), dict):
            raise ValueError(f'Invalid citation data in {output}; leaving it unchanged')
        if not isinstance(existing_data.get('metadata'), dict):
            raise ValueError(f'Invalid citation metadata in {output}; leaving it unchanged')
        if existing_data['metadata'].get('last_updated') == today:
            print('Citations data is already up-to-date.')
            return False

    scholar_user_id = load_scholar_user_id()
    if client is None:
        from scholarly import scholarly
        client = scholarly
    client.set_timeout(15)
    client.set_retries(3)
    print(f'Fetching citations for Google Scholar ID: {scholar_user_id}')
    author_data = client.fill(client.search_author_id(scholar_user_id))
    if not isinstance(author_data, dict) or not isinstance(author_data.get('publications'), list):
        raise ValueError('Scholar did not return a publication list')

    citation_data = {'metadata': {'last_updated': today}, 'papers': {}}
    for pub in author_data['publications']:
        pub_id = pub.get('pub_id') or pub.get('author_pub_id')
        if not pub_id or pub_id in citation_data['papers']:
            raise ValueError('Scholar returned a missing or duplicate publication ID')
        citation_data['papers'][pub_id] = {
            'title': pub.get('bib', {}).get('title', 'Unknown Title'),
            'year': pub.get('bib', {}).get('pub_year', 'Unknown Year'),
            'citations': pub.get('num_citations', 0),
        }

    if existing_data is not None and existing_data['papers'] == citation_data['papers']:
        print('No changes in citation data.')
        return False

    # Write beside the target so replace is atomic, including on first creation.
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=output.parent, prefix='.citations-', delete=False) as stream:
            temporary_path = Path(stream.name)
            yaml.safe_dump(citation_data, stream, width=1000, sort_keys=True)
        os.replace(temporary_path, output)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    print(f'Citation data saved to {output}')
    return True


if __name__ == '__main__':
    try:
        get_scholar_citations()
    except Exception as error:
        print(f'Citation update failed: {error}', file=sys.stderr)
        sys.exit(1)
