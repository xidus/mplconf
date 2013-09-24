#!/usr/bin/python -OB
# -*- coding: utf-8 -*-
# Version: Sat 4 May 2013
#   * PEP 8
#   * rcParams settings moved to mplrc.py
#
# Version: Thu 21 Jun 2012
#   * Added function invert(hexc) to invert hex-colours
#
# Version: Sun  8 Apr 2012
#   * Changes to fill_between_steps
#       + extend variable
#       + left/right close-ends variables
#   * Additional options to MPl setup
#       + Dictionaries for different types of setup are set
#         and can be loaded with a single function call.
# Version: Sat 10 Mar 2012
#
"""
Matplotlib-specific auxiliary functions
=======================================

IO Keymap
---------

fullscreen : f               # toggling
home : h, r, home            # home or reset mnemonic
back : left, c, backspace    # forward / backward keys to enable
forward : right, v           #   left handed quick navigation
pan : p                      # pan mnemonic
zoom : o                     # zoom mnemonic
save : s                     # saving current figure
grid : g                     # switching on/off a grid in current axes
yscale : l                   # toggle scaling of y-axes ('log'/'linear')
xscale : L, k                # toggle scaling of x-axes ('log'/'linear')
all_axes : a                 # enable all axes

To make:
--------

* Make SaveWebFig|SaveFig4Web|SaveFig(media='web')-option

* fill_between_steps(... , close_ends=True):

"""

import datetime as dt

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as md


# -------------------------------------------------------------------------- #
def fig_style(dct):
    for obj in dct:
        mpl.rc(obj, **dct[obj])


def mplrc(*args):
    """
    Updates mpl.rcParams with style of choice

    Choices:
    --------

    default : always used as the first settings files to be applied.
              it can be added to *args if a different order is needed.

    usetex : include to set text.usetex to True (off by default)

    publish_digital : Nice settings with grey axes facecolor.

    publish_printed : Almost the same as the efault setting,
                      but WITH text.usetex set to True.

    """

    import os
    import json

    # Uncomment to display path for matplotlibrc-file
    # >>> print mpl.matplotlib_fname()

    # To see all the set values in interactive mode, type
    # >>> import matplotlib.rcsetup as rc
    # >>> rc.defaultParams
    #
    args = list(args)

    if not args:
        args = ['default']

    if 'default' not in args:
        args = ['default'] + args

    fnames = ['mplrc_{}.json'.format(fname) for fname in args]
    dname = os.path.dirname(os.path.realpath(__file__))

    for fname in fnames:

        try:
            ifname = os.path.join(dname, fname)
            mpl.rcParams.update(json.load(open(ifname)))
            # print 'Updated MPL rc parameters using {} ...'.format(fname)

        except:
            print 'Could not load custom MPL rc parameters for {} ...'.format(fname)
            continue


# -------------------------------------------------------------------------- #
def rmath(s):
    """If text.usetex is False, this can ease the pain of manually writing TeX strings."""
    return r'$\mathrm{{{}}}$'.format('\ '.join(s.split(' ')))


# -------------------------------------------------------------------------- #
# SAVING FIGURES (Note the capitalization of SaveFig vs. savefig.)
def SaveFig(fname,
            dpi=600,
            facecolor='w',
            edgecolor='w',
            orientation='portrait',
            papertype=None,         # PS only ('letter', 'legal', 'a0'-'a10', ..)
            transparent=False,
            bbox_inches=None,       # boundary box. 'tight' => fig.suptitle cropped away.
            pad_inches=.1           # pad_inches
            ):

    raise Exception('SaveFig() is deprecated. Please use plt.savefig() instead')

    plt.savefig(fname, dpi=dpi, facecolor=facecolor, edgecolor=edgecolor,
                orientation=orientation, papertype=papertype,
                transparent=transparent, bbox_inches=bbox_inches,
                pad_inches=pad_inches
                )


# -------------------------------------------------------------------------- #
def fill_between_steps(x, y,
                       where='post',
                       l='open',
                       r='open',
                       bottom=0,
                       plotkwargs=None,
                       fillkwargs=None,
                       nofill=False
                       ):
    """
    A fill_between for stepfunctions.

    ---
    To test this, import and run e.g.

        wh = 'post'; clf(); fill_between_steps(x, y, where=wh); step(x, y, where=wh, c='r'); plot(x, y, c='g');

    There is a problem with the way the standard fill_between function works,
    when using the 'mid' option. The line is shown correctly, but the filling
    underneath does not!

    Why this does not work is unclear, since the points are correctly shifted
    and mid-ified, which can be seen by the matching of the lines from the
    standard step() function.

    ---
    bottom: if None, the value 0 is used as the bottom.

    """

    # To be sure that data arrays are NumPy arrays
    x, y = np.array(x), np.array(y)

    # Create step-versions of the two arrays
    stepx = stepsx(x, where=where, left=l, right=r)
    stepy = stepsy(y, where=where, left=l, right=r, bottom=bottom)

    # Default kwargs for the line and fill plot
    if plotkwargs is None:
        # plotkwargs = dict(color='b', linewidth=1.5)
        plotkwargs = {}

    if fillkwargs is None:
        # fillkwargs = dict(facecolor='b', linewidth=0, alpha=0.2)
        fillkwargs = {}

    # Plot line
#    plothandle = plt.plot(x, y, ls='steps-%s' % where, **plotkwargs)
    plothandle = plt.plot(stepx, stepy, **plotkwargs)

    # Plot fill
    if nofill is False:
        plt.fill_between(stepx, stepy, bottom, **fillkwargs)

    # Only return the handles and labels for the line
    return plothandle


def stepsx(x,
           where='post',
           left='closed',
           right='closed'
           ):
    """
    Converts an array to double-length for step plotting

    Assumes that x[i] < x[i+1] for i in range(len(x))
    """
    if where not in ('pre', 'mid', 'post'):
        raise RuntimeError

    if where == 'pre':
        # Returns [x1, x1, x2, x2, x3, x3, ..., xn]
        newx = np.array(zip(x, x)).ravel()[:-1]

        # Extend to the left
        extend = 'left'

    elif where == 'post':
        # Returns [    x1, x2, x2, x3, x3, ..., xn, xn]
        newx = np.array(zip(x, x)).ravel()[1:]

        # Extend to right
        extend = 'right'

    elif where == 'mid':
        # Keep first and last (nth) points
        x_1, x_n = [x[0]], [x[-1]]

        # Half the difference between consecutive points
        diffx = (x[1:] - x[:-1]) / 2.0

        # Shift the points halfway to the right to get the middle point positions
        # We lose the first (we shift away from it) and last (excluded since len(diffx) < len(x)) points
        midx = x[:-1] + diffx

        # Add the first and the last points to the middle x values
        midx = x_1 + list(midx) + x_n

        # Do the same to these points as if 'pre' were selected
        # But remove the first point as well, since this is doubled
        newx = np.array(zip(midx, midx)).ravel()[1:-1]

        # Extend to both sides
        extend = 'both'

    # Extend
    dx = newx[1] - newx[0]
    if extend == 'left' or extend == 'both':
        newx = np.concatenate([[newx[0] - dx], newx])

    if extend == 'right' or extend == 'both':
        newx = np.concatenate((newx, [newx[-1] + dx]))

    # Open or closed?
    if left == 'closed':
        newx = np.concatenate([[newx[0]], newx])

    if right == 'closed':
        newx = np.concatenate([newx, [newx[-1]]])

    return newx


def stepsy(y,
           where='post',
           left='closed',
           right='closed',
           bottom=0
           ):
    """
    Converts an array to double-length for step plotting
    """

    if where not in ('pre', 'mid', 'post'):
        raise RuntimeError

    if where == 'pre':
        # Returns [    y1, y2, y2, y3, y3, ..., yn, yn]
        newy = np.array(zip(y, y)).ravel()[1:]

        # Extend to the left
        extend = 'left'

    elif where == 'post':
        # Returns [y1, y1, y2, y2, y3, y3, ..., yn    ]
        newy = np.array(zip(y, y)).ravel()[:-1]

        # Extend to right
        extend = 'right'

    elif where == 'mid':
        # Returns [y1, y1, y2, y2, y3, y3, ..., yn, yn]
        newy = np.array(zip(y, y)).ravel()[:]

        # Extend to both sides
        extend = 'both'

    # Extend
    if extend == 'left' or extend == 'both':
        newy = np.concatenate([newy[:1], newy])

    if extend == 'right' or extend == 'both':
        newy = np.concatenate([newy, newy[-2:-1]])

    # Open or closed?
    if left == 'closed':
        newy = np.concatenate([[bottom], newy])

    if right == 'closed':
        newy = np.concatenate([newy, [bottom]])

    return newy


# -------------------------------------------------------------------------- #
def diurnal(dts, **plot_kwargs):
    """
    Makes diurnal plot from input datetimes (dts)
    Returns plot handles
    """
    dts = list(dts)
    times = []
    for i, d in enumerate(dts):
        times.append(dt.datetime(1, 1, 2, d.hour, d.minute, d.second))
    mdts, mtimes = md.date2num(dts) // 1, md.date2num(times)
    p = plt.plot(mdts, mtimes, **plot_kwargs)
    return p


def mdiurnal(mdts, **plot_kwargs):
    """
    Makes diurnal plot from input matplotlib datetimes (mdts)
    Returns plot handles
    """
    dts = md.num2date(mdts)
    p = diurnal(dts, **plot_kwargs)
    return p


# -------------------------------------------------------------------------- #
# def month_letter_formatter(x, pos=None):
#     thisind = np.clip(int(x + 0.5), 0, N - 1)
#     return r.date[thisind].strftime('%b')[0]

# ticker.FuncFormatter(month_letter_formatter)
# -------------------------------------------------------------------------- #
