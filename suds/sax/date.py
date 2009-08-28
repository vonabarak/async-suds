# This program is free software; you can redistribute it and/or modify
# it under the terms of the (LGPL) GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the 
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library Lesser General Public License for more details at
# ( http://www.gnu.org/licenses/lgpl.html ).
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# written by: Nathan Van Gheem (vangheem@gmail.com)

"""
The I{xdate} module provides classes for converstion
between XML dates and python objects.
"""

from logging import getLogger
from suds import *
from suds.xsd import *
import time
import datetime as dt
import re

log = getLogger(__name__)


class Date:
    """
    An XML date object.
    Supported formats:
        YYYY-MM-DD
        YYYY-MM-DD(z|Z)
        YYYY-MM-DD+06:00
        YYYY-MM-DD-06:00
    @ivar date: The object value.
    @type date: L{dt.date}
    """
    def __init__(self, date):
        """
        @param date: The value of the object.
        @type date: (L{dt.date}|L{str})
        @raise ValueError: When I{date} is invalid.
        """
        if isinstance(date, dt.date):
            self.date = date
            return
        if isinstance(date, basestring):
            self.date = self.__parse(date)
            return
        raise ValueError, type(date)
    
    def year(self):
        """
        Get the I{year} component.
        @return: The year.
        @rtype: int
        """
        return self.date.year
    
    def month(self):
        """
        Get the I{month} component.
        @return: The month.
        @rtype: int
        """
        return self.date.month
    
    def day(self):
        """
        Get the I{day} component.
        @return: The day.
        @rtype: int
        """
        return self.date.day
        
    def __parse(self, s):
        """
        Parse the string date.
        Supported formats:
            YYYY-MM-DD
            YYYY-MM-DD(z|Z)
            YYYY-MM-DD+06:00
            YYYY-MM-DD-06:00
        Although, the TZ is ignored because it's meaningless
        without the time, right?
        @param s: A date string.
        @type s: str
        @return: A date object.
        @rtype: L{dt.date}
        """
        try:
            year, month, day = s[:10].split('-', 2)
            year = int(year)
            month = int(month)
            day = int(day)
            return dt.date(year, month, day)
        except:
            log.debug(s, exec_info=True)
            raise ValueError, 'Invalid format "%s"' % s
        
    def __str__(self):
        return unicode(self)
    
    def __unicode__(self):
        return self.date.isoformat()


class Time:
    """
    An XML time object.
    Supported formats:
        HH:MI:SS
        HH:MI:SS(z|Z)
        HH:MI:SS.ms
        HH:MI:SS.ms(z|Z)
        HH:MI:SS(+|-)06:00
        HH:MI:SS.ms(+|-)06:00
    @ivar date: The object value.
    @type date: L{dt.time}
    """
    
    def __init__(self, time, adjusted=True):
        """
        @param time: The value of the object.
        @type time: (L{dt.time}|L{str})
        @param adjusted: Adjust for I{local} Timezone.
        @type adjusted: boolean
        @raise ValueError: When I{time} is invalid.
        """
        if isinstance(time, dt.time):
            self.time = time
            return
        if isinstance(time, basestring):
            self.time = self.__parse(time)
            if adjusted:
                self.__adjust()
            return
        raise ValueError, type(time)
    
    def hour(self):
        """
        Get the I{hour} component.
        @return: The hour.
        @rtype: int
        """
        return self.time.hour
    
    def minute(self):
        """
        Get the I{minute} component.
        @return: The minute.
        @rtype: int
        """
        return self.time.minute
    
    def second(self):
        """
        Get the I{seconds} component.
        @return: The seconds.
        @rtype: int
        """
        return self.time.second
    
    def microsecond(self):
        """
        Get the I{microsecond} component.
        @return: The microsecond.
        @rtype: int
        """
        return self.time.microsecond
    
    def __adjust(self):
        """
        Adjust for TZ offset.
        """
        if hasattr(self, 'offset'):
            today = dt.date.today()
            tz = Timezone()
            delta = Timezone.adjustment(self.offset)
            d = dt.datetime.combine(today, self.time)
            d = ( d + delta )
            self.time = d.time()
        
    def __parse(self, s):
        """
        Parse the string date.
        Patterns:
            HH:MI:SS
            HH:MI:SS(z|Z)
            HH:MI:SS.ms
            HH:MI:SS.ms(z|Z)
            HH:MI:SS(+|-)06:00
            HH:MI:SS.ms(+|-)06:00
        @param s: A time string.
        @type s: str
        @return: A time object.
        @rtype: L{dt.time}
        """
        try:
            offset = None
            part = Timezone.split(s)
            hour, minute, second = part[0].split(':', 2)
            hour = int(hour)
            minute = int(minute)
            second, ms = self.__second(second)
            if len(part) == 2:
                self.offset = self.__offset(part[1])
            if ms is None:
                return dt.time(hour, minute, second)
            else:
                return dt.time(hour, minute, second, ms)
        except:
            log.debug(s, exec_info=True)
            raise ValueError, 'Invalid format "%s"' % s
        
    def __second(self, s):
        """
        Parse the seconds and microseconds.
        @param s: A string representation of the seconds.
        @type s: str
        @return: Tuple of (sec,ms)
        @rtype: tuple.
        """
        part = s.split('.')
        if len(part) == 1:
            return (int(part[0]), None)
        else:
            return (int(part[0]), int(part[1]))
        
    def __offset(self, s):
        """
        Parse the TZ offset.
        @param s: A string representation of the TZ offset.
        @type s: str
        @return: The signed offset in hours.
        @rtype: str
        """
        if len(s) == len('-00:00'):
            return int(s[:3])
        if len(s) == 0:
            return Timezone.local
        if len(s) == 1:
            return 0
        raise Exception()

    def __str__(self):
        return unicode(self)
    
    def __unicode__(self):
        time = self.time.isoformat()
        return '%s%+.2d:00' % (time, Timezone.local)


class DateTime(Date,Time):
    """
    An XML time object.
    Supported formats:
        YYYY-MM-DDTHH:MI:SS
        YYYY-MM-DDTHH:MI:SS(z|Z)
        YYYY-MM-DDTHH:MI:SS.ms
        YYYY-MM-DDTHH:MI:SS.ms(z|Z)
        YYYY-MM-DDTHH:MI:SS(+|-)06:00
        YYYY-MM-DDTHH:MI:SS.ms(+|-)06:00
    @ivar date: The object value.
    @type date: L{dt.date}
    """
    def __init__(self, date):
        """
        @param tm: The value of the object.
        @type tm: ( L{dt.time}| L{dt.datetime} | L{str} )
        @raise ValueError: When I{tm} is invalid.
        """
        if isinstance(date, dt.datetime):
            Date.__init__(self, date.date())
            Time.__init__(self, date.time())
            self.datetime = \
                dt.datetime.combine(self.date, self.time)
            return
        if isinstance(date, basestring):
            part = date.split('T')
            Date.__init__(self, part[0])
            Time.__init__(self, part[1], 0)
            self.datetime = \
                dt.datetime.combine(self.date, self.time)
            self.__adjust()
            return
        raise ValueError, type(date)
    
    def __adjust(self):
        """
        Adjust for TZ offset.
        """
        if hasattr(self, 'offset'):
            tz = Timezone()
            delta = Timezone.adjustment(self.offset)
            d = ( self.datetime + delta )
            self.datetime = d
            self.date = d.date()
            self.time = d.time()

    def __str__(self):
        return unicode(self)
    
    def __unicode__(self):
        s = []
        s.append(Date.__unicode__(self))
        s.append(Time.__unicode__(self))
        return 'T'.join(s)
    
    
class Timezone:
    """
    Timezone object used to do TZ conversions
    @cvar local: The (A) local TZ offset.
    @type local: int
    @cvar patten: The regex patten to match TZ.
    @type patten: L{re.RegexObject}
    """

    local = ( 0-time.timezone/60/60 )
    pattern = re.compile('([zZ])|([\-\+][0-9]{2}:[0-9]{2})')
    
    @classmethod
    def split(cls, s):
        """
        Split the TZ from string.
        @param s: A string containing a timezone
        @type s: basestring
        @return: The split parts.
        @rtype: tuple
        """
        m = cls.pattern.search(s)
        if m is None:
            return (s,)
        x = m.start(0)
        return (s[:x], s[x:])
    
    @classmethod
    def adjustment(cls, offset):
        """
        Get the adjustment to the I{local} TZ.
        @return: The delta between I{offset} and local TZ.
        @rtype: L{dt.timedelta}
        """
        delta = ( cls.local - offset )
        return dt.timedelta(hours=delta)





def DT(s):
    t = DateTime(s)
    print '\n"%s"\n %s' % (s, t)

if __name__ == '__main__':
    print 'TIME'
    t = Time(dt.datetime.now().time())
    print t
    t = Time('10:30:22.445')
    print t
    t = Time('10:30:32z')
    print t
    t = Time('10:30:42-02:00')
    print t
    print 'DATE'
    d = Date(dt.datetime.now().date())
    print d
    d = Date('2009-07-28')
    print d
    d = Date('2009-07-29Z')
    print d
    d = Date('2009-07-30-06:00')
    print d
    d = Date('2009-07-31+06:00')
    print d
    print 'DATETIME'
    t = DateTime(dt.datetime.now())
    print t
    
    DT('2009-07-28T10:10:22')
    DT('2009-07-28T10:20:22+02:00')
    DT('2009-07-28T10:30:22Z')
    DT('2009-07-28T10:40:22-05:00')
    DT('2009-07-28T00:50:22-05:00')
    DT('2009-07-28T10:11:22-07:00')
    
    Timezone.local = 4
    print '\nTZ=4'

    DT('2009-07-28T10:10:22')
    DT('2009-07-28T10:20:22+02:00')
    DT('2009-07-28T10:30:22Z')
    DT('2009-07-28T10:40:22-05:00')
    DT('2009-07-28T00:50:22-05:00')
    DT('2009-07-28T10:11:22-07:00')