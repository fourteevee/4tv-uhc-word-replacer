import json
import string
from os import walk
from os.path import exists, abspath, expanduser, join
from random import randint
from re import search, compile, findall
from tomllib import load as toml_load
from pyinputplus import inputFilepath, inputStr, inputYesNo

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
                                    
Description: This is a program that, when run from the command line, creates a mod in js that can 
be used with TUHC. It replaces any given string with any other string, accounting for typing quirks.
Authors: Amelia Pytosh, yabobay
Date Nov 3rd, 2022
Version: b1.1.1
Depends: pyinputplus, Python 3.11+

Version timeline goals:
1.1.1: Fish puns DONE!
1.1.2: Cat puns IN PROGRESS!
1.1.3: Horse puns IN PROGRESS!
1.1.4: Various misc puns (Maybe this can be where we account for feferi's ----------E thingy) IN PROGRESS!
1.2.0: Damara Google translate API bullshit NOT STARTED!
1.3.0: Homestuck 2 NOT STARTED!
2.0.0: Do the thing in the comment directly below vvv LOL NOT STARTED!

# Ultimate baller rev. 2 update: use an swf decompiler to get each individual    #
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
- Shift away from global variables
- Replace the chumhandles and names dicts, along with all of the text-quirking code and all of the functions for
character-specific text modifications into a huge class that handles all of its stuff through a single object.
- Make all "error" variables into arguments and make their name more clear as to what their function is.

"""
# TODO TODO TODO TODO TODO
DEBUG = False
# Enable to speed up program debugging. End users do not need to use this and should not use this.
# TODO TODO TODO TODO TODO

FUN_MODE = True
# Set to false to disable all easter eggs.
# TODO: Add some various easter eggs, maybe False by default :(?


class Character():
    name = ""
    chumhandle = ""
    short_chumhandle = ""
    input_word_quirked = ""
    output_word_quirked = ""
    rules = {}

    def __str__(self):
        """
        Returns a string representation of the character object.
        :return: "<name>, <chumhandle>, <input_word>, <output_word>, <rules>"
        Example: "Kanaya Maryam GA input Output {. . .}"
        """
        return self.name + " " + self.chumhandle + " " + self.input_word_quirked + " " + self.output_word_quirked + " " + str(
            self.rules)

    def set_name(self, name: str):
        """
        Sets the name for the character. Queries the user if not provided.
        :param name: The name, a string.
        :return: Nothing!
        """
        self.name = inputStr("Enter the character's name: ") if not name else name

    def set_chumhandle(self, chumhandle: str):
        """
        Sets the chumhandle for the character. Queries the user if not provided.
        :param chumhandle: Chumhandle, a string.
        :return: Nothing!
        """
        self.chumhandle = inputStr("Enter the character's chumhandle: ") if not chumhandle else chumhandle

    def set_short_chumhandle(self, short_chumhandle: str):
        """
        Sets the short chumhandle for the character. Queries the user if not provided.
        :param short_chumhandle: The short chumhandle, a string.
        :return: Nothing!
        """
        self.short_chumhandle = inputStr("Enter the character's chumhandle acronym: ") \
            if not short_chumhandle else short_chumhandle
        # I know this is on a new line but do not be mistaken, this is a single line of code. The if statement is not
        # separated from the rest of the assignment.

    def set_input_word(self, input_word: str):
        """
        Sets the input word for the character. Queries the user if not provided.
        :param input_word: The input word, a string.
        :return: Nothing!
        """
        input_word = inputStr("Enter the word you want to replace: ") if not input_word else input_word
        self.input_word_quirked = self._generate_quirk_word(self, input_word)

    def set_output_word(self, output_word: str):
        """
        Sets the output word for the character. Queries the user if not provided.
        :param output_word: The output word, a string.
        :return: Nothing!
        """
        output_word = inputStr("Enter the word you want to replace it with: ") if not output_word else output_word
        self.output_word_quirked = self._generate_quirk_word(self, output_word)

    def set_rules(self, rules: dict):
        """
        Sets the rules for the character.
        :param rules: A dict of rules as per the tomllib read.
        :return: Nothing!
        """
        self.rules = rules

    def _generate_quirked_word(self, word: str) -> str:
        """
        This function takes a word and returns a quirked version of it. The name starts with an underscore because it
        should only be called from within the class. This is not technically enforced, but it is a convention.
        :param word: The word to be quirked.
        :return: The quirked word.
        """
        rules = self.rules
        if rules == {}:
            return word
        else:
            for rule in rules:
                type = ""
                subtype = ""
                for rule_data in rules[rule]:
                    if rule_data == "type":
                        type = rules[rule]["type"].lower()
                    elif rule_data == "subtype":
                        subtype = rules[rule]["subtype"].lower()
                if type == "replacement":
                    if subtype == "regex":
                        pass
                        # TODO: Do this later lmao
                    elif subtype == "one-to-one":
                        word = word.replace(rules[rule]["start"], rules[rule]["end"])
                        # Potential TODO, change the syntax from "start" and "end" to "pattern" and "replacement"
                elif type == "case":
                    if subtype == "upper":
                        # UPPER
                        word = word.upper()
                    elif subtype == "lower":
                        # lower
                        word = word.lower()
                    elif subtype == "capitalize":
                        # Capitalize
                        word = word.capitalize()
                    elif subtype == "inverse":
                        # iNVERSE
                        # TODO: One of these two is wrong VVV
                        word = word.swapcase()
                    elif subtype == "alternating":
                        # aLtErNaTiNg
                        word = word.swapcase()
                    elif subtype == "alternating_words":
                        # alternating WORDS
                        pass
                        # TODO: Also do this one later
                elif type == "attachments":
                    if subtype == "prefix":
                        pass
                        # word = rules[rule]["prefix"] + word
                        # this is broken until I can make it work per-line rather than just for individual words
                    elif subtype == "suffix":
                        # word = word + rules[rule]["suffix"]
                        # same.
                        pass
                elif type == "puns":
                    if subtype == "substitution":
                        caps = True if word.isupper() else False
                        first = True if (word[0].isupper() if len(word) > 0 else False) else False
                        # caps and first are used to preserve capitalization of the word through punning.
                        # "first" means the first letter of the word ONLY is capitalized.
                        # "caps" means the entire word is capitalized.
                        # TODO: This should use the other rules to determine capitalization, not just the string itself.
                        #   Just in case the speaker is using a different capitalization scheme to the ones I have
                        #   implemented.
                        for pun in rules[rule]["puns"]:
                            # For each pun
                            if pun in word:
                                # If the pun is in the word
                                if word == pun:
                                    # If the word is the pun EXACTLY
                                    word = word.replace(pun, rules[rule]["puns"][pun])
                                    if caps:
                                        # If the word was all caps
                                        word = word.upper()
                                    elif first:
                                        # If the word was only the first letter capitalized
                                        word = word[0].upper() + word[1:]
                                    break
                                    # Breaking might be overkill!
                    elif subtype == "cursing":
                        pass
                        # TODO do this much later
                elif type == "none":
                    # This could be left blank but I like to be explicit just in case we need it later.
                    pass
                else:
                    print("ERROR: Rule type not recognized: ", self.name, type, subtype)
            return word

    def __init__(self, data: dict, input_word: str, output_word: str):
        # When creating a new character, you pass it a dict of data, and the words you want to replace.
        # The dict of data will just be the DIRECT output of loading the TOML file.
        # Format for the dict of data can be found in the README.md file TODO: (when I get around to it)
        self.name = data["name"].split(" ")[0].upper()
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


def main():
    """
    This is the main body of the program.
    :return: Nothing :)
    """
    # TODO TODO TODO TODO TODO
    if DEBUG:
        debug_function()
    # TODO TODO TODO TODO TODO

    input_path, output_path = setup_filepaths()

    input_word = "fuck" if DEBUG else inputStr("Please enter the word you want to replace: ")
    output_word = "shit" if DEBUG else inputStr("Please enter the word you want to replace it with: ")

    characters = []
    for path, subdirs, files in walk("Characters"):
        for name in files:
            if len(join(path, name).split("\\")) < 3:
                # At this point you have a file object at join(path, name)
                # that is a character file or is in the appropriate folder
                with open(join(path, name), "rb") as character_file:
                    # Load that file, and parse the toml data it contains.
                    character_data = toml_load(character_file)
                    # Create a new character object with the data we just loaded.
                    characters.append(Character(character_data, input_word, output_word))
    write_boilerplate(input_word, output_word, output_path, "header")

    for character in characters:
        # For each character, search for instances of the input word in the input file, then, if found, replace it with
        # the output word and write it to the output file.
        search_and_replace(input_path, output_path, character.input_word_quirked, character.output_word_quirked,
                           character.name, character.short_chumhandle)

    write_boilerplate(input_word, output_word, output_path, "footer")


def search_and_replace(input_path: str, output_path: str, input_quirked: str, output_quirked: str,
                       character_name: str, character_chumhandle: str):
    """
    This function searches for the input word in the input file and replaces it with the output word.
    This takes into account the quirks of the character. It makes a number of calls to other functions.
    :param input_path: The path to the input file.
    :param output_path: The path to the output file.
    :param input_quirked: The input word, with the quirks of the character applied.
    :param output_quirked: The output word, with the quirks of the character applied.
    :param character_name: The name of the character, formatted as "FIRSTNAME" taking only the first word of the name
        and capitalizing it.
    :param character_chumhandle: The chumhandle of the character, formatted as "CH". Two letters, capitalized.

    Either character_name or character_chumhandle can be "N/A" if the character does not have one of those.
    Just make sure that you know that if this is done, no rules will be applied to that character. There is no
    need to create a character file for a character that does not use quirks.
    :return: Nothing! :)
    """
    last_page_number = 000000
    with open(input_path, "r", encoding="utf-8") as open_file:
        # And here it begins, we start by reading the mspa.json file and parsing its contents.
        file_contents = open_file.read()
        # Taking the file and reading its contents as a single huge block
        json_contents = json.loads(file_contents)
        # Converting that block into a json formatted mega-structure. I will try and explain how this is structured
        # later, but it is honestly very confusing and often inconsistent. I think I have covered all my bases, but that
        # is what user testing is for, right?
        for story in json_contents:
            # "story" objects I *think* refers to the literal stories present on MSPA, be that JB, HS, whatever.
            # There are only a few of these, and they contain an absolutely unreal amount of "object_ids".
            for object_id in json_contents[story]:
                # I *would have* named this "page" but it seems to include some stuff that isn't a page. The key is a
                # page number, and the value is *usually* a dict full of shit, although there are a few lists for some
                # reason? TODO: look into that

                if type(json_contents[story]) == list:
                    pass

                elif type(json_contents[story]) == dict:
                    for item in json_contents[story][object_id]:
                        # An item is part of the dictionary value of an object, not every object has every value but
                        # all of them have titles, pageIds and content.
                        match item:
                            # All of these different items are extant for each page of the comic. We don't need
                            # most of them, but they're here just in case I wanted to do something with them in the
                            # future or if someone wanted to fork this program.
                            case "title":
                                # This is the title of the page, the text that appears at the top. This /can/ be
                                # different than the "next" text from the previous page, but it usually isn't.
                                pass

                            case "pageId":
                                # This is the page number of the page, in MSPA format.
                                if search(r"^\d\d\d\d\d\d$", json_contents[story][object_id][item]):
                                    # We make sure that, first, the page number is actually properly formatted
                                    # there are a few instances where it isn't a 6-digit number and those are indeed
                                    # ignored in this program, but it covers like 99.999% of all pages.
                                    if last_page_number != int(json_contents[story][object_id][item]):
                                        # Second, we make sure that the page number we are reading is not the same
                                        # page number as the last item we were working on. Now that I think about it,
                                        # I don't think this statement matters because if I didn't check it would just
                                        # be overwriting the same value, but whatever, it's here.
                                        last_page_number = int(json_contents[story][object_id][item])

                                else:
                                    last_page_number = 0
                            case "timestamp":
                                # This indicates the time in which the page was posted.
                                pass

                            case "flag":
                                # I have no idea what this is.
                                pass

                            case "media":
                                # This contains the link to the image/swf/mp4/whatever that exists on the page.
                                # Fun fact, this is the reason that every page of Homestuck is limited to a single
                                # piece of media. There are ways around this, but it is very, VERY hack-y
                                pass

                            case "content":
                                # Here's the good stuff, the page content, which is usually words exclusively.
                                for line_unstripped in json_contents[story][object_id][item].split("<br />"):
                                    line = format_input(strip_html(line_unstripped))
                                    # Go ahead and read the format_input() and strip_html() functions below to
                                    # figure out what this does, but in short words it basically converts the raw
                                    # line of text split from an entire page's content and cleans all the extra
                                    # formatting off of it, rendering it much easier to modify.

                                    # figure out the chum handle of the person speaking in this line
                                    try:
                                        detected_name = line[0:line.index(':')]
                                    except ValueError:
                                        # If there is no colon in the line, then it is not a line of dialogue or
                                        # we just can't identify who is speaking. In either case, we set it to length
                                        # 15 and call it a day. (15 is greater length than any name or handle)
                                        detected_name = line[0:15]
                                        # TODO: Note for the future. If the horizons widen on this project, we will
                                        #   want to make sure that we set it to length 0 instead of 15 just in case.
                                        #   Setting it to 15 just makes it easier to debug right now and causes no
                                        #   issues with default homestuck.
                                    # if the chum handle matches a character with some sort of typing quirk
                                    if "".join(detected_name) in [character_chumhandle, "P" + character_chumhandle,
                                                                  "C" + character_chumhandle,
                                                                  "F" + character_chumhandle] \
                                            and character_chumhandle != "N/A":
                                        # We also make sure to check for "P", "C", and "F" because those are prefixes
                                        # applied when a character is talking in a different period of time from the
                                        # current "focused character". "C" is for "current", "P" is for "past", and "F"
                                        # is for "future".
                                        srch = compile(r"[^" + string.ascii_letters + r"1234567890]+" +
                                                       input_quirked.replace("(", "\(").replace(")", "\)") +
                                                       r"[^" + string.ascii_letters + r"1234567890]+")
                                        # This compiles a regex for the input text. It breaks down as such:
                                        # [^ - Negated set, meaning "match any character not in this list"
                                        #   abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 - The list.
                                        # ]+ - "+" identifies "1 or more" meaning "make sure there is at least one"
                                        # input_quirked[key] - This is the input word, converted into whatever
                                        #                      character's quirk that we are currently working on.
                                        # [^ - Same as the first one.
                                        #   abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890
                                        # ]+
                                        # All of this comes together to produce a regex that specifically looks for
                                        # the exact word that the user inputs. This helps avoid mis-identifications for
                                        # words that happen to be in other words. i.e. "playtest" has "test" in it.
                                        # It does this by making sure there is a non-alphanumeric character before and
                                        # after the word in question, be that a space, a "start-of-text" character, or
                                        # whatever else.
                                        if search(srch, line):
                                            # Now we search the line using the regex.
                                            extras = search(srch, line).group().split(input_quirked) \
                                                if input_quirked else ["", ""]
                                            # "extras" are the extra bits on the ends of identifications, be that
                                            # spaces, commas, whatever. This allows us to re-add them in after doing the
                                            # replacement.
                                            write_to_mod(line, line.replace(extras[0] + input_quirked + extras[1],
                                                                            extras[0] + output_quirked +
                                                                            extras[1]), last_page_number, output_path)
                                            # write_to_mod() writes the appropriate line of text to the mod file to
                                            # replace one word with another. You can see that we add the extras back on.

                                    elif "".join(detected_name) == character_name and character_name != "N/A":
                                        # This is important for finding the chars who do not have a chumhandle, but only
                                        # a name. Otherwise it is just a duplicate of the above code.
                                        for length in [6, 8, 12, 13]:
                                            if line[0:length] == character_name:
                                                srch = compile(r"[^" + string.ascii_letters + r"1234567890]+"
                                                               + input_quirked.replace("(", "\(").replace(")", "\)") +
                                                               r"[^" + string.ascii_letters + r"1234567890]+")
                                                if search(srch, line):
                                                    extras = search(srch, line).group().split(input_quirked) \
                                                        if input_quirked else ["", ""]
                                                    write_to_mod(line, line.replace(extras[0] + input_quirked +
                                                                                    extras[1], extras[0] +
                                                                                    output_quirked + extras[1]),
                                                                 last_page_number, output_path)
                                    elif character_name == "N/A" and character_chumhandle == "N/A":
                                        # And finally, everyone else. because there are no other typing quirks present
                                        # in other characters (besides roxy when s/he is drunk, I guess? Good luck
                                        # sorting that out lol), we can just pass it all to "other" which just replaces
                                        # the text without doing any substitutions.
                                        srch = compile(r"[^" + string.ascii_letters + r"1234567890]+" +
                                                       input_quirked.replace("(", "\(").replace(")", "\)") +
                                                       r"[^" + string.ascii_letters + r"1234567890]+")

                                        if search(srch, line):
                                            extras = search(srch, line).group()\
                                                .split(input_quirked) if input_quirked else ["", ""]
                                            write_to_mod(line, line.replace(extras[0] + input_quirked + extras[1],
                                                                            extras[0] + output_quirked + extras[1]),
                                                         last_page_number, output_path)
                            case "next":
                                # This indicates the title of the next page, i.e. the link at the bottom of the page.
                                pass

                            case "previous":
                                # This indicates the title of the previous page. i.e. the link at the very bottom of the
                                # page.
                                pass

                            case "theme":
                                # This indicates the page theme. Like homosuck, trickster mode, etc.
                                pass

                            case "scratchBanner":
                                # I have no idea what this is.
                                pass


def format_input(content: str) -> str:
    """
    This takes the raw escaped shit from the mspa.json and makes it actually not shit.
    I don't know what else to say, that's all there is to it.
    :param content: A string to remove all the html escaped shit from.
    :return: A string with all the html escaped shit removed from it.
    """

    return content.replace("\\\"", "\"").replace("\\n", "\n") \
        .replace("\\t", "\t").replace("\\\\", "\\").replace("</ br>", "</br>") \
        .replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", "\"").replace("&amp;", "&")


def format_output(content: str) -> str:
    """
    This takes the final compiled string and re-formats it for js.
    I don't know what else to say, that's all there is to it.
    :param content: A string to replace all the improperly formatted js stuff.
    :return: A string with all the js stuff properly formatted.
    """

    return content.replace("\"", "\\\"").replace("\n", "\\\n").replace("\t", "\\t").replace("'", "\\\'")


def strip_html(content: str) -> str:
    """
    This takes in a string and returns it with all html tags removed.
    :param content: A string to remove all html tags from
    :return: A string without html tags
    """
    clean = compile(r"<[^<>]+>")
    for occurrence in findall(clean, content):
        # this accounts for multiple html tags in one string, which is basically a certainty.
        content = content.replace(occurrence, "")
    return content


def peixes_capital_e(content: str) -> str:
    """
    You know that thing where feferi gets -----EXIT-----ED and she does that thing with the ----E to make it look like
    a trident? This does that. This will NOT convert backwards, that is TODO!
    :param content: The string to be converted. Can be multiple words
    :return: The converted string.
    """
    if determine_excitedness(content) >= 0.8:
        # This is a very basic check to see if the string is excited enough to be converted.
        words = text.split(" ")
        caps_words_indexes = []
        for index, word in enumerate(words):
            if word.isUpper():
                caps_words_indexes.append(index)
        for index in caps_words_indexes:
            length = randint(5, 18)  # These numbers are arbitrary, and may be changed in future versions!
            error = randint(0, 100)
            if error <= 70:
                # 70% chance of a capital E being converted into a trident
                words[index] = words[index].replace("E", "-" * length + "E")
    return " ".join(words)


def vriska_vowel_converter(content: str, construct: bool = True) -> str:
    """
    Converts a string into a Vriska vowel-extended version of itself. Takes a single word as input!
    :param content: A string containing a single word. This is the word to be converted.
    :param construct: Either makes the word vriska-y or un-vriskifies it. True for vriska-y, False for un-vriskifying.
    :return: The converted string.
    """
    if construct:
        # If a word is being converted into a vriska-y version of itself
        error = randint(0, 100)
        # "error" in the sense of "What is the percent chance that the speaker does not make an error".
        vowels = {}
        # This is a dictionary of all the vowels in the word, and their indexes.

        for index, letter in enumerate(content):
            if letter in "aeiou":
                # VOWELS!
                vowels[index] = letter
        match len(vowels):
            # Match how many vowels there are in the word
            case 0:
                # Do nothing
                return content
            case 1:
                # If there is only one, we can do a much faster version of this process
                if error <= 50:
                    for letter in content:
                        if letter in "aeiou":
                            return content.replace(letter, letter * 8)
            case _:
                # If there is more than one, spin up the process to convert all of them
                # TODO: This breaks because when the vowels get extended they change the indexes of the other vowels
                easter_egg = 0
                while error <= 50 and len(vowels) > 1:
                    easter_egg += 1 if FUN_MODE else 0
                    selection = choice(list(vowels.keys()))
                    content = content.replace(vowels[selection], vowels[selection] * 8)
                    del vowels[selection]
                    error = randint(0, 100)
                if easter_egg > 3:
                    # TODO: Add easter egg
                    # AMELIA: Wow, that's a lot of vowels!
                    pass
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
            content = content.replace(repeated_vowels[index] * 8, repeated_vowels[index])
        return content


def determine_excitedness(content: str) -> float:
    """Determines how excited the speaker is.

    :param content: The string to be converted.
    :return: The converted string.
    """
    caps = 0
    characters = 0
    all = 0

    for letter in content:
        # For each character in the string, check if it is alphanumeric. If it is, add it to the total character count.
        if letter.isalpha():
            # For each of those, if it is uppercase, add it to the uppercase character count.
            if letter.isupper():
                caps += 1
            characters += 1
        all += 1
    # The percentage of uppercase characters is the excitedness of the speaker.
    return round(caps / characters, 2)


def write_to_mod(original: str, replace: str, page: int, output_path: str):
    """
    This code takes an input string, an output string and a page number, and uses that to build a single
    archive.mspa.story[].content.replace() line.
    :param original: The original text from the comic that is the target for replacement
    :param replace: The text to replace original with.
    :param page: The page number that this content is located on
    :return: Nothing :)
    """
    page = "0" * (6 - len(str(page))) + str(page)
    # Sometimes the page number doesn't have padded 0's, this converts it into the appropriate format and also makes it
    # into a string.
    original = format_output(original)
    replace = format_output(replace)

    with open(output_path, 'a', encoding="utf-8") as open_file:
        open_file.write("      archive.mspa.story['" + str(page) + "'].content = archive.mspa.story['" + str(page) +
                        "'].content.replace('" + original + "', '" + replace + "')\n")


def setup_filepaths() -> tuple:
    """
    This function sets up the filepaths for the input and output files.
    :return: A tuple containing the input and output filepaths.
    """
    valid = True if DEBUG else False
    input_path = "mspa.json" if DEBUG else ""
    output_path = "mod.js" if DEBUG else ""
    # If the program is in debug mode, it will use the default filepaths. Otherwise, it will ask the user for them.
    # If you wish to use this program in debug mode, make sure to put the input file in the same directory as the
    # program and create an empty file called "mod.js" in the same directory.
    while not valid:
        input_path = inputFilepath("Please enter the filepath for your mspa.json file "
                                   "(Located in Asset Pack/archive/data/mspa.json: ")
        input_path = abspath(expanduser(input_path))
        # This converts the input filepath into an absolute path, which is necessary for the program to work.
        if exists(input_path):
            valid = True
        else:
            print("File doesn't exist!")

    valid = True if DEBUG else False
    while not valid:
        output_path = inputFilepath("Please enter the filepath for your finished mod: ")
        output_path = abspath(expanduser(output_path))
        if exists(output_path):
            if inputYesNo(output_path + " exists, overwrite? ") != "no":
                valid = True
            else:
                valid = False
        else:
            valid = True
    return input_path, output_path


def write_boilerplate(input_word: str, output_word: str, output_path: str, position: str):
    """
    Writes the boilerplate code to the output file.
    :param output_path: The path to the output file.
    :return: Nothing :)
    """
    if position == "header":
        with open(output_path, "w", encoding="utf-8") as open_file:
            # Here we quickly write all the boilerplate code that lives at the top of any mod. Once the mod has been
            # generated, the author is able to edit whatever they want. Credit would be preferred, but I'm not your mom.
            # Go wild.
            boilerplate = ""
            boilerplate += "module.exports = {\n"
            boilerplate += "    title: \"Mod where \\\"" + input_word + \
                           "\\\" is replaced with \\\"" + output_word + "\\\"!\",\n"
            boilerplate += "    author: \"Amelia P. " \
                           "(<a href='https://github.com/fourteevee/tuhc-word-replacer'>GitHub</a>\",\n"
            boilerplate += "    modVersion: 1.0,\n"
            boilerplate += "    description: `<h3>File auto-generated by the TUHC word replacer. All instances of \\\"" \
                           + input_word + "\\\" replaced with \\\"" + output_word + "\\\".</h3>`,\n"
            boilerplate += "    trees: {\n"
            boilerplate += "        './advimgs/': 'assets://advimgs/',\n"
            boilerplate += "        './storyfiles/': 'assets://storyfiles/',\n"
            boilerplate += "        './sweetbroandhellajeff/': 'assets://sweetbroandhellajeff/',\n"
            boilerplate += "        './archive/comics/': 'assets://archive/comics/'\n"
            boilerplate += "    },\n"
            boilerplate += "\n"
            boilerplate += "    edit(archive {\n"
            open_file.write(boilerplate)
    elif position == "footer":
        with open(output_path, "a") as open_file:
            open_file.write("    },\n")
            open_file.write("}")
        # Finally, we write the boilerplate footer code and call it a day!


def debug_function():
    """
    This function is only called if the program is in debug mode. It is used to test the program without having to
    fuck around with running the entire program which can take a number of minutes depending on how slow your computer
    is.
    """
    pass
    # exit(0)


if __name__ == "__main__":
    main()
