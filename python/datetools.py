#!/usr/bin/env python
'''
For working with dates
'''

# Standard imports:
import datetime

def nextSunday(d, count):
    '''
    Given a date, `d`, return the date `count`-th nearest Sunday.

    A negative value for `count` move back in time to Sundays before.
    A positive value for `count` moves forward in time to following
    Sundays.  We raise `ValueError` if `count` is zero.
    '''

    if not isinstance(d, datetime.date):
        raise TypeError(
            'Non-date (%s, %s) was passed to nextSunday()!' % (
                type(d), d))
    if not isinstance(count, int):
        raise TypeError(
            'Non-int (%s, %s) was passed as count to nextSunday()!' % (
                type(count), count))
    if count == 0:
        raise ValueError(
            'Count of zero was passed to nextSunday()!')

    # Handle a non-Sunday start by advancing a partial week.
    if d.weekday() != 6:
        if count > 0:
            d += datetime.timedelta(
                days=6 - d.weekday())
            count -= 1
        else:
            d -= datetime.timedelta(
                days=d.weekday() + 1)
            count += 1

    # Now that we are on a Sunday, the rest of the way is simple.
    return d + datetime.timedelta(weeks=count)

def followingDays(d, count):
    '''
    Given a date, `d`, return the date of each day that follows,
    precisely `count` of them.
    '''

    return [
        d + datetime.timedelta(days=index + 1)
        for index in range(count)
        ]

def inclusiveDateRange(firstDate, lastDate):
    '''
    Return all the dates from `firstDate` through `lastDate`.
    '''

    # FIXME: Naiive, but I have no Internet connectivity at the
    # moment!
    result = []
    d = firstDate
    while d <= lastDate:
        result.append(d)
        d += datetime.timedelta(days=1)
    return result

def dateOfEaster(year):
    '''
    Return the date of Easter for a given `year`.

    http://aa.usno.navy.mil/faq/docs/easter.php
    '''

    y = year
    c = y / 100
    n = y - 19 * ( y / 19 )
    k = ( c - 17 ) / 25
    i = c - c / 4 - ( c - k ) / 3 + 19 \
        * n + 15
    i = i - 30 * ( i / 30 )
    i = i - ( i / 28 ) * ( 1 - ( i / 28 ) \
        * ( 29 / ( i + 1 ) ) \
        * ( ( 21 - n ) / 11 ) )
    j = y + y / 4 + i + 2 - c + c / 4
    j = j - 7 * ( j / 7 )
    l = i - j
    m = 3 + ( l + 40 ) / 44
    d = l + 28 - 31 * ( m / 4 )
    return datetime.date(year, m, d)

def sundayCycleForDate(d):
    '''
    Return the Sunday cycle for the Gospel reading ('A', 'B', or 'C')
    for a given date, `d`.
    '''

    christmasDate = datetime.date(d.year, 12, 25)
    firstSundayOfAdventDate = nextSunday(christmasDate, -4)
    if d >= firstSundayOfAdventDate:
        return 'ABC'[d.year % 3]
    else:
        return 'CAB'[d.year % 3]

def weekdayCycleForDate(d):
    '''
    Return the weekday cycle for the non-Gospel reading ('I' or 'II')
    for a given date, `d`.
    '''

    christmasDate = datetime.date(d.year, 12, 25)
    firstSundayOfAdventDate = nextSunday(christmasDate, -4)
    if d >= firstSundayOfAdventDate:
        return ['I', 'II'][d.year % 2]
    else:
        return ['II', 'I'][d.year % 2]
