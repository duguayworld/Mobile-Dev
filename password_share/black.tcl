# black.tcl -
#
#   Experimental!
#
#  Copyright (c) 2007-2008 Mats Bengtsson
#
# $Id: black.tcl,v 1.2 2009/10/25 19:21:30 oberdorfer Exp $

package require Tk

namespace eval ttk::theme::black {
  variable version 0.0.1
  variable dir [file dirname [info script]]

  package provide ttk::theme::black $version

  # NB: These colors must be in sync with the ones in black.rdb

  variable colors
  array set colors {
      -disabledfg "#7372a7"
      -frame      "#20192a"
      -dark       "#52367e"
      -darker     "#33234c"
      -darkest    "#20192a"
      -lighter    "#8c598c"
      -lightest   "#ffffff"
      -selectbg   "#be6d89"
      -selectfg   "#33234c"
      }

  ttk::style theme create black -parent clam -settings {

    # -----------------------------------------------------------------
    # Theme defaults
    #
    ttk::style configure . \
        -background $colors(-frame) \
        -foreground #ffffff \
        -bordercolor $colors(-darkest) \
        -darkcolor $colors(-dark) \
        -lightcolor $colors(-lighter) \
        -troughcolor $colors(-darker) \
        -selectbackground $colors(-selectbg) \
        -selectforeground $colors(-selectfg) \
        -selectborderwidth 0 \
        -font TkDefaultFont

    ttk::style map "." \
        -background [list disabled $colors(-frame) \
        active $colors(-darker)] \
        -foreground [list disabled $colors(-disabledfg)] \
        -selectbackground [list  !focus $colors(-darker)] \
        -selectforeground [list  !focus #33234c]

    # ttk widgets.
    ttk::style configure TButton \
        -width -22 -padding {5 5} -relief raised
    ttk::style configure TMenubutton \
        -width -22 -padding {5 5} -relief raised
    ttk::style configure TCheckbutton \
        -indicatorbackground "#ffffff" -indicatormargin {3 3 12 3}
    ttk::style configure TRadiobutton \
        -indicatorbackground "#ffffff" -indicatormargin {3 3 12 3}

    ttk::style configure TEntry \
        -fieldbackground #ffffff \
        -foreground #000000 \
        -padding {50 10}
    ttk::style configure TCombobox \
        -fieldbackground #ffffff \
        -foreground #000000 \
        -padding {50 10}
    ttk::style configure TSpinbox \
        -foreground #000000

    ttk::style configure TNotebook.Tab \
        -padding {24 12 24 12}

    # tk widgets.
    ttk::style map Menu \
        -background [list active $colors(-darker)] \
        -foreground [list disabled $colors(-disabledfg)]

    ttk::style configure TreeCtrl \
        -background 24292e -itembackground {gray60 gray50} \
        -itemfill #ffffff -itemaccentfill yellow
  }
}

# A few tricks for Tablelist.

namespace eval ::tablelist:: {

  proc blackTheme {} {
    variable themeDefaults

    array set colors [array get ttk::theme::black::colors]

    array set themeDefaults [list \
      -background      "#24292e" \
      -foreground      "#ffffff" \
      -disabledforeground $colors(-disabledfg) \
      -stripebackground      "#191919" \
      -selectbackground      "#4a6984" \
      -selectforeground      "#8b8b00" \
      -selectborderwidth 0 \
      -font        TkTextFont \
      -labelbackground    $colors(-darker) \
      -labeldisabledBg    "#24292e" \
      -labelactiveBg    "#24292e" \
      -labelpressedBg    "#24292e" \
      -labelforeground    #ffffff \
      -labeldisabledFg    "#ffffff" \
      -labelactiveFg    #ffffff \
      -labelpressedFg    #ffffff \
      -labelfont    TkDefaultFont \
      -labelborderwidth    2 \
      -labelpady    1 \
      -arrowcolor    "" \
      -arrowstyle    sunken10x9 \
      ]
  }
}
