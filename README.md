# Band Gantt

Visualize the tenures of the members of a band.

App built with [Dash](https://github.com/plotly/dash)

Uses data from the [MusicBrainz API](https://musicbrainz.org/doc/Development/XML_Web_Service/Version_2)

 - Search for a band by name:

   - Format: `https://musicbrainz.org/ws/2/artist?query=<QUERY>&limit=<LIMIT>&offset=<OFFSET>&fmt=json`

   - Example: https://musicbrainz.org/ws/2/artist?query=LCD+Soundsystem&limit=10&fmt=json


 - Get band info:

   - Format: `https://musicbrainz.org/ws/2/artist/<MBID>?inc=<INC>&fmt=json`

    - Example: https://musicbrainz.org/ws/2/artist/2aaf7396-6ab8-40f3-9776-a41c42c8e26b?inc=artist-rels&fmt=json

