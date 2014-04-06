# Pasticcio

A very simple pastebin web application.

## Authentication

Authentication is not enforcer, instead users are *identified* by an external source that must set the `REMOTE_USER` environment variable.

## Syntax highlighting

To generate the required CSS you need to pick a *style* from the list of available styles (see [Pygments Demo][pygments-demo]) and run the command:

    $ pygmentize -f html -S <stylename> > pasticcio/static/css/pygments.css

[pygments-demo]: http://pygments.org/demo/

## Crontab

A crontab entry must be setup to expire pastes; for example to run the expire command every 5 minutes you must write the following line in `/etc/cron.d/pasticcio-expire`:

    */5 * * * * /path/to/bin/pasticcio -c /etc/pasticcio.conf cleaner

## License

All code is BSD licensed, see LICENSE file.
