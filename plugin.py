###
# Copyright (c) 2019, Michael Burns
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot import utils, plugins, ircutils, callbacks, world, conf, log
import os
import requests
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('DSWeather')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class DSWeather(callbacks.Plugin):
    """Weather info from DarkSky"""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(DSWeather, self)
        self.__parent.__init__(irc)
        locationdb_file = conf.supybot.directories.data.dirize("DSWeather-locations.json")
        self.log.debug("location db:  " + locationdb_file)
        if os.path.exists(locationdb_file):
            with open(locationdb_file) as f:
                self.locationdb = json.load(f)
        else:
            self.log.info("No location db found, creating...")
            self.locationdb = {}
        world.flushers.append(self._sync_locationdb)

    def _sync_locationdb(self):
        locationdb_filename = conf.supybot.directories.data.dirize("DSWeather-locations.json")
        with open(locationdb_filename, 'w') as f:
            json.dump(self.locationdb, f)

    def die(self):
        world.flushers.remove(self._sync_locationdb)
        self.db.flush()
        self._sync_locationdb()
        super().die()

    def _get_location(location):
        self.log.debug("checking location " + str(location))
        lat = "42.55433425"
        lon = "-71.4438279891107"
        self.log.debug("Found location %s,%s" % (lat, lon))
        return (lat, lon)


    def _get_weather(self, latitude, longitude, extra=None):
        return ("46.44", "partly cloudy")
        baseurl = "https://api.darksky.net/forecast/"
        r = requests.get(baseurl + self.registryValue('key') + "/%s,%s" % (str(lat), str(lon)))
        return (r.json()['currently']['temperature'], r.json()['currently']['summary'])



    def weather(self, irc, msg, args, channel, things):
        """get the weather for a location"""
        (lat,lon) = self._get_location(things)
        (temp,status) = self._get_weather(lat, lon)
        self.irc.reply("The weather in \"%s\" currently %s and %s" % (things, temp, status))
    weather = wrap(weather, ['channel', any('something')])


Class = DSWeather


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
