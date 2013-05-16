#
# Copyright (c) 2011, David Cooper <dave@kupesoft.com>
# All rights reserved.
#
# Dedicated to Kate Lacey
#
# Permission to use, copy, modify, and/or distribute this software
# for any purpose with or without fee is hereby granted, provided
# that the above copyright notice, the above dedication, and this
# permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHORS DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# THE AUTHORS BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#


from fitparse.exceptions import FitParseError
from fitparse.base import FitFile


class Activity(FitFile):
    def parse(self, *args, **kwargs):
        return_value = super(Activity, self).parse(*args, **kwargs)
        if self.records[0].get_data('type') != 'activity':
            raise FitParseError("File parsed is not an activity file.")
        return return_value
