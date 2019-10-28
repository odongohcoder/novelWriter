# -*- coding: utf-8 -*-
"""novelWriter LaTeX Converter

 novelWriter – LaTeX Converter
===============================
 Extends the Tokenizer class to write LaTeX

 File History:
 Created: 2019-10-24 [0.3.1]

"""

import textwrap
import logging
import re
import nw

from nw.convert.tokenizer import Tokenizer

logger = logging.getLogger(__name__)

class ToLaTeX(Tokenizer):

    def __init__(self, theProject, theParent):
        Tokenizer.__init__(self, theProject, theParent)
        return

    def doAutoReplace(self):
        Tokenizer.doAutoReplace(self)

        repDict = {
            "\u2013" : "--",
            "\u2014" : "---",
            "\u2500" : "---",
            "\u2026" : "...",
        }
        xRep = re.compile("|".join([re.escape(k) for k in repDict.keys()]), flags=re.DOTALL)
        self.theText = xRep.sub(lambda x: repDict[x.group(0)], self.theText)

        return

    def doConvert(self):

        texTags = {
            self.FMT_B_B : r"\textbf{",
            self.FMT_B_E : r"}",
            self.FMT_I_B : r"\textit{",
            self.FMT_I_E : r"}",
            self.FMT_U_B : r"\underline{",
            self.FMT_U_E : r"}",
        }

        if self.wordWrap > 0:
            tWrap = textwrap.TextWrapper(
                width                = self.wordWrap,
                initial_indent       = "",
                subsequent_indent    = "",
                expand_tabs          = True,
                replace_whitespace   = True,
                fix_sentence_endings = False,
                break_long_words     = True,
                drop_whitespace      = True,
                break_on_hyphens     = True,
                tabsize              = 8,
                max_lines            = None
            )
            tComm = textwrap.TextWrapper(
                width                = self.wordWrap-2,
                initial_indent       = "",
                subsequent_indent    = "",
                expand_tabs          = True,
                replace_whitespace   = True,
                fix_sentence_endings = False,
                break_long_words     = True,
                drop_whitespace      = True,
                break_on_hyphens     = True,
                tabsize              = 8,
                max_lines            = None
            )

        self.theResult = ""
        thisPar = []
        for tType, tText, tFormat, tAlign in self.theTokens:

            begText = ""
            endText = "\n"
            if tAlign == self.A_CENTRE:
                begText = "\\begin{center}\n"
                endText = "\\end{center}\n\n"

            # First check if we have a comment or plain text, as they need some
            # extra replacing before we proceed to wrapping and final formatting.
            if tType == self.T_COMMENT:
                tText = "%% %s" % tText

            elif tType == self.T_TEXT:
                tTemp = tText
                for xPos, xLen, xFmt in reversed(tFormat):
                    tTemp = tTemp[:xPos]+texTags[xFmt]+tTemp[xPos+xLen:]
                tText = tTemp

            tLen = len(tText)

            # The text can now be word wrapped, if we have requested this and it's needed.
            if self.wordWrap > 0 and tLen > self.wordWrap:
                if tType == self.T_COMMENT:
                    aText = tComm.wrap(tText)
                    tText = "\n% ".join(aText)
                else:
                    tText = tWrap.fill(tText)

            # Then the text can receive final formatting before we append it to the results.
            # We also store text lines in a buffer and merge them only when we find an empty line
            # indicating a new paragraph.
            if tType == self.T_EMPTY:
                if len(thisPar) > 0:
                    self.theResult += begText
                    for tTemp in thisPar:
                        self.theResult += "%s\n" % tTemp
                    self.theResult += endText
                thisPar = []

            elif tType == self.T_HEAD1:
                self.theResult += begText
                self.theResult += "{\\Huge %s}\n" % tText
                self.theResult += endText

            elif tType == self.T_HEAD2:
                self.theResult += "\\chapter*{%s}\n\n" % tText

            elif tType == self.T_HEAD3:
                self.theResult += "\\section*{%s}\n\n" % tText

            elif tType == self.T_HEAD4:
                self.theResult += "\\subsection*{%s}\n\n" % tText

            elif tType == self.T_SEP:
                self.theResult += begText
                self.theResult += "%s\n" % tText
                self.theResult += endText

            elif tType == self.T_TEXT:
                thisPar.append(tText)

            elif tType == self.T_PBREAK:
                self.theResult += "\\newpage\n\n"

            elif tType == self.T_COMMENT and self.doComments:
                self.theResult += "%s\n\n" % tText

            elif tType == self.T_COMMAND and self.doCommands:
                self.theResult += "%% @%s\n\n" % tText

        return

# END Class ToLaTeX