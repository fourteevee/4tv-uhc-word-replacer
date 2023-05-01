from io import TextIOWrapper
import json
import string
from argparse import ArgumentParser, FileType
from os import walk, listdir
from os.path import exists, abspath, expanduser, join, isfile
from random import randint, choice
from re import search, compile, findall, match
import toml
from pyinputplus import inputFilepath, inputStr, inputYesNo
from dataclasses import dataclass
from logging import Logger, getLogger, StreamHandler, Formatter, DEBUG, INFO, WARNING, ERROR, CRITICAL
from sys import stdout as STDOUT
from datetime import datetime

"""
 _____ _                               __  __ _      _       _       
/__   \ |__   ___   /\ /\ _ __   ___  / _|/ _(_) ___(_) __ _| |      
  / /\/ '_ \ / _ \ / / \ \ '_ \ / _ \| |_| |_| |/ __| |/ _` | |      
 / /  | | | |  __/ \ \_/ / | | | (_) |  _|  _| | (__| | (_| | |      
 \/   |_| |_|\___|  \___/|_| |_|\___/|_| |_| |_|\___|_|\__,_|_|      
                                                                     
               ___          __  __  _____         ___                
        /\  /\/___\/\/\    /__\/ _\/__   \/\ /\  / __\ /\ /\         
 _____ / /_/ //  //    \  /_\  \ \   / /\/ / \ \/ /   / //_/  _____  
|_____/ __  / \_// /\/\ \//__  _\ \ / /  \ \_/ / /___/ __ \  |_____| 
      \/ /_/\___/\/    \/\__/  \__/ \/    \___/\____/\/  \/          
                                                                     
             ___      _ _           _   _                            
            / __\___ | | | ___  ___| |_(_) ___  _ __                 
   _____   / /  / _ \| | |/ _ \/ __| __| |/ _ \| '_ \   _____        
  |_____| / /__| (_) | | |  __/ (__| |_| | (_) | | | | |_____|       
          \____/\___/|_|_|\___|\___|\__|_|\___/|_| |_|               
                                                                     
 __    __              _     __            _                         
/ / /\ \ \___  _ __ __| |   /__\ ___ _ __ | | __ _  ___ ___ _ __     
\ \/  \/ / _ \| '__/ _` |  / \/// _ \ '_ \| |/ _` |/ __/ _ \ '__|    
 \  /\  / (_) | | | (_| | / _  \  __/ |_) | | (_| | (_|  __/ |       
  \/  \/ \___/|_|  \__,_| \/ \_/\___| .__/|_|\__,_|\___\___|_|       
                                    |_|                              
"""

_DESCRIPTION = "This is a program that, when run from the command line, creates a mod in js that can be used with TUHC. It replaces any given string with any other string, accounting for typing quirks."

"""
Authors: Amelia Pytosh, yabobay
Date: April 30, 2023
Version: b2.0.0
Depends: pyinputplus, stdiomask, Python 3.11

Goals:
1: Fish puns DONE!
2: Cat puns IN PROGRESS!
3: Horse puns IN PROGRESS!
4: Various misc puns (Maybe this can be where we account for feferi's ----------E thingy) IN PROGRESS!
5: Damara Google translate API bullshit NOT STARTED!
6: Homestuck 2 NOT STARTED!
7: Do the thing in the comment directly below vvv LOL NOT STARTED!

# Ultimate baller rev. 3 update: use an swf decompiler to get each individual    #
# image and line of text from it, and then replace the text as normal as below   #
# In addition, use cv2 to get the text from images and, rather than trying to    # 
# figure out how to in-place replace the text, just generate a second file       #
# with a list of all swfs and images that contain the word that needs replacing. #
# An exercise for the mod author!                                                #

More todo ideas:
- Swearing system would be a system similar to fishpuns or catpuns where it would be a dict of words but maybe the vals
would be either a censored version of that word based on severity or just a severiry rating which the user could do with
as they please.

- Latula word replacer "Z" replacer would use a dict of nouns and a very low percent chance of accidentially tossing in
a "z" on the end of a word.

- Sollux and others change their quirk over the story. We can account for this by adding a little bit of code
to each of their sections to check the page number and if it after XYZ page number, use a different quirk.
Sollux: Alive -> Blind -> Half-dead
Caliborn: Callie alive -> Supreme
Aradia: Dead -> Alive
etc.

- Whispering characters could literally be determined with a dict of manually identified pages with whispering on it. 
Personally? No way in hell I'm doing that any time soon.

- All of the text converters or otherwise text-input-taking functions could be made into a standard form, either taking
whole strings of words or just single words.

- Add puns for meulin and nepeta when catpuns exist

- Add cursing to horuss and rufioh when i figure out how to do that

- Also add horsepuns to equius and horuss

"""


class LeveledLogger(Logger):

    def __init__(self, name: str, prefix: str = "", suffix: str = "", is_dated: bool = False, depth_markers: set = (
        "├──",  # Prefix for sub-item for an item
        "└──",  # Prefix for last sub-item for an item
        "│  ",  # Spacer for sub-item and word wrap
    )):
        """Creates a LeveledLogger Object

        Arguments:
            name -- Sets the name of the logger. This is used to identify the logger object later.

        Keyword Arguments:
            prefix -- Prefix to attach to each line (default: {""})
            suffix -- Suffix to attach to each line (default: {""})
            is_dated -- Whether or not to add a timestamp (default: {False})
            depth_markers -- The markers to use for depth (default: {( "├──", # Prefix for sub-item for an item "└──", # Prefix for last sub-item for an item "│  ", # Spacer for sub-item and word wrap )})
        """
        super().__init__(name)
        self.addHandler(hdlr=StreamHandler(STDOUT))
        self._current_depth = 0
        self._depth_markers = depth_markers
        self.prefix, self.suffix, self.is_dated = prefix, suffix, is_dated

    def _format(self, msg: str = "", is_last: bool = False, is_wrapped: bool = False) -> str:
        """Formats a log message with appropriate decorations

        Keyword Arguments:
            msg -- message to add formatting to (default: {""})
            is_last -- Whether or not this is the last item in a subtask (default: {False})
            is_wrapped -- Wether or not this is a wrapped line of text (default: {False})

        Returns:
           The formatted message
        """
        segments = [
            datetime.now().strftime(
                "[%Y-%m-%d %H:%M:%S] ") if self.is_dated else "",
            self.prefix,
            self._depth_markers[2] * (self._current_depth -
                                      1 if self._current_depth > 0 else 0),
            self._depth_markers[1 if is_last else 2 if is_wrapped else 0] if self._current_depth > 0 else "",
            msg,
            self.suffix
        ]
        if is_last:
            self.decrease_depth()
        return "".join(segments)

    def increase_depth(self):
        # Increases depth
        if self._current_depth < 32:
            self._current_depth += 1
        else:
            print("ERROR: Cannot increase depth any further!")

    def decrease_depth(self):
        # Decreases depth. Don't use directly, use the is_last flag instead!
        if 0 < self._current_depth:
            self._current_depth -= 1
        else:
            print("ERROR: Cannot decrease depth any further!")

    def debug(self, msg: str, is_last=False, is_wrapped=False):
        super().debug(msg=self._format(msg, is_last, is_wrapped))

    def info(self, msg: str, is_last=False, is_wrapped=False):
        super().info(msg=self._format(msg, is_last, is_wrapped))

    def warning(self, msg: str, is_last=False, is_wrapped=False):
        super().warning(msg=self._format(msg, is_last, is_wrapped))

    def error(self, msg: str, is_last=False, is_wrapped=False):
        super().error(msg=self._format(msg, is_last, is_wrapped))

    def critical(self, msg: str, is_last=False, is_wrapped=False):
        super().critical(msg=self._format(msg, is_last, is_wrapped))


log = LeveledLogger(name="tuhc_word_replacer", is_dated=True)


class Character():
    # TODO: Assess this class and see if it can be cut down due to new functions / classes added.
    name = ""
    chumhandle = ""
    short_chumhandle = ""
    input_word_quirked = ""
    output_word_quirked = ""
    rules = {}

    def __str__(self):
        """Returns a string representation of the character object.

        Returns:
            "<name>, <chumhandle>, <input_word>, <output_word>, <rules>"
            Example: "Kanaya Maryam GA input Output {. . .}"
        """
        log.debug(msg="Character.__str__ called for " + self.name)
        return self.name + " " + self.chumhandle + " " + self.input_word_quirked \
            + " " + self.output_word_quirked + " " + str(self.rules)

    def set_name(self, name: str):
        """Sets the name for the character. Queries the user if not provided.

        Arguments:
            name -- The name to set it to
        """
        log.debug(msg="Character.set_name called for " + self.name)
        self.name = inputStr(
            "Enter the character's name: ") if not name else name

    def set_chumhandle(self, chumhandle: str):
        """Sets the chumhandle for the character. Queries the user if not provided.

        Arguments:
            chumhandle -- Chumhandle
        """
        log.debug(msg="Character.set_chumhandle called for " + self.name)
        self.chumhandle = inputStr(
            "Enter the character's chumhandle: ") if not chumhandle else chumhandle

    def set_short_chumhandle(self, short_chumhandle: str):
        """Sets the short chumhandle for the character. Queries the user if not provided.

        Arguments:
            short_chumhandle -- The short chumhandle
        """
        log.debug(msg="Character.set_short_chumhandle called for " + self.name)
        self.short_chumhandle = inputStr("Enter the character's chumhandle acronym: ") \
            if not short_chumhandle else short_chumhandle
        # I know this is on a new line but do not be mistaken, this is a single line of code. The if statement is not
        # separated from the rest of the assignment.

    def set_input_word(self, input_word: str):
        """Sets the input word for the character. Queries the user if not provided.

        Arguments:
            input_word -- The input word
        """
        log.debug(msg="Character.set_input_word called for " + self.name)
        input_word = inputStr(
            "Enter the word you want to replace: ") if not input_word else input_word
        self.input_word_quirked = self._generate_quirk_word(self, input_word)

    def set_output_word(self, output_word: str):
        """Sets the output word for the character. Queries the user if not provided.

        Arguments:
            output_word -- The output word
        """
        log.debug(msg="Character.set_output_word called for " + self.name)
        output_word = inputStr(
            "Enter the word you want to replace it with: ") if not output_word else output_word
        self.output_word_quirked = self._generate_quirk_word(self, output_word)

    def set_rules(self, rules: dict):
        """Set the rules for the character

        Arguments:
            rules -- The dictionary of rules
        """
        log.debug(msg="Character.set_rules called for " + self.name)
        self.rules = rules

    def _generate_quirked_word(self, text: str) -> str:
        """This function takes a word and returns a quirked version of it.

        Arguments:
            text -- The word to quirk

        Returns:
            The quirked word
        """
        rules = self.rules.copy()
        if not rules:
            log.debug(msg="Character._generate_quirked_word called for " +
                      self.name + " but no rules were found.")
            return text
        else:
            log.debug(msg="Character._generate_quirked_word called for " +
                      self.name + " with the following rules: ")
            log.increase_depth()
            for rule_index, rule in enumerate(rules.items()):
                is_last = rule_index == len(rules) - 1
                rule_index = str(rule_index)
                rule_name, rule_data = rule

                try:
                    rule_category, rule_subcategory = rule_data["type"].lower(
                    ), rule_data["subtype"].lower()
                except KeyError:
                    rule_category, rule_subcategory = "none", "none"
                match rule_category, rule_subcategory:
                    case "replacement", "regex":
                        log.debug(msg="[" + rule_index + "] Replace any word matching the pattern \"" +
                                  rule_data["pattern"] + "\" with \"" + rule_data["replacement"] + "\".", is_last=is_last)
                        # TODO: Do this later lmao
                    case "replacement", "one-to-one":
                        log.debug(msg="[" + rule_index + "] Replace \"" + rule_data["start"] +
                                  "\" with \"" + rule_data["end"] + "\".", is_last=is_last)
                        text = text.replace(
                            rule_data["start"], rule_data["end"])
                        # Potential TODO, change the syntax from "start" and "end" to "pattern" and "replacement"

                    case "case", "upper":
                        # UPPERCASE
                        log.debug(
                            msg="[" + rule_index + "] SET TEXT TO UPPERCASE.", is_last=is_last)
                        text = text.upper()
                    case "case", "lower":
                        # lowercase
                        log.debug(
                            msg="[" + rule_index + "] set text to lowercase.", is_last=is_last)
                        text = text.lower()
                    case "case", "capitalize":
                        # Capitalized
                        log.debug(
                            msg="[" + rule_index + "] Capitalize Each Word In Text.", is_last=is_last)
                        text = text.capitalize()
                    case "case", "inverse":
                        # iNVERTED
                        log.debug(
                            msg="[" + rule_index + "] sET TEXT TO INVERSE CASE.", is_last=is_last)
                        text = text.swapcase()
                    case "case", "alternating":
                        # aLtErNaTiNg
                        log.debug(
                            msg="[" + rule_index + "] sEt TeXt To AlTeRnAtInG cAsE.", is_last=is_last)
                        text = text.swapcase()
                    case "case", "alternating_words":
                        # alternating WORDS
                        log.debug(
                            msg="[" + rule_index + "] set EVERY other WORD in TEXT to UPPERCASE.", is_last=is_last)
                        pass
                        # TODO: Do this later

                    case "attachments", "prefix":
                        # add a prefix to the text
                        log.debug(msg="[" + rule_index + "] Prefix the text with \"" +
                                  rule_data["prefix"] + "\".", is_last=is_last)
                        text = rule_data["prefix"] + text
                    case "attachments", "suffix":
                        # add a suffix to the text
                        log.debug(msg="[" + rule_index + "] Suffix the text with " +
                                  rule_data["suffix"] + "\".", is_last=is_last)
                        text = text + rule_data["suffix"]
                    case "puns", "substitution":
                        caps = True if text.isupper() else False
                        first = True if (text[0].isupper() if len(
                            text) > 0 else False) else False
                        # caps and first are used to preserve capitalization of the word through punning.
                        # "first" means the first letter of the word ONLY is capitalized.
                        # "caps" means the entire word is capitalized.
                        # TODO: This should use the other rules to determine capitalization, not just the string itself.
                        #   Just in case the speaker is using a different capitalization scheme to the ones I have
                        #   implemented.
                        try:
                            puns = toml.load(
                                join(".", "Characters", "Puns", rule_data["puns"] + ".toml"))
                        except FileNotFoundError:
                            log.error(msg="[" + rule_index + "] ** ERROR in rules: could not find puns file \"" + str(
                                rule_data["puns"]) + ".toml\" **", is_last=is_last)
                            continue
                        if puns:
                            log.debug(msg="[" + rule_index + "] Replace any words found in \"" + str(
                                rule_data["puns"]) + ".toml\" with their replacement.", is_last=is_last)
                            for pun in puns:
                                # For each pun
                                if pun in text:
                                    # If the pun is in the word
                                    if text == pun:
                                        # If the word is the pun EXACTLY
                                        text = text.replace(
                                            pun, rules[rule]["puns"][pun])
                                        if caps:
                                            # If the word was all caps
                                            text = text.upper()
                                        elif first:
                                            # If the word was only the first letter capitalized
                                            text = text[0].upper() + text[1:]
                                        break
                        else:
                            log.warn(msg="[" + rule_index + "] * WARNING in rules: no puns found in puns file \"" + str(
                                rule_data["puns"]) + ".toml\" *", is_last=is_last)
                    case "puns", "cursing":
                        log.debug(msg="[" + rule_index + "] Replace any words found in \"" + str(
                            rule_data["cursing"]) + ".toml\" with their replacement.", is_last=is_last)
                        # TODO: Do this much later
                    case "none", "none":
                        # This could be left blank but I like to be explicit just in case we need it later.
                        log.debug(
                            msg="[" + rule_index + "] Make no changes to the text", is_last=is_last)
                    case _:
                        log.error(msg="[" + rule_index + "] ** Error in " + self.name + "'s rules: Unrecognized category/subcategory combination \"" +
                                  rule_data["type"] + "/" + rule_data["subtype"] + "\" **", is_last=is_last)
            return text

    def __init__(self, data: dict, input_word: str, output_word: str):
        """Creates a new Character object

        Arguments:
            data -- The content from the toml.read operation on a character file
            input_word -- The input word
            output_word -- The output word
        """
        # When creating a new character, you pass it a dict of data, and the words you want to replace.
        # The dict of data will just be the DIRECT output of loading the TOML file.
        # Format for the dict of data can be found in the README.md file
        self.name = data["name"].split(" ")[0].upper()
        log.debug(msg="Character.__init__ called for " + self.name)
        log.increase_depth()
        # The character file format has "name" as "Firstname Lastname", but we only want the first name, in uppercase.
        self.chumhandle = data["handle"]
        # The chumhandle is just the chumhandle in full. Think terminallyCapricious or ectoBiologist.
        self.short_chumhandle = data["handle_short"]
        # The short chumhandle is the shortened version of the chumhandle. Think TC or EB
        data.pop("name")
        data.pop("handle")
        data.pop("handle_short")
        # We don't need these anymore, so we can just remove them from the dict so we don't have to deal with them later
        # TODO: If the format changes at all, more items will need to be removed from the dict.
        self.rules = data
        self.input_word_quirked = self._generate_quirked_word(input_word)
        self.output_word_quirked = self._generate_quirked_word(output_word)
        log.debug(msg="Character.__init__ finished for " +
                  self.name, is_last=True)


class ModFile:
    def __init__(self, file: TextIOWrapper, input_word: str, output_word: str):
        """Creates a ModFile object

        Arguments:
            file -- The writable output file object
            input_word -- The input word
            output_word -- The output word
        """
        self.file = file
        self._lines = []

        # please make that into a list of lines
        self._HEADER = [
            "module.exports = {",
            f"    title: \"Mod where \\\"{input_word}\\\" is replaced with \\\"{output_word}\\\"!\",",
            "    author: \"Amelia P. <a href='https://github.com/fourteevee/tuhc-word-replacer'>GitHub</a>\",",
            "    modVersion: 1.0,",
            "    description: `<h3>File auto-generated by the TUHC word replacer.",
            f"                \"All instances of \\\"{input_word}\\\" replaced with \\\"{output_word}\\\".</h3>`,",
            "    trees: {",
            "        './advimgs/': 'assets://advimgs/',",
            "        './storyfiles/': 'assets://storyfiles/',",
            "        './sweetbroandhellajeff/': 'assets://sweetbroandhellajeff/',",
            "        './archive/comics/': 'assets://archive/comics/'",
            "    },",
            "",
            "    edit(archive) {"
        ]

        self._FOOTER = [
            "    },",
            "}"
        ]

    def write_out(self):
        """Writes the content of the mod file object and closes internal object
        """
        if not self.file.closed:
            for line in [*self._HEADER, *["      " + line for line in self._lines], *self._FOOTER]:
                print(line, file=self.file)
            self.file.close()
        else:
            print("ERROR: File is closed!")

    def add_replacement(self, original: str, replace: str, story: str, page: str, section: str):
        """This code takes an input string, an output string and a page number, and uses that to build a single archive.mspa.story[].content.replace() line.

        Arguments:
            original -- The original content
            replace -- The content to replace it with
            story -- The story ID for the replacement
            page -- The page ID for the replacement
            section -- The section to do the replacement on
        """
        if not self.file.closed:
            # Sometimes the page number doesn't have padded 0's, this converts it into the appropriate format and also makes it
            # into a string.
            self._lines.append(
                f"archive.mspa.{story}['{page}'].{section} = archive.mspa.{story}['{page}'].{section}.replace('{format_output(original)}', '{format_output(replace)}')")
        else:
            print("ERROR: File is closed, cannot add any additional replacements!")


class PesterLog:
    def __init__(self, log_type, content):
        """Creates a new PesterLog Object

        Arguments:
            log_type -- Name of the log "PESTER", "CHAT", etc.
            content -- The json content of the pesterlog-having page
        """
        self.log_type = log_type
        self.dialogue = self._extract_dialogue(content)
        self.original_dialogue = content

    def _extract_dialogue(self, content):
        """Extracts the dialogue from the raw json

        Arguments:
            content -- The raw json file for the page

        Returns:
            The dialog items
        """
        dialog_regex = compile(
            r"(?:(?:<br \/>)(?:(?:<span)(?: (?:style=\\\"(.*?)\\\".([A-Z]*?):(?:(.*?)<\/span>)))))")
        dialog_items = []
        for search_result in findall(dialog_regex, content):
            dialog_items.append({"speaker": search_result.groups()[1], "speech": search_result.groups()[
                                2], "style": search_result.groups()[0], "original_name": search_result.groups()[1]})
        return dialog_items

    def set_line(self, line_number, speaker, speech, style):
        """Sets a particular line in the dialog

        Arguments:
            line_number -- Which line number to change
            speaker -- Set the speaker
            speech -- Set the content of their speech
            style -- Set css styles
        """
        self.dialogue[line_number] = {
            "speaker": speaker, "speech": speech, "style": style}

    def __str__(self):
        return "|" + self.log_type + "LOG| " + "".join(["<br /><span style=\"" + item["style"] + "\">" + item["speaker"] + ":" + item["speech"] + "</span>" for item in self.dialogue])


class Page:
    def __init__(self, story, page, page_content):
        """Create a new page object

        Arguments:
            story -- The story ID for the page
            page -- The page ID for the page
            page_content -- The content of the page
        """
        self.story = story
        self.page = page
        self.title = page_content["title"]
        # self.page_id = page_content["pageId"] | None
        # self.timestamp = page_content["timestamp"] | None
        # self.flag = page_content["flag"] | None
        try:
            self.media = page_content["media"]
        except KeyError:
            self.media = None
        # self.next = page_content["next"] | None
        # self.previous = page_content["previous"] | None
        # self.theme = page_content["theme"] | None
        # self.scratchBanner = page_content["scratchBanner"] | None

        if page_content["content"]:
            self.content = self._parse_content(page_content["content"])
        else:
            self.content = None
            self.content_type = "empty"

    def _parse_content(self, content) -> str | PesterLog:
        """Determine if this is a pesterlog page or not (And create the PesterLog object if so)

        Arguments:
            content -- The page json content

        Returns:
            The page content as a str or as a PesterLog object.
        """
        log_regex = compile(r"\|(.*)LOG\| (.*)")
        log = match(log_regex, content)
        if log:
            self.content_type = "log"
            return PesterLog(log.groups()[0], log.groups()[1])
        else:
            self.content_type = "regular"
            return content

    def __str__(self):
        return f"Page {self.page} of {self.story}: {self.title}"


class StoryFile:
    def __init__(self, file: TextIOWrapper, input_word: str, output_word: str):
        """Create a new StoryFile object

        Arguments:
            file -- The writable text file object
            input_word -- input_word
            output_word -- output_word
        """
        self._raw_file = json.load(file)
        file.close()
        log.debug(msg="StoryFile.__init__ called")
        self.pages = self._derive_pages()
        self.input_word = input_word
        self.output_word = output_word
        log.debug(msg="StoryFile.__init__ finished", is_last=True)

    def _derive_pages(self):
        """Create page objects for file

        Returns:
            A list of page objects
        """
        pages = []
        log.debug(msg="StoryFile._derive_pages called")
        log.increase_depth()
        for story_id, story_content in self._raw_file.items():
            if type(story_content) == dict:
                log.debug("Searching in story \"" + story_id + "\" for pages.")
                log.increase_depth()
                for page_id, page_content in story_content.items():
                    log.debug(msg="Found page: \"" + page_id + "\"")
                    pages.append(Page(story_id, page_id, page_content))
                log.debug(msg="Finished searching in story \"" +
                          story_id + "\" for pages.", is_last=True)
        return pages


def main():
    """Main body of program
    """

    # Parse any command line arguments
    parser = ArgumentParser(description=_DESCRIPTION)
    parser.add_argument(
        "input_word", help="The word you want to replace.", nargs="?")
    parser.add_argument(
        "output_word", help="The word you want to replace it with.", nargs="?")
    parser.add_argument("input_file", help="The input file to read from.",
                        nargs="?", type=FileType("r", encoding="utf-8"))
    parser.add_argument("output_file", help="The output file to write to.",
                        nargs="?", type=FileType("a", encoding="utf-8"))
    parser.add_argument(
        "-v", "--verbose", help="Prints more information to the console.", action="store_true")
    parser.add_argument(
        "-q", "--quiet", help="Prints less information to the console.", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(DEBUG)
    else:
        log.setLevel(INFO)

    log.debug("Parsing command line arguments.")
    log.increase_depth()
    if not args.input_word:
        args.input_word = inputStr(
            "Please enter the word you want to replace: ")
    if not args.output_word:
        args.output_word = inputStr(
            "Please enter the word you want to replace it with: ")
    if not args.input_file:
        args.input_file = open(inputFilepath(
            "Please enter the path to the input file: ", mustExist=True), "r", encoding="utf-8")
    if not args.output_file:
        args.output_file = open(inputFilepath(
            "Please enter the path to the output file: "), "a", encoding="utf-8")
    log.debug("Command line arguments parsed successfully.", is_last=True)

    log.debug(msg="Loading mspa.json file:")
    log.increase_depth()
    mspa_json = StoryFile(args.input_file, args.input_word, args.output_word)
    log.debug(msg="mspa.json file loaded successfully.", is_last=True)

    log.debug(msg="Preparing mod.js file:")
    log.increase_depth()
    mod_js = ModFile(args.output_file, args.input_word, args.output_word)
    log.debug(msg="mod.js file prepared successfully.", is_last=True)

    characters = [file for file in listdir(
        "Characters") if isfile(join("Characters", file))]
    log.debug("Loading characters:")
    log.increase_depth()
    for character_index, character_file in enumerate(characters.copy()):
        # Create a new character object with the TOML from the appropriate character file.
        characters[character_index] = Character(toml.load(
            join("Characters", character_file)), args.input_word, args.output_word)
    log.debug(msg="Characters loaded successfully.", is_last=True)

    log.debug(msg="Beginning replacement process:")
    log.increase_depth()
    for page in mspa_json.pages:
        changes = {"title": (page.title, None),
                   "content": (page.content, None)}

        input_word_variant, output_word_variant = get_variant(
            page.title, args.input_word, args.output_word)
        if input_word_variant and output_word_variant:
            changes["title"] = (page.title, page.title.replace(
                input_word_variant, output_word_variant))
        elif page.title.find(args.input_word.upper()) != -1:
            changes["title"] = (page.title, page.title.replace(
                args.input_word.upper(), args.output_word.upper()))
        if page.content_type == "log":
            changed = False
            for line_number, line in enumerate(page.content.dialogue):
                for character in characters:
                    if (line.speaker != character.name and line.speaker != character.chumhandle and line.speaker != character.short_chumhandle):
                        continue
                    elif (character.name == "N/A" and character.chumhandle == "N/A" and character.short_chumhandle == "N/A"):
                        input_word_variant, output_word_variant = get_variant(
                            line.speech, args.input_word, args.output_word)
                        if input_word_variant and output_word_variant:
                            changed = True
                            page.content.dialog.set_line(line_number, line.speaker, line.speech.replace(
                                input_word_variant, output_word_variant), line.style)
                    else:
                        if character.input_word_quirked:
                            if line.speech.find(character.input_word_quirked) != -1:
                                changed = True
                                page.content.dialog.set_line(line_number, line.speaker, line.speech.replace(
                                    character.input_word_quirked, character.output_word_quirked), line.style)
                        else:
                            input_word_variant, output_word_variant = get_variant(
                                line.speech, args.input_word, args.output_word)
                            if input_word_variant and output_word_variant:
                                changed = True
                                page.content.dialog.set_line(line_number, line.speaker, line.speech.replace(
                                    input_word_variant, output_word_variant), line.style)
                    input_word_variant, output_word_variant = get_variant(
                        line.speech, args.input_word, args.output_word)
                    if input_word_variant and output_word_variant:
                        changed = True
                        page.dialog.set_line(line_number, line.speaker.replace(
                            input_word_variant, output_word_variant), line.speech, line.style)
            if changed:
                changes["content"] = (
                    page.content.original_dialogue, str(page.content.dialogue))
        elif page.content_type == "regular":
            input_word_variant, output_word_variant = get_variant(
                page.content, args.input_word, args.output_word)
            if input_word_variant and output_word_variant:
                changes["content"] = (page.content, page.content.replace(
                    input_word_variant, output_word_variant))
        if changes["title"][1]:
            # original: str, replace: str, story:str, page: str, section: str
            log.debug(msg="Adding replacement for title of page " +
                      page.page + " of story " + page.story + ".")
            mod_js.add_replacement(
                *changes["title"], page.story, page.page, "title")
        if changes["content"][1]:
            log.debug(msg="Adding replacement for content of page " +
                      page.page + " of story " + page.story + ".")
            mod_js.add_replacement(
                *changes["content"], page.story, page.page, "content")
    log.debug(msg="Replacement process finished.", is_last=True)

    log.debug(msg="Writing out mod.js file.")
    log.increase_depth()
    mod_js.write_out()
    log.debug(msg="mod.js file written out successfully.", is_last=True)


def format_output(content: str) -> str:
    """This takes the final compiled string and re-formats it for js.
    I don't know what else to say, that's all there is to it.

    Arguments:
        content -- A string to replace all the improperly formatted js stuff.

    Returns:
        A string with all the js stuff properly formatted.
    """

    return content.replace("\"", "\\\"").replace("\n", "\\\n").replace("\t", "\\t").replace("'", "\\\'")


def get_variant(content: str, input_word: str, output_word: str) -> tuple:
    """This checks if the content contains the input word.

    Arguments:
        content -- The content to search from
        input_word -- The input word to format
        output_word -- The output word to format

    Returns:
        A tuple contianing the input and output words properly varied
    """
    if content.find(input_word) != -1:
        # If the input word is in the content verbatim
        return input_word, output_word
    elif content.find(input_word.upper()) != -1:
        # If the input word is in the content with all caps
        return input_word.upper(), output_word.upper()
    elif content.find(input_word.lower()) != -1:
        # If the input word is in the content with all lowercase
        return input_word.lower(), output_word.lower()
    elif content.find(input_word.capitalize()) != -1:
        # If the input word is in the content with only the first letter capitalized
        return input_word.capitalize(), output_word.capitalize()
    else:
        # If the input word is not in the content
        return None, None


def peixes_capital_e(content: str) -> str:
    """You know that thing where feferi gets -----EXIT-----ED and she does that thing with the ----E to make it look like
    a trident? This does that. This will NOT convert backwards, that is TODO!

    Arguments:
        content -- The content to trident-ify

    Returns:
        The trident-ified content!
    """
    if determine_excitedness(content) >= 0.8:
        # This is a very basic check to see if the string is excited enough to be converted.
        words = content.split(" ")
        caps_words_indexes = []
        for index, word in enumerate(words):
            if word.isUpper():
                caps_words_indexes.append(index)
        for index in caps_words_indexes:
            length = randint(5, 18)  # The length of the trident
            error = randint(0, 100)
            if error <= 70:
                # 70% chance of a capital E being converted into a trident
                words[index] = words[index].replace("E", "-" * length + "E")
    return " ".join(words)


def vriska_vowel_converter(content: str, construct: bool = True) -> str:
    """Converts a string into a Vriska vowel-extended version of itself. Takes a single word as input! TODO: This is some of my least favorite code and definitely needs to be un-spaghettified.

    Arguments:
        content -- A string containing a single word. This is the word to be converted.

    Keyword Arguments:
        construct -- Either makes the word vriska-y or un-vriskifies it. True for vriska-y, False for un-vriskifying. (default: {True})

    Returns:
        The properly formatted string
    """
    if construct:
        # If a word is being converted into a vriska-y version of itself
        error = randint(0, 100)
        # "error" in the sense of "What is the percent chance that the speaker does not make an error".
        vowels = {"a": False, "e": False, "i": False, "o": False, "u": False}
        for letter in content:
            if letter in "aeiou":
                # VOWELS!
                vowels[letter] = index
        for vowel, exists in vowels:
            if exists:
                if error <= 70:
                    # 70% chance of a vowel being converted into a vriska-y version of itself.
                    content = content.replace(vowel, vowel * 8)
                error = randint(0, 100)
        return content

    else:
        # Convert it back into a normal word from a vriska-y word
        repeated_vowels = {}
        for index, letter in enumerate(content):
            if letter in "aeiou":
                if letter * 8 in content:
                    # I don't really know what to say here in particular other than, "Man, I really am glad I am using
                    # python right now!".
                    repeated_vowels[index] = letter
        for index in repeated_vowels:
            content = content.replace(
                repeated_vowels[index] * 8, repeated_vowels[index])
        return content


def determine_excitedness(content: str) -> float:
    """Determine the excitedness of the speaker based on capitalization

    Arguments:
        content -- The content to scan

    Returns:
        A percentage indicating how excited they are
    """
    capitalized_characters = 0
    alphabet_characters = 0

    for character in content:
        # For each character in the string, check if it is alphabetic. If it is, add it to the total character count.
        if character.isalpha():
            # For each of those, if it is uppercase, add it to the uppercase character count.
            if character.isupper():
                capitalized_characters += 1
            alphabet_characters += 1
    # The percentage of uppercase characters is the excitedness of the speaker.
    return round(capitalized_characters / alphabet_characters, 2)


if __name__ == "__main__":
    main()
