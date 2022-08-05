from os.path import exists, abspath, expanduser
from pyinputplus import inputFilepath, inputStr, inputYesNo
from re import search, compile, findall
import json
import string

"""
Title: Word replacer for the Unofficial Homestuck Collection.
Description: This is a program that, when run from the command line, creates a mod in js that can be used with TUHC. It
replaces any given string with any other string, accounting for typing quirks.
Author: Amelia Pytosh
Date July 24th, 2022
Version: b1
Depends: pyinputplus
"""

# Ultimate baller rev. 2 (or b2?) update: use an swf decompiler to get each individual
# image and line of text from it, and then replace the text as normal as below
# In addition, use cv2 to get the text from images and, rather than trying to
# figure out how to in-place replace the text, just generate a second file
# with a list of all swfs and images that contain the word that needs replacing.
# An exercise for the mod author!

output_valid = False
input_path = inputFilepath("Please enter the filepath for your mspa.json file "
                           "(Located in Asset Pack/archive/data/mspa.json: ")
input_path = abspath(expanduser(input_path))

while not output_valid:
    output_path = inputFilepath("Please enter the filepath for your finished mod: ")
    output_path = abspath(expanduser(output_path))
    if exists(output_path):
        if inputYesNo(output_path + " exists, overwrite? ") != "no":
            output_valid = True
    else:
        output_valid = True

input_word = inputStr("Please enter the word you want to replace: ")
output_word = inputStr("Please enter the word you want to replace it with: ")


def main() -> None:
    """
    This is the main body of the program, and it does most of the work. Yes, I know, "don't write everything in main!"
    Well, it's my program and I'll do what I want.
    :return: Nothing :)
    """
    last_page_number = 0
    # This keeps track of the last page number that was being worked on, it comes up later down the line.
    input_quirked = generate_quirks(input_word, True)
    # You can go down to generate_quirks to see what this does, but it basically generates a list of all variations of
    # the user's input word in order to replace it in the comic.
    output_quirked = generate_quirks(output_word, False)
    # Ditto, but the opposite.
    chum_handles = {"AA:": "aradia", "AT:": "tavros", "TA:": "sollux", "CG:": "karkat",
                    "AC:": "nepeta", "GA:": "kanaya", "GC:": "terezi", "AG:": "vriska",
                    "CT:": "equius", "TC:": "gamzee", "CA:": "eridan", "CC:": "feferi",
                    "UU:": "calliope", "uu": "caliborn"}
    # This is a list of conversions from chum handles to character names, which are all in lowercase to match the rest
    # of the program's keys. Colons are included to make searches easier, because "CA" at the start of a line could
    # easily be "CALIBORN", for instance.
    names = {"ARADIA:": "aradia", "TAVROS:": "tavros", "SOLLUX:": "sollux",
             "KARKAT:": "karkat", "NEPETA:": "nepeta", "KANAYA:": "kanaya",
             "TEREZI:": "terezi", "VRISKA:": "vriska", "EQUIUS:": "equius",
             "GAMZEE:": "gamzee", "ERIDAN:": "eridan", "FEFERI:": "feferi",
             "DAMARA:": "damara", "RUFIOH:": "rufioh", "MITUNA:": "mituna",
             "KANKRI:": "kankri", "MEULIN:": "meulin", "PORRIM:": "porrim",
             "LATULA:": "latula", "ARANEA:": "aranea", "HORUSS:": "horuss",
             "KURLOZ:": "kurloz", "CRONUS:": "cronus", "MEENAH:": "meenah",
             "CALLIOPE:": "calliope", "CALIBORN:": "caliborn",
             "ERISOLSPRITE:": "erisolsprite", "ARQUIUSPRITE:": "arquiusprite",
             "DAVEPETASPRITE:": "davepetasprite"}
    # Same goes here, but for character names in all-caps format that is present near the later parts of the comic.

    with open(output_path, "w") as open_file:
        # Here we quickly write all the boilerplate code that lives at the top of any mod. Once the mod has been
        # generated, the author is able to edit whatever they want. Credit would be preferred, but I'm not your mom.
        # Go wild.
        boilerplate = ""
        boilerplate += "module.exports = {\n"
        boilerplate += "    title: \"Mod where \\\"" + input_word + \
                       "\\\" is replaced with \\\"" + output_word + "\\\"!\",\n"
        boilerplate += "    author: \"Amelia P. " \
                       "(<a href='https://github.com/fourteevee/tuhc-word-replacer'>GitHub</a>\",\n"
        boilerplate += "    modVersion: 2.0,\n"
        boilerplate += "    description: `<h3>File auto-generated by the TUHC word replacer. All instances of \\\"" \
                        + input_word + "\\\" replaced with \\\"" + output_word + "\\\".</h3>`,\n"
        boilerplate += "    trees: {\n"
        boilerplate += "        './advimgs/': 'assets://advimgs/',\n"
        boilerplate += "        './storyfiles/': 'assets://storyfiles/',\n"
        boilerplate += "        './sweetbroandhellajeff/': 'assets://sweetbroandhellajeff/',\n"
        boilerplate += "        './archive/comics/': 'assets://archive/comics/'\n"
        boilerplate += "    },\n"
        boilerplate += "\n"
        boilerplate += "    edit(achive {\n"
        open_file.write(boilerplate)

    with open(input_path, "r") as open_file:
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
                                    if "".join(line[0:3]) in chum_handles.keys():
                                        # This determines if the first 3 characters of the line of text match
                                        # a chum handle that matches a character with some sort of typing quirk.
                                        key = chum_handles["".join(line[0:3])]
                                        # this converts that chum handle into a lowercase character name
                                        srch = compile(r"[^" + string.ascii_letters + r"1234567890]+"
                                                       + input_quirked[key] + r"[^" +
                                                       string.ascii_letters + r"1234567890]+")
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
                                            extras = search(srch, line).group().split(input_quirked[key])
                                            # "extras" are the extra bits on the ends of identifications, be that
                                            # spaces, commas, whatever. This allows us to re-add them in after doing the
                                            # replacement.
                                            write_to_mod(line, line.replace(extras[0] + input_quirked[key] + extras[1],
                                                                            extras[0] + output_quirked[key] + extras[
                                                                                1]),
                                                         last_page_number)
                                            # write_to_mod() writes the appropriate line of text to the mod file to
                                            # replace one word with another. You can see that we add the extras back on.

                                    elif "".join(line[0:7]) in names.keys():
                                        # This does the same thing as above, but for troll names. 6 letters.
                                        key = names["".join(line[0:7])]
                                        srch = compile(r"[^" + string.ascii_letters + r"1234567890]+"
                                                       + input_quirked[key] + r"[^" +
                                                       string.ascii_letters + r"1234567890]+")

                                        if search(srch, line):
                                            extras = search(srch, line).group().split(input_quirked[key])
                                            write_to_mod(line, line.replace(extras[0] + input_quirked[key] + extras[1],
                                                                            extras[0] + output_quirked[key] + extras[
                                                                                1]),
                                                         last_page_number)

                                    elif "".join(line[0:9]) in names.keys():
                                        # This does the same as above, but for caliborn and calliope.
                                        key = names["".join(line[0:9])]
                                        srch = compile(r"[^" + string.ascii_letters + r"1234567890]+"
                                                       + input_quirked[key] + r"[^" +
                                                       string.ascii_letters + r"1234567890]+")

                                        if search(srch, line):
                                            extras = search(srch, line).group().split(input_quirked[key])
                                            write_to_mod(line, line.replace(extras[0] + input_quirked[key] + extras[1],
                                                                            extras[0] + output_quirked[key] + extras[
                                                                                1]),
                                                         last_page_number)

                                    elif "".join(line[0:13]) in names.keys():
                                        # This does the same as above, but for arquiusprite and erisolsprite
                                        key = names["".join(line[0:13])]
                                        srch = compile(r"[^" + string.ascii_letters + r"1234567890]+"
                                                       + input_quirked[key] + r"[^" +
                                                       string.ascii_letters + r"1234567890]+")

                                        if search(srch, line):
                                            extras = search(srch, line).group().split(input_quirked[key])
                                            write_to_mod(line, line.replace(extras[0] + input_quirked[key] + extras[1],
                                                                            extras[0] + output_quirked[key] + extras[
                                                                                1]),
                                                         last_page_number)

                                    elif "".join(line[0:15]) in names.keys():
                                        # And finally, this does the same thing as above but specifically for
                                        # davepetasprite. I am sure there is a better way to do all of this and make it
                                        # much more condensed, but I just need a break from writing code for a bit
                                        # before I try to tackle that.
                                        key = names["".join(line[0:15])]
                                        srch = compile(r"[^" + string.ascii_letters + r"1234567890]+"
                                                       + input_quirked[key] + r"[^" +
                                                       string.ascii_letters + r"1234567890]+")

                                        if search(srch, line):
                                            extras = search(srch, line).group().split(input_quirked[key])
                                            write_to_mod(line, line.replace(extras[0] + input_quirked[key] + extras[1],
                                                                            extras[0] + output_quirked[key] + extras[
                                                                                1]),
                                                         last_page_number)
                                    else:
                                        # And finally, everyone else. because there are no other typing quirks present
                                        # in other characters (besides roxy when she is drunk, I guess? Good luck
                                        # sorting that out lol), we can just pass it all to "other" which just replaces
                                        # the text without doing any substitutions.
                                        key = "other"
                                        srch = compile(r"[^" + string.ascii_letters + r"1234567890]+"
                                                       + input_quirked[key] + r"[^" +
                                                       string.ascii_letters + r"1234567890]+")

                                        if search(srch, line):
                                            extras = search(srch, line).group().split(input_quirked[key])
                                            write_to_mod(line,
                                                         line.replace(extras[0] + input_quirked[key] + extras[1],
                                                                      extras[0] + output_quirked[key] + extras[1]),
                                                         last_page_number)
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

    with open(output_path, "a") as open_file:
        open_file.write("    },\n")
        open_file.write("}")
    # Finally, we write the boilerplate footer code and call it a day!


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


def generate_quirks(content: str, is_input: bool) -> dict:
    """
    This is easily going to be the longest function in the program, I am already sure of that.
    Unfortunately, I am also going to avoid commenting all over the place down there, so I'll
    give you the rundown up here instead.

    First, we create a dictionary of all the characters who have quirks (and a single item for everyone else).
    Then, we go through that dictionary and set the value for each key to be the appropriately quirked version of
    "content" by using string.replace()'s for each character in the text that might need quirking.

    Finally, once all that is done, we return the dictionary.

    Unfortunately there is much work to be done with this. I have the basics down but there are many a todo
    below this, indicating things I still need to work on.

    :param content: The string to produce quirked versions of.
    :param is_input: A boolean that helps hint that the content that is being passed to this function is intended to be
    input text, rather than the output text. This currently is only used by gamzee and honestly I forget why it is, but
    there you go.
    :return: Returns a dictionary wherein keys are character names in lowercase and values are the quirked version of
    "content" for each character.
    """
    quirks = {"aradia": "", "tavros": "", "sollux": "", "karkat": "", "nepeta": "", "kanaya": "",
              "terezi": "", "vriska": "", "equius": "", "gamzee": "", "eridan": "", "feferi": "",
              "damara": "", "rufioh": "", "mituna": "", "kankri": "", "meulin": "", "porrim": "",
              "latula": "", "aranea": "", "horuss": "", "kurloz": "", "cronus": "", "meenah": "",
              "calliope": "", "caliborn": "", "erisolsprite": "", "arquiusprite": "", "davepetasprite": "",
              "other": ""}
    for character in quirks.keys():
        match character:
            case "aradia":
                quirks[character] = content.replace("o", "0").replace("O", "0")
                # TODO: Account for alive version

            case "tavros":
                tavros = content.split(", ")
                for split in range(len(tavros)):
                    # First letter of each sentence (or after each comma) is un-capped, otherwise, all caps!
                    if len(tavros[split]) > 0:
                        tavros[split] = tavros[split][0] + tavros[split][1:].upper()
                    else:
                        tavros[split] = ""
                quirks[character] = ", ".join(tavros)
                # TODO: Account for whispering

            case "sollux":
                # Man, this guy loves to use those silly puns of his.
                quirks[character] = content.replace("s", "2").replace("i", "ii").replace("I", "II") \
                    .replace("to", "two").replace("too", "two").replace("To", "Two").replace("Too", "Two") \
                    .replace("tonight", "twoniight").replace("together", "twogether").replace("Together", "Twogether") \
                    .replace("Tonight", "Twoniight")
                # TODO: Account for blind and half-dead

            case "karkat":
                # Yeah this one is easy.
                quirks[character] = content.upper()
                # TODO: Account for whispering

            case "nepeta":
                quirks[character] = content.replace("ee", "33").replace("EE", "33")
                # TODO: Account for cat puns? unlikely.

            case "kanaya":
                kanaya = content.split(" ")
                for word in range(len(kanaya)):
                    # First letter of each word is in caps, otherwise ignore punctuation and caps.
                    if len(kanaya[word]) > 0:
                        kanaya[word] = kanaya[word][0].upper() + kanaya[word][1:]
                    else:
                        kanaya[word] = ""
                quirks[character] = " ".join(kanaya)
                # TODO: This might not catch everything. Check for results later.

            case "terezi":
                quirks[character] = content.upper().replace("A", "4").replace("I", "1").replace("E", "3")
                # TODO: Account for whispering

            case "vriska":
                quirks[character] = content.replace("b", "8").replace("B", "8").replace("ait", "8") \
                    .replace("AIT", "8").replace("ate", "8").replace("ATE", "8")
                # TODO: Account for when she says something with 8 repeated letters. i.e. "joooooooohn" should become
                # TODO: "juuuuuuuune" to reference the original function of this program
                # TODO: sometimes she gets excited and deviates from her formula and replaces random vowels with "8"
                # TODO: i.e "break" becoming "8r8k"

            case "equius":
                quirks[character] = content.replace("x", "%").replace("X", "%").replace("loo", "100") \
                    .replace("ool", "001").replace("LOO", "100").replace("OOL", "001").replace("cross", "%")

            case "gamzee":
                enraged = False
                # Okay this is a big one so I'll write a bit extra here.
                if is_input:
                    if enraged:
                        # When gamzee is enraged, he TYPES like THIS, with every other word full caps and otherwise no
                        # caps.
                        gamzee = content.split()
                        # This was actually originally intended to be the code for his normal speaking,
                        # but I fucked it up so that it did it for words instead of characters, which just so happened
                        # to work for his enraged version anyway.
                        for letter in range(len(gamzee)):
                            if letter % 2 == 0:
                                gamzee[letter] = gamzee[letter].lower()
                            else:
                                gamzee[letter] = gamzee[letter].upper()
                        quirks[character] = "".join(gamzee)
                    else:
                        gamzee = [char for char in content]
                        # I have no idea what "char for char in content" means, but it works. Thanks stackoverflow :)
                        spaces = 0
                        for letter in range(len(gamzee)):
                            if gamzee[letter] not in list(string.ascii_letters):
                                # We are flipping each letter, so if we encounter a space, then don't change
                                # capitalization.
                                spaces += 1
                            else:
                                if (letter - spaces) % 2 == 0:
                                    gamzee[letter] = gamzee[letter].lower()
                                elif (letter - spaces) % 2 == 1:
                                    gamzee[letter] = gamzee[letter].upper()
                        quirks[character] = "".join(gamzee)
                # TODO: Determine if we actually need to do anything different for output text. This may just work.

            case "eridan":
                quirks[character] = content.replace("w", "ww").replace("v", "vv").replace("W", "Ww").replace("V", "Vv")

            case "feferi":
                quirks[character] = content.replace("E", "-E").replace("H", ")(").replace("h", ")(")
                # TODO: Account for excitement where she does -----------E instead of -E
                #   Fish puns? also not happening.

            case "damara":
                quirks[character] = content
                # TODO: come back to this one, maybe get really crazy and do some google translate api bullshit?

            case "rufioh":
                quirks[character] = content.replace("i", "1").replace("I", "1")
                # TODO: write a thing that checks for swears and progressively censors them based on badness.
                #  This might be basically impossible.

            case "mituna":
                quirks[character] = content.upper().replace("A", "4").replace("B", "8").replace("E", "3") \
                    .replace("I", "1").replace("O", "0").replace("S", "5").replace("T", "7")
                # TODO: The wiki is awesome. "including but not limited to". You will need to find out if there is
                #  anything missing.

            case "kankri":
                quirks[character] = content.replace("B", "6").replace("O", "9")

            case "meulin":
                quirks[character] = content.upper().replace("EE", "33")
                # TODO: Again, catpuns. Unlikely.

            case "porrim":
                quirks[character] = content.replace("o", "o+").replace("0", "0+") \
                    .replace("plus", "+").replace("Plus", "+")

            case "latula":
                quirks[character] = content.replace("a", "4").replace("i", "1").replace("e", "3") \
                    .replace("A", "4").replace("I", "1").replace("E", "3")
                # TODO: Account for "Z"s at the end of words sometimes? what the fuck ever

            case "aranea":
                quirks[character] = content.replace("b", "8").replace("great", "gr8").replace("Great", "Gr8")
                # TODO: Account for replacement of "ate" and "ait" when agitated? might be impossible

            case "horuss":
                quirks[character] = content.replace("x", "%").replace("X", "%").replace("loo", "100") \
                    .replace("ool", "001").replace("LOO", "100").replace("OOL", "001")
                # TODO: Same goes here as with rufioh, figure out swear words.

            case "kurloz":
                quirks[character] = content
                # TODO: Does this guy even talk?

            case "cronus":
                if content.isupper():
                    quirks[character] = content.replace("v", "w").replace("w", "wv")\
                        .replace("V", "W").replace("W", "Wv")
                else:
                    quirks[character] = content.replace("V", "W").replace("W", "WV").replace("B", "8")
                # TODO: This currently only works if the whole line is in caps, need to refine the search per-word

            case "meenah":
                quirks[character] = content.replace("E", "-E").replace("H", ")(")
                # TODO: Same thing with feferi here.

            case "calliope":
                quirks[character] = content.lower().replace("u", "U")
                # TODO: Account for agitation and alternate version

            case "caliborn":
                quirks[character] = content.upper().replace("U", "u")
                # TODO: Account for when he takes over calliope.

            case "erisolsprite":
                quirks[character] = content.replace("w", "ww").replace("v", "vv").replace("i", "ii").replace("s", "2") \
                    .replace("W", "WW").replace("V", "VV").replace("I", "II").replace("S", "2")

            case "arquiusprite":
                quirks[character] = content.replace("x", "%").replace("X", "%").replace("loo", "100") \
                    .replace("ool", "001").replace("LOO", "100").replace("OOL", "001").replace("cross", "%")

            case "davepetasprite":
                quirks[character] = content.replace("ee", "33").replace("EE", "33")

            case _:
                # TODO: This is everyone else. Data structure for this is un-accounted for, so figure it out shitlips!
                quirks["other"] = content
    return quirks


def write_to_mod(original: str, replace: str, page: int) -> None:
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

    with open(output_path, 'a') as open_file:
        open_file.write("      archive.mspa.story['" + str(page) + "'].content = archive.mspa.story['" + str(page) +
                        "'].content.replace('" + original + "', '" + replace + "')\n")


if __name__ == "__main__":
    main()
