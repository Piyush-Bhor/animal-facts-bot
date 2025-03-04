import re
import praw
import random
import time
import sys
import string


BLACKLIST = (
    'suicidewatch',
    'depression',
    'snakes',
    'mturk',
    'babyelephantgifs',
    'learnprogramming',
    'cscareerquestions',
    'python',
    'India',
    'japan'
    )

history = 'commented.txt'
reply_history = 'repliedto.txt'
unsubscribed_list = 'unsubscribed.txt'
if len(sys.argv) > 1:
    wait_time = int(sys.argv[1])
else:
    wait_time = 90

if len(sys.argv) > 2:
    number_of_messages = int(sys.argv[2])
else:
    number_of_messages = 50


def authenticate():
    print('Authenticating...\n')
    reddit = praw.Reddit('animal-facts-bot', user_agent='/u/AnimalFactsBot')
    print('Authenticated as {}\n'.format(reddit.user.me()))
    return reddit


def check_messages(reddit):
    print("Checking my messages...\n")
    for comment in reddit.inbox.comment_replies(limit=number_of_messages):
        print("Checking comment ID " + comment.id, end='\r')
        if unsubscribed_author_check(comment):
            if not comment.subreddit.user_is_banned and not comment.submission.locked:
                file_obj_r = open(reply_history, 'r')
                if comment.id not in file_obj_r.read().splitlines():
                    try:
                        comment_body = comment.body.lower()
                        if 'good bot' in comment_body:
                            print (comment_body)
                            comment.reply(
                                'Thanks! You can ask me for more facts any time. Beep boop.')
                            print('     Thanked someone for "good bot"\n')
                            record_already_replied(file_obj_r, comment)
                        elif 'bad bot' in comment_body or 'unsubscribe' in comment_body:
                            comment.reply(
                                comment.author.name +
                                " has been unsubscribed from AnimalFactsBot. I won't reply to your comments any more.")
                            print('     Unsubbed ' + comment.author.name + '\n')
                            unsubscribe(comment.author)
                            record_already_replied(file_obj_r, comment)
                        elif 'more' in comment_body:
                            comment.reply(
                                "It looks like you asked for more animal facts! " +
                                random_fact())
                            print('     Gave someone more facts!\n')
                            record_already_replied(file_obj_r, comment)
                        elif 'thank' in comment_body:
                            print('Thanks found in commment ' + comment.id)
                            comment.reply('You are most welcome. Beep boop.')
                            print('     Replied to a thank you\n')
                            record_already_replied(file_obj_r, comment)
                        elif 'TIL' in comment.body:
                            comment.reply("I'm always happy to help people learn!")
                            print('     Replied to a TIL\n')
                            record_already_replied(file_obj_r, comment)
                        elif 'best bot' in comment_body:
                            comment.reply(
                                "It sounds like you called me the 'best bot'. That's awesome!")
                            print('     Replied to a "best bot"\n')
                            record_already_replied(file_obj_r, comment)
                        elif re.search('(fuck)|(bitch)|(shit)', comment_body):
                            comment.reply(
                                "https://www.youtube.com/watch?v=hpigjnKl7nI")
                            print('     WATCH YO PROFANITY\n')
                            record_already_replied(file_obj_r, comment)
                        elif re.search(r'(\scats?\s)|(\sdogs?\s)', ' ' + comment_body + ' '):
                            comment.reply(
                                "Did you ask for cat or dog facts? I'm sorry, if I did cat or dog facts I'd be spamming every thread on reddit. Reply 'more' if you'd like a random animal fact.")
                            print('     Explained why I cant do cat or dog facts\n')
                            record_already_replied(file_obj_r, comment)
                        elif 'silly' in comment_body:
                            comment.reply('I am programmed to be silly!!!')
                            print('     Explained why I am silly\n')
                            record_already_replied(file_obj_r, comment)
                        elif 'hate' in comment_body:
                            comment.reply("Please don't hate. Beep boop.")
                            print('     Replied to a "hate" comment\n')
                            record_already_replied(file_obj_r, comment)
                        elif 'animalfactsbot' in comment_body:
                            print('found my name')
                            comment.reply(
                                "You said my name! Would you like to know more about me? I am written in Python. I am running from a computer in Washington state. I have given an animal fact to redditors " +
                                str(
                                    number_of_facts_given()) +
                                " times!")
                            print('     Told someone about myself.\n')
                            record_already_replied(file_obj_r, comment)
                        else:
                            commented_obj_r = open(history, 'r')
                            if comment.id not in commented_obj_r.read().splitlines():
                                check_comment_for_animal(comment, reddit)
                            commented_obj_r.close()
                    except:
                        print("failed to reply to a message")
                file_obj_r.close()


def number_of_facts_given():
    commented_obj_r = open(history, 'r')
    count = len(commented_obj_r.read().splitlines())
    commented_obj_r.close()
    return count + 50000


def number_of_facts(ALL_FACTS):
    count = 0
    for array in ALL_FACTS:
        count += len(array)
    return count


def record_already_replied(read_file, comment):
    read_file.close()
    file_obj_w = open(reply_history, 'a+')
    file_obj_w.write(comment.id + '\n')
    file_obj_w.close()
    time.sleep(wait_time)


def unsubscribe(redditor):
    unsub_w = open(unsubscribed_list, 'a+')
    unsub_w.write(redditor.name + '\n')
    unsub_w.close()


def unsubscribed_author_check(comment):
    unsub_r = open(unsubscribed_list, 'r')
    if comment.author and comment.author.name in unsub_r.read().splitlines():
        unsub_r.close()
        return False
    else:
        unsub_r.close()
        return True


def random_fact():
    fact_collection = random.choice(ALL_FACTS)
    return random.choice(fact_collection)


def botengine(animal, regex, reddit, facts, comment):
    text = ' '.join(word.strip(string.punctuation)
                    for word in comment.body.lower().split())
    text = ' ' + text + ' '
    match = re.findall(regex, text)
    if match:
        print(
            animal.upper() +
            " found in comment with comment ID: " +
            comment.id)
        if comment.subreddit.display_name.lower() not in BLACKLIST:
            if comment.subreddit.user_is_banned:
                print("     Not commenting because I am banned from " +
                      comment.subreddit.display_name + "\n")
            else:
                if not unsubscribed_author_check(comment):
                    print("     Not commenting because author is unsubscribed.")
                else:
                    file_obj_r = open(history, 'r')
                    if comment.id not in file_obj_r.read().splitlines():
                        if comment.author.name == reddit.user.me():
                            print('     Skipping my own comment...\n')
                        else:
                            print(
                                '     by ' +
                                comment.author.name +
                                ' in ' +
                                comment.subreddit.display_name +
                                '\n      commenting a fact...')
                            try:
                                comment.reply(random.choice(facts))
                                file_obj_w = open(history, 'a+')
                                file_obj_w.write(comment.id + '\n')
                                file_obj_w.close()
                            except:
                                print("Failed to comment - either timed out or deleted/locked comment")
                            finally:
                                file_obj_r.close()
                                time.sleep(wait_time)
                    else:
                        print('     Already commented on this!\n')

def check_mentions(reddit):
    print("Checking mentions...")
    for mention in reddit.inbox.mentions():
        check_comment_for_animal(mention, reddit)


def check_comment_for_animal(comment, reddit):
    botengine('aardvark', r'\saardvarks?\s', reddit, AARDVARK_FACTS, comment)
    botengine('aardwolf', r'\saardwolfs?\s', reddit, AARDWOLF_FACTS, comment)
    botengine('african grey', r'\safrican (grey|gray)s?\s', reddit, AFRICAN_GREY_FACTS, comment)
    botengine('albatross', r'\salbatross(es)?\s', reddit, ALBATROSS_FACTS, comment)
    botengine('alligator', r'\salligators?\s', reddit, ALLIGATOR_FACTS, comment)
    botengine('alpaca', r'\salpacas?\s', reddit, ALPACA_FACTS, comment)
    botengine('anaconda', r'\sanacondas?\s', reddit, ANACONDA_FACTS, comment)
    botengine('anglerfish', r'\sangler ?fish(es)?\s', reddit, ANGLERFISH_FACTS, comment)
    botengine('ant', r'\sants?\s', reddit, ANT_FACTS, comment)
    botengine('anteater', r'\santeaters?\s', reddit, ANTEATER_FACTS, comment)
    botengine('antelope', r'\santelopes?\s', reddit, ANTELOPE_FACTS, comment)
    botengine('armadillo', r'\sarmadillos?\s', reddit, ARMADILLO_FACTS, comment)
    botengine('atlantic puffin', r'\spuffins?\s', reddit, ATLANTIC_PUFFIN_FACTS, comment)
    botengine('avocet', r'\savocets?\s', reddit, AVOCET_FACTS, comment)
    botengine('axolotl', r'\saxolotls?\s', reddit, AXOLOTL_FACTS, comment)
    botengine('honeybadger', '\shoney badgers?\s', reddit, HONEYBADGER_FACTS, comment) # Needs to be here out of order so that it gets picked up before regular badger
    botengine('badger', '\sbadgers?\s', reddit, BADGER_FACTS, comment)
    botengine('ball python', r'\sballpython?\s', reddit, BALLPYTHON_FACTS, comment)
    botengine('barnacle', '\sbarnacles?\s', reddit, BARNACLE_FACTS, comment)
    botengine('bear', '\sbears?\s', reddit, BEAR_FACTS, comment)
    botengine('beaver', '\sbeavers?\s', reddit, BEAVER_FACTS, comment)
    botengine('bison', '\sbisons?\s', reddit, BISON_FACTS, comment)
    botengine('blobfish', '\sblobfish?\s', reddit, BLOBFISH_FACTS, comment)
    botengine('bobcat','\sbobcats?\s',reddit, BOBCAT_FACTS,comment)
    botengine('buffalo', '\sbuffalos?\s', reddit, BUFFALO_FACTS, comment)
    botengine('butterfly', '\sbutterfl(y|ies)?\s', reddit, BUTTERFLY_FACTS, comment)
    botengine('camel', '\scamels?\s', reddit, CAMEL_FACTS, comment)
    botengine('capybara', '\scapybaras?\s', reddit, CAPYBARA_FACTS, comment)
    botengine('chameleon', '\schameleons?\s', reddit, CHAMELEON_FACTS, comment)
    botengine('cheetah', '\scheetahs?\s', reddit, CHEETAH_FACTS, comment)
    botengine('chevrotain','\schevrotain?\s', reddit , CHEVROTAIN_FACTS , comment)
    botengine('chicken' , '\schickens?\s', reddit, CHICKEN_FACTS, comment)
    botengine('chimpanzee', '\schimpanzees?\s', reddit, CHIMPANZEE_FACTS, comment)
    botengine('chinchilla', '\schinchillas?\s', reddit, CHINCHILLA_FACTS, comment)
    botengine('chipmunk', '\schipmunks?\s', reddit, CHIPMUNK_FACTS, comment)
    botengine('clownfish', '\sclown ?fish(es)?\s', reddit, CLOWNFISH_FACTS, comment)
    botengine('cobra', '\scobras?\s', reddit, COBRA_FACTS, comment)
    botengine('conure', '\sconures?\s', reddit, CONURE_FACTS, comment)
    botengine('cougar', '\scougars?\s', reddit, COUGAR_FACTS, comment)
    botengine('cow', '\scows?\s', reddit, COW_FACTS, comment)
    botengine('coyote','\scoyotes?\s',reddit,COYOTE_FACTS,comment)
    botengine('crab', '\scrabs?\s', reddit, CRAB_FACTS, comment)
    botengine('crane', '\scranes?\s', reddit, CRANE_FACTS, comment)
    botengine('crayfish', '\scrayfish(es)?\s', reddit, CRAYFISH_FACTS, comment)
    botengine('crocodile', '\scrocodiles?\s', reddit, CROCODILE_FACTS, comment)
    botengine('cuttlefish', '\scuttle ?fish(es)?\s', reddit, CUTTLEFISH_FACTS, comment)
    botengine('deer', '\sdeer?\s', reddit, DEER_FACTS, comment)
    botengine('degu', '\sdegus?\s', reddit, DEGU_FACTS, comment)
    botengine('dingo', '\sdingos?\s', reddit, DINGO_FACTS, comment)
    botengine('dodo', '\sdodos?\s', reddit, DODO_FACTS, comment)
    botengine('dolphin', '\sdolphins?\s', reddit, DOLPHIN_FACTS, comment)
    # botengine('dragon', '\sdragons?\s', reddit, DRAGON_FACTS, comment)   Disabled because this was only a temp feature during Game of Thrones season. Dragons aren't real.
    botengine('dugong', '\sdugongs?\s', reddit, DUGONG_FACTS, comment)
    botengine('eagle', '\seagles?\s', reddit, EAGLE_FACTS, comment)
    botengine('earthworm', '\searthworms?\s', reddit, EARTHWORM_FACTS, comment)
    botengine('earwig', '\searwigs?\s', reddit, EARWIG_FACTS, comment)
    botengine('echidna', '\sechidnas?\s', reddit, ECHIDNA_FACTS, comment)
    botengine('eland', '\selands?\s', reddit, ELAND_FACTS, comment)
    botengine('elephant', '\selephants?\s', reddit, ELEPHANT_FACTS, comment)
    botengine('elephant shrew', '\selephant ?shrews?\s', reddit, ELEPHANT_SHREW_FACTS, comment)
    botengine('elk', '\selks?\s', reddit, ELK_FACTS, comment)
    botengine('emu', '\semus?\s', reddit, EMU_FACTS, comment)
    botengine('falcon', '\sfalcons?\s', reddit, FALCON_FACTS, comment)
    botengine('ferret', '\sferrets?\s', reddit, FERRET_FACTS, comment)
    botengine('fire salamander', '\sfire salamanders?\s', reddit, FIRESALAMANDER_FACTS, comment)
    botengine('flamingo', '\sflamingos?\s', reddit, FLAMINGO_FACTS, comment)
    # botengine('fly', '\sfl(y|ies)?\s', reddit, FLY_FACTS, comment)
    botengine('fox', '\sfox(es)?\s', reddit, FOX_FACTS, comment)
    botengine('frog', '\sfrogs?\s', reddit, FROG_FACTS, comment)
    botengine('gazelle', '\sgazelles?\s', reddit, GAZELLE_FACTS, comment)
    botengine('gecko', '\sgeckos?\s', reddit, GECKO_FACTS, comment)
    botengine('gibbon', '\sgibbons?\s', reddit, GIBBON_FACTS, comment)
    botengine('giraffe', '\sgiraffes?\s', reddit, GIRAFFE_FACTS, comment)
    botengine('goat', '\sgoats?\s', reddit, GOAT_FACTS, comment)
    botengine('goose', '\s(goose|geese)\s', reddit, GOOSE_FACTS, comment)
    botengine('gopher', '\sgophers?\s', reddit, GOPHER_FACTS, comment)
    botengine('gorilla', '\sgorillas?\s', reddit, GORILLA_FACTS, comment)
    botengine('grasshopper', '\sgrass ?hoppers?\s', reddit, GRASSHOPPER_FACTS, comment)
    botengine('hamster', '\shamsters?\s', reddit, HAMSTER_FACTS, comment)
    botengine('hawk', '\shawks?\s', reddit, HAWK_FACTS, comment)
    botengine('hedgehog', '\shedgehogs?\s', reddit, HEDGEHOG_FACTS, comment)
    botengine('hippo', '\shippos?\s', reddit, HIPPO_FACTS, comment)
    botengine('honeybee', '\shoney bees?\s', reddit, HONEYBEE_FACTS, comment)
    botengine('horse', '\shorses?\s', reddit, HORSE_FACTS, comment)
    botengine('hummingbird', '\shummingbirds?\s', reddit, HUMMINGBIRD_FACTS, comment)
    botengine('husky', '\s(husky|huskie)s?\s', reddit, HUSKY_FACTS, comment)
    botengine('ibex', '\sibex(es)?\s', reddit, IBEX_FACTS, comment)
    botengine('iguana', '\siguanas?\s', reddit, IGUANA_FACTS, comment)
    botengine('jackal', '\sjackals?\s', reddit, JACKAL_FACTS, comment)
    botengine('jellyfish', '\sjelly ?fish(es)\s', reddit, JELLYFISH_FACTS, comment)
    botengine('jerboa', '\sjerboas?\s', reddit, JERBOA_FACTS, comment)
    botengine('kangaroo', '\skangaroos?\s', reddit, KANGAROO_FACTS, comment)
    botengine('kiwi', '\skiwis?\s', reddit, KIWI_FACTS, comment)
    botengine('koala', '\skoalas?\s', reddit, KOALA_FACTS, comment)
    botengine('kookaburra', '\skookaburras?\s', reddit, KOOKABURRA_FACTS, comment)
    botengine('ladybug', '\s(ladybug|lady bug)s?\s', reddit, LADYBUG_FACTS, comment)
    botengine('lamprey', '\slampreys?\s', reddit, LAMPREY_FACTS, comment)
    botengine('lemur', '\slemurs?\s', reddit, LEMUR_FACTS, comment)
    botengine('leopard', '\sleopards?\s', reddit, LEOPARD_FACTS, comment)
    botengine('lion', '\slions?\s', reddit, LION_FACTS, comment)
    botengine('lizard', '\slizards?\s', reddit, LIZARD_FACTS, comment)
    botengine('llama', '\sllamas?\s', reddit, LLAMA_FACTS, comment)
    botengine('lobster', '\slobsters?\s', reddit, LOBSTER_FACTS, comment)
    botengine('lynx', '\slynx(es)?\s', reddit, LYNX_FACTS, comment)
    botengine('manatee', '\smanatees?\s', reddit, MANATEE_FACTS, comment)
    botengine('mantis shrimp', '\smantis shrimps?\s', reddit, MANTIS_SHRIMP_FACTS, comment)
    botengine('markhor', '\smarkhors?\s', reddit, MARKHOR_FACTS, comment)
    botengine('meerkat', '\smeerkats?\s', reddit, MEERKAT_FACTS, comment)
    botengine('mink', '\sminks?\s', reddit, MINK_FACTS, comment)
    botengine('mongoose', '\smongooses?\s', reddit, MONGOOSE_FACTS, comment)
    botengine('monkey', '\smonkeys?\s', reddit, MONKEY_FACTS, comment)
    botengine('moose', '\smoose\s', reddit, MOOSE_FACTS, comment)
    botengine('mouse', '\s(mouse)|(mice)\ss', reddit, MOUSE_FACTS, comment)
    botengine('narwhal', '\snarwhals?\s', reddit, NARWHAL_FACTS, comment)
    botengine('newt', '\snewts?\s', reddit, NEWT_FACTS, comment)
    botengine('nightjar', '\snightjars?\s', reddit, NIGHTJAR_FACTS, comment)
    botengine('ocelot', '\socelots?\s', reddit, OCELOT_FACTS, comment)
    botengine('octopus', '\socto(pus|puses|pusses|pi)\s', reddit, OCTOPUS_FACTS, comment)
    botengine('opossum', '\sopossums?\s', reddit, OPOSSUM_FACTS, comment)
    botengine('orangutan', '\sorangutans?\s', reddit, ORANGUTAN_FACTS, comment)
    botengine('orca', '\sorcas?\s', reddit, ORCA_FACTS, comment)
    botengine('oryx', '\soryx(es)?\s', reddit, ORYX_FACTS, comment)
    botengine('ostrich', '\sostrich(es)?\s', reddit, OSTRICH_FACTS, comment)
    botengine('otter', '\sotters?\s', reddit, OTTER_FACTS, comment)
    botengine('owl', '\sowls?\s', reddit, OWL_FACTS, comment)
    botengine('panda', '\spandas?\s', reddit, PANDA_FACTS, comment)
    botengine('pangolin', '\spangolins?\s', reddit, PANGOLIN_FACTS, comment)
    botengine('panther', '\spanthers?\s', reddit, PANTHER_FACTS, comment)
    botengine('parrot', '\sparrots?\s', reddit, PARROT_FACTS, comment)
    botengine('peacock', '\speacocks?\s', reddit, PEACOCK_FACTS, comment)
    botengine('peccary', '\speccar(y|ies)\s', reddit, PECCARY_FACTS, comment)
    botengine('penguin', '\spenguins?\s', reddit, PENGUIN_FACTS, comment)
    botengine('pig', '\spigs?\s', reddit, PIG_FACTS, comment)
    botengine('pigeon', '\spigeons?\s', reddit, PIGEON_FACTS, comment)
    botengine('platypus', '\splatypuse?s?\s', reddit, PLATYPUS_FACTS, comment)
    botengine('porcupine', '\sporcupines?\s', reddit, PORCUPINE_FACTS, comment)
    botengine('pufferfish', '\spuffer ?fish(es)?\s', reddit, PUFFERFISH_FACTS, comment)
    botengine('puma', '\spumas?\s', reddit, PUMA_FACTS, comment)
    botengine('prayingmantis', '\spraying mantis(es)?\s', reddit, PRAYINGMANTIS_FACTS, comment)
    botengine('quokka', '\squokkas?\s', reddit, QUOKKA_FACTS, comment)
    botengine('rabbit', '\srabbits?\s', reddit, RABBIT_FACTS, comment)
    botengine('raccoon', '\sraccons?\s', reddit, RACCOON_FACTS, comment)
    botengine('rattlesnake', '\srattlesnakes?\s', reddit, RATTLESNAKE_FACTS, comment)
    botengine('raven', '\sravens?\s', reddit, RAVEN_FACTS, comment)
    botengine('reindeer', '\sreindeers?\s', reddit, REINDEER_FACTS, comment)
    botengine('rhino', '\srhino?\s', reddit, RHINO_FACTS, comment)
    botengine('salmon', '\ssalmons?\s', reddit, SALMON_FACTS, comment)
    botengine('scorpion', '\sscorpions?\s', reddit, SCORPION_FACTS, comment)
    botengine('seagull', '\sseagulls?\s', reddit, SEAGULL_FACTS, comment)
    botengine('seahorse', '\sseahorses?\s', reddit, SEAHORSE_FACTS, comment)
    botengine('sea cucumber', '\ssea ?cucumbers?\s', reddit, SEA_CUCUMBER_FACTS, comment)
    botengine('sea urchin', '\s(sea ?)?urchins?\s', reddit, SEA_URCHIN_FACTS, comment)
    botengine('shark', '\ssharks?\s', reddit, SHARK_FACTS, comment)
    botengine('sheep', '\ssheep?\s', reddit, BEAR_FACTS, comment)
    botengine('shrimp', '\sshrimps?\s', reddit, SHRIMP_FACTS, comment)
    botengine('skunk', '\sskunks?\s', reddit, SKUNK_FACTS, comment)
    botengine('sloth', '\ssloths?\s', reddit, SLOTH_FACTS, comment)
    botengine('snail', '\ssnails?\s', reddit, SNAIL_FACTS, comment)
    botengine('snake', '\ssnakes?\s', reddit, SNAKE_FACTS, comment)
    botengine('spider', '\sspiders?\s', reddit, SPIDER_FACTS, comment)
    botengine('squirrel', '\ssquirrels?\s', reddit, SQUIRREL_FACTS, comment)
    botengine('starfish', '\sstarfish(es)?\s', reddit, STARFISH_FACTS, comment)
    botengine('stingray', '\sstingrays?\s', reddit, STINGRAY_FACTS, comment)
    botengine('stoat', '\sstoats?\s', reddit, STOAT_FACTS, comment)
    botengine('sturgeon', '\ssturgeons?\s', reddit, STURGEON_FACTS, comment)
    botengine('sunfish', '\ssunfish(es)?\s', reddit, SUNFISH_FACTS, comment)
    botengine('tarantula', '\starantulas?\s', reddit, TARANTULA_FACTS, comment)
    botengine('tardigrade', '\stardigrades?\s', reddit, TARDIGRADE_FACTS, comment)
    botengine('tarsier', '\starsiers?\s', reddit, TARSIER_FACTS, comment)
    botengine('tasmanian devil', '\stasmanian devils?\s', reddit, TASMANIAN_DEVIL_FACTS, comment)
    botengine('tiger', '\stigers?\s', reddit, TIGER_FACTS, comment)
    botengine('toad','\stoads?\s', reddit, TOAD_FACTS, comment)
    botengine('toucan', '\stoucans?\s', reddit, TOUCAN_FACTS, comment)
    botengine('trouser snake', '\strouser snakes?\s', reddit, TROUSER_SNAKE_FACTS, comment)
    botengine('trout', '\strout?\s', reddit, TROUT_FACTS, comment)
    botengine('tuatara', '\stuataras?\s', reddit, TUATARA_FACTS, comment)
    botengine('turtle', '\sturtles?\s', reddit, TURTLE_FACTS, comment)
    botengine('vampire bat', '\svampire bats?\s', reddit, VAMPIRE_BAT_FACTS, comment)
    botengine('vulture', '\svulture?\s', reddit, VULTURE_FACTS, comment)
    botengine('wallaby', '\swallab(y|ies)\s', reddit, WALLABY_FACTS, comment)
    botengine('walrus', '\swalrus\s', reddit, WALRUS_FACTS, comment)
    botengine('warthog', '\swarthogs?\s', reddit, WARTHOG_FACTS, comment)
    botengine('whale', '\swhales?\s', reddit, WHALE_FACTS, comment)
    botengine('wildebeest','\swildebeests?|gnu\s', reddit, WILDEBEEST_FACTS, comment)
    botengine('wolf', '\swol(f|ves)\s', reddit, WOLF_FACTS, comment)
    botengine('wolverine', '\swolverines?\s', reddit, WOLVERINE_FACTS, comment)
    botengine('yak', '\syaks?\s', reddit, YAK_FACTS, comment)
    botengine('zebra', '\szebras?\s', reddit, ZEBRA_FACTS, comment)
    botengine('zebrafish', '\szebrafishs?\s', reddit, ZEBRAFISH_FACTS, comment)


def animalfactsbot(reddit):
    check_messages(reddit)
    print("Pulling 1000 comments...")
    comment_list = reddit.subreddit('all').comments(limit=1000)
    print("     checking each comment for " +
          str(len(ALL_FACTS)) + " different animals\n")
    for comment in comment_list:
        check_comment_for_animal(comment, reddit)


AARDVARK_FACTS = (
    'Aardvarks live in many different types of habitats, such as grasslands, savannas, rainforests, woodlands and thickets throughout Africa in the areas south of the Sahara.',
    'Female aardvarks have a gestation of seven months and give birth to one young at a time.',
    'Aardvarks are also called ant bears.',
    'Aardvarks have four toes on the front feet and five toes on their back feet.',
    'Skilled diggers, an aardvark can dig up to 2 feet (.6 m) in 15 seconds, according to the African Wildlife Foundation.'
    'The aardvark is the only species in its order. It is literally like no other animal on earth.',
    'The aardvark is admired in African folklore because of its diligent search for food and its lack of fear of soldier ants. The Maasai tribe believe sighting an aardvark brings good fortune.',
    'The name Aardvark comes from South Africa’s Afrikaans language and means ‘earth pig’ or ‘ground pig’.',
    'Aardvarks can live to be over 24 years old in captivity. In the wild, they live between 10 – 23 years.',
    'Aardvarks can close their nostrils to keep out dirt and bugs while they dig.',
    'Aardvarks have excellent hearing and their long ears allow them to hear tiny sounds, such as termites under the ground.',
    'Aardvarks can dig fast or run in zigzag fashion to elude enemies, but if all else fails, they will strike with their claws, tail and shoulders, sometimes flipping onto their backs lying motionless except to lash out with all four feet.',
    'Skin of the aardvark body is thick and tough. It provides protection against bites of angry ants and termites. ',
    'Aardvark can travel between 16 and 30 kilometers per night while searching for the food.',
    'Aardvark is excellent swimmer thanks to its webbed feet.',
    'An aardvark has a long snout that ends with a pig-like nose, rabbit-like ears and a tail similar to a kangaroo\'s. Yet it is not closely related to any of those animals.',
    'Aardvarks are about the size of a small pig. Typically, they weigh from 110 to 180 lbs. (50 to 82 kilograms).',
    'If it stuck its tongue out, an aardvark would be much longer. Their tongues can be up to 12 inches (30.5 cm) long.',
    'Aardvarks live in many different types of habitats, such as grasslands, savannas, rainforests, woodlands and thickets throughout Africa in the areas south of the Sahara.',
    'Aardvarks have spoon-shaped claws which are like steel – and used to rip into extremely hard ground and termite mounds.',
    'Aardvarks change burrows frequently, providing opportunity for subsequent residents like wild dogs, pythons, warthogs and South African shelduck.',
    'Aardvarks are nocturnal and travel up to 16km every night, foraging for food.',
    'Aardvarks feed almost exclusively on ants and termites, and are known to eat around 50,000 in one night. They can eat plants and often feed on an African cucumber known as the aardvark cucumber.',
    'Aardvarks are prey to many animals including lions, leopards, hunting dogs, hyenas, and pythons.',
    'Aardvarks are solitary and only come together to mate; females have a gestation period of seven months. One cub is born between May and July and will remain in the burrow for the first two weeks of life.',
    )

AFRICAN_GREY_FACTS = (
    'The Congo African Grey is the largest of the African Grey parrots, sporting a lighter gray color in its plumage, and a solid black beak.',
    'An African Grey has the mental and emotional capacities of a 5-year-old human child.',
    'The African Grey parrot is famous for its intelligence and ability to mimic human speech.',
    'African Grey Parrots form very strong bonds with their owners and can be quite emotionally needy',
    'Not only will African Greys develop outstanding vocabularies, they may even come to understand what you are saying.',
    'Alex, the most famous African Grey, can recognize and identify verbally close to 50 objects, 7 colors, and 5 shapes.',
    'African Greys tend to train you to do their bidding',
    'African Grey parrots generally inhabit savannas, coastal mangroves, woodland and edges of forest clearings in their West and Central Africa range.',
    'African Greys are susceptible to feather picking, calcium deficiency, vitamin-A and vitamin-D deficiency, respiratory infection, psittacosis and psittacine beak and feather disease (PBFD).',
    )

AARDWOLF_FACTS = (
    'Aardwolf is small animal. It can reach 3 feet in length and up to 30 pounds in weight. Bushy tail is 7.9 to 11.8 inches long.',
    'Body of aardwolf is covered with two layers of dense fur that can be yellowish-white or reddish in color. Black stripes cover both sides of the body, including their limbs.',
    'Aardwolf has a mane that stretches from the head to the tail. Aardwolf raises its mane to appear bigger (and scarier) when it is threatened.',
    'Aardwolf has narrow muzzle and pointed ears. Its front legs are longer than hind legs. Aardwolf has 5 toes on front feet.',
    'Unlike other hyenas, aardwolf has poorly developed teeth. It has long and sticky tongue which is specialized for diet based on insects.',
    'Aardwolf\'s diet consists almost exclusively of termites. It can eat up to 300 000 termites per night. Maggots and other invertebrates with soft bodies are occasionally consumed. Aardwolf will eat small mammals, birds and carrion only when termites cannot be found.',
    'Aardwolf is nocturnal creature (active during the night).',
    'Besides humans, jackals are main enemies of aardwolves.',
    'Aardwolf is solitary and territorial animal. It occupies territory of 1 to 4 square miles. Boundaries of territory are marked with urine, dung and scent produced in anal gland. Aardwolf fiercely defends its territory (by fighting with other aardwolves).',
    'Aardwolf lives in underground burrows. Even though it can dig a hole in a ground using the claws, aardwolf prefers abandoned burrows of other animals such as aardvark and porcupine.',
    'Aardwolf is a silent animal that vocalizes only when it is threatened. Clucking and growling sounds can be heard occasionally.',
    'Aardwolves are monogamous animals (one couple mate for a lifetime). Mating season takes place in the June and July.',
    'Pregnancy in females lasts 90 days and ends with 2 to 4 cubs. Babies spend first month of their life hidden in a den.',
    'Both parents take care of their young. Father guards the den against predators. Young aardwolves drink mother\'s milk during the first 3 or 4 months. After that period, they will join their parents in foraging for food.',
    'Aardwolves will leave their family group at the age of one year to begin independent life.',
    'Aardwolf can survive 8 years in the wild and up to 15 years in captivity.',
    )

ALBATROSS_FACTS = (
    'Albatrosses are known to live until their fifties sixties.',
    'The Wandering albatross has a wingspan that measures up to 11 feet 4 inches from end to end, the largest of any living bird.',
    'When albatrosses find a mate they will pair for life, a union that will often last for 50 years.',
    'The top albatross predator is the tiger shark, that will prey on young chicks shortly after nesting season',
    'Simply using thermal currents, albatrosses can glide for several hundred miles without flapping.',
    'Albatrosses can smell out prey from over 12 miles away.',
    'Of the 22 regognised species of albatrosses, all are listed as at some level of concern; 3 species are Critically Endangered, 5 species are Endangered, 7 species are Near Threatened, and 7 species are Vulnerable.',
    'The scientific name for the albatross is Diomedeidae.',
    'Albatrosses perform dances to attract a mate, these are then repeated each time they meet.',
    'The body of an albatross is covered with white, black, brown, red or yellow feathers. They were used for decoration of hats in the past.',
    'Albatrosses can reach the speed of 40 miles per hour.',
    'Albatrosses have no problem drinking sea water. The salt they take in is absorbed and moves through their blood stream into a pair of salt glands above their eyes and finally excreted via the nostrils.',
    'Albatrosses spend over 80% of their life at sea, visiting land only for breeding.',
    'In all albatross species, both parents incubate the egg in stints. Incubation lasts around 70 to 80 days (longer for the larger albatrosses), the longest incubation period of any bird.',
    )

ALLIGATOR_FACTS = (
    'Alligators have been living on Earth for millions of years and are sometimes described as ‘living fossils’.',
    'Alligators live in freshwater environments, such as ponds, marshes, wetlands, rivers, and swamps, as well as brackish environments.',
    'There are two different species of alligator, the American alligator and the Chinese alligator.',
    'The American alligator, Alligator mississippiensi, is the largest reptile in North America.',
    'American alligators live in south-eastern areas of the United States such as Florida and Louisiana.',
    'Chinese alligators are found in the Yangtze River but they are critically endangered and only a few remain in the wild.',
    'Like other reptiles, alligators are cold-blooded.',
    'Alligators use their tails, which accounts to half of their body length, to propel in the water.',
    'Alligators can weigh over 450 kg (1000 lb).',
    'Alligators are social creatures and often stay in groups called congregations. These groups are typically seen basking in the sun or taking a swim.',
    'Although alligators have no vocal cords, males bellow loudly to attract mates and warn off other males by sucking air into their lungs and blowing it out in intermittent, deep-toned roars.',
    'Alligators have a powerful bite but the muscles that open the jaw are relatively weak. An adult human could hold the jaws of an alligator shut with their bare hands.',
    'Alligators eat a range of different animals such as fish, birds, turtles and even deer.',
    'Alligator eggs become male or female depending on the temperature, male in warmer temperatures and female in cooler temperatures.',
    'Like crocodiles, alligators are part of the order ‘Crocodylia’.',
    )

ALPACA_FACTS = (
    'The hair of the Alpaca is called "fleece" or "fiber" rather than "fur" or "wool".',
    'The oldest known records of Alpacas was 1,000 years before the great pyramids of Giza.',
    'The Alpaca is prey to mountain lions, coyotes, bears, and other carnivores. In its native Andes, their long neck helps spot predators among the rocks of the mountain slopes. On US ranchs, llamas, donkeys, and guard dogs such as Anatolian shepherd dogs are often used as herd guardians.',
    'Humming is the most common sound an Alpaca makes, a sort of musical purring. The mom calls to her cria by humming, or they hum to communicate with each other within the herd.',
    'During breeding, which lasts from 20 to 30 minutes, a male Alpaca trumpets or "orgles" a lovesong to his mate.',
    'Alpacas have a life expectancy of about 20 years.',
    'The Alpaca is an herbivore, grazing on grass and munching weeds, shrubs and trees.',
    'Alpacas process their food through 3 stomachs where special secretions enable the animal to absorb 50% more nutrients than sheep.',
    'Like their cousins the Llamas, Alpacas spit when angry or annoyed.',
    'Alpacas “cush” when seated, meaning they fold their legs under their body making them easy to transport in a smaller vehicle.',
    'Alpacas love to sunbathe.',
    'Alpacas’ tails are used to express feelings to each other.',
    )

ANACONDA_FACTS = (
    'Anaconda can be 30 feet long (like a school bus) and weigh up to 550 pounds (like 11 kids). Females are larger than males.',
    'Anaconda hunts on the ground and in the water, but it spends most of its life in the water where it moves more easily.',
    'Anacondas grow constantly their entire life.',
    'When animal dies, Anaconda swallows whole prey in one piece.',
    'Anacondas Give Birth to Live Young.',
    'Baby Anacondas are 2 feet long and they are capable for individual life from the moment they are born.',
    'Anacondas can Remain Submerged for Up to Ten Minutes at a Time.',
    'The Green Anaconda is the Heaviest Known Snake, but Not the Longest.',
    'They’re Members of the Boa Family.',
    'Caimans are alligator-like predators that frequent South American waterways. Anacondas are known to hunt these reptilian neighbors, but often sustain significant injuries while doing so.',
    'While getting around, snakes (including Anaconda) have several options, of which “sidewinding” is perhaps the most athletic. Unlike normal slithering, this exhausting technique involves a given reptile using large, J-shaped coils to hastily pull itself along. In general, smaller snakes are more likely to sidewind, although—as the above footage shows—their big cousins will sometimes follow suit.',
    'Nicki Minaj sang a song named "Anaconda".',
    )

ANGLERFISH_FACTS = (
    'The scientific name for the Anglerfish is Lophiiformes.',
    'An Anglerfish can weigh up to 110lbs/50kgs.',
    'There are more than 200 species of Anglerfish',
    'Anglerfish typically live at the bottom of the ocean, between 400 to 2,000 metres, in complete darkness.',
    'The light of an Anglerfish lure comes from tiny bacteria called photoplankton',
    'The Anglerfish lure, worn only by females, is a piece of dorsal spine that lights up in order to attract prey.',
    'The mouth of an Anglerfish is so big, and its body is so pliable, that it can swallow prey up to twice its size.',
    'Male Anglerfish are significantly smaller than their female counterparts, and when a male encounters a female, it latches on onto her with his sharp teeth. Eventually, the male physically fuses with the female.',
    'When a male Anglerfish has fused to a female, it loses all its organs apart from its testes.',
    'A female Anglerfish will carry six or more males on her body.',
    'According to the National Geographic, the Anglerfish is quite possibly the ugliest animal on the planet.',
    'The Anglerfish lives in what is easily Earth\'s most inhospitable habitat: the lonely, lightless bottom of the sea.',
    'Although uncommon, some Anglerfish live in shallow, tropical waters.',
    'Most Anglerfish are less than a foot in length, although some can grow up to 3.3 feet in length.',
    'The Anglerfish lure is only worn by females and is a piece of dorsal spine that protrudes above their mouths like a fishing pole.',
    'The Anglerfish have mouths so big and their bodies are so pliable, they can actually swallow prey up to twice their own size.',
    'When a young, free-swimming male Anglerfish encounters a female, he latches onto her with his sharp teeth. Over time, the male physically fuses with the female, connecting to her skin and bloodstream and losing his eyes and all his internal organs except the testes. A female will carry six or more males on her body.',
    'The Anglerfish have a luminescent organ, called the esca, at the tip of a modified dorsal ray.',
    'Because of the small amount of food available in their environment, the Anglerfish has adapted to store food when there is an abundance.',
    )

ANT_FACTS = (
    'There are more than 12,000 species of ants all over the world.',
    'An ant can lift 20 times its own body weight. If a second grader was as strong as an ant, she would be able to pick up a car!',
    'Some queen ants can live for many years and have millions of babies!',
    'Ants don’t have ears. Ants "hear" by feeling vibrations in the ground through their feet.',
    'Ants are the longest living of all insects, living for up to 30 years.',
    'When ants fight, it is usually to the death!',
    'When foraging, ants leave a pheromone trail so that they know where they’ve been.',
    'One ant species (Trap-Jaw Ants) owns the record for the fastest movement within the animal kingdom.',
    'The largest ant colony ever found was over 6000 Km or 3750 miles wide.',
    'All worker, soldier, and queen ants are female.',
    'Some ant species are asexual, they clone themselves and do not require any males.',
    'Ants and humans are the only creatures that farm other creatures.',
    'Some ants can swim.',
    'Ants can be found on every continent except for Antarctica.',
    'Ants have transparent abdomens that can show the color of the food they eat.',
    'Ants do not breathe through a centralized respiratory system, like many other insects ants breath throughout their entire body.',
    )

ANTEATER_FACTS = (
    'Anteaters are toothless creatures.',
    'Since ants can bite, anteaters must eat them quickly. They are flicking their tongue 150-160 times in minute during feeding to grab enough ants and avoid bites.',
    'Anteaters are solitary animals and they gather only during mating season. A group of anteaters is called a "parade".',
    'Pregnancy lasts 190 days and ends with single baby. Baby anteaters stay with their mother for 2 years or until she becomes pregnant again. The mother carries the baby on her back during the first year.',
    'Anteaters live up to 15 years in the wild and 25 years in captivity.',
    'There are four species of anteaters.',
    'Anteaters can range from the size of a squirrel, to even seven feet long!',
    'Anteaters sleep up to fifteen hours a day.',
    'Anteaters produce formic acid in their stomach instead of hydrochloric acid, which mammals usually produce.',
    'Anteaters have very poor eyesight and rely on their keen sense of smell to find food.',
    'Anteaters can eat up to 35,000 insects a day.',
    'Anteaters will never destroy an anthill because they need it as a source of food.',
    'Anteaters have tongues that can be 2 feet long.',
    'Anteaters are most closely related to sloths.',
    )

ANTELOPE_FACTS = (
    'Antelopes are a large and diverse group of animals of the cow family (Bovidae).',
    'Antelopes live in Africa, Asia, Middle East, and North America. Antelopes can be found in grasslands, mountains, deserts, and wetlands. There are 90 different species of antelopes.',
    '25 species of antelopes are endangered. Poaching and loss of habitat are the main reasons why they are faced with extinction.',
    'The Giant Eland is the largest species of antelope, with a body length ranging from 220 to 290 centimeters (87–114 inches) and stand approximately 130 to 180 centimeters (4.3 to 5.9 feet) at the shoulder. They weigh from 400 to 1,000 kilograms (880 to 2,200 pounds).',
    'The Royal Antelope is the world’s smallest species of antelope; it stands up to merely 25 centimeters (10 inches) at the shoulder and weighs 2.5 to 3 kilograms (5.5 to 6.6 pounds).',
    'All antelopes have even-toed hooves, horizontal pupils, stomachs adapted for re-chewing of the food (they are ruminants, just like all cows), and bony horns.',
    'All antelope have horns, they can be straight, spiral, curved or twisted; in some species they are only found on the males, whereas in others, such as gazelles, both males and females have them.',
    'The horns of antelopes are made of a bony core encased in a hard material made largely of keratin (the same substance our fingernails are made of!).',
    'Hooves are another specialty for many antelope. Each hoof has a split down the middle, dividing the hoof into two toes.',
    'Antelopes have extremely developed senses which help them detect predators while they still have time to escape.',
    'Depending on the species, 4-9 months after mating season, a baby antelope will be born. Baby antelope are an easy target and the mother keeps it on the secret location until it grows stronger.',
    'Some antelope are famous for their massive herds, like the thousands of wildebeests making their annual migration across the African plains.',
    )

ARMADILLO_FACTS = (
    'The average lifespan of an armadillo in the wild is 7-10 years.'
    'All 20 species of armadillos are found in the western hemisphere.'
    'Armadillos originated in South America.'
    'The only species of armadillo that has made it into the United States is the nine-banded species, which inhabits Texas and the Gulf Coast states and can be found as far north as Missouri.'
    'An armadillo burrow is about 7-8" wide and up to 15 feet deep.'
    'Armadillos are mainly insectivores, with over 90 percent of their diet consisting of animal matter, like insects and other invertebrates.'
    'Armadillos are known to eat the occasional reptile or amphibian - especially in colder weather.'
    'Armadillos have the ability to carry the bacterium that causes leprosy in humans (Mycobacterium leprae).'
    '"Armadillo" is Spanish for "little armored one".'
    'Armadillos are the only mammals whose body is covered with hard shell.'
    'Only three-banded armadillo can curl into the ball to protect itself from predators. Other armadillos run or dig a hole when they need to escape from predators.'
    'Nine-banded armadillos always give birth to four identical young — the only mammal known to do so.'
    'Armadillos can hold their breath for 4-6 minutes at a time.'
    'Because their heavy shell makes it hard for them to float, armadillos gulp air into their intestines to make them more buoyant.'
    'Armadillos belongs to the Dasypodidae family.',
    'There are 21 species of armadillo.',
    'The smallest armadillo is the pink fairy armadillo. The largest armadillo is the giant armadillo.',
    'The armor on the armadillo is made up of overlapping plates. The armor covers the back, head, legs, and tail.',
    'Armadillos are small to medium-sized mammals.',
    'The three-banded armadillo, can roll itself into a hard armored ball.',
    'Armadillos have poor eyesight, so they hunt with their highly developed sense of smell.',
    'Armadillos have wiry hairs along their sides and belly, wich they use to feel their way around.',
    'Armadillos have harp claws and strong legs for digging.',
    'Armadillos are picky about where they live based on the type of soil is found in the area. Armadillos usually prefer sandy or loam soils that are loose and porous.',
    'Armadillos are omnivores, which means they eat both meat and plants.',
    'Armadillos use their long, sticky tounge to catch ants, termites, beetles and other insects after digging them out of the ground.',
    'The nine-banded armadillo is the official state animal of Texas.',
    )

ATLANTIC_PUFFIN_FACTS = (
    'The Atlantic Puffin is the only puffin native to the Atlantic Ocean.',
    'The Atlantic Puffin breeds in Iceland, Norway, Greenland, Newfoundland, and many North Atlantic islands, and as far south as Maine in the west and the British Isles in the east.',
    'There are considered to be three subspecies of Atlantic puffin: Fratercula arctica arctica, Fratercula arctica grabae, Fratercula arctica naumanni.',
    'Like many seabirds, the Atlantic puffin spends most of the year far from land in the open ocean and only visits coastal areas to breed.',
    'Puffins mainly eat small fish, including sand eels, herring, hake and capelin.',
    'The average lifespan of a Puffin in the wild is about 20 years.',
    'Atlantic puffins steer with rudderlike webbed feet and can dive to depths of 200 feet, though they usually stay underwater for only 20 or 30 seconds.',
    'The Atlantic Puffin is sexually mature at 4 to 5 years old.',
    'The Atlantic Puffin is the official bird symbol of the province of Newfoundland and Labrador, Canada.',
    'When they take off, Atlantic Puffins patter across the surface of the water while vigorously flapping their wings, before launching themselves into the air.',
    'Atlantic Puffins tend to be monogamous. However, this is the result of their fidelity to their nesting sites rather than to their mates, and they often return to the same burrows year after year.',
    'Atlantic Puffins are colonial nesters, excavating burrows on grassy clifftops or reusing existing holes. They may also nest in crevices and amongst rocks.',
    'Atlantic Puffins tend to be very social birds and usually breed in large colonies.',
    'Atlantic puffins are excellent fliers. Flapping their wings at up to 400 beats per minute, puffins can reach speeds of 88 km/h (55mph)',
    'Atlantic Puffins have the same mate each year.',
    'Puffins create burrows, about 90 cm (3 ft.), in rocky cliffs either in the soil or between rocks. Often, couples will return to the same burrow year after year. At the back of the burrow, they build a nest lined with grasses, seaweed, and feathers. After the female lays a single egg, both parents take turn incubating the egg for about 40 days.',
    'The puffins’ genus name "Fratercula" comes from the Latin for “little brother”. The name refers to the sea bird’s black and white plumage, which was said to resemble the robes that monks once wore.',
    'Sixty percent of the world’s puffins breed in Iceland.',
    'Puffins are one of the few birds that have the ability to hold several small fish in their bills at a time. Their raspy tongues and spiny palates allow them to firmly grasp 10 to 12 fish during one foraging trip. They thus can bring more food back to their young compared with other seabirds that tend to swallow and regurgitate meals for their chicks.',
    )

AVOCET_FACTS = (
    'There are four different species of avocet which are the Pied avocet, the American avocet, the Red-necked avocet and the Andean avocet.',
    'The avocet is a type of wading bird.',
    'The avocet is generally found in watery habitats close to the coast',
    'The avocet has long legs and webbed feet to aid it in hunting in the shallows.',
    'The avocet is a relatively large and forceful species of bird, often reported to intimidate other birds into leaving its spot.',
    'The avocet has a long and thin, upturned beak which it sweeps from side to side in the water to catch food.',
    'The avocet is a relatively large and forceful species of bird, often reported to intimidate other birds into leaving its spot.',
    'The avocet flys, hunts, migrates and nests in large flocks.',
    'The avocet is Carnivorous.',
    'Avocets are known to breed on open ground, generally close to the water.',
    'Avocet chicks are nursed by both parents until they fly away from the nest at between 4 and 6 weeks old.',
    )

AXOLOTL_FACTS = (
    'The axolotl is a salamander – a type of amphibian with a lizard-like body, a long tail and smooth, moist skin. The axolotl has short legs and widely-spaced lidless eyes.',
    'Wild Axolotls are normally brown or black, not white.',
    'In the wild, Axolotls can only be found in the lakes and canals of Xochimilco, Mexico.',
    'Axolotls are endangered.',
    'The name Axolotl is based off of Xolotl, a dog-headed god from Aztec mythology.',
    'Axolotls have the ability to not only regenerate limbs like some other amphibians, but they can also rebuild their spine and even their brain.',
    'Sometimes an axolotl will damage a limb, and not only will that limb heal, but another one will grow too, giving the axolotl an extra limb!',
    'Because of their extraordinary regenerative ability, Axolotls are the subject of biological and medical research.',
    'Axolotls exhibit neoteny, meaning they reach maturity without going through metamorphosis.',
    'The feather-like branches that grow on an Axolotl head are actually their gills .',
    'If an axolotl is injected with a chemical called iodine, it will undergo metamorphosis and change into its adult form resembling a salamander',
    'Axolotls are carnivores (meat-eaters). Their diet consists of worms, insects, and other invertebrates.',
    )

BADGER_FACTS = (
    'Badgers are part of the family Mustelidae. This is the same family as otters, ferret, polecats, weasels, and wolverines.',
    'There are 11 species of badger, grouped into 3 types, the Melinae (Eurasian badgers), Mellivorinae (Honey badger) and Taxideinae (American badger).',
    'Badgers are found in North America, Ireland, Great Britain, and most of Europe. There are species in Japan, China, Indonesia and Malaysia. The honey badger is found in sub-Saharan Africa, the Arabian Desert, Turkmenistan, and India.',
    'Badgers have stocky bodies with short legs that are suitable for digging. They dig burrows underground called a sett. Their sett are often a maze of tunnels and chambers for sleeping around 6 badgers, setts are kept very clean.',
    'The badger has an elongated head with small ears and a distinctive black and white face, their body has greyish fur with black and white areas underneath.',
    'Badgers can grow to nearly a meter in length. The European badger is larger than the American badger and the Honey badger.',
    'Badgers on average weigh around 9 - 11 kg (20 - 24 lbs).',
    'The badger can run up to 30 km/h (19 mph) for a short period of time.',
    'A male badger is called a boar, the female is called a sow, and the young are called cubs.',
    'A group of badgers is called a cete, although they are often called clans. There are usually 2 - 15 badgers in a cete.',
    'The honey badger is a carnivorous species that has the reputation of being the most fearless and vicious of all mammals.',
    'Badgers were eaten in Britain during World War II and were once part of the Native American and settlers diets in the US. Russia still eats badger meat today.',
    'Badgers have featured in lots of British literature over the years, such as Brian Jacques\' Redwall series, \'Tommy Brock\' in Beatrix Potter\'s The Tale of Mr. Tod, \'Bill Badger\' in Mary Tourtel\'s Rupert Bear, \'Mr. Badger\' in Kenneth Grahame\'s The Wind in the Willows, and \'Trufflehunter\' in C. S. Lewis\'s Chronicles of Narnia.',
    )

BALLPYTHON_FACTS = (
    'The name ball python comes from their habit of rolling themselves into a tight ball when frightened.',
    'Ball pythons have an average lifespan of around 30 years.',
    'The oldest recorded ball python lives at the St. Louis Zoo and is more than 62 years old.',
    'Wild ball pythons rely on their labial pits to help them find prey. The labial pits function as a sort of infrared vision and allow the snake to see the heat produced by other living things.',
    'There are over 7,500 different ball python morphs on the market.',
    'The first designer ball python morph was an albino produced in 1992.',
    'The most expensive ball python morph is the lavender albino, which has gone for $40,000 in the past.',
    'Ball pythons are typically nocturnal or crepuscular, meaning that they are active during dusk, dawn, and/or nighttime.',
    'Ball pythons are the most popular pet snake and the second most popular pet reptile after the bearded dragon.',
    'Ball pythons shed their skin every 5 to 7 weeks on average',
    )

BARNACLE_FACTS = (
    'Although the barnacle is frequently confused for a mollusc because of its hard outer shell, it is actually a crustacean.',
    'In their juvenile form barnacles are free-floating, but eventually they attach themselves to any nearby rock, shell, or other object and stay there for the rest of their lives.',
    'Barnacles are often seen on crabs, whales, boats, rocks and on the shells of sea turtles.',
    'Some species of barnacle are parasitic, but most species are harmless.',
    'Barnacles have no true heart, although a sinus close to the esophagus performs a similar function.',
    'Barnacles have no gills, absorbing oxygen from the water through their limbs and the inner membrane of their carapaces.',
    'There are around 1220 species of barnacle.',
    'Barnacles can be pink, yellow, orange, green, brown or covered with stripes.',
    'Barnacles have a lifespan of 5 to 10 years.',
    'Barnacles can reach a size of up to 2.7 inches in diameter.',
    'Once a barnacle attaches to something, it stays attached for the rest of its life.',
    'Barnacles like to attach to areas with lots of other barnacles, as this indicates plenty of food and good conditions.',
    'Barnacles are omnivores, which mean they eat plants and meat. Their diet consists mainly of plankton and algae.',
    'The main enemies of barnacles are sea stars, snails and mussels.',
    'Barnacles feed by filtering food through their feathery appendages, which are modified legs.',
    'Barnacle mating season is during autumn and winter.'
    'Some barnacles are considered a delicacy.',
    'The US Naval Academy estimates that the hull-drag caused by barnacles increases the Navys petroleum bill by $250 million every year.',
    )

BEAR_FACTS = (
    'There are eight different species of bear! The North American Black Bear, the Brown Bear, the Polar Bear, the Asiatic Black Bear, the Spectacled Bear, the Giant Panda, the Sloth Bear, and the Sun Bear!',
    'The California Grizzly Bear became officially extinct in 1924. It is a subspecies of the Grizzly Bear which is a subspecies of the Brown Bear.',
    'The world\'s longest recorded living bear was Debby, a female polar bear born in the Soviet Union at some point in 1966. She died on November 17th 2008 in Canada at either age 41 or 42.',
    '98 percent of North America\'s grizzly bear population lives in Alaska.',
    'Spectacled Bears are the only species of bear to live in South America.',
    'The Black Bear can be found with black, brown, gray, silvery-blue and cream fur coats!',
    'The Spectacled Bear is sometimes known as the Andean Bear because they live in the Andes Mountains.',
    'The "Teddy Bear" comes from 1902 when U.S. President Theodore Roosevelt (a.k.a. Teddy) refused to shoot a bear cub that was brought to him. The act of kindness spread quickly and the name "Teddy Bear" became popular.',
    'The Giant Panda is seen as so valuable that the Chinese government has used them as gifts to other countries!',
    'Bears such as the American Black Bear and the Grizzly Bear hibernate in the winter. Their heart rates drop from a normal 55 to only 9!',
    )

BEAVER_FACTS = (
    'There are two species of beaver, the European or Eurasian beaver (Castor fiber) and the North American beaver (Castor canadensis).',
    'Beavers are the second largest rodent in the world after the capybara.',
    'The beaver is mainly a nocturnal animal.',
    'The large front teeth of the beaver never stop growing. The beavers constant gnawing on wood helps to keep their teeth from growing too long.',
    'Both male and female beavers have a pair of scent glands, called castors, at the base of their tails. They use the secretions from these glands, a musk-like substance called castoreum, to mark territory.',
    'Together beaver colonies create dams of wood and mud to provide still, deep water in order to protect against predators such as wolves, coyotes, bears or eagles, and also so they can float food and building material to their homes.',
    'Once the dams are completed and ponds formed, beavers will work on building their homes called lodges in the middle. The dome shaped lodges, like the dams, are constructed with branches and mud. Lodges have underwater entrances, making entry tough for most other animals.',
    'There are usually two dens within the lodge, one is for drying off after entering from the water and another, drier one, is where the family of up to four adults and six to eight young live.'
    'There were once more than 60 million North American beavers. But due to hunting for its fur, its glands for medicine and because the beavers tree-felling and dams affect other land uses, the population has declined to around 12 million.',
    'The beaver has a good sense of hearing, smell, and touch. It has poor eyesight, but does have a set of transparent eyelids which allow them to see under water.',
    'Using their broad, scaly tail, beavers will forcefully slap the water as an alarm signal to other beavers in the area that a predator is approaching.',
    'Beavers are slow on land but using their webbed feet they are very good swimmers. A beaver can stay under water for up to 15 minutes.',
    'Beavers are herbivores. They like to eat the wood of trees such as the aspen, cottonwood, willow, birch, maple, cherry and also eat pondweed and water lilies.',
    'Adult beavers are around 3 feet long and have been known to weigh over 25 kg (55 lb). Females are as large or larger than males of the same age.',
    'Beavers can live up to 24 years in the wild.',
    'The beaver is the national animal of Canada, and is featured on the Canadian five-cent piece.',
    'Beavers like to keep themselves busy, they are prolific builders during the night. Hence the saying "As busy as a beaver".',
    )

BISON_FACTS = (
    'The bison has long shaggy brown fur, a mane, and beard under its chin. It has a big head with short black horns and a hump on its shoulders.'
    'An adult bison can weigh up to 2,000 pounds and stand 6 feet tall.',
    'Bison may be big, but they’re also fast. They can run up to 35 miles per hour. They’re extremely agile.',
    'Bison can be found in most of Canada, the United States, and parts of Mexico.',
    'Classifications of Bisons include: American Bison, Bison occidentalis, Bison antiques, Steppe bison, and European bison',
    'Bison mainly live on plains, prairies, and river valleys.',
    'The bison is a grazer. Its diet is made up of mostly grasses and sedges',
    'Bisons generally appear to be sluggish, lazy and peaceful',
    'The average lifespan of a bison is 10-20 years.',
    'Bison have poor eyesight but they have excellent senses of smell and hearing.',
    'Female bison give birth to one calf after 9 months.',
    'Bison live in a variety of groups. Each bison group has a dominant male or female.',
    'Bisons are the largest Mammals in North America.',
    'The scientific name for Bison is bison bison bison.',
    'In winter, Bisons can dig through snow to get to the vegetation below.',
    'The muscle-filled large hump on a Bison\'s back allows it to plough through snow.'
    'Bison live in a variety of groups. Each bison group has a dominant male or female.',
    'Yellowstone National Park is the only place in the U.S. where bison have continuously lived since prehistoric times.',
    'When bison are born, their fur is orange-red. After a few months, their fur steadily grows more brown.',
    )

BLOBFISH_FACTS = (
    'The blobfish is a deep sea fish that lives off the coasts of mainland Australia and Tasmania.',
    'Blobfish are typically shorter than 30cm.',
    'Blobfish live at depths between 600 and 1200 meters, where the pressure is 60 to 120 times greater than at sea level.',
    'The flesh of the blobfish is primarily gelatinous mass with a density slightly less than water.',
    'In September 2013 the blobfish was voted "Ugliest Animal" and adopted as mascot of the Ugly Animal Preservation Society.',
    'The popular impression of the blobfish as bulbous & gelatinous is partially due to decompression damage done to it when brought to the surface from the depths which it lives; they look more like a normal bony fish when they are kept in their natural depths.',
    'The blobfish is listed as an endangered species.',
    )

BOBCAT_FACTS = (
    'An adult bobcat\'s tail averages just 6 to 7 inches in length.',
    'The word bobcat a reference to their tail. In barbershop lingo, hair that’s been cut short is sometimes called “bobbed.”',
    'Wild bobcats do the majority of their hunting in low-light conditions.',
    'Although adult bobcats only weigh 33 pounds, they can hunt and kill adult white tailed deer which can weigh 250 pounds.',
    'Bobcats lay claim to an area of land that can be anywhere from 1 to 18 square miles in size.',
    'Bobcats can’t always consume their victims in one sitting. Sometimes, they use dirt, snow, leaves, or grass to bury the uneaten pieces of especially large corpses, and will return periodically to dig up their leftovers.',
    'The scientfic name for the bobcat is "Lynx rufus".',
    'Wild bobcats have an average life span of 10 to 12 years',
    'The bobcat is believed to have evolved from the Eurasian lynx, which crossed into North America by way of the Bering Land Bridge as early as 2.6 million years ago',
    'The bobcat is crepuscular meaning it is active mostly during twilight (around dawn or dusk).',
    'Bobcats rarely attack people because they are scared of humans.',
    'In Native American mythology, the bobcat is often twinned with the figure of the coyote in a theme of duality.',
    'The historical range of the bobcat was from southern Canada, throughout the United States, and as far south as the Mexican state of Oaxaca, and it still persists across much of this area.',
    )

BUFFALO_FACTS = (
    'Buffalo are the largest animals found in North America and can grow to 6-7 feet long, weighing up to 2,000 lbs. True buffalo only live in Asia and Africa.',
    'Buffalo are large members of the Bovidae family. There are two types of buffalo: the African or Cape buffalo and the Asian water buffalo. They are dark gray or black animals that look a lot like bulls. They are often confused with bison',
    'The water buffalo is the largest bovine. It is 8 to 9 feet (2.4 to 2.7 meters) from head to rump with its tail adding an extra 2 to 3.3 feet (60 to 100 centimeters). They weigh a massive 1,500 to 2,650 lbs. (700 to 1,200 kilograms).',
    'The African buffalo is smaller, but they are still quite impressive in size. They are 4.26 to 4.92 feet long (130 to 150 cm) from head to hoof and weigh 935 to 1,910 lbs. (425 to 870 kg).',
    'Buffalo are herbivores, and so eat only vegetation. Their favorite foods are grass and herbs, but water buffalo will also eat aquatic plants. Both African and Asian buffalo will eat shrubs and trees when they can not find grass or herbs to eat.',
    'Buffalo are considered to be an adult when they reach 3 years old. Adults mate from July to October and it takes nine months for the calf to be born. When the calves are born they are a light tan color and are dependent on their mother for a least one year.',
    'Buffalo are social animals and live in groups called herds. Water buffalo herds are segregated by gender. African buffalo herds are mostly of mixed gender. An African herd often has more than 1,000 members.',
    'Male water buffalo have horns that curve backward. These horns can grow to 5 feet (1.5 meters) long. Females also have horns, but they are much smaller.',
    'African buffalo have a democracy. When they are ready to travel, they will stand and turn in the direction they want to go. The majority of "votes" wins and the head female will lead the herd in the winning direction.',
    'African buffalo are very aggressive and have a tendency to attack humans. They are very protective of each other and take care of sick and old members of the herd, shielding them from predators.',
    'Water buffalo have been domesticated for more than 5,000 years. They have buttressed humanity’s survival with their meat, horns, hides, milk, butterfat, and power, plowing and transporting people and crops.',
    'Wild water buffalo are at-risk and live only in a small number of protected areas stretching across India, Nepal, Bhutan, and a wildlife reserve in Thailand. Populations are likely to diminish as they are interbred with domesticated water buffalo.',
    )

BUTTERFLY_FACTS = (
    'There are over 17,500 recorded butterfly species in the whole world. Out of this number, 750 can be found in America.',
    'Butterflies belong to the Lepidoptera class of insects which are characterized by their large scaly wings.',
    'The Cabbage White species of butterfly is the most commonly found in the US. While they are called Cabbage White, they are characterized by their two black markings at the top of their wings.',
    'Butterflies can vary greatly in size. The biggest butterfly species has a 12 inch wingspan, while the smallest ever recorded only covers half an inch.',
    'Monarch butterflies are the only insect in the whole world that travels over 2,500 miles on average every winter.',
    'The North American Monarch is one species of butterfly that has been the most severely impacted by recent climate changes, with their numbers seeing dips and spikes over the last few years.',
    'A group of butterflies is known as a flutter.',
    'Butterflies don’t taste with taste buds, but rather sensors located under their feet.',
    'Contrarily to popular perception, the wings of butterflies are totally clear and the colors we see are the effect of light reflecting on the tiny scales covering them.',
    'Many adult butterflies do not excrete waste at all. As a matter of fact, many adult butterflies use everything they eat as energy.',
    )

CAMEL_FACTS = (
    'There are two species of true camel. The dromedary, is a single humped camel that lives in the Middle East and the Horn of Africa area. The bactrian, is a two-humped camel that lives in areas of Central Asia.',
    'There are four camel-like mammals that live in South America, llama and alpaca are called "New World camels", while guanaco and vicuna are called "South American camels".',
    'Camels have been domesticated by humans for thousands of years. Used mostly for transport or to carry heavy loads, they also provide a source of milk, meat, and hair/wool.',
    'Camels live on average 40 to 50 years.',
    'Camels are 1.85 m (6 ft 1 in) at shoulder level and 2.15 m (7 ft 1 in) at the hump.',
    'Camels are capable of running as fast as 65 km/h (40 mph) for a short period of time, and can maintain a speed of around 40 km/h (25 mph).',
    'Dromedary camels weigh 300 to 600 kg (660 to 1,320 lb) and bactrian camels weigh 300 to 1,000 kg (660 to 2,200 lb).',
    'Camels do not actually hold liquid water in their humps. The humps contain fatty tissue reserves, which can be converted to water or energy when required. They can survive up to six months without food or water by using up these fatty stores.',
    'Camels are well suited to the hot sandy deserts they roam in. Their thick coat insulates them from heat and also lightens during summer to help reflect heat.',
    'A camels long legs help its body to be high from the hot desert surface and a pad of thick tissue called a pedestal raises the body slightly when the camel sits so cool air can pass underneath.',
    'A large camel can drink around 30 gallons (113 liters) in just 13 minutes, making them able to rehydrate faster than any other mammal.',
    'Long eyelashes, ear hair, and closable nostrils keep sand from affecting the camel, while their wide feet help them move without sinking into sand.',
    'Camels have long been used in wartimes. Romans used camels for their ability to scare off horses who are afraid of their scent, and in recent times, camels have been used to carry heavy gear and troops across hot sandy deserts.',
    'There are estimated to be over 14 million camels in the world. Camels introduced to desert areas of Australia are the worlds largest populations of feral camels.',
    )

CAPYBARA_FACTS = (
    'The capybara is the largest living rodent in the world. Adults typically range from 3.48 to 4.4 feet long, stand 20 to 24 inches tall, and weigh between 77 and 146 pounds.',
    'Capybaras can be found in all South American countries but Chile. However, sightings are fairly common in Florida and one was seen on the Central Coast of California in 2011.',
    'Capybaras can both run as fast as horses and remain completely underwater for up to five minutes.',
    'The capybara appears on the 2-peso coin of Uruguay.',
    'Capybaras tend to live in groups. The size of these groups can range from 10 in the wet season and up to 100 capybaras in drier months.',
    'Capybaras are herbivores. In a typical day, they eat around 6-8 pounds of grass.',
    'The capybara is a semiaquatic mammal, and actually has slightly webbed feet to aid with swimming.',
    'Capybaras are autocoprophagous. This means that they eat their own feces, which helps them better digest grass and extract the most protein and nutrients from their food as possible.',
    'The gestation period for a capybara is typically 130-150 days. Most litters will have 3 or 4 young, but the number can range from 1 to as many as 8 young at once.',
    'Predators of the capybara include jaguars, pumas, ocelots, caimans, eagles, and anacondas.',
    'The name "capybara" is derived from the Tupi language, spoken by the native Tupi people of Brazil. The translated name means "one who eats slender leaves".',
    'Capybaras are very popular captive animals in Japan. One common practice, said to have originated in 1982 and attributed to the Izu Shaboten Zoo, is to keep hot springs in capybara enclosures for them to bathe and relax in during the winter.'
    'Capybaras are well to do to put their webbed feet to use in water, and the Vatican classifies them as fish in regards to dietary concerns.',
    )

CHAMELEON_FACTS = (
    'Chameleons are a very unique branch of the lizard group of reptiles.',
    'There are around 160 species of chameleon.',
    'Chameleons live in warm varied habitats from rainforests to deserts.',
    'Almost half of the world’s chameleon species are native to Madagascar.',
    'Special color pigment cells under the skin called chromatophores allow some chameleon species to change their skin color, creating combined patterns of pink, blue, red, orange, green, black, brown, yellow, and purple.',
    'Chameleon change color for camouflage but this is not always the main reason. Some show darker colors when angry, or when trying to scare others',
    'Male chameleons show light multi-colored patterns when vying for female attention.',
    'Chameleons living in the desert change to black when its cooler to absorb heat, then to a light grey to reflect heat.',
    'Chameleons have amazing eyes. The bulging upper and lower eyelids are joined and the pupil peaks out from a pinhole sized gap.',
    'The chameleons’ eyes can rotate and focus separately on 180-degree arcs, so they can see two different objects at the same time. This gives them a full 360-degree field of vision.',
    'Chameleons feed by ballistically projecting their tongues often over twice the length of their body to catch prey, forming a suction cup as it hits its target.',
    'Chameleons are not deaf but they do not actually have ear openings.',
    'Chameleons eat insects and birds.',
    'Chameleons are different from many reptiles because some of the species, like the Jackson’s chameleon, have live births. These species can give birth to eight to 30 young at one time',
    'According to International Union for Conservation of Nature’s Red List of Threatened Species, many species of chameleon are endangered.',
    )

CHEETAH_FACTS = (
    'The cheetah is the fastest land animal in the world. They can reach a top speed of around 113 km per hour.',
    'A cheetah can accelerate from 0 to 113 km in just a few seconds.',
    'Cheetahs are extremely fast however they tire quickly and can only keep up their top speed for a few minutes before they are too tired to continue.',
    'Cheetahs are smaller than other members of the big cat family, weighing only 45 – 60 kilograms.',
    'One way to always recognise a cheetah is by the long, black lines which run from the inside of each eye to the mouth. These are usually called “tear lines” and scientists believe they help protect the cheetah’s eyes from the harsh sun and help them to see long distances.',
    'Cheetahs are the only big cat that cannot roar. They can purr though and usually purr most loudly when they are grooming or sitting near other cheetahs.',
    'While lions and leopards usually do their hunting at night, cheetahs hunt for food during the day.',
    'A cheetah has amazing eyesight during the day and can spot prey from 5 km away.',
    'Cheetahs cannot climb trees and have poor night vision.',
    'With their light body weight and blunt claws, cheetahs are not well designed to protect themselves or their prey. When a larger or more aggressive animal approaches a cheetah in the wild, it will give up its catch to avoid a fight.',
    'Cheetahs only need to drink once every three to four days.',
    )

CHEVROTAIN_FACTS = (
   'The Chevrotain is an animal that looks like a tiny deer with fangs .',
   'They are also known as the mouse deer.',
   'These tiny animals are shy and mysterious, and not much is known about them.',
   'At first glance, these animals look like a weird mash-up of a deer, a mouse, and a pig.',
   'Depending on the species, a chevrotain can be anywhere from 4 to 33 pounds.',
   'The family has been separated into two genera: true chevrotains (Hyemoschus) and the mouse deer (Tragulus).',
   'They have an extra thick coat and robust muscles around the neck and rump, these adorable fighters are protected from bites during combat.',
   'Chevrotains are the most primitive of ruminants.',
   'The water chevrotain is known for its ability to dive underwater when it senses a predator nearby.',
   'Chevrotains are able to hold their breath for about four minutes.',
    )

CHICKEN_FACTS = (
    'Chickens have beaks, similar to ducks.',
    'Chickens lay eggs that you can consume; they go good with gammon,',
    'Chickens are sometimes kept as pets, although not normally thought of as domestic animals.',
    'Chickens can actually fly, contrary to popular belief',
    )

CHIMPANZEE_FACTS = (
    'Chimpanzees are omnivores which mean that they eat both plants and animals.',
    'Chimpanzee communities can range in size from 15 to 120 chimps of both sexes and all ages.',
    'Chimpanzees have a hierarchy, and generally each community has an alpha male who is considered the most powerful member of the group.',
    'Chimpanzees can communicate with each other even over long distances with loud calls called pant-hoots, or by drumming the buttresses of trees.',
    'Chimpanzees say hello to each other by panting.',
    'Chimpanzees indicate displeasure by grunting and flicking their wrists at the one who has offended them.',
    'Chimpanzees can be found in 21 African countries.',
    'Most chimpanzee mothers give birth to one young an average of every five to six years in the wild. Young chimps stay with their mothers for up to 10 years.',
    'Chimpanzees grow up to 1.2 meters tall.  Their arms grow longer than their legs, which helps them to walk along by clenching their fists and putting their weight on their knuckles.',
    'Chimpanzees are one of only two species in the genus Pan, the other being the bonobo, and both are found sub-Saharan Africa.',
    )

CHIPMUNK_FACTS = (
    'Chipmunks are the smallest members of the squirrel family. The smallest species can weigh 1.1 to 1.8 ounces and can reach 7.2 to 8.5 inches in length. The largest species can weigh up to 4.4 ounces and reach up to 11 inches in length.',
    'Chipmunks have fluffy tail that can reach 3 to 5 inches in length.',
    'Chipmunks are very vocal animals. They produce bird-like noises that can be heard in the case of near danger and during the mating season, when females wants to attract males.',
    'There are more than 20 different species of chipmunks, some of which can be found in North America and which belong to the Tamias genus, with two subgenus species called Tamias and Neotamias.',
    'The most endangered species of chipmunk is the Palmers genus.',
    'Chipmunks are very talkative creatures, and they boast a distinct and unique way of talking to each other, often making bird-like noises. They also use many different gestures as a way of communicating with one another which is highly amusing to watch.',
    'A single chipmunk can store up to 8lbs of food in a burrow.',
    'Chipmunks are known to be very territorial around their burrows and nests. Their territory can extend up to ½ an acre around the burrow, but an adult chipmunk will only usually defend up to 50 ft from the entrance of their burrow when they have to.',
    'Chipmunks have 4 toes on their back paws but 5 toes on their front ones!',
    'Male chipmunks are called Bucks and females are referred to as Does.',
    'Unlike other squirrels, chipmunks live mainly in underground burrows. They can be 30 feet long and 3 feet wide. All burrows are divided in several sections: nursery, food storing chamber, and resting area.',
    )

CHINCHILLA_FACTS = (
    'Chinchillas are nocturnal creatures who are mostly awake at night. They are typical asleep during the day. Therefore, it is best to place your Chinchilla cage in a quiet place away from direct sunlight.',
    'Chinchillas can overheat. No, not like a car, but a Chinchilla is very sensitive to heat and humidity. In their original home, the weather is cool and dry. They are best in temperatures of 15 degrees centigrade to 25 degrees centigrade.',
    'Chinchillas grow their teeth for life. Their teeth never stop growing and they can even grow as much as 12 inches per year.',
    'Chinchillas have the softest fur in all of land mammals. Their fur is so soft and luxurious that the first reason why Chinchillas were hunted by the native tribes who lived in The Andes Mountains is not for their meat, but for their fur.',
    'Chinchillas take dust baths. Yes, they do not take water or wet baths. Their fur is so dense and will have a problem completely drying out. It is why they take dust baths instead to help get rid of oils and dirt. It is like a Chinchilla using a dry shampoo.',
    'Chinchillas use their tail for balance and are high jumpers and prolific climbers! In the wild, they lived in rocky and mountainous areas, so they are able to jump from high places (about 6 feet).'
    'Chinchillas are very compassionate animals. If another female cannot produce milk, another female can adopt the babies.',
    'The breeding season for chinchillas runs from November to May in the Northern Hemisphere and from May to November in the Southern Hemisphere.',
    'Chinchillas are omnivores; they eat both plants and meat. Primarily, they eat grass and seeds, but they also eat insects and bird eggs when they get the chance. To eat, they hold their food in their front paws and nibble on it.',
    'Though chinchilla fur is highly valued for use in clothing and coats, the Convention on International Trade in Endangered Species has restricted the sale and trade of wild chinchillas since 1975. Many chinchillas are bred commercially for their fur.',
    'Chinchillas are native to Chile and Peru. In the wild they live in groups and make their home in burrows and natural outcroppings and crevices.',
    )

CLOWNFISH_FACTS = (
    'Clownfish is a fish that is frequently called clown anemonefish and goes by the scientific name Amphiprioninae, is actually false anemonefish.'
    'The length of clownfish can range from 3.1 inches to 6.3 inches with an average of 4.3 inches.',
    'There are at least 30 known species of clownfish, most of which live in the shallow waters of the Indian Ocean, the Red Sea, and the western Pacific.',
    'The movie Finding Nemo caused home-acquarium demand for clownflish to triple.',
    'Clownfish use stinging anemones for their own protection and in return drives off intruders and preens its host by removing parasites.',
    'All clownfish are born male and have the ability to switch their sex. If once they become female, the change is irreversible.',
    'Clownfish rarely stray more than a few yards from their host anemone.',
    )

COBRA_FACTS = (
    'Cobras are classified in the phylum Chordata, subphylum Vertebrata, class Reptilia, order Squamata and family Elapidae.',
    'Genetically, true cobras are members of the genus Naja, but according to Viernum, often the name cobra references several species of snakes, most of which are in the venomous snake family Elapidae.',
    'Cobras are large snakes and many species reach more than 6 feet long (2 meters).',
    'The most well-known distinctive physical characteristic of cobras is their hood.',
    'There are 270 different types of Cobras and their relatives, including Taipans, Adders, Mambas, and Kraits, and they all have short fangs and are all extremely poisonous.',
    'Cobras live in hot tropical areas in Africa, Australia, and Southern Asia and their relatives, the Coral Snake, can be found in the United States.',
    'Cobras are cannibals, which means that they will eat other snakes as well as birds, bird eggs, and small mammals. Kraits feed almost totally on other snakes.',
    'Despite that common name, king cobras are not classified as true cobras, which belong to the genus "Naja".',
    'Cobras have potent neurotoxic venom, which acts on the nervous system.',
    'Some cobras, including all spitting cobras, have cytotoxic venom that attacks body tissue and causes severe pain, swelling and possible necrosis (death of cells and tissue).',
    'The origin of the genus name of Cobras, "Naja" is from the Sanskrit "nāga" (with a hard "g") meaning "snake".',
    'Naja is a genus of venomous elapid snakes known as cobras.',
    'Spitting cobras have a specialized venom delivery mechanism, in which their front fangs, instead of releasing venom through the tips, have a rifled opening in the front surface which allows the snake to propel the venom out of the mouth.',
    'The Caspian cobra (N. oxiana) of Central Asia is the most venomous Naja species.',
    'Cobras are a medically important group of snakes due to the number of bites and fatalities they cause across their geographical range.',
    'Cobras belong to the family Elapidae, a type of poisonous snake with hollow fangs fixed to the top jaw at the front of the mouth.',
    )

CONURE_FACTS = (
    'A conure is a medium size parrot and is sometimes called the "little Macaw" due to their bright vibrant colors.'
    'Conures are very playful birds and will live up to 30 years.'
    'The Sun conure is the most colorful of all conures with mostly gold tones. The Nanday conure is mostly green.'
    'Conures are native to South America but are considered endangered.'
    'A conure has a few distinct sounds and are very loud. Their call can be carried for miles.'
    'Some conures are able to learn words and some will mimic sounds like a whistle or doorbell while others will only squawk.'
    'Conures are often called the clowns of the parrot world due to their constant attention seeking behavior including hanging upside-down and swaying back and forth or "dancing".'
    'Despite being large for parakeets, conures are lightly built with long tails and small (but strong) beaks.'
    'Conures originate from the Western Hemisphere, namely Central and South America.'
)   

COUGAR_FACTS = (
    'The cougar, also known as puma, mountain lion, mountain cat, catamount or panther, depending on the region, holds the Guinness record for the animal with the highest number of names. It has over 40 names in English alone.',
    'The cougar has the greatest range of any large wild terrestrial mammal in the Western Hemisphere, extending from the Yukon in Canada to the southern Andes of South America.',
    'Cougars primary food sources include ungulates such as deer, elk, moose, and bighorn sheep, as well as domestic cattle, horses, and sheep, particularly in the northern part of its range. It will also hunt species as small as insects and rodents.',
    'Adult cougars stand about 60 to 76 centimeters (2.0 to 2.5 ft) tall at the shoulders. The length of adult males is around 2.4 meters (8 ft) long nose to tail, with overall ranges between 1.5 and 2.75 m (5 and 9 ft) nose to tail suggested for the species in general. Males typically weigh 53 to 90 kilograms (115 to 198 pounds), averaging 62 kg (137 lb). Females typically weigh between 29 and 64 kg (64 and 141 lb), averaging 42 kg (93 lb).',
    'Cougar size is smallest close to the equator and larger towards the poles.',
    'Female cougars reach sexual maturity between one-and-a-half to three years of age. They typically average one litter every two to three years throughout their reproductive life. Only females are involved in parenting and they are fiercely protective of their cubs.',
    'Aside from humans, no species preys upon mature cougars in the wild. The cat is not, however, the apex predator throughout much of its range. In its northern range, the cougar interacts with other powerful predators such as the brown bear and gray wolf. In the south, the cougar must compete with the larger jaguar. In Florida it encounters the American Alligator.',
    'Like almost all cats, the cougar is a solitary animal. Only mothers and kittens live in groups, with adults meeting only to mate. It is secretive and typically most active around dawn and dusk.',
    'Cougars have large paws and proportionally the largest hind legs in the cat family. This physique allows its great leaping and short-sprint ability. An exceptional vertical leap of 5.4 m (18 ft) is reported for the cougar. Horizontal jumping capability from standing position is suggested anywhere from 6 to 12 m (20 to 40 ft).',
    'The cougar can run as fast as 55 to 72 km/h (35 to 45 mi/h), but is best adapted for short, powerful sprints rather than long chases.',
    )

COW_FACTS = (
    'There are well over 1 billion cattle in the world.',
    'Cattle are sacred in India. There are an estimated 300 million cattle in India.',
    'Young cattle are generally known as calves. Adult females are generally called cows. Adult males that are not castrated are generally called bulls.',
    'Cattle are red/green color blind.',
    'In the sometimes controversial sport of bull fighting, bulls are angered by the movement of the cape rather than its red color.',
    'Cattle trained to be draft animals are known as oxen (ox).',
    'Cows are social animals, and they naturally form large herds. Like people, they will make friends and bond to some herd members, while avoiding others',
    'Cows can hear lower and higher frequencies better than humans.',
    'An average dairy cow weighs about 1,200 pounds.',
    'A cows normal body temperature is 101.5°F.',
    'The average cow chews at least 50 times per minute.',
    'The typical cow stands up and sits down about 14 times a day.',
    'An average cow has more than 40,000 jaw movements in a day.',
    'Cows actually do not bite grass; instead they curl their tongue around it.',
    'Cows have almost total 360-degree panoramic vision.',
    'Cows have a single stomach, but four different digestive compartments.',
    'Cows are pregnant for 9 months just like people',
    'A dairy cow can produce 125 lbs. of saliva a day',
    'If you took all the cows in the world and rounded them up into a sphere, that sphere would be nearly 1,200 meters wide!',
    'Cows are very social animals, and many of them have best friends! When separated, they often search for friends and family even years later.'
    'Cows are considered sacred for Hindus in India.',
    )

COYOTE_FACTS = (
    'Coyotes are members of the Canidae family and share a lot of the same traits of their relatives: wolves, dogs, foxes and jackals.',
    'Coyotes have narrow, elongated snouts, lean bodies, yellow eyes, bushy tails and thick fur.',
    'Coyotes hunt at night and howl to communicate their location. They are also known for being "wily", in fact, they are very smart creatures and have a heightened sense of hearing, smell and sight.',
    'Coyotes fur may be gray, white, tan or brown, depending on where they live.',
    'Coyotes that live in the mountains have darker coats and ones that live in the desert have lighter coats.',
    'Coyotes live in North America and roam the plains, forests, mountains and deserts of Canada, the United States, Mexico and Central America. Some even live in tropical climates.',
    'Coyotes are solitary creatures and mark their territory with urine. When hunting deer, however, they use teamwork and form packs. They take turns pursuing the deer until it tires',
    'Coyotes are not picky eaters. They eat small game such as rodents, rabbits, fish and frogs, and larger game like deer. Their diet is 90 percent mammalian',
    'They are typically thought to be only meat eaters, but they are actually omnivores — they eat meat and vegetation.',
    'Coyotes have been known to kill livestock and pets, but they usually help control agricultural pests, such as rodents. In cities, coyotes will eat pet food or garbage.',
    'Both the male and female participate in taking care of the pups. The male will bring food to the female and the pups and help protect them from predators.',
    'Coyotes are not endangered. In fact, some believe that the coyote population has never been higher. Farmers and ranchers have tried controlling the population with poisons, guns and traps, but the populations are still growing, according to the International Union for Conservation of Nature (IUCN).',
    )
CRAB_FACTS = (
    'Crabs are decapods from the crustacean family.',
    'Crabs have 10 legs, however, the first pair are its claws which are called chelae.',
    'Crabs have a thick external skeleton called an exoskeleton. It is a shell made of calcium carbonate and provides protection for the soft tissue underneath.',
    'Crabs live in all the world\'s oceans, in fresh water, and on land. There are over 4500 species of crabs.',
    'Other animals with similar crab names such as hermit crabs, king crabs, porcelain crabs, horseshoe crabs, and crab lice, are not true crabs.',
    'Crabs usually have a distinct sideways walk. However, some crabs can walk forwards or backwards, and some are capable of swimming.',
    'The collective name for a group of crabs is a "cast".',
    'Crabs communicate with each other by drumming or waving their pincers.',
    'Male crabs tend to often fight with each other over females or hiding holes.',
    'The Pea Crab is the smallest known species at just a few millimetres wide. The largest species is the Japanese Spider Crab, with a leg span of up to 4 m (13 ft).',
    'Crabs are omnivores, they feed mainly on algae, but also bacteria, other crustaceans, molluscs, worms, and fungi.',
    'Some crab species can naturally autotomise (shed) limbs such as their claws, which then regenerate after about a year.',
    'Crabs make up 20 percent of all marine crustaceans caught by humans each year. This adds up to a total of 1.5 million tons annually',
    'The most consumed species of crab in the world is the Japanese Blue Crab.',
    )

CRANE_FACTS = (
    'Cranes live on all continents except Antarctica and South America.',
    'Cranes eat a range of items from small rodents, fish, amphibians, and insects to grain, berries, and plants.',
    'Cranes create their nests in shallow water.',
    'Cranes are known as perennially monogamous breeders, establishing long-term pair bonds that may last the lifetime of the bird.',
    'Male cranes and female cranes do not vary in external appearance, however, on average males tend to be slightly larger than females.',
    'The tallest flying bird in the world is the Sarus Crane.',
    'Cranes range from sizes of 90 cm (35 in) in length to 176 cm (69 in).',
    'Most species of crane are dependent on wetlands and require large areas of open space.',
    'The only two species of crane that do not always roost in wetlands are the two African crowned cranes, which are the only cranes to roost in trees.',
    'Female cranes typically lay two eggs, and the eggs will hatch after a period of around 30 days.',
    )

CRAYFISH_FACTS = (
    'The name "crayfish" comes from the Old French word escrevisse.',
    'The oldest records of crayfish are 115 million years old.',
    'There are 200 species of crayfish in North America.',
    'Crayfish like to eat hot dogs and cat food.',
    'Crayfish can range in colors such as sandy yellow, pink, red, dark brown, and even blue.',
    'Crayfish live on every continent except for Africa and Antarctica.',
    'Very small crayfish are called dwarf crayfish.',
    )

CROCODILE_FACTS = (
    'There are 23 different species of crocodiles that live on this planet.',
    'Crocodiles do not chew their food! Instead, they swallow stones to grind their food inside their stomachs.',
    'Crocodiles with open mouths is not necessarily a sign of aggression. Instead, that is their only way cooling off.',
    'Crocodiles do not possess any sweat glands.',
    'The muscles responsible for opening a crocodile\'s jaws are weak, such that even humans can keep a crocdile\'s mouth closed.',
    'However, opening their mouth when it is closed is almost impossible',
    'After mating, a female crocodile can lay between 20 to 80 eggs.',
    'Crocodiles can have a lifespan of up to 80 years.',
    'The skin on the back of the crocodile is so hard and tough, not even a bullet can pierce it.',
    'The closest relatives of the crocodile in the animal kingdom are rather disparate: Birds and Dinosaurs.',
    'Crocodiles normally drown their prey by dragging them underwater before cutting their meat into smaller chunks.',
    'Crocodiles can shoot out from the water at almost 12 meters per second!',
    'The smallest crocodile is the dwarf crocodile. It grows to about 5.6 feet (1.7 meters) in length and weighs 13 to 15 pounds (6 to 7 kilograms). The largest crocodile is the saltwater crocodile. The largest one ever found was 20.24 feet (6.17 m) long. They can weigh up to 2,000 pounds (907 kg).',
    'Crocodiles lay 10 to 60 eggs at a time. The hatchlings stay in their eggs for 55 to 110 days. They are 7 to 10 inches (17.8 to 25.4 centimeters) long when they are born and don\'t mature until they are 4 to 15 years.',
    )

CUTTLEFISH_FACTS = (
    'Cuttlefish are cephalopods, not fish. Cephalopods include octopus, squid, and nautilus.',
    'Cuttlefish, along with most cephalopods, are the ocean’s most intelligent invertebrates.',
    'Cuttlebone, found in the body of a cuttlefish, is used by pet birds to get calcium.',
    'Cuttlefish have green-blue blood and 3 hearts!',
    'A cuttlefish’s camouflage is so good that it can take on a checkerboard pattern placed beneath it.',
    'Cuttlefish are color blind.',
    'Cuttlefish taste with their suckers.',
    'Cuttlefish have 8 arms and 2 long tentacles used for feeding.',
    'The largest cuttlefish is the Australian giant cuttlefish, which is the size and shape of an American football.',
    'Cuttlefish have W shaped eyelids so they can see in front and behind themselves at the same time.',
    'Interestingly enough, cuttlefish are known for their sexual dimorphism, particularly in regards to the size differences between adult males and females.',
    )

DEER_FACTS = (
    'Deer belong to the cervidae family.',
    'Deer constitute the second most diverse family after bovids.',
    'All male deer, except the Chinese water deer, possess antlers.',
    'Deer species range from very large to very small. The smallest deer is the Southern pudu and the largest deer is the moose.',
    'Deer can be found in many different ecosystems.',
    'The Chinese water deer does not have any antlers. Instead, it has very long canine teeth used to attract mates with.',
    'Deer feed primaraly on leaves.',
    'Deer were an important source for food for early hominids.',
    'Deer are regularly culled in Britain to help maintain the population; they are a preyed upon species so if their population grows too big the food source becomes scarce.',
    'The only known female deer that possess antlers is the reindeer.',
    'The male deer is called a buck but some larger males are referred to as stags. A female deer is called a doe or a hind.',
    'During the mating season, the male deer use their antlers to fight other males over does.',
    'Each year, deer antlers fall off and regrow. As they regrow they are covered in a furry coat called velvet.',
    'Deer can jump up to 3 meters (10 feet).',
    'Deer have extraordinary smelling abilities. They can smell food from large distances and they use this ability to communicate with each other and to detect the position of other group mates.',
    )

DEGU_FACTS = (
    'The word degu comes from the Mapudungun dewü (mouse, rat).',
    'Degus have an elaborate vocal repertoire comprising up to 15 unique sounds.',
    'Degus can live as long as 8 or 9 years although 5 to 6 years is the average lifespan.',
    'The degu is a South American caviomorph which inhabits the semi-arid (desert-like) scrub areas of central Chile. This is the only place in the world where degus can be found in the wild and is where degus originated.',
    'Degus are prone to diabetes due to their divergent insulin structure. For this reason, they are used frequently for research in this field.',
    'Unlike other octodontids, degus are diurnal (activity during the day, with a period of sleeping, or other inactivity, at night), and they have good vision.',
    'In case of predator\'s attack, the degu can shed its tail from its body. A shed tail will never grow back.',
    'To clean themselves, Degus take sand baths to keep their coat healthy and free of grease.',
    )

DINGO_FACTS = (
    'Dingoes actually originate from Southeast Asia, where they can still be found today.',
    'Dingoes mate once per year, from March to June.',
    'Dingoes cannot bark, but they can howl.',
    'Dingoes have permanently erect ears.',
    'Dingoes arrived in Australia from the Asian mainland about 5,000 years ago.',
    'Dingoes live to five or six years of age in the wild and fifteen years in captivity.',
    'Dingoes are considered pests in Australia',
    'The largest fence in the world was built to keep out Dingoes in Australia',
    'Just like humans, dingoes have rotating wrists. This allows them to use their paws like hands to catch prey. It also helps them better climb trees and even open doors.',
    'Dingoes can even swivel their heads about 180 degrees. Comparatively, owls can turn their heads 270 degrees; humans can only turn theirs 45 to 70 degrees.',
    'Having a dingo as a pet is a full time responsibility, as dingoes don\'t handle rejection well and will likely not emotionally recover from being placed in a new home.',
    )

DODO_FACTS = (
    'Dodos had an unusual diet involving stones. Dodo birds’ diet included seeds, nuts, bulbs, roots, and fallen fruit. In addition, they would also feed on palm fruit, shell fish, and crabs. This is a very similar diet to the modern crowned pigeon. Dodo birds used gizzard stones to aid their digestion.',
    'One of the more interesting dodo bird facts is that these birds lived in almost complete isolation. Scientists discovered that the dodo only ever lived on the island of Mauritius in the Indian Ocean. They were so isolated that their population didn’t even spread to the neighboring islands off the eastern coast of Africa. The simple reason for this is that the dodo was flightless and was therefore unable to reach any other island or land mass.',
    'One of the more intriguing dodo bird facts involves just how they became extinct. They lived on the island of Mauritius where there was an abundance of food and almost no predators. What, then, caused their extinction? In a word: people. Dodos were unfortunately not frightened of people, which made them very easy prey for human hunters. Sailors who arrived on the island of Mauritius from the year 1598 started hunting dodos, and initiated mass killings, to the point where these birds were extinct by 1681. Although people believed the dodo to be stupid because it readily approached men who were armed with clubs, these birds had no natural enemies and so had no experience with predators. They were simply curious, not stupid.',
    'In addition to being killed by people, the dodo was also affected by exposure to new animals. The sailors who arrived on Mauritius introduced new species to the island. They brought with them their domesticated animals, which preyed on the dodos, ate their eggs, and destroyed their natural habitat, leading to their extinction. These animals included dogs, pigs, cats, and rats. Due to their isolation, the dodo birds simply had no natural defenses and became extinct only 175 years after they were discovered.',
    'Unlike most other birds that build their nests in trees, dodos used to build their nests on the ground. This was largely because they couldn’t fly, and their nests didn’t need to be protected in trees because the dodo had no natural predators on Mauritius.',
    'There are many mysteries surrounding various dodo bird facts, including the fact that they were flightless birds. However, scientists believe that they do now have some of the answers. One of the reasons that the dodo became flightless was probably because there were virtually no potential predators in its natural habitat on the island of Mauritius. In addition, there was an abundance of food for these birds, so they really had no reason to fly. This is what is known as secondary flightlessness. The adaptation for flight is only maintained when it is absolutely necessary, because it requires such a great expenditure of energy for a bird. This was simply not required in the Mauritian environment, and so the adaptation was lost.',
    'Don’t let the rather strange appearance of the dodo fool you. One of the more bizarre dodo bird facts is that these birds could actually run quite fast. Although there is a lack of scientific evidence from the time when dodos were alive, modern scientists have managed to deduce this fact based on the dodo bird’s skeletal structure and the size of its legs.',
    'The dodo was alive before the invention of the camera so for a long time, it was hard for us to know exactly what this bird looked like. To complicate matters, very few skeletal remains were found. Therefore, for centuries our understanding of the appearance of dodos was based on anecdotal evidence and amateur sketches. It was only in 2007 that a complete skeleton of a dodo bird was found, which could confirm many of the dodo bird facts. However, exact facts about the dodo’s plumage, girth and coloring are still in question.',
    'Although there is some anecdotal evidence and a few skeletons to furnish us with many dodo bird facts, there are some things that have never been reported. There is no information whatsoever about the dodo’s mating habits, behaviors, or life expectancy. In that regard, the life cycle of a dodo seems deemed to remain an intriguing mystery forever.',
    'Scientists and the general population during the Victorian era were intrigued by newly emerging dodo bird facts. Lewis Carroll, the famous author, included these quirky birds in his children’s classic Alice in Wonderland. Contrary to popular characterizations, the dodos in this book are depicted as being quite solemn and wise.',
    'The fact that the dodo bird is immortalized in the saying "As dead as a dodo" is a telling dodo bird fact that is relevant to all environmentalists today. The saying refers to all traces of something being completed wiped out, just as the dodo was on the island of Mauritius. This bird has come to represent conservationism and movements against eco-terrorism. The utter destruction of this interesting creature was entirely due to the direct and indirect causes introduced by people, who then failed to intervene and preserve this unique species.',
    'If you are lucky enough to visit the island of Mauritius, you will see dodos everywhere. Not live ones, of course, but replicas and images wherever you look. A little-known dodo bird fact is the extent to which these birds are present in Mauritius’ tourism industry. The image of the dodo has been transformed into just about every possible version that could pass as a tempting curio for the tourists visiting this island paradise. So, in addition to sugar and rum, the dodo is a significant contributor to the Mauritian tourism economy.',
    'Subfossil remains show the dodo was about 1 metre (3 ft 3 in) tall and may have weighed 10.6–17.5 kg (23–39 lb) in the wild. The dodo\'s appearance in life is evidenced only by drawings, paintings, and written accounts from the 17th century.',
    'Dodos did not have any natural predators.',
    )

DOLPHIN_FACTS = (
    'Known for their playful behavior, dolphins are highly intelligent. They are as smart as apes, and the evolution of their larger brains is surprisingly similar to humans.',
    'Compared to other animals, dolphins are believed to be very intelligent.',
    'The Killer Whale (also known as Orca) is actually a type of dolphin.',
    'Bottlenose dolphins are the most common and well known type of dolphin.',
    'Female dolphins are called cows, males are called bulls, and young dolphins are called calves.',
    'Dolphins live in schools or pods of up to 12 individuals.',
    'Dolphins often display a playful attitude which makes them popular in human culture. They can be seen jumping out of the water, riding waves, play fighting, and occasionally interacting with humans swimming in the water.',
    'Dolphins use a blowhole on top of their heads to breathe.',
    'Dolphins have excellent eyesight and hearing as well as the ability to use echolocation for finding the exact location of objects.',
    'Dolphins communicate with each other by clicking, whistling and other sounds.',
    'Some dolphin species face the threat of extinction, often directly as a result of human behavior. The Yangtze River Dolphin is an example of a dolphin species which may have recently become extinct.',
    'Some fishing methods, such as the use of nets, kill a large number of dolphins every year.',
    'Dolphins can be also found that are colored Pink.',
    )

DRAGON_FACTS = (
    'The word “dragon” comes from the Greek word “draconta”, which means “to watch.” The Greeks saw dragons as beasts that guarded valuable items. In fact, many cultures depict dragons as hoarding treasure.',
    'Ancient Greeks and Sumerians spoke of giant “flying serpents” in their scrolls and lectures. Dragons are depicted as snake- or reptile-like.',
    'The Komodo dragon is a type of monitor lizard, which is aggressive and deadly. They can be 10 feet long and use toxic bacteria in their mouths to wound their prey.',
    'In medieval times, dragons were considered very real, but demonic. Religions had widely different views of dragons: some loved them and some feared them.',
    'In many cultural stories, dragons exhibit features of other animals, like the head of elephants, claws of lions, and beaks of predatory birds. Their body colors are widely different – red, blue, green, gold, but usually earth tones. In some cultures, the colors have specific meanings.',
    '“Dragon” is actually a family term that includes other mythological creatures, such as cockatrices, gargoyles, wyverns, phoenix, basilisks, hydras, and even some hybrid man-dragon creatures.',
    'The dragon was traditionally used by the Emperor of China as a symbol of his imperial power and strength, and was more generally a symbol of strength, power, and good luck.',
    'Due to its importance as a traditional mythological creature, the Han Chinese commonly referred to themselves as the Descendents of the Dragon. ("long de chuan ren").',
    'Of the twelve animals representing the Chinese zodiac, the Dragon is the most popular year for childbirth; more children are born during the years of the Dragon than any other year.',
    'In ancient Chinese folklore, a school of golden koi fish spent a hundred years trying to swim upstream to the top of a waterfall. One koi finally reached the top, and the gods recognized it for its perseverence and determination by turning it into a golden dragon, the image of power and strength.',
    )

DUGONG_FACTS = (
    'The dugong is one of four living species of the order Sirenia, which also includes three species of manatees.',
    'The largest dugong populations occur in wide, shallow, protected areas like bays, mangrove channels, and waters of inshore islands.',
    'The dugong differs from the manatee by having a fluked, dolphin-like tail and a downturned snout.',
    'Dugongs are vulernable to extinction because they have been hunted for thousands of years for meat and oil.',
    'Dugongs can be found near East Africa, South Asia, and Australia.',
    'Dugongs are herbivores and can typically be found hanging out near seagrass meadows.',
    'Dugongs can weigh anywhere between 500 and 1100 pounds.',
    'The average dugong is nearly 10 feet in length.',
    'It is thought that the legends of mermaids may have originated from sailors seeing the fluked tails of dugongs from a distance.',
    'Dugongs can often live for upwards of 70 years.',
    'Dugongs can stay underwater for 6 minutes before surfacing.',
    )

EAGLE_FACTS = (
    'Eagles build their nests on high cliffs or in tall trees.',
    'There are over 60 different species of eagle.',
    'Eagles feature prominently on the coat of arms of a large number of countries, such as Germany, Mexico, Egypt, Poland, and Austria.',
    'Golden eagles have been known to hunt foxes, wild cats and even young deer and goats.',
    'Female golden eagles usually lay between one and four eggs each breeding season.',
    'The Great Seal of the United States features a bald eagle. The bald eagle is the national bird of the United States.',
    'Female bald eagles are larger than male bald eagles.',
    'Bald eagles eat mostly fish, swooping down to the water and catching them with their powerful talons.',
    'Bald eagles live for around 20 years in the wild.',
    'Bald eagles build very large nests, sometimes weighing as much as a ton!',
    'The bald eagle was added to the list of endangered species in the United States in 1967 and its numbers have recovered well since.',
    'Eagles have amazing eyesight and can detect prey up to two miles away.',
    )

EARTHWORM_FACTS = (
    'Earthworms breathe through their skin.',
    'Each earthworm is both male and female, producing both eggs and sperm.',
    'The earthworm\'s digestive system is a tube running straight from the mouth, located at the tip of the front end of the body, to the rear of the body, where digested material is passed to the outside.',
    'There are approximately 2,700 different kinds of earthworms.',
    'In one acre of land, there can be more than a million earthworms.',
    'The largest earthworm ever found was in South Africa and measured 22 feet from its nose to the tip of its tail.',
    'If an earthworm’s skin dries out, it will die.',
    'Even though earthworms don’t have eyes, they can sense light, especially at their anterior. They move away from light and will become paralyzed if exposed to light for too long (approximately one hour).',
    'Earthworms secrete a fluid that helps them to crawl and dig better through dirt, all while keeping their skin moist. ',
    'Most earthworms will live between 1 and 2 years. However, they can live as long as up to 8 years. ',
    'Earthworm tunnels also help to hold soils in place and stop erosion through water.',
    'Each adult earthworm can produce up to 80 eggs each year.',
    'In only 90 days, the total number of earthworms in a given area can double.',
    'We are 75% water. Earthworms are 90% water.',
    'Earthworms\' bodies are made up of ringlike segments called annuli.',
    'Earthworms\' bodies are covered in setae, or small bristles, which the worm uses to move and burrow.',
    'Earthworms have a central and peripheral nervous system.',
    'Water, as well as salts, can also be moved through the skin of an earthworm by active transport.',
    'Earthworms have the ability to regenerate lost segments, but this ability varies between species and depends on the extent of the damage.',
    )

EARWIG_FACTS = (
    'There are nearly 2,000 different species of earwig.',
    'Although earwigs are able to fly, they often don\'t.',
    'Earwigs are nocturnal.',
    'The earwig is thought to get its name from people fearing that earwigs crawled into your ear to lay their eggs.',
    'Earwigs are omnivores.',
    'Female earwigs lay up to 80 small eggs which hatch within a couple of weeks.',
    'Earwigs moult 5 times over the course of their lifetime',
    'The earwig has a small body size, that is split into three parts',
    'The earwig has sharp pincers on its abdomen and large wings that generally remain concealed against the body of the earwig.',
    'Earwigs often hide in small, moist crevices during the day',
    'Amphibians such as frogs, newts and toads are among the most common predators of the earwig along with birds and other larger insects such as beetles.',
    )

ECHIDNA_FACTS = (
    'Male echidnas have a bizarre 4-headed penis.',
    'Echidnas are covered with fur and spiky spines. These spines are modified hairs, similar to that of the porcupines. There are tiny muscle bundles connected to the base of each spine so the echidna can control the spine\'s movement and direction.',
    'A mother echidna lays a single leathery egg in her pouch, then carries it for about ten days before it hatches. The baby echidna, called a puggle, is born hairless and spineless - but with formidable claws.',
    'Female echidnas produce milk, but they have no nipples. Instead, they secrete milk in two small, hairy areas known as aerola patches, which are connected to the milk glands. A baby echidna suckles milk straight out of its mom\'s skin.',
    'Echidna is Named After the Greek "Mother of Monsters".',
    'Echidnas are weird - they have a mish-mash of reptilian and mammalian features, which was recognized early on by biologists. In 1802, British anatomist Everard Home, named the curious animal after the Greek goddess Ekhidna (meaning \'she viper\') who was half-snake and half-woman.',
    'Echidnas are egg-laying mammals. Along with the platypus, the echidna is a member of the monotremes, an order of egg-laying mammals found in Australia.',
    'At the end of their slender snouts, echidnas have tiny mouths and toothless jaws. They use their long, sticky tongues to feed on ants, termites, worms, and insect larvae.',
    'The echidna has a very large brain for its body size. Part of this might be due to their enlarged neocortex, which makes up half of the echidna\'s brain (compare this to about 30 percent in most other mammals and 80 percent in humans).',
    )

ELAND_FACTS = (
    'The common eland (Taurotragus oryx), also known as the southern eland or eland antelope, is a savannah and plains antelope found in East and Southern Africa.',
    'Common elands form herds of up to 500 animals, but are not territorial.',
    'The common eland is used by humans for leather, meat, and rich, nutritious milk, and has been domesticated in many areas.',
    'While the common eland\'s population is decreasing, it is classified as \'Least Concern\' by the International Union for Conservation of Nature (IUCN).',
    'Mainly a herbivore, the eland\'s diet is primarily grasses and leaves.',
    'The name \'eland\' is Dutch for \'elk\' or \'moose\'.',
    'Eland herds are accompanied by a loud clicking sound that has been subject to considerable speculation. It is believed that the weight of the animal causes the two halves of its hooves to splay apart, and the clicking is the result of the hoof snapping together when the animal raises its leg.',
    'Common elands are nomadic and crepuscular. They eat in the morning and evening, rest in shade when hot and remain in sunlight when cold.',
    )

ELEPHANT_FACTS = (
    'There are two types of elephant, the Asian elephant and the African elephant (although sometimes the African Elephant is split into two species, the African Forest Elephant and the African Bush Elephant).',
    'Elephants are the largest land-living mammal in the world.',
    'Both female and male African elephants have tusks but only the male Asian elephants have tusks. They use their tusks for digging and finding food.',
    'Female elephants are called cows. They start to have calves when they are about 12 years old and they are pregnant for 22 months.',
    'An elephant can use its tusks to dig for ground water. An adult elephant needs to drink around 210 litres of water a day.',
    'Elephants have large, thin ears. Their ears are made up of a complex network of blood vessels which help regulate their temperature. Blood is circulated through their ears to cool them down in hot climates.',
    'Elephants have no natural predators. However, lions will sometimes prey on young or weak elephants in the wild. The main risk to elephants is from humans through poaching and changes to their habitat.',
    'The elephant’s trunk is able to sense the size, shape and temperature of an object. An elephant uses its trunk to lift food and suck up water then pour it into its mouth.',
    'An elephant’s trunk can grow to be about 2 meters long and can weigh up to 140 kg. Some scientists believe that an elephant’s trunk is made up of 100,000 muscles, but no bones.',
    'Female elephants spend their entire lives living in large groups called herds. Male elephant leave their herds at about 13 years old and live fairly solitary lives from this point.',
    'Elephants can swim – they use their trunk to breathe like a snorkel in deep water.',
    'Elephants are herbivores and can spend up to 16 hours days collecting leaves, twigs, bamboo, and roots.',
    )

ELEPHANT_SHREW_FACTS = (
    'Elephant shrews, or jumping shrews, are small insectivorous mammals native to Africa, belonging to the family Macroscelididae, in the order Macroscelidea, (there are 19 species of elephant shrew, placed in four genera) whose traditional common English name comes from resemblance between their long noses and the trunk of an elephant, and an assumed relationship with the shrews.',
    'Elephant shrews are widely distributed across the southern part of Africa, and although common nowhere, can be found in almost any type of habitat, from the Namib Desert to boulder-strewn outcrops in South Africa to thick forest.',
    'Elephant shrew is classified as endangered largely due to a fragmented forest environment and anthropogenic factors.',
    'Despite their weight of under half a kilogram, elephant shrews have been recorded to reach speeds of 28.8 km/h, making it one of the fastest small mammals.',
    'Elephant shrews are small, quadrupedal, insectivorous mammals resembling rodents or opossums, with scaly tails, elongated snouts, and rather long legs for their size, which are used to move in a hopping fashion like rabbits.',
    'Elephant shrews vary in size from about 10 cm to almost 30 cm, from just under 50 g to over 500 g.',
    'The short-eared elephant shrew has an average size of 150 mm (5.9 in).',
    'Elephant shrew lifespans are about two and a half to four years in the wild.',
    'Elephant shrew have large canine teeth, and also high-crowned cheek teeth similar to those of ungulates.',
    'Elephant shrew are diurnal and very active.',
    'Elephant shrew are not highly social animals, but many live in monogamous pairs.',
    'Elephant shrews mainly eat insects, spiders, centipedes, etc.',
    )

ELK_FACTS = (
    'Elks are larger than a deer, but not as massive as moose.',
    'Elks are usually 4 to 5 feet tall and weigh anywhere from 325 to 1,100 lbs.',
    'Elks are social animals and live in groups called herds, which can range anywhere from 200 to 400 elks',
    'Elks primarily eat grass and woody growth, depending on the season. They also eat dandelions, violets, hawkweed, aster, clover, and mushrooms',
    'A calf, an elk baby, can stand up on its own after just 20 minutes. They usually weigh around 31 to 35 lbs when they are born.',
    'There are about 750,000 elk today in Northern American.',
    'Elk antlers have six tines, or branches, total.',
    'Elk can reach a top speed of 45 miles per hour. The average horse can gallop at a top speed of 29 mph',
    'Elk have a maximum vertical jump of eight feet.',
    'Elk antlers can grow more than an inch every day and can weigh as much as 40 pounds. Bulls grow new antlers every year and are covered with a soft coating called velvet.',
    'Adult elks usually stay in single-sex groups for most of the year',
    'The gestation period for an elk lasts somewhere between 240 to 262 days.',
    'There are estimated to be over 200,000 elks living in the Greater Yellowstone Ecosystem',
    'The Rocky Mountain elk is the official state animal for Utah.'
    'Elk are members of the Cervidae family, which includes caribou, deer, and moose.',
    'An elk\'s stomach has four chambers: the first stores food, and the other three digest it.',
    'When alarmed, elk raise their heads high, open their eyes wide, move stiffly, and rotate their ears to listen.',
    'Elk threaten each other by curling back their upper lip, grinding their teeth, and hissing softly.',
    'Elk are among the noisiest ungulates, communicating danger quickly and identifying each other by sound.',
    'A cow (female elk) can weigh up to 500 pounds (225 kg).',
    'A bull (male elk) can weigh up to 700 pounds (315 kg).',
    'Prior to European settlement, more than 10 million elk roamed nearly all of the United States and parts of Canada.',
    'Elk live in a variety of habitats, from rainforests to alpine meadows and dry desert valleys to hardwood forests.',
    'Bull elk lose their antlers each March, but they begin to grow them back in May in preparation for the late-summer breeding season.',
    'In early summer, elk migrate to high mountain grazing grounds where the females will give birth.',
    )


EMU_FACTS = (
    'Emus are very docile and curious, and are easily tamed in captivity.',
    'Emus feed on grains, flowers, berries, soft shoots, insects, grubs and whatever else they can find. They even eat stones, dirt and tin cans by accident.',
    'When food is plentiful, emus store large amounts of fat in their bodies. They use these fat stores to survive while looking for more food.',
    'The emu belongs to a family of flightless birds called Ratites. Most Ratites are now extinct, and only the emu, ostrich, cassowary, kiwi, and rhea are alive today.',
    'Emus pair in summer and breed in the cooler months. The female develops blue skin on her neck and her feathers turn a darker brown. She struts around the male making special noises to say that she is ready to mate.',
    'Emus are found only in Australia. They live in most of the less-populated areas of the continent and although they can survive in most regions, they avoid dense forest and severe desert.',
    'Emus can grow to between 5 to 6.5 feet (1.5 – 2 metres) in height and weigh up to 130 pounds (60 kg). Males are slightly smaller than females. Males make a grunting sound like a pig and females make a loud booming sound.',
    'The emu is the largest bird in Australia, and the second largest in the world after the ostrich.',
    'Emu chicks grow very quickly, up to 2 pounds (1 kg) a week, and are full-grown in 12 to 14 months. They stay with their family group for another six months or so before they split up to breed in their second season.',
    'Emus must drink every day, and they don’t waste water. On very hot days they breathe rapidly, using their lungs as evaporative coolers. Their large nasal passages have multiple folds inside. In cooler weather they use these folds to recycle air and create moisture for reuse.',
    'The Australian military has lost a war against emus in 1932, in what is called the Great Emu War. The emu population remained virtually the same after the battle.',
    )

FALCON_FACTS = (
    'Peregrine falcons have been clocked at reaching speeds of 242 miles per hour while diving for prey, making them the fastest recorded animal ever.',
    'Falcon is a carnivore. Its diet is based on rodents, frogs, fish, bats, and small birds.',
    'Falcons have a lifespan between 12 and 20 years in the wild, depending on species. Some species can live up to 25 years in captivity.',
    'The gyrfalcon (Falco rusticolus) is the largest falcon species. It is up to 61 centimeters (24 inches) long with a wingspan of up to 130 centimeters (51 inches) and weigh up to 1,350 grams (47.6 ounces).',
    'The Seychelles kestrel (Falco araea) is the smallest falcon species. It is 18–23 centimeters 7-9 inches long with a wingspan of 40–45 centimeters (16-18 inches) and a weight of 73-87 grams (2.5-3 unces).',
    'Falcons have excellent eyesight which they use to locate their prey. They can see up to 8 times more clearly than the sharpest human eye.',
    'Most species of falcon are dark brown or grey-colored with white, yellow, and black spots and markings on the body.',
    'Falcons are strong, fast fliers with great aerial agility, which makes them successful hunters capable of taking down prey 6 times their own body weight! Usually they kill cleanly, breaking the back of their victims.',
    'The falcon is a bird of prey that, typically sitting close to the top of the food chain, has few predators. Falcons may be killed by other large birds of prey, such as eagles and owls. The eggs and chicks are vulnerable to mammals that may climb into the nest if it is too low to the ground.',
    'Falcons can process four types of light while humans can only process three. This means that the falcon has a very good night vision and can also see ultraviolet rays.',
    )

FERRET_FACTS = (
    'The Latin name for ferret, Mustela putorius furo, means smelly little thief.',
    'Ferrets are carnivorous mammals in the weasel family, along with otters, badgers, weasels, milks and wolverines.',
    'Ferrets do not occur naturally in the wild and were originally domesticated for hunting.',
    'The largest feral ferret population is currently decimating wildlife in New Zealand.',
    'The Ferret has become the third most popular pet in the US behind cats and dogs.',
    'Ferrets are around the size and shape of a zucchini. They usually weigh around 1 to 5.5 lbs. (0.5 to 2.5 kg) and have a head and body length of 8 to 18 inches (20.5 to 46 centimeters). Their tails are close to half their body length and range from 2.8 to 7.5 in (7 to 19 cm).',
    'Ferrets are related to wolverines, ermines, minks and weasels in the Mustela genus.',
    'The domesticated ferret can be born with a wide range of fur colors, including dark-eyed white, sable, black sable, silver, albino, cinnamon and chocolate. Black-footed ferrets aren’t nearly as colorful. They are a pale color with white foreheads, muzzles and throats and black feet.',
    'Ferrets are carnivores, which means they eat only meat. Black-footed ferrets eat usually eat small mammals, such as possums, rabbits, prairie dogs, hedgehogs and rodents. A domesticated ferret typically eats factory-made chow. A healthy diet for pet ferrets consist of 36 percent protein, around 20 percent fats and is low in carbohydrates, according to the American Ferret Association.',
    'Male ferrets are known as hobs and female ferrets are called jills. In the wild, hobs and jills mate around March and April. After a gestation period of 35 to 45 days, a jill will give birth to one to six babies. Baby ferrets are called kits.',
    'The ancient Greeks probably domesticated ferrets about 2,500 years ago to hunt vermin, according to the Woodland Park Zoo. The practice then spread across Europe. Sailors kept ferrets on ships to control rats. It is likely that that is how ferrets came to North America in the 1700s.',
    'A group of ferrets is called a "business."',
    'Like dogs, ferrets have long canine teeth. Like cats, domesticated ferrets can be litterbox trained.',
    'Ferrets have a light musky odor, according to the American Ferret Association. In fact, the Latin the species name for the domesticated ferrets is smelly weasel: Mustela = weasel and putorius = smelly. Spaying or neutering minimizes the smell. They also have scent glands, which release a scent as a defense.',
    'Usually considered a subspecies of the European polecat, ferrets are often listed as Mustela putorius furo. But according to the California Department of Fish and Wildlife, some experts use Mustela furo, Putorius putorius furo and Putorius furo.',
    )

FIRESALAMANDER_FACTS = (
    'Fire salamanders live in central European forests and are more common in hilly areas.',
    'Fire salamanders prefer deciduous forests, since they like to hide in fallen leaves and around mossy tree trunks.',
    'Fire salamanders need small brooks or ponds with clean water in their habitat for the development of the larvae.',
    'Fire salamanders are active in the evening and the night, but on rainy days they are active in the daytime as well.',
    'The diet of the fire salamander consists of various insects, spiders, earthworms, and slugs, but they also occasionally eat newts and young frogs.',
    'Fire salamanders weigh about 40 grams.',
    'The fire salamander can grow to be 15–25 centimeters (5.9 - 9.8 inches) long.',
    'The fire salamander\'s primary alkaloid toxin, Samandarin, causes strong muscle convulsions and hypertension combined with hyperventilation in all vertebrates',
    'The poison glands of the fire salamander are concentrated in certain areas of the body, especially around the head and the dorsal skin surface.',
    )

FLAMINGO_FACTS = (
    'Flamingos are a type of wading bird that live in areas of large shallow lakes, lagoons, mangrove swamps, tidal flats, and sandy islands.',
    'The word "flamingo" comes from the Spanish word "flamenco" which came from the earlier Latin word "flamma" meaning flame or fire.',
    'There are six species of flamingo in the world. Two are found in the Old World and four species live in the New World - Americas.',
    'The most widespread flamingo is the Greater flamingo found in areas of Africa, Southern Europe and Southwest Asia. The Lesser flamingo is the most numerous and lives in the Great Rift Valley of Africa to Northwest India.',
    'The four flamingo species in the New World include the Chilean flamingo, found in temperate South American areas, the Andean Flamingo and James\'s flamingo found in the high Andes mountains in Peru, Chile, Bolivia and Argentina and the American flamingo of the Caribbean islands, Belize and Galapagos islands.',
    'The Greater flamingo is the largest species, at up to 1.5 m (5 ft) tall and weighing up to 3.5 kg (8 lbs). The Lesser flamingo is just 90 cm (3 ft) tall, weighing 2.5 kg (5.5 lbs).',
    'In the wild, flamingos live 20 - 30 years and sometimes over 50 years in captivity.',
    'Flamingo legs can be longer than their entire body. The backward bending \'knee\' of a flamingo\'s leg is actually its ankle, the knee is out of sight further up the leg.',
    'Quite often flamingos will stand on one leg, with the other tucked under the body. Its not fully understood why they do this but it is believed to conserve body heat.',
    'The flamingo is a filter-feeder, holding its curved beak upside down in the water it sucks in the muddy water and pushes the mud and silt out the side while tiny hair-like filters along the beak called lamellae sieve food from the water.',
    'The pink to reddish color of a flamingo\'s feathers comes from carotenoids (the pigment that also makes carrots orange) in their diet of plankton, brine shrimp and blue-green algae.',
    'Flamingos are social birds, they live in colonies of sometimes thousands, this helps in avoiding predators, maximizing food intake, and is better for nesting.',
    'Flamingo colonies split into breeding groups of up to 50 birds, who then perform a synchronized ritual "dance" whereby they stand together stretching their necks upwards, uttering calls while waving their heads and then flapping their wings.',
    'The flamingo is the national bird of the Bahamas.',
    )

FLY_FACTS = (
    'Flies are found on every continent except for the innermost polar regions of the Arctic Circle and Antarctica',
    'Flies are omnivores - they will eat just about everything from nectar to animal blood',
    'The lifespan of a fly averages around one month',
    'The time from egg to fly only takes about 2 weeks',
    'The International Space Station has a Fruit Fly Lab',
    'Flies can see behind themselves',
    'House flies can fly about 5 miles per hour',
    'Hear a fly buzzing?  That is due to their wings beating about one thousand times per second',
    'Flies taste with their feet',
    'House flies can transmit several diseases, including cholera, dysentery, typhoid, and many others',
    'Flies usually defecate when they land',
    'Flies do not have jaws or teeth, they must drink their food',
    )

FOX_FACTS = (
    'A group of foxes is called a "skulk" or "leash".',
    'Grey foxes can retract their claws like cats do.',
    'A male is called a ‘dog fox’ while a female is called a ‘vixen’. Young foxes are known as ‘kits’.',
    'Foxes are generally solitary animals; unlike wolves, they hunt on their own rather than in packs.',
    "Foxes' pupils are vertical, similar to a cat, helping them to see well at night.",
    "The tip of a red fox’s tail is white, whereas swift foxes have a black-tipped tail.",
    "Foxes have excellent hearing. Red foxes can reportedly hear a watch ticking 40 yards away!",
    'Foxes only live up to 5 years in the wild, but up to 14 in captivity!',
    'Foxes are legal to own in 21 states!',
    'Adult red foxes usually live alone except during the mating season in January and February and when raising young.'
    'Foxes stink, their funny ‘musky’ smell comes from scent glands at the base of their tail.',
    "Foxes have whiskers on their legs and face, which help them to navigate.",
    "Foxes are one of the most well known wild animals in the UK, and are native to Britain.",
    "Foxes use 28 different types of calls to communicate with each other.",
    "A fox can run up to 30 miles per hour.",
    "Foxes are usually monogamous.",
    "Foxes have excellent hearing. They can hear low-frequency sounds and rodents digging underground.",
    "The fox does not chew its food.  Instead it uses its carnassial or shearing teeth to cut the meat into manageable chunks.",
    "There are 21 species of fox.",
    "Foxes have a lifespan of 2 to 5 years, but some have lived to be 14 years old in captivity.",
    "The silver fox is not a different species of fox, but merely a melanistic form of the red fox.",
    'The red fox is the most wide-spread carnivore in the world.'
    'The latin name for fox is Vulpes Vulpes.',
    )

FROG_FACTS = (
    'A frog is an amphibian. They lay their eggs in water. The eggs hatch into a tadpole which lives in water until it metamorphoses into an adult frog.',
    'Tadpoles look more like fish than frogs, they have long finned tails and breathe through gills.',
    'An amphibian can live both on land and in water.',
    'Although frogs live on land their habitat must be near swamps, ponds or in a damp place. This is because they will die if their skin dries out.',
    'Instead of drinking water, frogs soak it into their body through their skin.',
    'Frogs breathe through their nostrils while also absorbing about half the air they need through their skin.',
    'Frogs use their sticky, muscular tongue to catch and swallow food. Unlike humans, their tongue is not attached to the back of its mouth. Instead it is attached to the front, enabling the frog to stick its tongue out much further.',
    'The common pond frog is ready to breed when it is only three years old.',
    'Frogs in the wild face many dangers and are lucky to survive several years. In captivity however, frogs can live for much longer.',
    'Frogs can see forwards, sideways and upwards all at the same time. They never close their eyes, even when they sleep.',
    'Remarkably, frogs actually use their eyes to help them swallow food. When the frog blinks, its eyeballs are pushed downwards creating a bulge in the roof of its mouth. This bulge squeezes the food inside the frog\'s mouth down the back of its throat.',
    )

GAZELLE_FACTS = (
    'A gazelle can run up to 60 miles per hour.',
    'Baby gazelles are called calves or fawns.',
    'Depending on the species, adult gazelles range in weight from 26 pounds to 165 pounds.',
    'Gazelles use a bounding leap when running called "pronking" or "stotting".',
    'When pregnant, gazelles carry their young for about six months before giving birth.',
    'The name "gazelle" comes from an Arabic poetic form.',
    'Gazelles generally live up to 10 to 12 years.',
    'To evade predators, gazelles may zigzag rather than running in a straight line.',
    'A gazelle will flick its tails or stomp its feet to warn others of a lurking predator.',
    'Gazelles can stand on their back legs to reach leaves high in the branches of trees.',
    'The horns of the Edmi gazelle can grow to 14 inches (35.5 centimeters) long.',
    )

GECKO_FACTS = (
    'Geckos vary in size. Smallest species of geckos, dwarf gecko, reaches ¾ inches in length. Largest species of geckos, tokay gecko, reaches 14 inches in length.',
    'Geckos are usually brightly colored. Body coloration depends on the colors of their environment because it plays important role in the camouflage.',
    'Geckos are nocturnal (active at night) creatures. Their eyes are adapted to a low level of light.',
    'Due to their small size, geckos are often preyed on by snakes, birds, mammals, and some large spider species.',
    'Geckos eat different types of fruit, flower nectar, insects, and worms.',
    'Gecko has a fat tail which is used as a reservoir of fats. It also help gecko to balance while it walks and climbs the trees.',
    'Just like other lizards, gecko can throw away its tail in the case of a danger. Tailless gecko will regenerate its missing body part after short period of time.',
    'Teflon is the only material to which gecko cannot stick (using its "suction cups") and walk without gliding.',
    'Unlike other reptiles, geckos are able to produce various sounds which are used in communication. They produce barking, chirping or clicking noise during mating season or when defending their territory.',
    'Geckos have long lifespan. Leopard gecko can survive more than 20 years in captivity. Other species live between 8 and 10 years.',
    'Some species of geckos have no legs and look more like snakes.',
    'Most species of gecko don’t have eyelids, so they lick their eyes to clean them.',
    'Some gecko species can fly! The flying gecko, or parachute gecko, is a genus of arboreal gecko species found in Southeast Asia. While they aren’t capable of independent flight, they get their name from their ability to glide using the flaps of skin found on their feet and their flat, rudder-like tails.',
    'The smallest gecko species is less than 2 centimeters in length.'
    'The GEICO gecko is a gold dust day gecko with a Cockney accent, voiced by English actor Jake Wood.',
    )

GIBBON_FACTS = (
'Gibbon vocalizations are often referred to as song because of the way they modulate their pitch. Gibbons sing alone and in duets and they start each day by singing at sunrise.'
'Gibbons are famous for the swift and graceful way they swing through the trees by their long arms. This method of locomotion is called brachiation.'
'Gibbons are not monkeys. They are part of the ape family and are classified as lesser apes because they are smaller than the great apes.'
'Like all apes, gibbons are tailless. Unlike most of the great apes, gibbons frequently form long-term pair bonds.'
'Gibbons can make leaps up to 8 m (26 ft).'
'Gibbons walk bipedally with their arms raised for balance. They are the fastest and most agile of all tree-dwelling, nonflying mammals.'
'gibbons fur coloration varies from dark to light brown shades, and any shade between black and white, though a completely "white" gibbon is rare.'
)

GIRAFFE_FACTS = (
    'A male giraffe can weigh as much as a pick up truck! That’s about 1400 kilograms.',
    'Although a giraffe’s neck is 1.5 – 1.8 meters, it contains the same number of vertebrae at a human neck.',
    'A giraffe\'s habitat is usually found in African savannas, grasslands or open woodlands.',
    'The hair that makes up a giraffes tail is about 10 times thicker than the average strand of human hair.',
    'The distinctive spots that cover a giraffe’s fur act as a good camouflage to protect the giraffe from predators. When the giraffe stands in front of trees and bushes the light and dark colouring of its fur blends in with the shadows and sunlight.',
    'It is possible to identify the sex of the giraffe from the horns on its head. Both males and females have horns but the females are smaller and covered with hair at the top. Male giraffes may have up to 3 additional horns.',
    'Giraffes are ruminants. This means that they have more than one stomach. In fact, giraffes have four stomachs, the extra stomachs assisting with digesting food.',
    'Drinking is one of the most dangerous times for a giraffe. While it is getting a drink it cannot keep a look out for predators and is vulnerable to attack.',
    'Male giraffes sometimes fight with their necks over female giraffes. This is called “necking”. The two giraffes stand side by side and one giraffe swings his head and neck, hitting his head against the other giraffe. Sometimes one giraffe is hit to the ground during a combat.',
    'A female giraffe gives birth while standing up. The calf drops approximately 6 feet to the ground, but it is not hurt from the fall.',
    'Giraffes have bluish-purple tongues which are tough and covered in bristly hair to help them with eating the thorny Acacia trees.',
    )

GOAT_FACTS = (
    'Goats do not have teeth on their upper jaw',
    'Goats have the uncanny ability to yell like humans. Their calls are known as bleating.',
    'A baby goat is a kid and giving birth is called kidding.',
    'According to Norse mythology, during a thunderstorm Thor, the god of thunder, rode in a chariot pulled by two goats, Tanngrisni and Tanngnost.',
    'Goat population is roughly 600 million maintained worldwide (not including feral populations).',
    'Goats are fussy eaters that take a lot of time to search out the best snacks. Goats will often stand on their hind legs to reach the best part of foliage that may be out of reach of sheep.',
    'Goat Milk is alkaline and cow milk is acid. Goat milk is lower in cholesterol and higher in calcium, phosphorus, and vitamin A.',
    'The largest number of goats in the United States resides in Texas, however, goats can be raised anywhere in the United States.',
    'Goats are members of the Bovidae family, which also includes antelopes, cattle, and sheep.',
    'There are two types of goats: domestic goats (Capra hircus), which are raised and bred as farm animals; and mountain goats (Oreamnos americanus), which live in steep, rocky areas in the American Northwest.',
    'There are about 200 breeds of domestic goat, according to the Smithsonian Institution.',
    'Mountain goats are found in the Rocky Mountains, typically in Alaska, western Montana, central Idaho, South Dakota, Colorado, and Washington. The wide spread of their cloven hooves allows them to climb steep mountain sides with ease.',
    'Goats and sheep are different species, and there are several physical and behavioral differences.',
    'Mountain goats have bright white coats that help them blend into the snowy areas of their home ranges. Domestic goats have coats that are yellow, chocolate, or black.',
    'Goats were one of the first domesticated animals and were first domesticated around 9,000 years ago, according to the Smithsonian.',
    'In bright light, the pupil in a goat\'s eye is rectangular rather than round.',
    'Goat meat — called chevon or cabrito — is eaten all over the world.',
    'More people consume goat milk than the milk from any other animal.',
    'The phrase "Judas goat" is a term that has been used to describe a goat that is trained to herd other animals to slaughter while its own life is spared.',
    )

GOOSE_FACTS = (
    'Some geese migrate every year. Others stay in the same place year round.',
    'Geese eat seeds, nuts, grass, plants, and berries. They love blueberries.',
    'Geese can live almost anywhere. They like fields, parks, and grassy areas near water.',
    'Geese fly in a “V” formation. If one goose is injured, other geese will stay with it until it dies or can rejoin the flock.',
    'Geese are sometimes raised like chickens for their meat or eggs.',
    'Male geese protect the nest while the female geese sit on the eggs.',
    'Goose is actually the term for female geese, male geese are called ganders. A group of geese on land or in water are a gaggle, while in the air they are called a skein.',
    'European geese descend from wild greylag geese, birds with short necks and round bodies. Asian geese, the breeds now known as African and Chinese, descend from the swan goose and have long, elegant necks and a distinct knob on their beaks.',
    'Geese can live up to twenty years if well cared for.',
    'A baby goose is called a gosling.',
    'A group of geese is called a gaggle',
    'Goose eggs hatch after 25 to 30 days of incubation',
    'It takes about 10 weeks before a gosling is able to fly',
    'Young geese remain with their family group for about one year',
    'Canadian geese are monogamous, and most couples stay together all of their lives.',
    'Geese make loud honking noise, especially when angered.',
    'A group of geese is called a skein when flying, and a gaggle on the ground.',
    'Originally the word goose was reserved for the female bird. The male was a gander.',
    'The offspring of a goose and a swan is called swoose. The plural is either swooses or sweese.',
    'Geese were probably the first type of poultry diomesitcated by humans, over 3000 years ago in Egypt.',
    )

GOPHER_FACTS = (
    'Pocket gophers, commonly referred to as gophers, are burrowing rodents of the family Geomyidae.',
    'The gopher has large cheek pouches lined with fur which it uses to carry food and nesting material.',
    'About 35 species of gophers live in Central and North America.',
    'Gophers are commonly known for their extensive tunneling activities.',
    'Gophers weigh around 0.5 lb (230 g), and are about 6–8 in (150–200 mm) in body length, with a tail 1–2 in (25–51 mm) long.',
    'A gophers daily intake of food is equal to 60 percent of its body weight.',
    'Mating season of gophers takes place during the spring.',
    'Gopher can survive 2 to 3 years (rarely up to 5) in the wild.',
    'Natural enemies of gophers are owls, hawks, coyotes, weasels, and snakes.',
    'The gopher is an iconic mascot and one of the most distinctive features of the Go programming language.',
    'A gopher plays a key role in the film Caddyshack.',
    'Most gophers have brown fur that often closely matches the color of the soil in which they live.',
    'Gophers eat plant roots, shrubs, and other vegetables such as carrots, lettuce, radishes, and any other vegetables with juice.',
    'Pocket gophers are solitary outside of the breeding season, aggressively maintaining territories that vary in size depending on the resources available.',
    )

GRASSHOPPER_FACTS = (
    'Grasshoppers have typanal organs on their bellies, but no ears.',
    'Grasshoppers make music by stridulating or crepitating.',
    'Grasshoppers cause billions of dollars of damage to crops annually.',
    'Grasshoppers existed as early as 300 million years ago.',
    'Grasshoppers can jump twenty times the length of their bodies.',
    'Grasshoppers go through three stages of development: egg, nymph, and adult.',
    'In Africa, Central America, and South America, grasshoppers are eaten as a source of protein.',
    'Grasshoppers can grow up to five inches. Females are usually bigger than males.',
    'There are 11,000 known species of grasshoppers.',
    'A single grasshopper can eat half its bodyweight in a day.',
    )

GORILLA_FACTS = (
    'There are only about 700 mountain gorillas and they live high in the mountains in two protected parks in Africa. Lowland gorillas live in central Africa.',
    'You may have seen baby gorillas being carried on the back of their mothers, but for the first few months after birth the mother holds the baby gorilla to her chest.',
    'An adult male gorilla is called a silverback because of the distinctive silvery fur growing on their back and hips. Each gorilla family has a silverback as leader who scares away other animals by standing on their back legs and beating their chest!',
    'Young male gorillas usually leave their family group when they are about 11 years old and have their own family group by the age of 15 years old. Young female gorillas join a new group at about 8 years old.',
    'Gorillas are herbivores. They spend most of their day foraging for food and eating bamboo, leafy plants and sometimes small insects. Adult gorillas can eat up to 30 kilograms of food each day.'
    'An adult gorilla is about 1 meter tall to their shoulders when walking on all fours using their arms and their legs.',
    'A gorilla can live for 40 – 50 years.',
    'Gorillas are considered to be very intelligent animals. They are known for their use of tools and their varied communication. Some gorillas in captivity at a zoo have been taught to use sign language.',
    'Gorillas are endangered animals. Their habitat is destroyed when people use the land for farming and the trees for fuel. Gorillas are also killed by poachers and sometimes get caught in poacher’s snares meant for other animals.',
    'The scientific name of the western lowland gorilla is "Gorilla gorilla gorilla".'
    )

HAMSTER_FACTS = (
    'Hamsters are rodents from the subfamily Cricetinae.',
    'There are 25 species of hamster.',
    'Hamsters have thick silky fur, short tails, small ears, short legs, wide feet, and large eyes.',
    'Hamsters usually live in burrows underground during the day, they are crepuscular which means they come out at twilight to feed.',
    'Wild hamsters feed mainly on seeds, fruits, vegetables, and sometimes insects.',
    'Hamsters are very good diggers, they will create burrows in the soil that can be over half a meter deep, containing various rooms for different purposes.',
    'Hamsters have large cheek in which they carry food back to their burrows. Full pouches can make their heads double or triple in size.',
    'Hamsters do not have good eyesight, they are nearsighted and also colour-blind.',
    'The hamster relies on scent to find their way. They have scent glands which they rub on objects along a path.',
    'Depending on the species hamsters can be black, grey, honey, white, brown, yellow, red, or a combination of these colors.',
    'Hamsters are great as pets because they are easy to breed in captivity, easy to care for, and interact well with people. They are also used as laboratory animals.',
    'The Syrian hamster is the most popular and well known breed kept as pets. All Syrian hamsters as pets are believed to have descended from one pair in 1930.',
    'Syrian hamsters live 2 - 3 years in captivity, and less in the wild. Other popular pet types such as Russian dwarf hamsters live about 2- 4 years in captivity.',
    'Hamsters range in size from the largest breed, the European hamster at 13.4 inches (34 cm) long, to the smallest, the dwarf hamster at 2 - 4 inches (5.5 - 10.5 cm) long.',
    )

HAWK_FACTS = (
    'Hawks can vary in size depending on the species.',
    'Hawks have excellent eyesight. They can see 8 times better than humans and can locate prey from 100 feet away.',
    'Hawks are diurnal animals (active during the day).',
    'Hawks build nests on trees or build nests on the ground in marshes.',
    'Average lifespan of a hawk is 10 to 20 years in the wild.',
    'Hawks are characterized by sharp talons, a curved bill, and muscular legs.',
    'The largest species of hawks, the northern goshawk can weigh up to 2.2 kilograms (4.85 pounds)',
    'Hawks eat small mammals such as mice, squirrels, and rabbits, as well as insects, smaller birds, turtles, and reptiles',
    'After eating, a hawk will regurgitate a pellet that contains feathers and small bones',
    'Hawks tend to mate during the spring and spend the majority of their time alone',
    'Female hawks lay 1 to 5 eggs per year',
    'Both the male and female hawks will create their nest, improve it, and take care for their eggs',
    'Female hawks are generally larger than male hawks',
    )

HEDGEHOG_FACTS = (
    'There are 17 species of hedgehog. They are found in parts of Europe, Asia, and Africa and were introduced in New Zealand by settlers.',
    'Hedgehogs are nocturnal animals, often sleep during the day in a nest or under bushes and shrubs before coming out to feed at night.',
    'Hedgehogs are not related to other spine covered creatures such as the porcupine or echidna.',
    'The spines of a hedgehogs, are stiff hollow hairs, they are not poisonous or barbed and cannot be easily removed, they fall out naturally when a hedgehog sheds its baby spines and grows adult spines a process called "quilling".',
    'Hedgehogs have about 5,000 to 6,500 spines at any one time, each which last about a year',
    'Its illegal to sell hedgehogs in Georgia, USA',
    'Its illegal to own and sell hedgehogs in California, CA, because they are considered an invasive species.',
    'Most hedgehog species will roll into a tight ball if threatened, making it hard for its attacker to get past the spiky defenses.',
    'A baby hedgehog is called a hoglet.',
    'Hedgehogs communicate through a combination of snuffles, grunts, and squeals.',
    'Hedgehogs have weak eyesight but a strong sense of hearing and smell. They can swim, climb, and run surprising quickly over short distances.',
    'For their size hedgehogs have a relatively long lifespan. They live on average for 4-7 years in the wild and longer in captivity.',
    'Hedgehogs in colder climates, such as the UK, will hibernate through winter.',
    'If hedgehogs come in contact with humans they can sometimes pass on infections and diseases.',
    'The hedgehog is a pest in countries such as New Zealand where it has been introduced, as it does not have many natural predators and eats native species of insects, snails, lizards, and baby ground-nesting birds.',
    )

HIPPO_FACTS = (
    'The name hippopotamus means ‘river horse’ and is often shortened to hippo.',
    'The hippopotamus is generally considered the third largest land mammal (after the white rhinoceros and elephant).',
    'Hippopotamuses spend a large amount of time in water such as rivers, lakes, and swamps.',
    'Resting in water helps keep hippopotamuses temperature down.',
    'Hippopotamuses give birth in water.',
    'Hippopotamuses have short legs, a huge mouth, and a body shaped like a barrel.',
    'The closest relations of the hippopotamus are surprisingly cetaceans such as whales and dolphins. Scientists believe this family of animals diverged in evolution around 55 million years ago.',
    'Although hippos might look a little chubby, they can easily outrun a human.',
    'Hippos can be extremely aggressive, especially if they feel threatened. They are regarded as one of the most dangerous animals in Africa.',
    'Hippos are threatened by habitat loss and poachers who hunt them for their meat and teeth.',
    'A male hippopotamus is called a ‘bull’. A female hippopotamus is called a ‘cow’. A baby hippo is called a ‘calf’.',
    'A group of hippos in known as a ‘herd’, ‘pod’, ‘dale’, or ‘bloat’.',
    'Hippos typically live for around 45 years.',
    )

HONEYBADGER_FACTS = (
    'Honey badgers have been known to fight lions',
    'Honey badgers are really good at digging',
    'Honey badgers have thick skin and can survive venomous snake bits',
    'Honey badgers can release a stinky liquid just like skunks',
    'A honey badger\'s diet can consist of almost anything',
    'Honey badgers are very smart and sometimes use tools to help them complete tasks',
    'The honey badger is part of the weasel family',
    'The honey badger got its name because of its love for honey',
    'Honey badgers are often very mean and will pick fights with other animals, which often are bigger than them',
    'Honey badgers are from parts of Africa and Asia',
    'Honey badgers are great swimmers and can climb trees',
    'Honey badgers are nocturnal',
    'Honey badgers are mostly solitary and only meet up to hunt or mate',
    'Beekeepers will often keep their bees elevated to prevent honey badgers from getting to their hives.',
    'Honey badgers are substantially resistant to venom, and easily survive snakebites that would kill a human',
    )

HONEYBEE_FACTS = (
    'The honey bee has been around for millions of years.',
    'Honey bees, scientifically also known as Apis mellifera, which mean "honey-carrying bee", are environmentally friendly and are vital as pollinators.',
    'Honey bee is the only insect that produces food eaten by man.',
    'Honey from the honey bee is the only food that includes all the substances necessary to sustain life, including enzymes, vitamins, minerals, and water; and it\'s the only food that contains "pinocembrin", an antioxidant associated with improved brain functioning.',
    'Honey bees have 6 legs, 2 compound eyes made up of thousands of tiny lenses (one on each side of the head), 3 simple eyes on the top of the head, 2 pairs of wings, a nectar pouch, and a stomach.',
    'Honey bees have 170 odorant receptors, compared with only 62 in fruit flies and 79 in mosquitoes. Their exceptional olfactory abilities include kin recognition signals, social communication within the hive, and odor recognition for finding food. Their sense of smell is so precise that it could differentiate hundreds of different floral varieties and tell whether a flower carried pollen or nectar from meters away.',
    'The honey bee\'s wings stroke incredibly fast, about 200 beats per second, thus making their famous, distinctive buzz. A honey bee can fly for up to six miles, and as fast as 15 miles per hour.',
    'The average worker bee produces only about 1/12th teaspoon of honey in her lifetime. Doesn\'t this fact make you love every drop of honey? Read and you will understand why it makes so much sense to say: "as busy as a bee".',
    'A hive of bees will fly 90,000 miles, the equivalent of three orbits around the earth to collect 1 kg of honey.',
    'It takes one ounce of honey to fuel a bee\'s flight around the world (National Honey Board).',
    'A honey bee visits 50 to 100 flowers during a collection trip.',
    'The bee\'s brain is oval in shape and only about the size of a sesame seed (iflscience.com), yet it has remarkable capacity to learn and remember things and is able to make complex calculations on distance travelled and foraging efficiency.',
    'A colony of bees consists of 20,000 - 60,000 honeybees and one queen. Worker honey bees are female, live for about 6 weeks, and do all the work.',
    'Each honey bee colony has a unique odor for members\' identification.',
    )

HORSE_FACTS = (
    'Horses can sleep both lying down and standing up.',
    'Horses can run shortly after birth.',
    'You can generally tell the difference between male and female horses by their number of teeth: males have 40 while females have 36 (but honestly, most us are going to use the much “easier” way).',
    'Domestic horses have a lifespan of around 25 years.',
    'The Przewalski’s horse is the only truly wild horse species still in existence. The only wild population is in Mongolia. There are however numerous populations across the world of feral horses e.g. mustangs in North America.',
    'A 19th century horse named ‘Old Billy’ is said to have lived 62 years.',
    'Horses have around 205 bones in their skeleton.',
    'Horses have been domesticated for over 5000 years.',
    'Horses have bigger eyes than any other mammal that lives on land.',
    'Because horse’s eyes are on the side of their head, they are capable of seeing nearly 360 degrees at one time.',
    'Horses gallop at around 44 kph (27 mph).',
    'The fastest recorded sprinting speed of a horse was 88 kph (55 mph).',
    'Estimates suggest that there are around 60 million horses in the world.',
    'Scientists believe that horses have evolved over the past 50 million years from much smaller creatures.',
    'A male horse is called a stallion. A female horse is called a mare.',
    'A young male horse is called a colt. A young female horse is called a filly.',
    'An adult horse’s brain weights 22 oz, about half that of a human.',
    'The first cloned horse was a Haflinger mare in Italy in 2003.',
    'Horses with pink skin can get a sunburn.',
    'A group of horses will not go to sleep at the same time - at least one of them will stay awake to look out for the other',
    'Male horses are one of few male mammals to not have nipples.',
    )

HUMMINGBIRD_FACTS = (
    'Hummingbirds are New World birds found only in the Americas',
    'There are more than 340 species of hummingbirds.',
    'Hummingbirds are one of the smallest kinds of bird in the world. With most species 7.5 - 13 cm (3 - 5 in) in length. The Bee hummingbird is the smallest at just 5 cm (2 in). The largest is the Giant Hummingbird reaching over 20 cm (8 in).',
    'They are called hummingbirds due to the sound created by their rapidly beating wings.',
    'Depending on the species, a hummingbird\'s wings can flap on average around 50 times per second, and can reach as high as 200 times per second. This allows them to fly faster than 15 m/s (54 km/h or 34 mph).',
    'The hummingbird can hover, fly forwards, backwards, and even upside down.',
    'Hummingbirds drink the nectar of flowers which gives them a good source of glucose energy, they will catch insects every now and again for a protein boost.',
    'A hummingbird\'s bill varies dramatically depending on the species. Most have a fairly long, thin bill that allows them to reach down to the nectar of a flower. With the bill slightly open they use their tongue to quickly lap up the nectar inside.',
    'Apart from insects, hummingbirds have the highest metabolism of all animals due to the need to keep their wings rapidly beating. Because of this, the hummingbird visits hundreds of flowers each day, consuming more than their own weight in nectar each day.'
    'Because they need to conserve energy, hummingbirds do not spend all day flying, they spend the majority of their time perched digesting their food.',
    'To conserve energy overnight a hummingbird enters a hibernation-like sleep state called torpor.',
    'Depending on the species, hummingbirds live on average 3 to 5 years but have been known to live as long as 12 years.',
    'Most hummingbirds of the United States and Canada migrate over 3000km south in fall to spend winter in Mexico or Central America. Some South American species also move north to these areas during the southern winter.',
    'Before migrating, the hummingbird will store up a layer of fat equal to half its body weight in order to slowly use up this energy source while flying.',
    )

HUSKY_FACTS = (
    'Huskies have a double-layer coat that can keep them warm in temperatures as low as -60 degrees Fahrenheit.',
    'A husky\'s howl can be heard up to ten miles away.',
    'Huskies were brought to the US from Siberia during the Nome Gold Rush in 1909.',
    'Huskies\' coats come in six different shades.',
    'Heterochromia, a condition in which each eye is a different color, is common in huskies.',
    'Huskies were bred by the Chukchi Eskimos of northeastern Siberia.',
    'The color of a husky\'s nose depends on the color of its coat.',
    'Huskies have hair between their toes to keep their feet warm.',
    'When diptheria broke out in Nome, Alaska in 1925, a sled dog team led by the husky, Balto, transported medicine to the town before the epidemic could spread any further. The dogs made the trip during a blizzard, braving strong winds and temperatures as low as -23 degrees Fahrenheit.',
    'They\'re good dogs, Brent.',
    'DNA found on the ancient bone of an Arctic Wolf suggests that Huskies are one of the oldest of dog breeds.',
    'Males typically grow to be 21-23.5 inches in height from ground to shoulder, and weigh between 45-60 pounds',
    )

IGUANA_FACTS = (
    'Green iguanas can survive 40 foot falls.',
    'Iguanas can live between 4 and 60 years!',
    'The heaviest iguana is the blue iguana weighing upwards of 30 lbs (14 kilograms).',
    'Often great swimmers, iguanas typically live near water so that they can safely swim away from danger.',
    'Don\'t even try to beat iguanas at this task: holding their breath. Iguanas can hold their breath a very long time. Around 45 minutes, in fact!',
    'Green iguanas can vary in color more than just green, like blue, purple, or orange.',
    'Iguanas absorb water through their skin.',
    'After female iguanas lay their eggs, she never returns. Bye Mom!',
    'Iguanas are mainly herbivorous.',
    )

IBEX_FACTS = (
    'Ibex are wild goats that live in the mountainous regions of Europe, north central Asia, and northern Africa.',
    'There are five species of ibex, according to the Integrated Taxonomic Information System (ITIS). They have long, curved horns and cloven hooves.',
    'Ibex are related to antelopes, buffalo, bison, cattle, goats, and sheep.',
    'Ibex are typically about 1 to 5.5 feet (30 to 170 centimeters) from their hooves to withers, the highest part of the shoulders at the base of the neck.',
    'Both male and female ibex have very long horns, which are used for territorial defense and sexual selection.',
    'Ibex are herbivores; they only eat vegetation, such as shrubs, bushes, and grasses.',
    'Ibex make their homes on cliffs that would be dangerous for predators.',
    'Ibex are very nimble. They can jump more than 6 feet (1.8 meters) straight up without a running start. This helps them climb mountainous terrain with ease.',
    )

JACKAL_FACTS = (
    'There are three species of Jackal, the Common Jackal (Canis aureus), the Side-striped Jackal (Canis adustus), and the Black-backed Jackal (Canis mesomelas). Common Jackals are also known as Golden Jackals, Asiatic Jackals, and Oriental Jackals.',
    'Jackals vary in size depending on the species. On average, a jackal can reach 15 to 35 pounds in weight and 15 to 20 inches in height at the shoulder.',
    'Jackals are opportunistic feeders. That mean that they will eat whatever is available. Jackals like to eat snakes and other reptiles, smaller gazelles, sheep, insects, fruit, berries, and sometimes even grass.',
    'Main predators of jackals are leopards, hyenas, and eagles. Young animals are especially easy target of eagles.',
    'Jackals sometimes eat remains of dead animals that were killed by large predators.',
    'Jackals are very vocal animals. They use wide variety of sounds to communicate. Most notable sounds include: yips, howls, growls, and "owl-like hoots". Siren-like howl is produced when the food is located.',
    'Jackals are fast animals. They can run 40 miles per hour, but they usually run only 10 miles per hour for longer periods of time.',
    'Jackals respond only to the sounds produced by the members of their family. They ignore all other calls.',
    'Jackals mate for lifetime (they are monogamous). Pregnancy in females lasts around 2 months and ends usually with 2 to 4 cubs. Large litters may consist of up to 9 cubs.',
    'Jackals can survive 8 to 9 years in the wild and up to 16 years in captivity.',
    'Jackals can live solitary life, be part of a couple or part of a large group, called pack. Life in pack ensures protection against predators and ensures cooperative hunt which results in killing of the larger prey.',
    )

JELLYFISH_FACTS = (
    'Jellyfish live in the sea and are found in all oceans.',
    'Some jellyfish live in fresh water.',
    'Jellyfish can be large and brightly colored. They can often be transparent or translucent.',
    'Some jellyfish can be very hard to see, nearly invisible to the human eye. Box jellyfish are almost transparent.',
    'Although the word is mentioned in their name, jellyfish are not fish.',
    'A group of jellyfish is called a ‘bloom’, ‘swarm’, or ‘smack’. Large blooms can feature over 100,000 jellyfish.',
    'Jellyfish don’t have brains.',
    'Jellyfish use their tentacles to sting. Most are harmless to humans but stings from some species, such as the box jellyfish, can be very painful and sometimes kill.',
    'Jellyfish eat plankton. Some sea turtles eat jellyfish.',
    'Jellyfish can clone themselves.',
    'Some jellyfish can glow in the dark.',
    'The Lions Mane Jellyfish is the largest of the Jellyfish species.',
    'Lion’s Mane Jellyfish have tentacles up to 190 feet long and a bell diameter of almost 7 feet wide.',
    'The Lion’s Mane Jellyfish mouth is situated on the bell’s underside, surrounded by tentacles that are divided into eight clusters of up to 150 tentacles each.',
    'The Lion’s Mane jellyfish also possesses bioluminescent abilities, meaning it’s able to produce its own light and glow in the dark underwater.',
    )

JERBOA_FACTS = (
    'Jerboas are hopping desert rodents found throughout Northern Africa and East Asia, to Northern China and Manchuria.',
    'Jerboas tend to live in hot deserts.',
    'Jerboas look somewhat like miniature kangaroos, as they have many similarities. Both have long hind legs, very short forelegs and long tails.',
    'The bipedal locomotion of jerboas involves hopping, skipping, and running gaits. It is associated with rapid and frequent, difficult-to-predict changes in speed and direction, facilitating predator evasion.',
    'Jerboas are nocturnal. During the heat of the day they take shelter in burrows.',
    'When chased, jerboas can run at up to 24 kilometres per hour.',
    'Most species of jerboa have excellent hearing that they use to avoid becoming the prey of nocturnal predators.',
    'The typical lifespan of a jerboa is around six years.',
    'Most jerboas rely on plant material as the main component of their diet, but they cannot eat hard seeds.',
    'Jerboas are solitary creatures. Once they reach adulthood, they usually have their own burrow and search for food on their own.',
    )

KANGAROO_FACTS = (
    'Kangaroos are marsupial animals that are found in Australia as well as New Guinea.',
    'There are four different kangaroo species, the red kangaroo, eastern grey kangaroo, western grey kangaroo, and antilopine kangaroo.',
    'Kangaroos can hop around quickly on two legs or walk around slowly on all four.',
    'Kangaroos can’t walk backwards.',
    'Kangaroos can jump very high, sometimes three times their own height.',
    'Kangaroos can swim.',
    'Baby kangaroos are known as ‘joeys’. A group of kangaroos is called a ‘mob’, ‘troop’, or ‘court’.',
    'The red kangaroo is the largest marsupial in the world.',
    'Kangaroos usually live to around six years old in the wild.',
    )

KIWI_FACTS = (
    'The Kiwi are flightless birds native to New Zealand',
    'Approximately the size of a domestic chicken, kiwi are by far the smallest living ratites (which also consist of ostriches, emus, rheas, and cassowaries).',
    'The Kiwi lay the largest egg in relation to their body size of any species of bird in the world.',
    'The kiwi is a national symbol of New Zealand, and the association is so strong that the term Kiwi is used internationally as the colloquial demonym for New Zealanders.',
    'The vestigial wings of the kiwi are so small that they are invisible under the bristly, hair-like, two-branched feathers.',
    'Unlike virtually every other palaeognath, which are generally small-brained by bird standards, kiwi have proportionally large encephalisation quotients.',
    'Kiwi are shy and usually nocturnal. Their mostly nocturnal habits may be a result of habitat intrusion by predators, including humans. In areas of New Zealand where introduced predators have been removed, such as sanctuaries, kiwi are often seen in daylight.',
    'Once bonded, a male and female kiwi tend to live their entire lives as a monogamous couple.',
    'The male kiwi incubates the egg, except for the great spotted kiwi, A. haastii, in which both parents are involved.',
    'Kiwi are no longer hunted and some Maori consider themselves the birds\' guardians.',
    'In 1851, London Zoo became the first zoo to keep kiwi. The first captive breeding took place in 1945.',
    )

KOALA_FACTS = (
    'Koalas are native to Australia. Koalas are not bears.',
    'During the day, koalas often sleep for up to 18 hours.',
    'Koala fossils found in Australia have been dated as long ago as 20 million years.',
    'Koalas eat eucalyptus leaves and almost nothing else. Eucalyptus is very difficult to digest, low in nutrients, and poisonous.',
    'Since eucalyptus is so difficult to chew, it wears down the koalas teeth until they are useless, and the koala starves to death.',
    'The brain size of modern koalas has reduced substantially from their ancestors, possibly as an adaptation to the low energy they get from their diets.',
    'The koala has the smallest brain to body mass ratio of all the mammals.',
    'The closest living relative of the koala is the wombat.',
    'Koalas have sharp claws which help them climb trees.',
    'Koalas have similar fingerprints to humans.',
    'Koalas have large noses that are coloured pink or black.',
    'Outside of breeding seasons, koalas are quiet animals.',
    'A baby koala is called a ‘joey’. Joeys live in their mother’s pouch for around six months and remain with them for another six months or so afterwards.',
    'Koalas cannot be kept legally as pets.',
    )

KOOKABURRA_FACTS = (
    'Though belonging to the group \'kingfisher\', the kookaburra is not associated with water',
    'The name \'kookaburra\' comes from an onamatopoeic interpretation of its call',
    'Kookaburras are generally carnivorous, eating mice, snakes, insects, and small reptiles',
    'The laughing kookaburra can emit a call that resembles the sound of echoing human laughter',
    'The average lifespan of a kookaburra is about 15 years',
    'The kookaburra is the largest member of the kingfisher family and can grow up to 18 inches in length',
    'The kookaburra is native to the forests and woodlands of Australia, Tasmania, and New Guinea',
    )

LADYBUG_FACTS = (
    'Ladybugs are a type of beetle. There are about 4,300 kinds of ladybugs in the world.',
    'Some ladybugs have no spots and others have up to 20 spots. Spots have nothing to do with a ladybug age.',
    'During winter ladybugs hibernate together to stay warm. Thousands of ladybugs may gather in the same location.',
    'Ladybugs are both male and female. Female ladybugs are larger than male ladybugs.',
    'A ladybug can live up to a year long and it can eat up to 5,000 insects in its lifetime.',
    'A ladybug‘s bright color warns predators that it does not taste good.',
    'Ladybugs smell with their feet and antennae.',
    'When a ladybug flies, its wings beat 85 times a second.',
    'If food is scarce, ladybugs will do what they must to survive, even if it means eating each other.',
    'Ladybugs got their name from Catholic farmers, who prayed to the Virgin Mary to save their crops from pests. When the ladybugs appeared and ate the pests they were called “the beetles of our lady”.',
    )

LAMPREY_FACTS = (
    'The lamprey is a jawless fish with a terrifying mouth found in both saltwater and freshwater systems in most temperate regions of our planet.'
    'The sea lamprey is considered to be a parasitic fish because it bores holes into its prey while feeding on their blood and bodily fluids, slowly killing their prey and damaging the species overall survival rate.'
    'A single parasitic lamprey can kill over 40 pounds or more of fish in its lifetime.'
    'Lampreys have sometimes inaccurately been called "lamprey eels," but they are actually more closely related to sharks.'
    'Lamprey belongs to a superclass of jawless fish known agnathans. The unique thing about the agnathan class is that it’s a prehistoric group that is largely extinct.'
    'The proteins in their saliva widen the blood vessels of their prey while their abrasive tongue and piercing teeth damage the skin of its victim and induce blood flow.'
    'Lamprey breed in high quality, deep, fast flowing rivers with clean gravel in which to spawn and a sandy substrate for the larvae to burrow into.'
    'Lampreys possess vertebral structures called arcualia, tiny cartilaginous skeletal elements that are homologous with the neural arches of vertebrates.',
    )

LEMUR_FACTS = (
    'Lemurs live about 18 years.',
    'Lemurs can range in weight from 30 grams (1.1 oz) to 9 kilograms (20 lb) across species.',
    'Most lemur species have a tail longer than their body.',
    'Lemurs are the smallest of all known primates.',
    'Blue-eyed lemurs are one of the two (non-human) primates to have truly blue eyes.',
    'Lemurs can slow their metabolism and reproduce less when these adaptations are needed.',
    'There are 105 known species of lemur.',
    'Dwarf lemurs store fat in their tails for nourishment when they go dormant during dry seasons.',
    'Lemurs can live up to 30 years in captivity, or 16-20 years in the wild, depending on the species.',
    )

LEOPARD_FACTS = (
    'Leopards are part of the cat family, Felidae. The scientific name for a leopard is Panthera pardus.',
    'Leopards are well known for their cream and gold spotted fur, but some leopards have black fur with dark spots. These black leopards are often mistaken for panthers.',
    'Adult leopards are solitary animals. Each adult leopard has its own territory where it lives and, although they often share parts of it, they try to avoid one another.',
    'A leopard’s body is built for hunting. They have sleek, powerful bodies and can run at speeds of up to 57 kilometers per hour. They are also excellent swimmers and climbers and can leap and jump long distances.',
    'A leopard’s tail is just about as long as its entire body. This helps it with balance and enables it to make sharp turns quickly.',
    'Leopards are mostly nocturnal, hunting prey at night.',
    'Leopards protect their food from other animals by dragging it high up into the trees. A leopard will often leave their prey up in the tree for days and return only when they are hungry!',
    'Female leopards give birth to a litter of two or three cubs at a time. By the time a cub is two years old it will leave the company of its mother and live on their own.',
    'When a female leopard is ready to mate she will give a scent and rub her body on the trees to leave her smell there. Male leopards either smell the females scent or hear her call to know that she is ready to mate.',
    'Some people believe that the bones and whiskers of leopards can heal sick people. Many leopards are killed each year for their fur and body parts and this is one reason why the leopard is an endangered animal. While they were previously found in the wild in a number of areas around the world, their habitat is largely restricted to sub-Saharan Africa with small numbers also found in India, Pakistan, Malaysia, China, and Indochina.',
    )

LYNX_FACTS = (
    'The Eurasian lynx is one of the widest ranging cats in the world and can be found in the forests of western Europe, Russia, and central Asia.',
    'These fur-ocious felines are the largest of the lynx species, and the third largest predator in Europe after the brown bear and the wolf.',
    'These incredible cats are strict carnivores, feeding mostly on ungulates (hoofed mammals) such as deer. When food is scarce lynx will also eat smaller prey like hares, foxes, and rabbits.',
    'Lynx can be considered quite a secretive creature. The sounds it makes are very low and often not heard, and their presence in an area can go unnoticed for years.',
    'Come meal time, the lynx stalks its prey from the cover of thick vegetation. It then pounces on its unsuspecting lunch, delivering a fatal bite to the neck or snout.',
    'The Eurasian lynx distinctive features are its black tufts at the tips of its ears and a long white facial ruff. It has grey, rusty, or red fur which grows thicker in winter. Its coat is also patterned, almost always with dark spots.',
    'Although they may hunt during the day (particularly when food is scarce), the Eurasian lynx is mainly nocturnal or crepuscular (active during dawn and dusk). They spend the day sleeping in dense vegetation.',
    'Lynx measure around 90-110 cm in length, and around 60-70 cm in height.',
    'In the wild, the Eurasian lynx can survive up to 17 years. Captive Eurasian lynx in sanctuaries have been known to live to up to 24 years.',
    )

LION_FACTS = (
    'Lions are the second largest big cat species in the world (behind tigers).',
    'The average male lion weighs around 180 kg (400 lb) while the average female lion weighs around 130 kg (290 lb).',
    'The heaviest lion on record weighed an amazing 375 kg (826 lb).',
    'Lions can reach speeds of up to 81 kph (50 mph) but only in short bursts because of a lack of stamina.',
    'The roar of a lion can be heard from 8 kilometers (5.0 miles) away.',
    'Most lions found in the wild live in southern and eastern parts of Africa.',
    'Lions are very social compared to other cat species, often living in prides that feature females, offspring, and a few adult males.',
    'Male lions are easy to recognize thanks to their distinctive manes. Males with darker manes are more likely to attract female lions (lionesses).',
    'Lions are the national animal of Albania, Belgium, Bulgaria, England, Ethiopia, Luxembourg, the Netherlands, and Singapore.',
    'Lions in the wild live for around 12 years.',
    'When lions breed with tigers the resulting hybrids are known as ligers and tigons. There are also lion and leopard hybrids known as leopons, and lion and jaguar hybrids known as jaglions.',
    'Lionesses are better hunters than males and do most of the hunting for a pride.',
    'In the wild, lions rest for around 20 hours a day.',
    'There is an Lion god in Hinduism called "Lakshmi Narashmiha Swamy".',
    )

LIZARD_FACTS = (
    'Some lizards can detach their tails if caught by predators.',
    'The upper and lower eyelids of chameleons are joined, leaving just a small hole for them to see through. They can move their eyes independently however, allowing them to look in two different directions at the same time.',
    'Chameleons have long tongues which they rapidly extend from their mouth, too fast for human eyes to see properly.',
    'Chameleons generally eat insects.',
    'Some chameleons have the ability to change color. This helps them communicate with each other and can also be used for camouflage.',
    'Geckos have no eyelids.',
    'Geckos have unique toes which allow them to be good climbers.',
    'Iguanas have a row of spines which run down their back and tail.',
    'The Komodo dragon is the largest type of lizard, growing up to 3 meters (10 feet) in length.',
    'Komodo dragons are found on a number of different Indonesian Islands.',
    'Komodo dragons are carnivores and can be very aggressive.',
    )

LOBSTER_FACTS = (
    'Lobsters were once considered the the go-to prison food. In Colonial times, it was fed to pigs and goats and only eaten by paupers.',
    'Lobsters turn red when cooked, but in nature they can be green or yellow or even bright blue.',
    'Lobsters can grow up to four feet long and weigh as much as 40 pounds.',
    'Lobsters have a crusher claw and a pincer claw; some lobsters have the crusher claw on the right side and others have it on the left.',
    'Lobsters have poor eyesight, but have highly developed senses of smell and taste.',
    'Lobsters taste with their legs and chew with their stomachs.',
    'Lobsters keep growing forever. They do not get weaker or lose their ability to reproduce, and will keep on molting and growing.',
    'Lobsters are invertebrates which means they lack a backbone.',
    'Lobsters dont have brains as their nervous system is very primitive.',
    'Lobsters can be divided in two groups: clawed and spiny. Clawed lobsters, as the name suggests, have claws and inhabit cold waters. Spiny lobsters have long antennas instead of claws and can be found in the tropical (warm) waters.',
    'Deep-sea lobsters are blind. Other species have compound eyes. They cannot see clear image, but can detect movement even at night.',
    )

MARKHOR_FACTS = (
    'The markhor is the national animal of Pakistan.',
    'The word "markhor" means "snake" in Persian.',
    'Markhors are diurnal, meaning they are active early in the morning and late in the afternoon.',
    'Markhors spend most of their time on cliffs that are hard to reach for predators.',
    'The natural enemies of markhors are snow leapords, wolves, and black bears.',
    'Markhors have average lifespans of 10 to 13 years in the wild.',
    'Male markhors are solitary creatures while females and offpring live in groups of up to 9 animals.',
    'During the summer, male markhors reside in forests while females prefer rocky ridges.',
    'The mating season of markhors takes place in the winter, where males will fight each other to establish dominance.',
    'Markhors make alarm class that resemble the calls of common domestic goats.',
    'The markhor is an endangered species, with only around 2000 to 4000 existing in the wild.',
    'The markhor is mainly found in the northern areas of Pakistan, especially in the Chitral, Ghizar, and Hunza regions.',
    )

MANATEE_FACTS = (
    'Manatees are large, fully aquatic, mostly herbivorous marine mammals sometimes known as sea cows.',
    'Manatees measure up to 4.0 metres (13.1 ft) long, weigh as much as 590 kilograms (1,300 lb), and have paddle-like flippers.',
    'Manatees are occasionally called sea cows, as they are slow plant-eaters, peaceful, and similar to cows on land.',
    'When born, baby manatees have an average mass of 30 kilograms (66 lb).',
    'Generally, manatees swim at about 5 to 8 kilometres per hour (3 to 5 mph). However, they have been known to swim at up to 30 kilometres per hour (20 mph) in short bursts.',
    'Manatees are capable of understanding discrimination tasks and show signs of complex associative learning. They also have good long-term memory.',
    'Manatees typically breed once every two years; generally only a single calf is born.',
    'Manatees have four rows of teeth. Like sharks, these teeth are continually replaced.',
    'Manatees inhabit the shallow, marshy coastal areas and rivers of the Caribbean Sea and the Gulf of Mexico, the Amazon basin, and West Africa.',
    )

MANTIS_SHRIMP_FACTS = (
    'Mantis Shrimps can see ultraviolet and polarized light.',
    'Mantis Shrimp have trinocular vision, meaning they can see using three parts of the same eye.',
    'Mantis Shrimp can be categorized into "Spearers" and "Smashers", referencing tactics used to kill their prey.',
    'A Mantis Shrimp can punch at a speed of 10 meters per second, equivalent to a .22 bullet.',
    'Mantis Shrimp are known to break glass aquariums with their punches.',
    'Mantis Shrimp are not actually shrimp, they are instead stomatopods, a distant relative.',
    'A punch of a Mantis Shrimp momentarily causes the temperature of the surrounding water to reach the temperature of the Sun.',
    'Mantis Shrimp use their ability to see polarized light to commmunicate with other mantis shrimp in a way that is invisible to predators.',
    'Mantis Shrimp can make a low growling sounds and often grunt at dawn and dusk.',
    'Stomatopods, like Mantis Shrimp, are older than dinosaurs.',
    )

MEERKAT_FACTS = (
    'Meerkats can spot an eagle in flight more than a thousand feet away.',
    'Meerkats, or suricates, are a type of mongoose that live in the southern African plains, primarily in South Africa, Namibia, and Botswana.',
    'When foraging for food, a few meerkats will stand guard while the rest look for insects, lizards, birds, and fruit.',
    'Female meerkats give birth to two to four young each year. They are cared for by fathers and siblings who teach them to play and forage.',
    'Meerkat mobs sleep in a single furry pile inside a burrow. Each burrow is an extensive tunnel-and-room system that stays cool under the African sun.',
    'Meerkats have strictly defined roles in their societies including sentry, babysitter, hunter, and teacher.',
    'Meerkat coats can be gold, silver, orange, or brown. Their tails are 7.5 to 9.5 inches (19 to 24 cm) long.',
    'Meerkat burrows can be up to 6.5 feet (2 meters) deep and can have as many as 15 entrances. Mobs of meerkats live in more than one burrow at a time.',
    'Meerkats start their mornings by grooming and lying in the sun.',
    'Meerkats can eat scorpions. Adult meerkats have some immunity to scorpion venom. Mothers will cut off the the tail of a scorpion before feeding it to their young.',
    'Baby meerkats, called pups, are born under ground. They weigh 25 to 36 grams (0.9 to 1.3 ounces) and are blind, deaf, and almost hairless.',
    'A membrane covers and protects a meerkat\'s eyes while they dig. They can also close their ears to keep them free of soil.',
    'Meerkats live in groups of up to 40. These groups are called gangs or mobs.',
    'Meerkats are vicious fighters that often kill each other in skirmishes. Both sides line up across a field before charging forward with leaps and bounds. Before attacking, they try to psych out their opponents with aggressive posturing and bluffing to avoid serious conflict if possible.',
    )

MINK_FACTS = (
    'The mink is a mammal that belongs to the family of weasels.',
    'Mink can reach 15 to 28 inches in length and weigh between 16 and 56 ounces. American minks are larger than European minks.',
    'Minks are covered with soft fur that is usually black or dark brown in color. White marks can be seen on the chin, throat and chest.',
    'Minks have slender body with short legs, long neck, rounded head and small ears. Its tail usually reaches ½ of the body length.',
    'Minks have webbed feet and fur covered with oily substance which prevents soaking of the skin. This type of feet and fur represent adaptation to the life in the water.',
    'Minks are a semi-aquatic animal, which means that it spends part of its life in the water and other part on the ground. Mink can swim 1.5 to 1.8 feet in the second.',
    'Minks live in a den made of tree roots, leaves, stones, and branches. Dens are usually located near the water and they are equipped with several entrances. Mink sometimes use abandoned burrows of beavers or muskrats.',
    'Mink are nocturnal creatures (active during the night).',
    'Mink are carnivores (meat-eaters). Its diet consists of worms, fish, crayfish, amphibians, birds, and small mammals.',
    'The main predators of minks are birds of prey, lynx, foxes, coyotes, and humans.',
    'Minks produce a smelly substance that is used for self-defense and marking of the territory.',
    'Minks are territorial animals. Males live on a territory of 40 acres. Females occupy 2 times smaller of a territory.',
    'Minks are solitary creatures that gather only for mating. Mating season lasts from February to April.',
    'Female minks are able to postpone development of a fertilized egg if the weather conditions are bad. Because of that, pregnancy may last from 39 to 74 days. Females can have up to 10 babies, but they usually have 5.',
    "Mink babies are wrinkled and blind at birth. They depend on the mother's milk during the first 6 weeks of their life. At the age of 8 weeks, young minks are ready for independent life. Sexual maturity will be reached between 12th and 16th month.",
    'Minks can survive 3 to 4 years in the wild and 8 to 10 years in captivity.',
    )

LLAMA_FACTS = (
    'Llamas are members of the camelid, or camel, family.',
    'Llamas were first domesticated and used as pack animals 4,000 to 5,000 years ago by Indians in the Peruvian highlands.',
    'Llamas can grow as much as 6 feet tall.',
    'Llamas weigh 280 to 450 pounds and can carry about a quarter of their body weight, so a 400-pound male llama can carry about 100 pounds on a trek of 10 to 12 miles with no problem.',
    'In the Andes Mountains of Peru, llama fleece has been shorn and used in textiles for about 6,000 years. Llama wool is light, warm, and water-repellent.',
    'Llamas are hardy and well suited for harsh environments.',
    'Llamas are smart and easy to train.',
    'Llamas are vegetarians and have efficient digestive systems.',
    'Llama poop has almost no odor. Llama farmers refer to llama manure as "llama beans." It makes a great, eco-friendly fertilizer. The Incas in Peru burned dried llama poop for fuel.',
    'Llamas live to be about 20 years old.',
    'A baby llama is called a "cria." It\'s pronounced KREE-uh. Mama llamas usually only have one baby at a time. Llama twins are incredibly rare. Pregnancy lasts for about 350 days—nearly a full year. Crias weigh 20 to 35 pounds at birth.',
    'Llamas come in a range of solid and spotted colors including black, gray, beige, brown, red, and white.',
    'Llamas are social animals and prefer to live with other llamas or herd animals.',
    'A group of llamas is called a herd.',
    'Llamas don\'t bite. They spit when they\'re agitated, but that\'s mostly at each other.',
    'Yarn made from llama fiber is soft and lightweight, yet remarkably warm.',
    'The Llamas scientific name is \"Lama Glama\".',
    'Llamas spit when annoyed.',
    'Though llamas are related to camels, they do not have humps.',
    'Llamas were first imported into the United States in the late 1800s to be displayed in zoos.',
    'When one llama has an issue with another llama, it will stick its tongue out to express its displeasure.'
    'Llamas can reach speeds up to 35mph.'
    'In the ancient Incan society, llamas were the only beast of burden, and were a symbol of wealth among the Incan nobility. Many times, llama figurines were buried with the dead.'
    'One of the ways llamas communicate is by humming.'
    'The metabolism of llamas is very similar to that of a human diabetic.'
    'Some ranchers and farmers use \"guard llamas\" to safeguard their sheep or other livestock.',
    )

MONGOOSE_FACTS = (
    'Mongooses are weasel-like creatures that belong to the group of Carnivores.',
    'Mongooses live around 4 years in the wild and up to 20 years in captivity.',
    'Mongooses use scents to announce their reproductive status and to mark territory.',
    'Mongooses have non-retractable claws which mean that they cannot hide them when they want. Their claws are visible all the time.',
    'Mongooses are primarily found in Africa, their range covering most of the continent. Some species occupy parts of southern Asia and the Iberian Peninsula.',
    'Mongooses normally have brown or gray grizzled fur, and a number of species sport striped coats or ringed tails.',
    'Mongooses live in burrows and are nondiscriminatory predators. They feed on small animals such as rodents, birds, reptiles, frogs, insects, and worms.',
    'Some mongoose (such as the Indian gray mongoose) are well known for their ability to fight and kill venomous snakes, particularly cobras.',
    'Most mongoose species are highly social animals living in busy groups of 6 to 40 individuals called "packs" or "mobs".',
    'Several species of mongoose routinely crack open eggs, nuts, or shelled creatures such as crabs or mollusks by dropping or throwing them on rocks.',
    'Mongooses are diurnal, which means that they are active during the day and sleep at night.',
    'Mongooses tend to live in burrows that other animals have abandoned. They rarely dig burrows on their own.',
    'The mongoose is a member of the civet family, smaller than a domestic cat but larger than a squirrel.',
    'In North America the mongoose has been prevented from establishing a breeding population except on tropical islands. There they do some $50 million in damage a year, principally to the poultry industry.',
    'Mongooses were introduced to Hawaii and Puerto Rico in the late 1800s to control rats on sugar plantations. This project was ineffective because mongooses hunt in the daytime, while rats come out at night.',
    'The ancient Egyptians domesticated wild mongooses and considered them sacred (mummified mongooses have been discovered in tombs).',
    'There are about 30 different species of mongooses.',
    'The mongoose is mainly a terrestrial mammal, meaning they live on land, but some species have adapted to living in tree tops or partially in water.',
    )

MONKEY_FACTS = (
    'There are currently 264 known monkey species.',
    'Monkeys can be divided into two groups, Old World monkeys that live in Africa and Asia, and New World monkeys that live in South America.',
    'A baboon is an example of an Old World monkey, while a marmoset is an example of a New World monkey.',
    'Apes are not monkeys. Most monkeys have tails.',
    'Some monkeys live on the ground, while others live in trees.',
    'Different monkey species eat a variety of foods, such as fruit, insects, flowers, leaves, and reptiles.',
    'Groups of monkeys are known as a ‘tribe’, ‘troop’, or ‘mission’.',
    'The Pygmy Marmoset is the smallest type of monkey, with adults weighing between 120 and 140 grams.',
    'The Mandrill is the largest type of monkey, with adult males weighing up to 35 kg.',
    'Capuchin monkeys are believed to be one of the smartest New World monkey species. They have the ability to use tools, learn new skills, and show various signs of self-awareness.',
    'Spider monkeys get their name because of their long arms, legs, and tail.',
    'The monkey is the 9th animal that appears on the Chinese zodiac, appearing as the zodiac sign in 2016.',
    'Barbary macaques are the only species of monkey endemic to Europe at this moment in time, they primarily reside in Gibraltar, south of Spain, and in Morocco as well.',
    )

MOOSE_FACTS = (
    'Moose are the largest members of the deer family, weighing as much as 1200 pounds.',
    'Moose are foragers and will devour 73 pounds of vegetation a day in the summer and 34 pounds in the winter.',
    'Moose prefer Balsam Fir over White Spruce and have consequently left White Spruce savannas on Isle Royale National Park due to their foraging habits.',
    'One moose can house 75,000 ticks in the winter, which are beginning to drive a startling trend of deaths in moose populations.',
    'Moose shed their antlers every winter, and grow back in the spring covered in vascularized velvet for blood flow.',
    'Moose antlers can weigh up to 40 pounds.',
    'In Isle Royale Nation Park, the moose and wolf predator relationship has been observed since 1959, and may be ending soon with the death of the final two wolves.'
    'The mother moose stays with her offspring for a year and a half, fighting off wolves and bears that try to pick off the young calves.',
    'A rare genetic defect can cause moose antlers to grow perpetually, resulting in a warped set of antlers. The Algonquian peoples mistook this moose as an evil spirit, and named it the Wendigo.',
    'The scientific name for a moose is Alces alces.',
    'Male moose, called bulls, bellow loudly to attract mates each September and October.',
    'The patch of skin that hangs from a moose neck is called a bell.',
    'Moose antlers can spread six feet across.',
    'Collisions between moose and motor vehicles are common in Scandinavia.',
    'Moose occur throughout Alaska, Canada, the northeastern United States and as far south as the Rocky Mountains in Colorado.',
    'A group of moose is know as a Herd.',
    'The moose has an average lifespan of 8 to 12 years in the wild.',
    'Moose can run up to 35 miles per hour.',
    )
    
MOUSE_FACTS = (
    'Despite their tiny bodies (and even smaller stomachs!), mice eat between 15 and 20 times a day. Because of their frequent eating habits, they prefer to build their homes near food sources.'
    'Mice in the wild, usually only live for about five months, mostly because of predators such as cats, snakes and foxes. In a lab setting, mice can live for up to two years.'
    'The house mouse is found all over the world, except for Antarctica. Mus musculus has roots in central Asia, but because of its extraordinary adaptability, its range has expanded to the rest of the globe.'
    'Mice are able to squeeze through gaps as small as 6mm.'
    'Mice rely on their other sense such as smell, hearing and touch to get around.'
    'Research shows that mice can hear ultrasound up to to 90kHz.'
    )

NARWHAL_FACTS = (
    'Unlike some whale species that migrate, narwhals spend their lives in the Arctic waters of Canada, Greenland, Norway, and Russia. Most narwhals winter for up to five months under sea ice in the Baffin Bay-Davis Strait area.',
    'Narwhals feed on Greenland halibut, Arctic and polar cod, squid and shrimp. They do their chomping at the ice floe edge and in the ice-free summer waters.',
    'Narwhals can dive a mile-and-a-half deep in the ocean. Cracks in the sea ice above allow them to pop up for air when they need it.',
    'Narwhals change color as they age. Newborns are a blue-gray, juveniles are blue-black, and adults are a mottled gray. Old narwhals are nearly all white.',
    'There are no narwhals in captivity. In the 60s and 70s, several attempts at capturing and keeping narwhals resulted in all of the animals dying within several months.',
    'The narwhal tusk—most commonly found on males—is actually an enlarged tooth with sensory capability and up to 10 million nerve endings inside. Some narwhals have up to two tusks, while others have none. The spiraled tusk juts from the head and can grow as long at 10 feet.'
    'A narwhal tusk\'s tough core and soft outer layer result in a tusk that is both strong and flexible. It can bend significantly without cracking.',
    'A narwhal\'s tusk can be used to detect changes in temperature, water pressure, or salinity, which help the narwhal survive and find prey.',
    'Narwhals are carnivorous animals that live anywhere from 30 to 55 years.',
    'There are no narwhals that kept captive. All previous attempts to capture and keep narwhals have resulted in death within several months.',
    'Narwhals commonly dive 500 meters and can dive up to 1,500 meters. They can stay submerged for over 25 minutes at a time.',
    'Narwhals feed near the ice edge and have been identified as one of the main species that would be affected by climate change.',
    'In addition to a large tusk, narwhals also have a second tusk. This is about 1 meter long, but remains embedded in the skull.  Males with two protruding tusks have been discovered.',
    'Female narwhals usually give birth once around every 3 years. The gestation period lasts around 14 months.',
    'Narwhals travel in groups of around 15-20 and can even form large groups of 100 narwhals.',
    'Narwhals inhabit the waters of the Arctic Circle, around Greenland and Canada.',
    'There is roughly as much vitamin C in one ounce of narwhal skin as there is in one ounce of oranges',
    'Narwhal skin is a primary source of vitamins for the Inuit people of the Arctic.',
    )

NEWT_FACTS = (
    'Newts are a type of salamander.',
    'There are more than 100 known species of newts found in North America, Europe, North Africa, and Asia.',
    'Unlike other members of the salamander family, Newts are semi-aquatic, spending part of their lives on land and part in the water.',
    'During their terrestrial juvenile phase, newts are called "efts" (after the Old English name for newts).',
    'At least once species of newt has gone extinct: the Yunnan lake newt.',
    'The Old English name for the newt was "efte," which later became "euft" or "ewt(e)." The term "newt" came from merging in the article "an" (i.e. "an ewte" --> "a newt").',
    'Newts can regenerate their limbs, eyes, spinal cords, hearts, intestines, upper and lower jaws.',
    'Newts are born as tadpoles, then undergo metamorphosis where they develop legs and their gills are absorbed and replaced by lungs.',
    'Many newts produce toxins, and some produce enough to kill a human, but the toxins are only dangerous if ingested.',
    'Newts are also known as Tritones in historical literature, after the mythological figure Triton.',
    'Alhough newts have air-breathing lungs, they also absorb oxygen and other substances through their water-permeable skin.',
    'The newt\'s thin, sensitive, water-permeable skin make it an excellent bioindicator (i.e. indicator of the health of an ecosystem or environment).',
    'One of the characteristics distinguishing newts from other salamanders is its relatively rougher skin.',
    'Several species of newt are considered threatened or endangered, including the Edough ribbed newt, Kaiser\'s spotted net, and the Montseny brook newt.',
    'In the UK, it is illegal to catch, possess, or handle great crested newts without a license.',
    )

NIGHTJAR_FACTS = (
    'Poets sometimes use the nightjar as an indicator of warm summer nights.',
    'Nightjar is a crepuscular and nocturnal bird in the nightjar family that breeds across most of Europe and temperate Asia.',
    'Drinking and bathing of a nightjar take place during flight.',
    'The Latin name of a nightjar (Caprimulgus) refers to the old myth that the nocturnal nightjar suckled goats, causing them to cease to give milk.',
    'The female nightjar does not sing.',
    'Nightjars have a unique serrated comb-like structure on the middle claw that is used to preen and perhaps remove parasites.',
    'Nightjars drink by dipping to the water surface as they fly.',
    'Estimates of the European population of the European nightjar range from 470,000 to more than 1 million birds, suggesting a total global population of 2–6 million individuals.',
    'The maximum known age of a nightjar in the wild is just over 12 years.',
    'In cold or inclement weather, several nightjar species can slow their metabolism and go into torpor.',
    'The European nightjar is a bird of dry, open country with some trees and small bushes.',
    'The male European nightjar\'s song is a sustained churring trill, given continuously for up to 10 minutes with occasional shifts of speed or pitch.',
    )

OCELOT_FACTS = (
    'An ocelot is two times bigger than domestic cat. It can reach 28 to 35 inches in length and weigh between 24 and 35 pounds. Males are bigger than females. The length of the tail measures half of the body size.',
    'Ocelots have beautiful fur which is the reason why people hunt them. Color of the fur is usually tawny, yellow, or grayish-brown, covered with black rosettes and stripes.',
    'Ocelots have pointed teeth that are used for biting and blade-like teeth that are used for tearing food. They do not have teeth for chewing so they swallow chunks of food.',
    'Ocelots have raspy tongues, which successfully removes every little piece of meat from bones.',
    'Ocelots are carnivores (meat-eaters). They eat rodents, monkeys, tortoises, armadillos, rabbits, birds, lizards, fish, snakes, etc...',
    'Ocelots have excellent eyesight (adapted to night vision) and sense of hearing, which are used for detection of the prey.',
    'Ocelots are nocturnal animals. During the day, they rest in hollow trees, on branches, or dense vegetation.',
    'Due to its smaller size, ocelots are an easy prey for larger cats (such as jaguars and pumas), birds of prey (eagles), and large snakes (anaconda).',
    'Unlike other cat species, ocelots are not afraid of the water. They are excellent swimmers.',
    'Ocelots are territorial and solitary creatures. Males usually live in a territory of 30 square meters. Females occupy a territory that is two times smaller.',
    'Ocelots are active 12 hours a day. During that time, ocelots may travel up to 7 miles while they search for food.',
    'The average lifespan of an ocelot is 10 to 13 years in the wild and up to 20 years in captivity.',
    )

OCTOPUS_FACTS = (
    'There are around 300 species of octopus, usually located in tropical and temperate ocean waters. They are divided into finned deep-sea varieties that live on the ocean floor and finless, shallow water varieties found around coral reefs.',
    'Octopuses have two eyes in a globe-shaped head (mantle) off which protrude eight long limbs called tentacles that have two rows of sucker senses.',
    'Octopuses can squeeze into tight spaces as they are invertebrates which means they have no skeleton, although some species have a protective casing in their mantles.',
    'An octopus has a hard beak, like a parrot beak, which they use to break into and eat their pray such as crabs and shellfish.',
    'Octopuses have three hearts.',
    'The largest octopus is believed to be the giant Pacific octopus, Enteroctopus dofleini which weigh about 15 kg (33 lb), and has an arm span up to 4.3 m (14 ft).',
    'Octopuses are believed to be highly intelligent compared to other invertebrates.',
    'An octopus\'s main defense against predators such as sharks is to hide and camouflage itself by using certain skin cells to change its color. This can also be used to talk with or warn other octopuses.',
    'Octopuses can eject a thick, blackish ink in a large cloud to distract a predator while the octopus uses a siphon jet propulsion system to quickly swim away headfirst, with arms trailing behind.',
    'A last ditch defense is for the octopus to shed a tentacle similar to how a gecko or lizard can discard a tail. An octopus is able to regenerate a lost tentacle.',
    'Not all jellies have tentacles',
    'Octopuses have very good eyesight and an excellent sense of touch.',
    'A female octopus can lay on average about 200,000 eggs, however, fending for themselves only a handful of the hatchlings will survive to adulthood.',
    'Octopuses usually live for 6 - 18 months. Males only live a few months after mating, and females die of starvation shortly after their protected eggs hatch.',
    'Humans eat octopus in many cultures and it is also a popular fish bait.',
    )

OPOSSUM_FACTS = (
    'The opossum is a marsupial endemic to the Americas.',
    'Due to their unspecialized biology, flexible diet and reproductive habits, opossums have successfully colonized diverse locations.',
    'Opossums have remarkably strong immune systems and show partial or total immunity to the venom of rattlesnakes, cottonmouths, and other pit vipers. They are also resistant to rabies.',
    'All opossums have prehensile tails, and females have pouches.',
    'When threatened or harmed, adult opossums will \'play dead\', and this is the origin of the expression \'to play possum\'',
    'Opossum was traditionally eaten across the Americans, but is now eaten mainly in certain Carribean islands.',
    'A baby opossum is called a joey, mirroring their Australian marsupial cousins, such as kangaroos.',
    'Opossums typically live between two and four years.',
    'The opossum is typically known as a \'possum\' in the southern United States.',
    'The gestation period of an opossum is short, typically between 12 and 14 days, largely due to the species being marsupial, and having some functions of gestation occur once out of the womb.',
    'Opossums have 13 nipples, arranged in a circle of 12 with one in the middle.',
    )

ORANGUTAN_FACTS = (
    'Orangutans’ arms stretch out longer than their bodies – up to 8 ft. from fingertip to fingertip in the case of very large males.',
    'When on the ground, orangutans walk on all fours, using their palms or fists. Unlike the African apes, orangutans are not morphologically built to be knuckle-walkers.',
    'For the first few years of his/her life, a young orangutan holds tight to his/her mother’s body as she moves through the forest canopy.',
    'When male orangutans are fighting, they charge each other, grapple, and bite each other’s heads and cheekpads.',
    'Orangutans have tremendous strength, which enables them to brachiate and hang upside-down from branches for long periods of time to retrieve fruit and eat young leaves.',
    'From the age of thirteen years (usually in captivity) past the age of thirty, male orangutans may develop flanges of large size.',
    'Orangutans have the longest birth interval of any mammal. On average they only give birth once every 8 to 10 years.',
    'Orangutans are very smart. They perform as well as chimpanzees and gorillas in tests of cognitive ability. In captivity, they are excellent tool-users and versatile tool-makers. One captive orangutan was taught how to chip a stone hand-axe.',
    'Orangutans are red-haired apes that live in the tropical rainforests of Sumatra and Borneo in southeast Asia.',
    'The orangutan is one of humankind’s closest relatives – in fact, we share nearly 97 percent of the same DNA!',
    'Orangutans are daytime eaters, their diet consists mostly of fruit and leaves – but they also eat nuts, bark, insects and, once in a while, bird eggs, too.',
    'These amazing apes generally have long lives – in captivity orangutans can live for 50-60 years, and in the wild, 30-40 years.',
    'Orangutans live in the trees to avoid predators like tigers or leopards that hunt on the ground.',
    'Orangutans are solitary animals. Males always live on their own while females live alone or with their offspring. Males and females spend time together only during mating season.',
    'Orangutans are the largest arboreal mammals (animals that spend their life in the trees).',
    'Nonja, a Orangutan at Zoo Schoenbrunn in Vienna, Austria, has her own Facebook page, where pictures taken by her are uploaded. She also got famous for creating some paintings, showing Orangutans abilities to use tools.',
    )

ORYX_FACTS = (
    'Oryxes are species of antelope native to Africa and the Arabian Peninsula.',
    'The Arabian oryx was only saved from extinction through a captive breeding program and reintroduction to the wild.',
    'Small populations of several oryx speciies, such as the scimitar oryx, exist in Texas and New Mexico in wild game ranches.',
    'White oryxes are known to dig holes in the sand for the sake of coolness.',
    'The smallest species of oryx is the Arabian oryx. It became extinct in the wild in 1972, but was reintroduced in 1982 in Oman.',
    'The Arabian oryx was the first speicies to have its threat category downgraded from \'Extinct in the Wild\' to \'Vulnerable\'.',
    'All oryx species prefer near-desert conditions and can survive without water for long periods of time.',
    'Oryxes live in herds in numbers up to 600.',
    'Newborn oryx calves are able to run with their herd immediately after birth.',
    'Oryxes have been known to kill lions with their horns.',
    'Oryx horns make the animals a prized game trophy, which has led to the near-extinction of the two northern species.',
    )

ORCA_FACTS = (
    'The orca\'s large size and strength make it among the fastest marine mammals, able to reach speeds in excess of 55 km/h.',
    'Many orcas live with their mothers for their entire lives.',
    'The orca is not a fish, but a mammal. However it is not a whale, as it is part of the dolphin family.',
    'The largest orca caught was 10 meters long and weighed 10 tons, as heavy as an African elephant.',
    'Orcas live in groups of related females, led by the oldest female, called pods. A pod can have as few as three members or as many as one hundred or more.',
    'Orcas do not have smelling organs or a lobe in the brain dedicated to smelling, so it is believed they cannot smell.',
    'Orcas can sleep with one eye open, like dolphins, as they cannot completely go to sleep, having to go to the surface to get air from time to time.',
    'In captivity, an orca\'s dorsal fin often flops. This is possible as the fin is not made up of bones, but of large connective tissue.',
    'Orcas are the most widely distributed animals in the world, not counting humans. They can be found in all oceans, both in warm and cold waters and even in freezing waters.',
    'The oldest known orca lived to be 103.',
    'There is no record of a wild orca ever attacking a human.',
    'There are fifty-two orcas in captivity all over the world.',
    'Mother orcas give birth every three to ten years, after a 17-month pregnancy.',
    'In Argentina, orcas hurl themselves on-shore to grab sea lion pups.',
    'Whalers call the orca the \'killer of whales\'. It preys on sperm, gray, fin, humpback, and other whales.',
    'Orcas can weigh up to 6 tons.',
    'An orca\'s teeth can grow to be 4 inches (10 cm) long.',
    'The orca can reach speeds in excess of 30 knots (about 34 mph, or 56 kph).',
    'Resident orcas, the most commonly-sighted type of orcas, have a diet consisting primarily of fish and squid, while transient orcas feed on marine mammals.',
    )

OSTRICH_FACTS = (
    'Ostriches have three stomachs.',
    'An ostrich can run at 30 miles per hour for 10 miles at a time',
    'Ostriches in the wild live an average of 30 to 40 years',
    'Ostrich eggs contains 2000 calories, and measure 6 inches in diameter',
    'Ostriches are the largest and heaviest birds in the world',
    'The scientific name for an ostrich is Struthio camelus, from the Struthio genus of ratite family from Africa.',
    'Ostrich often swallows pebbles and sand that aid them in grinding up their ingested food in its gizzard, a peculiar muscular stomach.',
    'Ostrich are the only bird in the world that have only two toes on each foot. The inner toe has a claw that can measure up to 10 cm long.',
    'At breeding time, male ostriches scrape out a nest in the ground which is then used by more than one female to lay their eggs which can end up with 20 eggs in them. Females incubate the eggs during the day and males at night. The dads then do most of the chick raising, often defending the chicks from potential predators with their powerful kicks.',
    'Contrary to popular belief, ostriches do not bury their heads in sand. This myth likely began with Pliny the Elder (AD 23-79), who wrote that Ostriches: “imagine, when they have thrust their head and neck into a bush, that the whole of their body is concealed".',
    )

OTTER_FACTS = (
    'The otter is a carnivorous mammal in a branch of the weasel family called Lutrinae.',
    'There are 13 species of otter found all around the world.',
    'Some otter species spend all their time in the water while others are land and water based animals.',
    'An otter\'s den is called a \'holt\' or a \'couch\'.',
    'A group of otters are called a \'bevy\', \'family\', \'lodge\', or \'romp\', or, when in water the group is called a \'raft\'.',
    'Otters live up to 16 years in the wild.',
    'Otters are very active hunters, spending many hours a day chasing prey through water or scouring the rivers and the sea bed. They mainly eat fish but also frogs, crayfish, and crabs, some species carry a rock to help smash open shellfish.',
    'Otter species range in size from the smallest Oriental small-clawed otter at 0.6 m (2 ft) and 1 kg (2.2 lb). Through to the large Giant otter and Sea otters who can reach 1.8 m (5.9 ft) and 45 kg (99.2 lb).',
    'Four of the main otter species include the European otter, the North American river otter, the Sea otter, and the Giant otter.',
    'The European otter or Eurasian otter, are found in Europe, Asia, parts of North Africa, and the British Isles.',
    'The North American river otter was one of the most hunted animals for its fur after Europeans arrived. Sea otters have also been hunted in large numbers for their fur.',
    'Unlike most marine mammals, otters do not have a layer of insulating blubber. Instead, air is trapped in their fur which keeps them warm.',
    'The Giant otter is found in South America around the Amazon river basin.',
    'The otter is a very playful animal and are believe to take part in some activities just for the enjoyment. Some make waterslides to slide down into the water!',
    'Otters are a popular animal in Japanese folklore where they are called "kawauso". In these tales the smart kawauso often fool humans, kind of like a fox.',
    )

OWL_FACTS = (
    'Owls are nocturnal and hunt at night.',
    'There are around 200 different owl species.',
    'A group of owls is called a parliament.',
    'Most owls hunt insects, small mammals, and other birds.',
    'Some owl species hunt fish. Owls have powerful talons which help them catch and kill prey.',
    'Owls can turn their heads as much as 270 degrees.',
    'Owls are farsighted, meaning they can’t see things close to their eyes clearly.',
    'Owls are very quiet in flight compared to other birds of prey.',
    'The color of owl’s feathers helps them blend into their environment (camouflage).',
    'Barn owls can be recognized by their heart shaped face.',
    )

PANDA_FACTS = (
    'The giant panda is native to China. It has a black and white coat that features large black patches around its eyes.',
    'Pandas are an endangered species. Population estimates vary but there may be around 2000 left living in the wild.',
    'A giant panda cub weighs only around 150 grams (5 oz) at birth.',
    'Adult male pandas can weigh up to 150 kg (330 lb).',
    'Giant panda have a lifespan of around 20 years in the wild.',
    'Female pandas raise cubs on their own (the male leaves after mating).',
    'The diet of a panda is made up almost entirely of bamboo.',
    'Giant pandas eat as much as 10 kg (22 lb) of bamboo a day.',
    'Despite their appearance, Giant pandas are good climbers.',
    'The scientific name for the giant panda is ‘ailuropoda melanoleuca’.',
    'An animated movie from 2008 named ‘Kung Fu Panda’ features a giant panda called ‘Po’.',
    )

PANGOLIN_FACTS = (
    'The name "pangolin" comes from the Malay word pengguling, meaning "one who rolls up".',
    'Pangolins can also emit a noxious-smelling chemical from glands near the anus, similar to the spray of a skunk.',
    'Large pangolins can extend their tongues as much as 40 cm (16 in), with a diameter of only 0.5 cm (0.20 in).',
    'A pangolin can consume 140 to 200 g (4.9 to 7.1 oz) of insects per day.',
    'Pangolins have very poor vision, so they rely heavily on smell and hearing.',
    'Pangolins lack teeth, so also lack the ability to chew.',
    'The weight of a pangolin at birth is 80 to 450 g (2.8 to 15.9 oz) and the average length is 150 mm (5.9 in).',
    'Pangolin meat is considered a delicacy in southern China and Vietnam.',
    'Pangolin is the most trafficked animal in the world.',
    'All eight species of pangolin are categorized on IUCN Red List of Threatened Species.',
    )

PANTHER_FACTS = (
    'The animal known as a "panther" actually refers to 3 different types of big cats, leopards (Panthera pardus), or jaguars (Panthera onca) that have a black or white color mutation and a subspecies of the cougar (Puma concolor).',
    'The \'black panther\' is a black jaguar of the Americas or a black leopard of Asia and Africa. In fact, the black panther actually has normal rosettes (spots), they are often just too hard to see because the animal\'s fur is so dark. Melanism is the name of the dark color pigmentation mutation in a jaguar or leopard that cause the fur to be blackish, it occurs in about 6 percent of the population.',
    'The opposite of melanism is albinism which is an even rarer mutation that can occur in most animal species. The extremely rare "white panther" are albino leopards, jaguars, or cougars.',
    'Because the melanism gene is a dominant gene in jaguars, a black jaguar may produce either black or spotted cubs, while a pair of spotted jaguars can only have spotted cubs.',
    'Apart from color the black panther is believed to be less fertile than normal-colored big cats and also much more unpredictable and aggressive.',
    'Black panthers are great swimmers and are one of the strongest tree climbing big cats, often pouncing on prey from a tree. They are capable of leaping up to 20 feet to catch their prey, which includes medium sized animals like deer and monkeys, and smaller rabbits and birds.',
    'Black panthers have good hearing, extremely good eyesight, and a strong jaw.',
    'The black panther is often called \'the ghost of the forest\'. It is a smart, stealth-like attacker, its dark coat helps it hide and stalk prey very easily, especially at night.',
    'The light tan colored Florida panther is one of over 30 subspecies of cougar (Puma concolor) found in North America.',
    'The Florida panther has adapted to the subtropical forests and swamp environments of Florida, however they are very rare animals, as of 2013 it is believed only 160 Florida panthers remain in the wild.',
    )

PARROT_FACTS = (
    'There are around 372 different parrot species.',
    'Parrots are believed to be one of the most intelligent bird species. Some species are known for imitating human voices.',
    'Most parrot species rely on seeds as food. Others may eat fruit, nectar, flowers, or small insects.',
    'Parrots such as the budgerigar (budgie) and cockatiel, are popular as pets.',
    'Some parrot species can live for over 80 years.',
    'There are 21 different species of cockatoo.',
    'Cockatoos usually have black, grey, or white plumage (feathers).',
    'Keas are large, intelligent parrots that live in alpine areas of New Zealand’s South Island. They are the world’s only alpine parrot and are known for their curious and sometimes cheeky behaviour near ski fields where they like to investigate bags, steal small items, and damage cars.',
    'Kakapos are critically endangered flightless parrots and as of 2010, only around 130 are known to exist. They are active at night (nocturnal) and feed on a range of seeds, fruit, plants, and pollen. Kakapos are also the world’s heaviest parrot.',
    'The flag of Dominica features the sisserou parrot.',
    'Parrot toes are configured for maximum grip: two in front and two behind, like two pairs of opposable thumbs.',
    'Due to a combination of habitat destruction and persistent poaching for the pet trade, parrot species regularly land on the IUCN Red List of Threatened Species.',
    'The males and females of most parrot species look virtually identical.',
    'Psittacofulvins, a bacteria-resistant pigment that only parrots are known to produce, give the birds’ feathers their red, yellow, and green coloration.',
    'Many parrots have near-human lifespans.',
    )

PEACOCK_FACTS = (
    '"Peacock" is commonly used as the name for a peafowl of the pheasant family. But in fact "peacock" is the name for the colorfully plumaged male peafowl only. The females are called peahens, they are smaller and grey or brown in color. The name of a baby peafowl is a peachick.',
    'Peacocks are best known for their amazing eye-spotted tail feathers or plumage. During a display ceremony, the peacock will stand its tail feathers up to form a fan that stretches out nearly 2 m in length.',
    'A peacock\'s colourful display is believed to be a way to attract females for mating purposes, and secondly to make the peacock look bigger and intimidating if he feels threatened by predators.',
    'There are 3 varieties of peafowl, the Indian, the Green, and the Congo.',
    'The most common type of peafowl found in many zoos and parks around the world is the Indian peafowl. The head and neck of which is covered in shining, blue feathers arranged like scales. It is native to South Asia areas of Pakistan, Sri Lanka, and India (where it is the national bird).',
    'The Congo peafowl is native to Central Africa. It doesn\'t have a large plumage like other varieties. It is the national bird of the Democratic Republic of Congo.',
    'The Green peafowl is native to Southeast Asia, it has chrome green and bronze feathers. It lives in areas such as Myanmar (its national symbol) and Java. It is regarded as an endangered species due to hunting and a reduction in its habitat.',
    'White varieties of peacocks are not albinos, they have a genetic mutation that causes the lack of pigments in the plumage.',
    'Peacock feathers accounts for 60 percent of the bird\'s total body length and with a wingspan measuring 5 feet, it is one of the largest flying birds in the world.',
    'A peafowl can live to over the age of 20 years, the peacocks plumage looks its best when the male reaches the age of 5 or 6.',
    'Peacocks have spurs on their feet that are primarily used to fight with other males.',
    'Peafowl are omnivorous, they eat many types of plants, flower petals, seeds, insects, and small reptiles such as lizards.',
    'In Hindu culture, Lord Karthikeya, the god of war, is said to ride a peacock.',
    )

PECCARY_FACTS = (
    'Peccaries are found throughout Central and South America and in the southwestern area of North America.',
    'A peccary is a medium-sized animal, with a strong resemblance to a pig.',
    'Peccaries are omnivores, and will eat insects, grubs, and occasionally small animals, although their preferred foods consist of roots, grasses, seeds, fruit, and cacti—particularly prickly pear.',
    'Pigs and peccaries can be differentiated by the shape of the canine tooth, or tusk. In European pigs, the tusk is long and curves around on itself, whereas in peccaries, the tusk is short and straight.',
    'By rubbing the tusks together, Peccaries can make a chattering noise that warns potential predators not to get too close.',
    'Peccaries rely on their social structure to defend territory, protect against predators, regulate temperature, and interact socially.',
    'Three (possibly four) living species of peccaries are found from the southwestern United States through Central America and into South America and Trinidad.',
    'Peccary fossils have been found in all continents except Australia and Antarctica.',
    'Although they are common in South America today, peccaries did not reach that continent until about three million years ago during the Great American Interchange, when the Isthmus of Panama formed, connecting North America and South America.',
    'In many countries, especially in the developing world, peccaries are raised on farms as a source of food for local communities.',
    )

PENGUIN_FACTS = (
    'While other birds have wings for flying, penguins have adapted flippers to help them swim in the water.',
    'Most penguins live in the Southern Hemisphere.',
    'The Galapagos Penguin is the only penguin specie that ventures north of the equator in the wild.',
    'Large penguin populations can be found in countries such as New Zealand, Australia, Chile, Argentina, and South Africa.',
    'No penguins live at the North Pole.',
    'Penguins eat a range of fish and other sealife that they catch underwater.',
    'Penguins can drink sea water.',
    'Penguins spend around half their time in water and the other half on land.',
    'The Emperor Penguin is the tallest of all penguin species, reaching as tall as 120 cm (47 in) in height.',
    'Emperor Penguins can stay underwater for around 20 minutes at a time.',
    'Emperor Penguins often huddle together to keep warm in the cold temperatures of Antarctica.',
    'King Penguins are the second largest penguin. They have four layers of feathers to help keep them warm on the cold subantarctic islands where they breed.',
    'Chinstrap Penguins get their name from the thin black band under their head. At times it looks like they’re wearing a black helmet, which might be useful as they’re considered the most aggressive type of penguin.',
    'Crested penguins have yellow crests, as well as red bills and eyes.',
    'Yellow eyed penguins (or Hoiho) are endangered penguins native to New Zealand. Their population is believed to be around 4000.',
    'Little Blue Penguins are the smallest type of penguin, averaging around 33 cm (13 in) in height.',
    'Penguins’ black and white plumage serves as camouflage while swimming. The black plumage on their back is hard to see from above, while the white plumage on their front looks like the sun reflecting off the surface of the water when seen from below.',
    'Penguins in Antarctica have no land based predators.',
    )

PIG_FACTS = (
    'Pigs are intelligent animals. Some people like to keep pigs as pets.',
    'A pig’s snout is an important tool for finding food in the ground and sensing the world around them.',
    'Pigs have an excellent sense of smell.',
    'There are around 2 billion pigs in the world.',
    'Humans farm pigs for meat such as pork, bacon, and ham.',
    'Wild pigs (boar) are often hunted in the wild.',
    'In some areas of the world, wild boars are the main source of food for tigers.',
    'Feral pigs that have been introduced into new areas can be a threat to the local ecosystem.',
    'Pigs can pass a variety of diseases to humans.',
    'Relative to their body size, pigs have small lungs.',
    'Contrary to popular belief, pigs are actually considered to be very clean animals.',
    'Pigs cannot sweat, so they bathe in water and mud to cool themselves off.',
    'When pigs have ample space, they will try not to soil in the areas where they sleep and eat.',
    'Almost half the pigs in the world are owned by farmers in China.',
    )

PIGEON_FACTS = (
    'The size of a of pigeon depends on the species. Large pigeons can reach 19 inches in length and weigh 8.8 pounds. Small pigeons can reach 5 inches in length and weigh up to 0.8 ounces.',
    'Pigeons can have dull or colorful plumage, depending on the habitat and type of diet. The most common type of pigeon (that lives in the cities) has grayish plumage. On average, a pigeon has 10,000 feathers on their body.',
    'Pigeons have strong muscles used for flying. They can fly at the altitude of 6000 feet.',
    'Pigeons can move their wings ten times per second and maintain heartbeats at the rate of 600 times per minute.',
    'Pigeons can fly at the speed of 50 to 60 miles per hour. The fastest known pigeon managed to reach a speed of 92 miles per hour.',
    'Because of their incredible speed and endurance, pigeons are used for racing. Winners of 400 mile long races can earn million dollars.',
    'Pigeons were used as mail carriers during the First and Second World War. They saved numerous lives by delivering information while under enemy fire.',
    'Pigeons are herbivores. Their diet consists of seeds, fruits, and various plants.',
    'Pigeons are highly intelligent animals. They are able to recognize themselves in the mirror, to find the same person in two different pictures, and to recognize all letters of the English alphabet.'
    'Pigeons have exceptional eyesight and the ability to identify objects at a distance of 26 miles.',
    'Pigeons have a very sensitive sense of hearing. They are able to detect distant storms, earthquakes, and volcanic eruptions.',
    'Pigeons are social animals that live in the groups (flocks) composed of 20 to 30 animals.',
    'Pigeons are monogamous creatures. Pigeon couples can produce up to 8 broods per year when food is abundant.',
    'Female pigeons lay 2 eggs that hatch after an incubation period of 18 days. Young birds depend on their parents during the first two months of their life. Both parents take care of the chicks (called squabs).',
    'Pigeons can survive more than 30 years in the wild.',
    )

PLATYPUS_FACTS = (
    'Platypuses have no stomach',
    'A platypus\' bill is comprised of thousands of cells that can detect the electric fields generated by all living things, giving them a sixth sense',
    'Researchers have discovered a pre-historic platypus that was over 1 meter long, double the size of the modern animal.',
    'Platypuses nurse without nipples, milk oozing from the mammary glands on the abdomen of females and babies drink it by sucking on their mother\'s fur.',
    'Platypuses males have venomous spurs that only activate during mating season, indicating it is meant to fend off competing males',
    'When the first platypus specimen was sent back to England from Australia, scientists thought it was a hoax and that someone was playing a trick on them.',
    'Platypuses use gravel as makeshift teeth as they lack teeth inside their bill, making it hard to chew.',
    'A platypus\' tail holds half of the animal\'s body fat in case of food shortage.',
    'Platypuses have dense, thick fur that helps them stay warm underwater. Most of the fur is dark brown, except for a patch of lighter fur near each eye, and lighter-colored fur on the underside.',
    'Platypuses only live in freshwater areas that glow through the island of Tasmania, and the eastern and southeastern coast of Australia.',
    'Platypuses are the only mammals that lay eggs, a category called monotremes.',
    'Platypuses fur, being very thick and waterproof, used to be very popular in the fur trade until Australia banned platypus hunting to protect the species.',
    'Platypuses is the correct plural form, although platypi and platypodes are also accepted.',
    )

PUMA_FACTS = (
    'The puma concolor is also known as cougar and montain lion, but is referred to as puma by most scientists.',
    'Pumas are member of the felinae family, they are the largest of small cats.',
    'Pumas are fast, they can run up to 80kph (50mph).',
    'In the wild, pumas live up to 13 years.',
    'In captivity, pumas live up to 20 years.',
    'Unlike cats, pumas cannot roar.',
    'Baby pumas are called cubs and born after a period of gestation of approximately 91 days.'
    'From head to tail, puma\'s size varies between 1.5 and 2.7 meters (5 and 9 feet).',
    'Pumas can live anywhere, in montain, desert, or even sea-level, once there is shelter and prey.',
    'Puma are obligated carnivores (like all cats), they need to feed on meat to survive.',
    'Puma cubs born blind, they rely exclusively on their mother and begin to hunt after six months.',
    'Puma cubs begin to be weaned around three months of age.',
    )

PUFFERFISH_FACTS = (
    'Puffer fish vary in size from one inch long pygmy puffer, to a two feet long freshwater giant puffer.',
    'Scientists believe that puffer fish developed their puffing tactic as a method of self defense because they are poor swimmers that cannot escape from danger quickly.',
    'Sharks are the only species immune to the puffer fish\'s toxin. They can eat puffer fish without any negative consequences',
    'Puffer fish do not have scales. Their skin is thick and rough. Some species have spines on their skin, which offer additional protection against predators.',
    'Puffer fish toxin is found in only certain parts of the fish. Specially trained chefs cut away the edible flesh and serve it as a dangerous delicacy.',
    'Puffer fish have a set of four teeth that make a \'beak\' which the fish uses to open mussels, clams, and shellfish',
    'The average lifespan of the puffer fish is around 10 years',
    )

PORCUPINE_FACTS = (
    'The body of the porcupine is covered with sharp spines or quills.',
    'Some porcupines have up to 30,000 quills on their body.',
    'Porcupines can\'t shoot out their quills, but they will be easily released when predators touch the animal.',
    'When porcupines lose a quill, they are replaced with a new one.',
    'Porcupines are nocturnal animals. This means that they sleep during the day and become active in the evening.',
    'Porcupines use their strong feet and curved claws to climb trees. They are excellent climbers.',
    'A porcupine\'s home is called a den.',
    'Porcupines are herbivorous animals (they only eat plants). They like to eat leaves, stem, bark, fruit, etc.',
    'Porcupines can live a solitary life (left on their own) or in small groups of up to 6 members.',
    'During mating season, the female porcupine initiates close contact with male.',
    'Female porcupines usually give birth to 2 babies. Both parents will raise them.',
    'Baby porcupines are called porcupettes, and they are born with soft quills. Soft quills will harden in a few hours after birth.',
    'Young porcupine will leave its parents after a couple of months and begin its solitary life.',
    'Native Americans used porcupine quills to decorate themselves. They also used porcupines as a source of food.',
    'Porcupines can live 15-18 years.',
    )

PRAYINGMANTIS_FACTS = (
    'Mantises are distributed worldwide in temperate and tropical habitats.',
    'Mantises have triangular heads with bulging eyes supported on flexible necks.',
    'All Mantodea have forelegs that are greatly enlarged and adapted for catching and gripping prey and their upright posture, while remaining stationary with forearms folded, has led to the common name praying mantis.',
    'The closest relatives of mantises are the termites and cockroaches (Blattodea), which are all within the superorder Dictyoptera.',
    'Mantises are mostly ambush predators, but a few ground-dwelling species are found actively pursuing their prey.',
    'A mantis normally lives for about a year. In cooler climates, the adults lay eggs in autumn, then die.  The eggs are protected by their hard capsules and hatch in the spring.',
    'Female mantises sometimes practice sexual cannibalism, eating their mates after copulation.',
    'Mantises were considered to have supernatural powers by early civilizations, including Ancient Greece, Ancient Egypt, and Assyria.',
    'Mantises are among the insects most commonly kept as pets.',
    'Mantises have stereo vision. They locate their prey by sight; their compound eyes contain up to 10,000 ommatidia (clusters of photoreceptor cells).',
    )

QUOKKA_FACTS = (
    'Quokkas can go months without drinking; they get most of the water they need through the vegetation they eat.',
    'Quokkas are only found on small islands off the coast of Western Australia, Rottnest Island off of Perth, and Bald Island near Albany.',
    'Quokkas are small marsupials in the macropod family (like kangaroos) that are about the size of a housecat.',
    'Quokkas are mostly nocturnal; they sleep during the day and are active at night.',
    'Quokkas are herbivores. They eat mostly grasses and leaves.',
    'Quokkas are the only member of the genus Setonix',
    'Quokkas do not fear humans and will approach people closely if you visit them on Rottnest Island. However, it is illegal for humans to handle or feed them.',
    'Rottnest Island in Australia, where many quokkas live, was given its name when a Dutch explorer mistook the quokkas for rats. The name means "rat nest" in Dutch.',
    'A baby quokka is called a joey. Females can give birth to joeys twice a year. The joey will live in the pouch of its mother for six months.',
    )

RABBIT_FACTS = (
    'A rabbit’s teeth never stop growing, which is why it is very important to provide chews and treats for them to keep their teeth from becoming overgrown.',
    'Rabbits have 28 teeth.',
    'When rabbits are happy they can jump and twist. This is commonly called a "binky."',
    'The average size of a rabbit litter is usually between 4 and 12 babies, just after a short 30-day pregnancy.',
    'More than half of the world’s rabbits live in North America.',
    'Jackrabbits, which belong to the genus “Lepus”, have been clocked at speeds of 45 miles per hour.',
    'Rabbits have a life span about 8 years, though sterilized rabbits (those who are spayed/neutered) can live as long as 10-12 years.'
    'A rabbit can run between 25-45 miles per hour.',
    'Rabbits sleep about 8 hours a day.',
    'Rabbits cannot vomit. They don’t have enough muscles in their stomach.',
    'A male rabbit is called a buck, a female is a doe, and a baby is a kit/kitten.',
    'Rabbits are not the same species as hares, which, among other things, are larger and less social.',
    )

RACCOON_FACTS = (
    'The raccoon has the ability to rotate their hind feet a full 180 degrees which gives them the ability to climb down from trees head first.',
    'On the mammal IQ scale, raccoons rank higher than cats and just below monkeys.',
    'The raccoon’s scientific name, Procyon lotor, means “washer dog” although it is a closer relative to the bear family.',
    'Raccoon rabies makes up almost half of all wildlife rabies cases that are reported in the U.S.',
    'Raccoons range in weight from about 12-35 pounds and up to 50 percent of their body weight can be made up of fat.',
    'Breeding season for raccoons is between January and June, and they do not have more than one litter per year. Litters are anywhere from 1-7 babies.',
    'Raccoons can live up to 16 years in the wild, but most do not make it past 2.',
    'Raccoon pelts are sometimes sold as imitation mink, otter, or even seal fur.',
    'Raccoons climb with great ease and are not bothered by a drop of 35 to 40 feet!',
    'The raccoon is the official animal of Tennessee!',
    'Bandit-masked raccoons are a familiar sight just about everywhere, because they will eat just about anything. These ubiquitous mammals are found in forests, marshes, prairies, and even in cities.',
    'In the natural world, raccoons snare a lot of their meals in the water. These nocturnal foragers use lightning-quick paws to grab crayfish, frogs, and other aquatic creatures.',
    'Raccoons have a large array of vocalizations. Scientists have determined that they can make over 51 different sounds! They purr, whistle, growl, hiss, scream, and even whinny.',
    'Bobcats, great horned owls, wolves, eagle owls, lynxes, and coyotes are the most common predators of raccoons, but cars kill more raccoons than anything.',
    'Dakota Sioux believed that raccoons possessed supernatural powers.',
    )

RATTLESNAKE_FACTS = (
    'Rattlesnakes receive their name from the rattle located at the end of their tails, which makes a loud rattling noise when vibrated that deters predators or serves as a warning to passers-by.',
    'Rattlesnake babies are born with what is called a pre-button. The baby snake loses this piece when it sheds its skin for the first time. With the shedding a new button appears. With every shedding after that another button, or rattle, will be added. These buttons are made up of a material called Keratin, which is what scales and your fingernails are made of!',
    'The rattles are empty, so what makes the noise? The noise comes from each segment knocking together, so until a rattlesnake has two or more pieces it isn’t going to make a sound! But when it does… you WILL hear it… and you WILL RUN!',
    'The 36 known species of rattlesnakes have between 65 and 70 subspecies, all native to the Americas, ranging from southern Alberta and southern British Columbia in Canada to central Argentina.',
    'Newborn rattlesnakes are heavily preyed upon by a variety of species, including ravens, crows, roadrunners, raccoons, opossums, skunks, coyotes, weasels, whipsnakes, kingsnakes, and racers.',
    'Rattlesnakes feed on rodents, squirrels, rabbits, and other small critters.',
    'Rattlesnakes are believed to require at least their own body weight in water annually to remain hydrated. The method in which they drink depends on the water source. In larger bodies of water (streams, ponds, etc.), they submerge their heads and ingest water by opening and closing their jaws, which sucks in water. If drinking dew, or drinking from small puddles, they sip the liquid either by capillary action or by flattening and flooding their lower jaws.',
    'Rattlesnakes are a key element in Aztec mythology and were widely represented in Aztec art, including sculptures, jewelry, and architectural elements.',
    'Members of some Christian sects in the southern United States are regularly bitten while participating in "snake handling" rituals. Snake handling is when people hold venomous snakes, unprotected, as part of a religious service inspired by a literal interpretation of the Bible verses Mark 16:17-18 which reads, "In my name ... they will pick up snakes with their hands".',
    'The rattlesnake became a symbolic animal for the Colonials during the Revolutionary War period, and is depicted prominently on the Gadsden Flag. It continues to be used as a symbol by the United States military, and political movements within the United States.',
    'Rattlesnakes hibernate through the winter and come out in the spring to eat and mate.',
    'Rattlesnake eggs will stay inside their mother until they hatch. Most of the time, there are 8-10 babies born at once, each about 10 inches long. Babies are born venomous but cannot rattle and are often more aggressive than the adults.',
    'Rattlesnakes can range from one to eight feet, depending on the species (the big one is the eastern diamondback), according to the National Wildlife Federation. They are thick-bodied snakes with keeled (ridged) scales in a variety of colors and patterns. Most species are patterned with dark diamonds, rhombuses, or hexagons on a lighter background.',
    'The size of a rattlesnake depends on the species. The largest species can reach length of 8 feet. On average, rattlesnakes are 3 to 4 feet long.',
    'Rattlesnakes are not very colorful because they like to camouflage with their environment. They are usually black, brown, olive, or gray in color.',
    'The rattlesnake rattle grows continuously. A new segment is added each time the snake sheds its skin.',
    'The rattlesnakes rattling sound informs predators to stay away from them. When a rattlesnake is surprised, it can attack without producing a rattling sound.',
    'Rattlesnakes are venomous. They produce very strong hemotoxic venom (which destroys blood cells and vessels). It is used for hunting and for defense against predators. Rattlesnake bites are fatal for humans if not treated with antidote immediately.',
    'Some snakes are immune to the poison of rattlesnakes. Thanks to that feature, king snakes are main predators of rattlesnakes.',
    'Rattlesnakes have special kind of thermal receptors that are used for detection of warm-blooded creatures (their prey). They can also locate prey by using the tongue which collects scent molecules from the air. Also, rattlesnakes can sense vibrations in the ground.',
    'The optimal temperature for the survival of the rattlesnake is between 27 and 32 degrees celsius. They can survive freezing temperatures, but temperatures above 38 degrees is fatal for them.',
    'Rattlesnakes hibernate during the cold time of year. Usually large numbers of rattlesnakes gather in underground dens and curl around each other to stay warm.',
    'Rattlesnakes have triangular heads and vertical pupils. Their name comes from the rattle at the end of their tail. The rattle is made of keratin (the same substance builds nails and hair in humans).',
    'Rattlesnakes have a lot of enemies, from large birds like falcons and crows to larger mammals like raccoons and opossums. One of a rattlesnake’s biggest threats is actually another snake — the king snake, which is a constrictor.',
    'Rattlesnakes are able to consume animals much larger than themselves. They are able to greatly expand their jaws and skin to fit small rodents and birds into their bodies.',
    )

RAVEN_FACTS = (
    'Ravens are large, about the size of a red-tailed hawk. Crows are similar in size to a dove.',
    'Ravens have longer middle tail feathers. When extended for flight, the tail feathers appear to be wedge-shaped. A crow’s tail feathers are all the same length. Thus when spread open, the crow’s tail feathers appear fan-shaped.',
    'Ravens have larger, thicker, curved beaks, which are stronger than a crows’ beak.',
    'Ravens are often seen alone or in pairs, while crows often fly and feed in a group, referred to as a murder.',
    'Unlike crows with their distinctive cawing sound, the raven’s call is a deep, croaking sound.',
    'The raven’s lifespan is between 25 and 30 years, but they have been known to live up to 45 years. Crows usually live to 8 years, but can live longer when raised in captivity.',
    'The raven is the largest bird of the crow family; it is two times heavier than a common crow at 1.3 kg (3 pounds), being 60 cm (two feet) long, with a wingspan of almost 1 m (3.3 ft). Ravens can live 40 years in the wild and 70 in captivity.',
    'Ravens can soar high above the trees, unlike crows, which rely on active flight. Ravens are capable of aerial stunts similar to those executed by the birds of prey.',
    'Like in many other birds, when a raven is on a branch, their feet muscles and tendons automatically constrict the toes, so that the birds waste little energy on this.',
    'Ravens live from deserts to coniferous forests and coastal cliffs. In forests, they nest in stick-made nests on trees, on deserts in rock cavities.',
    'Common Ravens can mimic the calls of other bird species. When raised in captivity, they can even imitate human words; one Common Raven raised from birth was taught to mimic the word “nevermore”.',
    'The oldest known wild Common Raven was at least 22 years, 7 months old. It was banded and found in Nova Scotia.',
    )

REINDEER_FACTS = (
    'Reindeers, contrary to popular belief, cannot actually fly.',
    'Reindeers do not actually live in the north pole, and can be found in Lapland.',
    'Reindeers are actually bigger than most people think.'
)

RHINO_FACTS = (
    'Our planet is home to five species of rhinoceros – the black rhino, white rhino, Sumatran rhino, Javan rhino and Indian (or greater one-horned) rhino.',
    'They are known for their giant horns that grow from their snouts – hence the name rhinoceros, meaning \"nose horn\". Javan and Indian rhinos have one horn, where as the white, black and Sumatran rhinos have two.',
    'The largest of the five species is the white rhino, which can grow to 1.8m tall and and weigh a massive 2,500kg.',
    'They are herbivores, and instead like to munch on lots of grass and plants at night, dawn and dusk.',
    'During the heat of the day, these mammals can be found sleeping in the shade or wallowing in muddy pools to cool off. Mud protects their skin from the strong sun (like a natural sunblock) and wards off bugs.',
    'For the most part, rhinoceroses are solitary animals and like to avoid each other. But some species, particularly the white rhino, may live in a group, known as a crash.',
    'Males (called bulls) like to be left alone, unless in search of a female to breed with. They are very territorial and mark out their area of land with poop. Rhinos often use pongy piles to communicate with each other, since each individuals dung smells unique.',
    'Because of their huge bodies, strong horns and thick, armour-like skin, rhinos have no natural predators. When they feel threatened, their instinct is to charge directly at whatever has spooked them.',
    'It is estimated that there are only around 29.000 rhinos left in the wild, compared to 500,000 at the beginning of the 20th century. The main threat to these animals is illegal hunting, largely because their horns are used in traditional folk medicine, particularly in Asia.',
    )

SALMON_FACTS = (
    'Salmon tend to be anadromous, which means they hatch in fresh water, migrate to the ocean, and return to fresh water to reproduce, however this is not always the case.',
    'The majority of salmon worldwide are farmed, a process known as aquaculture.',
    'Salmon flesh is orange due to organic pigments in their diet of krill and shellfish. Farmed salmon are fed fishmeal and wheat, which results in white flesh. Since consumers were reluctant to purchase white salmon, the pigments are added to their feed.',
    'Salmon have an average of 2500 eggs, but can have up to 7000.',
    'Salmon can travel up to 3500 miles to spawn.',
    'Salmon can reach 20 inches to 5 feet in length and weigh 4 to 110 pounds, depending on the species.',
    'Salmon can be blue, red, or silver in color. Some species are covered with black spots and red stripes.',
    'Young salmon eat different types of insects, invertebrates, and plankton, while adult salmons eat small types of fish, squids, and shrimps.',
    'Salmon have a lot of natural enemies. They are often targeted by large fish, whales, sea lions, and bears.',
    'Salmon rely on their sense of smell, ocean currents, and moon to find waters where they were born.',
    'Most salmon will die as a result of exhaustion after spawning. A small percent of survived salmons will spawn a few more times in their lifetime.',
    'Newly hatched salmon are called alevin or sac fry. They stay in fresh water from 6 months to 3 years, until they become strong enough to swim to the ocean.',
    'Salmon is a name used for several species of fish in the Salmonidae family.',
    'The Chinook Salmon is the state fish of Alaska and is also known as the King Salmon.',
    'Salmon in the United States are found mainly on the Northwestern coastline as well as all around Alaska.',
    'Fossils found in British Columbia prove that salmon have been in existence for over 50 million years.',
    'In the animal kingdom, the salmon’s closest relatives are trout and char since they belong to the same family, Salmonidae.',
    'The biggest species of salmon is the Chinook, which can weigh as much as a hundred pounds.',
    'The nest where the female salmon lay their eggs is called a redd, where as many as 5,000 eggs may be found.',
    'The name “salmon” comes from the Latin word “salmo”, which means “to leap”.',
    )

SCORPION_FACTS = (
    'Scorpions are predatory animals of the class Arachnida, making them cousins to spiders, mites, and ticks.',
    'Scorpions have eight legs, a pair of pincers (pedipalps), and a narrow segmented tail that often curves over their back, on the end of which is a venomous stinger.',
    'The scorpion use their pincers to quickly grab prey and then whip their poisonous tail stinger over to kill or paralyze the prey. The tail is also used as a useful defense against predators.',
    'Scorpion species range in size from 0.09 cm to 20 cm.',
    'Scorpions can be found on all continents except for Antarctica.',
    'There are over 1750 known species of scorpion. While humans generally fear the scorpion and its poisonous sting only about 25 of the species have venom capable of killing a human.',
    'Under UV light such as a black light scorpions are known to glow due to the presence of fluorescent chemicals in their exoskeleton.',
    'The scorpion is nocturnal, often hiding during the day under rocks and in holes in the ground before emerging at night to feed.',
    'Scorpions can eat a massive amount of food in one meal. Their large food storage organs along with a low metabolism rate and an inactive lifestyle means that if necessary, they can survive 6-12 months without eating again.',
    'Areas of China have a traditional dish of fried scorpion, and scorpion wine features in Chinese medicine.',
    'The scorpion is one of the 12 signs of the Zodiac, with the Scorpio constellation identified in the stars.',
    'Scorpions moult, they shed their exoskeleton up to 7 times as they grow to full size. They become vulnerable to predators each time until their new protective exoskeleton hardens.',
    )

SEAGULL_FACTS = (
    'The smallest species of seagulls can reach 11.5 inches in length and weigh 4.2 ounces. Large species can reach 30 inches in length and weigh 3.8 pounds.',
    'The body of most seagulls is covered with white plumage. Wingtips are usually black or dark in color. Some species are grey or entirely white.',
    'The seagull has a strong body, elongated legs, and webbed feet. Their beak is slightly hooked and usually yellow in color.',
    'Seagulls are one of the rare animals that are able to drink salt water. They have special glands (located above the eyes) which eliminate excess salt from the body.',
    'The diet of seagulls includes different types of insects, earthworms, small rodents, reptiles, and amphibians. They also consume seed, fruit, and leftovers of human meals.',
    'Seagulls are very intelligent birds. They use bread crumbs to attract fish and produce rain-like sound with their feet to attract earthworms hidden under the ground. Seagulls transfer all hunting skills and techniques to their offspring.',
    'Seagulls often steal food from other birds, animals, and people. They occasionally eat young members of their own species.',
    'The main predators of seagulls are large birds of prey, such as eagles.',
    'Seagulls live in colonies that consist of few pairs of birds or couple of thousands birds.',
    'Seagulls use a wide repertoire of sounds and body language for communication.',
    'Seagulls are monogamous creatures (one mate for a lifetime). Mating couples gather each year during the mating season to reproduce and take care of their offspring.',
    'Even though they live in large colonies, breeding seagull couples occupy and defends their territory from nearby couple.',
    'Seagull couples collects plant material and build nests together. Nests are cup-shaped and usually located on the ground or hardly accessible cliffs.',
    'Depending on the species, female can lay one, two or three dark brown or olive green eggs. Incubation period lasts 22 to 26 days. Fathers play very important role in feeding of chicks. Young birds live in nursery flocks where they learn all skill required for independent life.',
    'Lifespan of seagulls depends on the species. Most seagulls can survive from 10 to 15 years in the wild.',
    )

SEAHORSE_FACTS = (
    'There are about 40 known species of seahorse.',
    'Seahorses prefer to swim in pairs with their tails linked together.',
    'Seahorses swim upright and avoid predators by mimicking the colour of underwater plants.',
    'Except for crabs, few marine predators eat the seahorse – it is too bony and indigestible.',
    'Seahorses propel themselves by using a small fin on their back that flutters up to 35 times per second. Even smaller pectoral fins located near the back of the head are used for steering.',
    'Because of their body shape, seahorses are rather inept swimmers and can easily die of exhaustion when caught in storm-roiled seas.',
    'Seahorses anchor themselves with their prehensile tails to sea grasses and corals, using their elongated snouts to suck in plankton and small crustaceans that drift by. They can suck up food from as far as 3cm away.',
    'The seahorse feeds constantly on plankton and tiny fish. It moves each of its eyes independently, so it can follow the activity of passing sea life without giving its presence away.',
    'Seahorses have no teeth and no stomach. Food passes through their digestive systems so quickly, they must eat almost constantly to stay alive.',
    'Seahorses can consume 3,000 or more brine shrimp per day.',
    'Seahorses are monogamous and mate for life.',
    'Seahorses are among the only animal species on Earth in which the male bears the unborn young.',
    'Male pregnancy in seahorse frees the female to make more eggs straight away and so reproduce quicker.',
    'Seahorses engage in an eight hour courtship dance which includes spinning around, swimming side by side and changing colours.',
    'When mating, the female seahorse releases up to 50 eggs into a pouch on the male’s abdomen.',
    'The male seahorse carries the eggs in his pouch until they hatch, then releases fully formed, miniature seahorses into the water.  As little as 5 or as many as 1,500 young can be born.',
    )

SEA_CUCUMBER_FACTS = (
    'Sea cucumbers can reproduce both sexually and asexually.',
    'Sea cucumbers breathe through a branched network of hollow tubules circulating through the anus.',
    'Sea cucumbers have no brain, but they do have a ring of neural tissue surrounding the oral cavity.',
    'At depths below 5.5 miles (8.9 km) under the sea, sea cucumbers can comprise up to 90 percent of the total mass of macrofauna.',
    'Many small animals, such as the pearl fish and many species of shrimp, can live in symbiosis with sea cucumbers.',
    'Sea cucumbers are scavengers, feeding on debris found on the ocean floor.',
    'Sea cucumbers are closely related to starfish and sea urchins.',
    'There are over 1,250 known species of sea cucumber.',
    'As a defense mechanism, sea cucumbers can expel some of their internal organs from their anus. These internal organs can regenerate relatively quickly.',
    'Most species of sea cucumber are around 4-12 inches long',
    'Sea cucumbers can easily get into and out of small crevices',
    'Sea cucumbers communicate by sending hormones through the water',
    'Some species of sea cucumber can emit a sticky substance that can tangle up predators',
    )

SEA_URCHIN_FACTS = (
    'Sea urchins or urchins are small, spiny, globular animals that, with their close kin, such as sand dollars, constitute the class Echinoidea of the echinoderm phylum.',
    'Common colors of sea urchins include black and dull shades of green, olive, brown, purple, blue, and red.',
    'Sea urchins move slowly, feeding primarily on algae.',
    'Sea urchins are preyed upon by sea otters, starfish, wolf eels, and triggerfish, among other predators.',
    'The name "urchin" is an old word for hedgehog, which sea urchins resemble.',
    'Like other echinoderms, sea urchin early larvae have bilateral symmetry, but they develop five-fold symmetry as they mature.',
    'The tube feet of a sea urchin are moved by a water vascular system, which works through hydraulic pressure.',
    'The structure of the sea urchin\'s mouth and teeth have been found to be so efficient at grasping and grinding that their structure has been tested for use in real-world applications.',
    'Sea urchins have conquered most sea habitats, on an extremely wide range of depths.',
    'The gonads of both male and female sea urchins, usually called sea urchin roe or corals, are culinary delicacies in many parts of the world.',
    )

SHARK_FACTS = (
    'Sharks do not have a single bone in their bodies. Instead they have a skeleton made up of cartilage; the same type of tough, flexible tissue that makes up human ears and noses.',
    'Some sharks remain on the move for their entire lives. This forces water over their gills, delivering oxygen to the blood stream. If the shark stops moving then it will suffocate and die.',
    'Sharks have outstanding hearing. They can hear a fish thrashing in the water from as far as 500 meters away!',
    'If a shark was put into a large swimming pool, it would be able to smell a single drop of blood in the water.',
    'Although most species of shark are less than one meter long, there are some species such as the whale shark, which can be 14 meters long.',
    'A pup (baby shark) is born ready to take care of itself. The mother shark leaves the pup to fend for itself and the pup usually makes a fast get away before the mother tries to eat it!',
    'Not all species of shark give birth to live pups. Some species lay the egg case on the ocean floor and the pup hatches later on its own.',
    'Great whites are the deadliest shark in the ocean. These powerful predators can race through the water at 30 km per hour.',
    'Unlike other species of shark, the great white is warm-blooded. Although the great white does not keep a constant body temperature, it needs to eat a lot of meat in order to be able to regulate its temperature.',
    'A shark always has a row of smaller teeth developing behind its front teeth. Eventually the smaller teeth move forward, like a conveyor belt, and the front teeth fall out.',
    )

SHEEP_FACTS = (
    'There are over 1 billion sheep in the world!',
    'Sheep have a field of vision (FOV) of around 300 degrees allowing them to look behind themselves without turning their head!',
    'Sheep have four stomachs!',
    'Ancient Egyptians believed that sheep were sacred to society. When a sheep died, it would be mummified just like a human.',
    'Sheep have 24 molar teeth and 8 incisor teeth.',
    'A collection or group of sheep is called a flock.',
    'Most sheep live between 6-11 years.',
    'China has the largest number of sheep in the world.',
    'A lamb is considered a sheep less than one year old.',
    'China has the largest number of sheep in the world.',
    'More than two thirds of U.S. sheep are in the Southern Plains, Mountain, and Pacific regions.',
    'Predators of sheep include coyotes, dogs, bears, big cats, foxes, and eagles.',
    'A sheep, depending on its type, can produce anywhere from two to 30 pounds of wool per year.',
    'In 1996, Dolly, a Finnish Dorset sheep, was the first mammal to be cloned from an adult cell.',
    'Texas, Wyoming, and California are the U.S. states with the highest number of sheep.',
    'Sheep have been shown to display emotions, some of which can be studied by observing the position of their ears.',
    'Sheep are known to self-medicate when they have some illnesses. They will eat specific plants when ill that can cure them.',
    'Sheep are precocial (highly independent from birth) and gregarious (like to be in a group).',
    'Sheep produce a thick woolly coat called a fleece to protect them from the weather, both hot and cold. ',
    'Due to human interaction, domestic sheep have evolved to require humans to shear them. Their wool never sheds.',
    )

SHRIMP_FACTS = (
    'Snapping shrimp produce a noise with their claws that is greater than a gunshot or jet engine.',
    'To attract fish, cleaning shrimp wave their white antennae and do a little dance.',
    'Harlequin shrimp, from the Pacific and Indian oceans, use their flat, oversize claws to sever arms from sea stars for food.',
    'Most shrimp are breeding machines -- within hours after their eggs hatch, females are carrying a new batch of fertilized embryos.',
    'Some species of shrimp also have a symbiotic relationship with fish and clean parasites, bacteria, and fungi off their host.',
    'While microwaving frozen shrimp might seem like a good shortcut when you need dinner in a hurry, it’s not a good idea.',
    'Shrimp are a very low-calorie food (a medium cooked shrimp has about 7 calories), which means you can eat quite a few without feeling guilty.',
    'Certain shrimp species are able to make a snapping sound that is louder than any other marine noise by hitting their large and small pincers together. It’s believed they do this to communicate with other shrimp or temporarily stun their prey.',
    'Shrimp acquire their food either by sifting through the sand of the ocean floor or filtering the surrounding waters to ingest small particles of various plant or animal species.',
    'Because of their small size, it is advantageous for shrimp to stay in groups in order to protect themselves from larger predators.',
    )

SKUNK_FACTS = (
    'Skunks are omnivores, which mean that they eat both plants and animals. They like to eat fruits, insects, worms, reptiles, and rodents.',
    'Skunks often attack beehive because they eat honeybees.',
    'Before it sprays the victim, a skunk will turn its back, lift its tail, start hissing, and stumping with its feet. Those are the warning signs that precede spraying.',
    'Skunk can spray its oily and smelly substance up to 10 feet distance.',
    'Skunks\'s worst predators are coyotes, bobcats, and owls.',
    'Skunks live up to 3 years in the wild. They can survive up to 10 years in captivity.',
    'Skunk can transmit rabies.',
    'Skunks are typically around the size of house cats. They grow to 8 to 19 inches long and weigh around 7 ounces to 14 lbs.',
    'Skunks appeared 40 million years ago, evolving from common ancestors with weasels and polecats.',
    'Skunks are found in the United States, Canada, South America, and Mexico.',
    'Skunks live in forest edges, woodlands, grasslands, and deserts. They typically make their homes in abandoned burrows, but will also live in abandoned buildings, under large rocks, and in hollow logs.',
    'Though they typically prefer to dine on insects and grubs, skunks are omnivores, consuming a vast diet of both plant and animal matter. Skunks are opportunistic eaters, and their diets are flexible, often shifting with the seasons.',
    'Skunks have strong forefeet and long nails, which make them excellent diggers. When no other form of shelter is available they may even burrow underneath buildings by entering foundation openings.',
    'Skunks are known to release a powerful smell through their anal glands when threatened. Skunks will usually only attack when cornered or defending their young, and spraying is not the first method of defense. A skunk will growl, spit, fluff its fur, shake its tail, and stamp the ground.',
    'Although skunks have very poor eyesight, they have excellent senses of smell and hearing.',
    'Skunks are nocturnal, which means they search for food at night and sleep in dens lined with leaves during the day.',
    'Skunks are slow and can run only 10 miles per hour.',
    'Skunks are immune to rattlesnake venom, bee stings, and scorpions.',
    'Female skunks can bear 3-10 young and male skunks reach sexual maturity from 4-6 months after birth, while females reach sexual maturity nine months to a year after birth.',
    'A group of skunks is called a surfeit.',
    )

SLOTH_FACTS = (
    'Sloths are a medium-sized mammal. There are two types of sloth the two-toed sloth and the three-toed sloth, they are classified into six different species.',
    'All sloths actually have three toes, but the two-toed sloth has only two fingers.',
    'Sloths are part of the order Pilosa so they are related to anteaters and armadillos.',
    'Sloths are tree-dwelling animals, they are found in the jungles of Central and South America.',
    'A sloth\'s body is usually 50 to 60 cm long. Skeletons of now extinct species of sloth suggest some varieties used to be as large as elephants.',
    'Sloths mainly eat the tree buds, new shoots, fruit, and leaves of the Cecropia tree. Some two-toed sloths also eat insects, small reptiles, and birds.',
    'Sloths have a four-part stomach that very slowly digests the tough leaves they eat, it can sometimes take up to a month for them to digest a meal. Digesting this diet means a sloth has very little energy left to move around making it one of the slowest moving animals in the world.',
    'Sloths can move along the ground at just 2 m (6.5 ft) per minute! In the trees they are slightly quicker at 3 m (10 ft) per minute.',
    'The slow movement and unique thick fur of the sloth make it a great habitat for other creatures such as moths, beetles, cockroaches, fungi, and algae. In fact, this green colored algae provides a camouflage so sloths can avoid predators.',
    'Sloths can extend their tongues 10 to 12 inches out of their mouths.',
    'The sloth has very long, sharp, and strong claws that they use to hold on to tree branches. The claws are also their only natural defense against predators.',
    'Sloths usually only leave the tree they live in to go to the toilet once a week on the ground. This is when they are most vulnerable to being attacked by their main predators such as jaguars, the harpy eagle and snakes.',
    'Two-toed sloths are nocturnal, being most active at night. While three-toed sloths are diurnal which means they are most active during the day.',
    'It used to be thought that sloths slept for 15 to 20 hours a day. However, its now believed they only sleep around 10 hours a day.',
    'In the wild, sloths live on average 10 - 16 years and in captivity over 30 years.',
    )

SNAIL_FACTS = (
    'Snails are gastropod mollusks, members of the ‘phylum Mollusca’ and the class ‘Gastropoda’.',
    'Snails have no back bone. When they feel threatened, they usually retreat into their shell to protect themselves.',
    'The largest land snail is the ‘Achatina achatina’, the Giant African Snail.',
    'Some land snails feed on other terrestrial snails.',
    'Most snails live from 2 to 5 years, but in captivity, some have exceeded 10 or 15 years of age.',
    'The mucus of the garden snail is used to treat wrinkles, spots, and scars on the skin.',
    'Most snail species are hermaphrodites, so they have both male and female reproductive organs.',
    'The speed of snails is around 0.5-0.8 inches per second. If they moved without stopping, it would take more than a week to complete 1 kilometer.',
    'Snails do not change shells when they grow up. Instead, the shell grows along with them.',
    'Snails host several types of parasites that, while may not kill them, are capable of affecting or killing their predators or animals that eat the snails. Even humans who eat poorly cooked snails can become seriously ill.',
    'A single garden snail (Helix aspersa) can have up to 430 hatchlings after a year.',
    'Many snails are in danger of extinction. Among these are the species ‘Aaadonta constricta’ and ‘Aaadonta fuscozonata’, and others of the ‘genus Aaadonta’ and ‘Achatinella’ are in critical danger of extinction.',
    'The size of the shell of a snail reflects its age.',
    'Land snails do not chew their food. They scrape it.',
    'Calcium carbonate is the main component of the snail shells.',
    'Snails can have lungs or gills depending on the species and their habitat. Some marine snails actually can have lungs and some land based snails can have gills.',
    'Most snail species have a ribbon-like tongue called a radula that contains thousands of microscopic teeth. The radula works like a file, ripping food up into tiny pieces.',
    'The majority of snails are herbivores eating vegetation such as leaves, stems, and flowers, some larger species and marine based species can be predatory omnivores or even carnivores.',
    'The giant African land snail grows to about 38 cm (15 in) and weigh 1 kg (2lb).',
    'The largest living sea snail species is the Syrinx aruanus who\'s shell can reach 90 cm (35 in) in length and the snail can weigh up to 18 kg (40lbs)!',
    'Common garden snails have a top speed of 45 m (50 yards) per hour.',
    'As they move along, snails leave behind a trail of mucus which acts as a lubricant to reduce surface friction. This also allows the snail to move along upside down.',
    'Depending on the species, snails can live 5 - 25 years.',
    'Snail is a common name for gastropod molluscs that can be split into three groups, land snails, sea snails and freshwater snails.',
    'North America has about 500 native species of land snails.',
    'Snails do not change shells when they grow. Instead, the shell grows along with them.',
    'A single garden snail (Helix aspersa) can have up to 430 hatchlings after a year.',
    'Most land snails have two set of tentacles, the upper one carry the eyes, while the lower one has the olfactory organs. However, they do not have ears or ear canals.',
    'Snails are strong and can lift up to 10 times their body weight in a vertical position.',
    'The snail Lymnaea, makes decisions by using only two types of neuron: one deciding whether the snail is hungry, and the other deciding whether there is food in the vicinity.',
    )

SNAKE_FACTS = (
    'Snakes don’t have eyelids.',
    'Snakes can’t chew food so they have to swallow it whole.',
    'Snakes have flexible jaws which allow them to eat prey bigger than their head!',
    'Snakes are found on every continent of the world except Antarctica.',
    'Snakes have internal ears but not external ones.',
    'Snakes used in snake charming performances respond to movement, not sound.',
    'There are around 3000 different species of snake.',
    'Snakes have a unique anatomy which allows them to swallow and digest large prey.',
    'Snakes shed their skin a number of times a year in a process that usually lasts a few days.',
    'Some species of snake, such as cobras and black mambas, use venom to hunt and kill their prey.',
    'Pythons kill their prey by tightly wrapping around it and suffocating it in a process called constriction. This bot is written in Python!',
    'Some sea snakes can breathe partially through their skin, allowing for longer dives underwater.',
    'Anacondas are large, non-venomous snakes found in South America that can reach over 5 m (16 ft) in length.',
    'Python reticulates can grow over 8.7 m (28 ft) in length and are considered the longest snakes in the world.',
    )

SPIDER_FACTS = (
    'Spiders are arachnids, not insects',
    'Spiders dont have antennae while insects do',
    'Spiders are found on every continent of the world except Antarctica',
    'Most spiders make silk which they use to create spider webs and capture prey',
    'An abnormal fear of spiders is called arachnophobia',
    'The largest specie of tarantula is the Goliath Birdeater',
    'There are around 3000 different species of snake.',
    'Giant Huntsman spiders have leg-spans of around 30cm (12 in)',
    'Female spiders can lay up to 3,000 eggs at one time',
    'Spiders are nearsighted',
    'Jumping spiders can jump up to 50x their own length',
    'While most spiders have eight eyes, there are some that only have six or less',
    )

STARFISH_FACTS = (
    'Starfish have no brain and no blood.',
    'There are around 2,000 species of sea star.',
    'Starfish usually have five arms and can regenerate them.',
    'Starfish cannot survive in fresh water.',
    'Starfish can eat inside out.',
    'Starfish can move using their tube feet',
    'Starfish have eyes.',
    'Starfish can reproduce sexually and asexually.',
    'Starfish use seawater, instead of blood, to pump nutrients through their bodies via a "water vascular system".',
    'A Starfish is not a fish.',
    'A common starfish has 5 arms, but some starfish have up to 40 arms!',
    'Starfish are carnivores, meaning they are meat eaters.',
    'Starfish cannot swim. They move across the ocean by hundreds of tube feet on their arms and body.',
    )

STOAT_FACTS = (
    'Stoats have very good eyesight, good hearing and a strong sense of smell.',
    'A female stoat can get pregnant when she is still a blind, deaf, toothless and naked baby – at only 2-3 weeks old.',
    'In countries with very cold, snowy winters, the fur of stoats turns white. This white fur is called ermine. It is very soft and thick and is used to make luxury fur coats.',
    'If stoats get the chance, they’ll kill more than they need for food and hide the rest in their den to eat later.',
    'Stoats can kill animals much bigger than themselves.',
    'The appearance of a stoat is similar to that of a weasel, although the stoat is considerably larger and has a distinctive black tip to its tail.',
    'Stoats are very agile and good climbers and may take young birds from a nest.',
    'Stoats are strong swimmers and are capable of crossing large rivers.',
    )

STURGEON_FACTS = (
    'Sturgeons are related to the paddlefish and perhaps to the bichir.',
    'Sturgeons are found in greatest abundance in the rivers of southern Russia and Ukraine and in the freshwaters of North America.',
    'Sturgeons are one of the oldest families of bony fish in existence.',
    'Most sturgeons are anadromous bottom-feeders, spawning upstream and feeding in river deltas and estuaries. While some are entirely freshwater, very few venture into the open ocean beyond near coastal areas.',
    'Sturgeons commonly range from 7–12 feet (2-3½ m) in length, while some species grow up to 18 feet (5.5 m).',
    'Sturgeons reach sexual maturity in 6-25 years, making them vulnerable to overfishing.',
    'Some species of sturgeon are harvested for their roe, which is made into caviar.',
    'Sturgeons have four soft barbels between the front of the snout and the toothless mouth, which protrudes to pick up food.',
    'Sturgeons can live 50 to 100 years or more, depending on the species.',
    )

SUNFISH_FACTS = (
    'The ocean sunfish (mola mola) is the heaviest known bony fish in the world, adults typically weigh between 247 and 1000 kg (545-2205 lb).',
    'Sunfish live on a diet mainly of jellyfish, but because jellyfish are nutritionally poor, sunfish need to consume large amounts to develop and maintain their bulk.',
    'Despite their size, sunfish are docile and pose no threat to human divers.',
    'Sunfish have an average life span in captivity of up to 10 years.',
    'Sunfish bask in the sun. They do this by swimming on their side and presenting their largest profile to the sun, near the water surface, which may be a method of helping their bodies warm up after deep water dives.',
    'Female sunfish can produce as many as 300 million eggs at a time, more than any other vertebrate.',
    'The dorsal fin of the sunfish is often mistaken for a shark fin, however can be distinguished as sharks keep their dorsal fin stationary, while sunfish swings its dorsal fin in a sculling motion'
    'The skin of adult sunfish range from brown to silvery-grey or white with a variety of mottled skin patterns.',
    'Sunfish neither has nor needs a swim bladder, as they constantly shuttle back and forth between depths instead of trying to maintain a position in the water.',
    'In the course of the evolution of the sunfish, its tail disappeared and was replaced by a lumpy pseudotail, the clavus, formed by the convergence of the dorsal and anal fins and is used by the sunfish as a rudder.',
    'Young sunfish school for protection, but this behaviour is abandoned as they grow.',
    'Sunfish by the time of adulthood, have the potential to grow more than 60 million times their birth size (a fraction of a gram), arguably the most extreme size growth of any vertebrate animal.',
    )

SQUID_FACTS = (
    'Many species of squid have a life span that is only about one year',
    'The Humboldt squid is very aggressive and will even attack sharks in the water.',
    'The only predators that giant squid have are sperm whales.',
    'Squid are strong swimmers and certain species can "fly" for short distances out of the water.',
    'The majority of squid are no more than 60 cm (24 in) long, although the giant squid may reach 13 m (43 ft).',
    'The smallest squid is the pygmy squid which can be less than 2.5 centimeters (1 inch) long.',
    'It wasn\'t until 2004 that researchers in Japan took the first images ever of a live giant squid.',
    'Giant squid have the largest eyes in the animal kingdom, measuring up to 10 inches in diameter.',
    'Squid, like cuttlefish, have eight arms arranged in pairs, and two longer tentacles with suckers.',
    'Squids belong to a particularly successful group of mollusks called the cephalopods, which have been around for about 500 million years.',
    'Giant squid mostly eat deep water fish and other squids including other giant squids.',
    )

SQUIRREL_FACTS = (
    'In fall, squirrels bury more food than they will recover.',
    'Squirrels can find food buried beneath a foot of snow.',
    'A squirrel’s front teeth never stop growing.',
    'Squirrels may lose 25 percent of their buried food to thieves.',
    'Squirrels zigzag to escape predators.',
    'Squirrels may pretend to bury a nut to throw off potential thieves.',
    'A newborn squirrel is about an inch long.',
    'Humans introduced squirrels to most of our major city parks.',
    'Squirrels are acrobatic, intelligent and adaptable.',
    'Squirrels don’t dig up all of their buried nuts, which results in more trees!',
    'Baby squirrels will only pee and poop in their mother’s mouth so that the mother can dispose of the waste outside the nest in order to keep predators from smelling the scent.',
    'Squirrels can rotate their ankles 180 degrees.',
    )

STINGRAY_FACTS = (
    'Stingrays are diverse group of fish characterized by flattened bodies.',
    'The largest species of stingray measure 6.5 feet in length and can weigh up to 790 pounds.',
    'Stingrays are closely related to sharks. Stingrays don’t have bones.',
    'Stringrays flattened body ends with long tail that usually contains spine and venom. Spines can be serrated in some species.',
    'There are more than 70 Species of stingray.',
    'Stringray mouths are located on the bottom side of their body. When they catch clams, shrimps, and mussels, they will crush and eat them using their powerful jaws.',
    'Stringray`s long tails usually have a spine and venom.',
    'Stingrays use camouflage for protection and hunting.',
    'Stingrays don’t use their eyes to find prey. They use their electro-sensors to locate their prey',
    'Stingrays are solitary, but can also live in groups.',
    'Stingrays have a lifespan of 15-25 years.',
    'Stringrays can be found in oceans in tropical and subtropical areas around the world. Stingrays like warm and shallow water.',
    'Stingrays are found both in freshwater and oceans.',
    'Stingrays give birth to 2-6 young stingrays each year.',
    'Baby stingrays are born fully developed; they look like miniature versions of adult stingrays. Babies take care of themselves from the moment of birth.',
    )

TARANTULA_FACTS = (
    'Female tarantulas can live 30 years or longer in the wild.',
    'The largest tarantulas have a leg span the size of a dinner table.',
    'Tarantulas are quite docile and rarely bite people.',
    'Tarantulas defend themselves by throwing needle-like hairs at their attackers.',
    'A fall can be fatal for a tarantula.',
    'Tarantulas have retractable claws on each leg, much alike a cat.',
    'Though tarantulas do not spin webs, they do use silk',
    'Most tarantulas wander during the summer months.',
    'Tarantulas cannot regenerate lost legs.',
    'Because tarantulas molt throughout their lives, replacing their exoskeletons as they grow, they have the ability to repair any damage they\'ve sustained.',
    'If a tarantula does feel threatened, it uses its hind legs to scrape barbed hairs from its abdomen and fling them in the direction of the threat.',
    'Tarantulas do not use webs to capture prey, they do it the hard way – hunting on foot.',
    'Like other spiders, tarantulas paralyze their prey with venom, then use digestive enzymes to turn the meal into a soupy liquid.',
    'Since falls can be so dangerous for tarantulas, it is important for them to get a good grip when climbing.',
    )

TARDIGRADE_FACTS = (
    'Nicknames for tardigrades include "water bears", "space bears", and "moss piglets"',
    'The first tardigrade was discovered by Johann August Ephraim Goeze in 1773.',
    'Tardigrades have been found everywhere in the world: from mountaintops to the deep sea to mud volcanoes; from tropical rain forests to the Antarctic.',
    'Tardigrades are one of the most resilient animals known. They can survive global extinction events like meteor impacts and even survive in the vacuum of space.',
    'Tardigrades can go without food or water for more than 30 years, drying out to the point where they are 3 percent or less of water.',
    'Tardigrades measure about 0.5 millimetres long when fully grown.',
    'About 1,150 species of tardigrades haven been described.',
    'All tardigrades of the same species have the same number of cells.',
    'Tardigrades can withstand 1,000 times more radiation than other animals; the median lethal dose is 5,000 Gy (of gamma rays).',
    'Many organisms that live in aquatic environments feed on tardigrades.',
    'Tardigrades work as pioneer species by inhabiting new developing environments in which to live. Their presence attracts other invertebrates and predators to populate the space.',
    'Tardigrades are the first known animal to survive in space.',
    )

TARSIER_FACTS = (
    'A Tarsier is one of the known smallest primates. It is an ancient ancestor of a modern day monkey.',
    'A Tarsier does not grow bigger than a man''s hand. It is about 15cm in height and between 115 and 130g in weight.',
    'A Tarsier have gray fur and a nearly naked tail.',
    'A Tarsier is recognizable due to its huge eyes and its long feet. It has the largest eyes, proportionate to its body size, of any animal on the planet.',
    'The Tarsier\'s large eyes enables it to have acute night vision that makes them a good hunter.',
    'The Tarsier\'s long feet enables it to jump from tree to tree up to 3 meters in distance.',
    'A Tarsier is mostly active at night and lives on a diet of insects.',
    'A Tarsier can usually be found in the beautiful archipelago called the Philippines.'
    )

TASMANIAN_DEVIL_FACTS = (
    'The tasmanian devil is a marsupial, therefore, the females have pouches in which they carry their young.',
    'Females tasmanian devils give birth to 20–30 young, but few survive because she only has 4 nipples.',
    'Tasmanian devils can run up to 13 km/h (8.1 mph).',
    'The tasmanian devil is native to Australia, but now only found on the island state of Tasmania',
    'Tasmanians are the size of a small dog',
    'The tasmanian devil has the strongest bite per unit body mass of any land mammal',
    'Tasmanian devils are nocturnal hunters',
    'Tasmanian devils live no longer than 5 years in the wild, but 7 in captivity.',
    'Tasmanian devils are named such because of their extreme temperment.',
    'Tasmanian devils are carnivorous and survive mostly on carrion.',
    'Tasmanian devils will eat pretty much anything they can get their teeth on, consuming everything—including hair, organs, and bones.',
    )

TIGER_FACTS = (
    'The tiger is the biggest species of the cat family.',
    'Tigers can reach a length of up to 3.3 meters (11 feet) and weigh as much as 300 kilograms (660 pounds).',
    'Subspecies of the tiger include the Sumatran Tiger, Siberian Tiger, Bengal Tiger, South China Tiger, Malayan Tiger, and Indochinese Tiger.',
    'Many subspecies of the tiger are either endangered or already extinct. Humans are the primary cause of this through hunting and the destruction of habitats.',
    'Around half of tiger cubs don’t live beyond two years of age.',
    'Tiger cubs leave their mother when they are around 2 years of age.',
    'A group of tigers is known as an ‘ambush’ or ‘streak’.',
    'Tigers are good swimmers and can swim up to 6 kilometers.',
    'Rare white tigers carry a gene that is only present in around 1 in every 10,000 tigers.',
    'Tigers usually hunt alone at night time.',
    'Tigers have been known to reach speeds up to 40 mph (65 kph).',
    'Less than 10 precent of hunts end successfully for tigers',
    'Tigers can easily jump over 5 meters.',
    'Various tiger subspecies are the national animals of Bangladesh, India, North Korea, South Korea, and Malaysia.',
    'There are more tigers held privately as pets than there are in the wild.',
    'Tigers that breed with lions give birth to hybrids known as tigons and ligers.',
    )

TOUCAN_FACTS = (
    'The average life span of toucans in the wild is up to 20 years.',
    'The toucan\'s beak is serrated like a knife, to tear apart its food.',
    'The toro toucan\'s bill is a third of the bird\'s length.',
    'Toucan bills are strong but light.',
    'Toucans are found in the wild only in the Americas.',
    'The exterior of a toucan bill is made of keratin; the interior, bone.',
    'Toucans regulate body temperature by adjusting the flow of blood to their beak.',
    'Toucans are extremely noisy birds, which makes them obvious targets for their predators.',
    'Toucans\' enormous bill is useless in defending against predators and, in fact, attracts humans to catch them for the pet trade.',
    'One special adaptation that toucans have in the wild is deafening each other while they are in small flocks. For instance, when they see a bird of prey, "they gather about it in a jeering band"',
    'In addition to fruit, Toco toucans eat insects and, sometimes, young birds, eggs, or lizards.',
    'The color of the toucan bill may be black, blue, brown, green, red, white, yellow, or a combination of colors.',
    'Toucans typically lay 2–21 white eggs in their nests.',
    'Toucans make their nests in tree hollows and holes excavated by other animals such as woodpeckers.',
    'The toucan family has five extant genera: Aulacorhynchus, Pteroglossus, Selenidera, Andigena, and Ramphastos.',
    'Toucan wings are small, as they are forest-dwelling birds who only need to travel short distances, and are often of about the same span as the bill-tip-to-tail-tip measurements of the bird.',
    'Both sexes of toucans use their bills to catch tasty morsels and pitch them to one another during a mating ritual fruit toss.',
    'While the beak of a toucan may deter predators due to its size, it is of little use in combat, due to it being a honeycomb of bone that actually contains a lot of air.',
    'Toucans use their beaks to reach fruit on branches that are too small to support their weight, and also to skin their pickings.',
    'Toucans live in small flocks of about six birds.',
    'Young toucans do not have a large bill at birth—it grows as they develop and does not become full size for several months.',
    'Researchers have discovered that the large bill of the toucan is a highly efficient thermoregulation system.',
    'The tongue of a toucan is long (up to 14–15 cm, or 6 inches), narrow, grey, and singularly frayed on each side, adding to its sensitivity as an organ of taste.',
    'Toucans are native to the Neotropics, from Southern Mexico, through Central America, into South America south to northern Argentina.',
    'Toucans are, due to their unique appearance, among the most popular and well known birds in the world.',
    'The constellation Tucana, containing most of the Small Magellanic Cloud, is named after the toucan.',
    'Toucans are the mascot of the Brazilian Social Democracy Party; its party members are called tucanos for this reason.',
    'Toucans are highly social and most species occur in groups of up to 20 or more birds for most of the time. ',
    'The toco toucan is the largest species of toucan.',
    )

TROUSER_SNAKE_FACTS = (
    'The Trouser Snake is the most feared yet desired animal in the Animal Kingdom.',
    'The Trouser Snake carries a venom sack that produces a white venom when it reaches maturity.',
    'The Trouser Snake does not like cold weather and will shrink in cold conditions.',
    'The Trouser Snake varies in color from pink to black.',
    'The Trouser Snake usually attacks women in the mouth or lower abdominal area, it has been known to also attack males.',
    'When threatened, the normally docile and relaxed trouser snake tenses up into an erect position in order to increase its size to scare off an attacker.',
    'When touched, the Trouser Snake will swell up to twice its original size in order to frighten off predators.',
    'The Trouser Snake is fang less, the average length is 5-6 inches (12.7cm - 15.24cm), although some reports have indicated over 8 inches (20cm) in length.',
    'The Trouser Snake has been known to use its body to viciously ram the opponent repeatedly until it is driven away.'
    )

TROUT_FACTS = (
    'Trout that live in different environments can have dramatically different colorations and patterns.',
    'Trout have fins entirely without spines, and all of them have a small adipose fin along the back, near the tail.',
    'Trout are usually found in cool (50–60 °F or 10–16 °C), clear streams and lakes.',
    'Trouts can be anadromous, migrating upstream to mate.',
    'Trout generally feed on other fish, and soft bodied aquatic invertebrates, such as flies, mayflies, caddisflies, stoneflies, mollusks, and dragonflies.',
    'Several species of trout were introduced to Australia and New Zealand by amateur fishing enthusiasts in the 19th century, effectively displacing and endangering several upland native fish species.',
    'Trout contain one of the lowest amounts of dioxins (a type of environmental contaminant) of all oily fishes.',
    'While trout can be caught with a normal rod and reel, fly fishing is a distinctive method developed primarily for trout, and now extended to other species.',
    'Because trout are cold water fish, during the winter they move from up-deep to the shallows, replacing the small fish that inhabit the area during the summer.',
    'As a group, trout are somewhat bony, but the flesh is generally considered to be tasty. The flavor of the flesh is heavily influenced by the diet of the fish.',
    )

TOAD_FACTS = (
    'While frogs need to live near water to survive, toads do not actually have to be located near water.',
    'The toad has skin in which lets out a bitter taste and smell in which burns the eyes and nostrils of its predators.',
    'The common toad moves around by crawling, unlike frogs which hop, it moves at the speed of 5 miles per hour.',
    'Toads can survive 20-40 years in the wild, and 50 years in captivity.',
    'Toad mating season begins March and ends in June!',
    'The common toad can be found throughout all of Europe besides northern Scotland and the Mediterranean islands.',
    'The main threat to toad survival is habitat destruction, the common toad is not endangered however.'
    'Twenty tons of common toads are killed on British roads annually.',
    'Grass snakes and hedgehogs prey on the toad as they are immune to its bitter taste and smell.',
    'The common toads skin color changes depending on their surroundings.',
    )

TUATARA_FACTS = (
    'Tuatara name derives from the Māori language, and means "peaks on the back".',
    'The single species of tuatara is the only surviving member of its order, which flourished around 200 million years ago.',
    'They have two rows of teeth in the upper jaw overlapping one row on the lower jaw, which is unique among living species.',
    'They are unusual in having a pronounced photoreceptive eye, the third eye, which is thought to be involved in setting circadian and seasonal cycles.',
    'The species has between five and six billion base pairs of DNA sequence, nearly twice that of humans.',
    'Tuatara feature in a number of indigenous legends, and are held as ariki (God forms).',
    'The tuatara was the inspiration for a DC Comics superhero, also with a third eye, called Tuatara, member of the Global Guardians.',
    'The Tuatara hypercar, designed and manufactured by SSC North America in Tri-Cities, Washington, is named after the reptile, noting its fast evolving DNA and "peaks on the back" as inspiration in the creation of the car.',
    'In Māori legends, tuatara are thought to be messengers of Whiro, the personification of darkness and evil.',
    'Tuatara are considered to be living fossils, a living animal which closely resembles animals known only from the fossil record.',
    'Tuatara can be a range of colors, olive green, brown, or orange-red, and their coloring can change throughout its life.',
    )

TURTLE_FACTS = (
    'Turtles have a hard shell that protects them like a shield, this upper shell is called a ‘carapace’.',
    'Turtles also have a lower shell called a ‘plastron’.',
    'Many turtle species (not all) can hide their heads inside their shells when attacked by predators.',
    'Turtles have existed for around 215 million years.',
    'Like other reptiles, turtles are cold blooded.',
    'The largest turtle is the leatherback sea turtle, it can weigh over 900 kg! (2000 lb)',
    'In some species of turtle, the temperature determines if the egg will develop into a male or female. Lower temperatures lead to a male while higher temperatures lead to a female.',
    'Some turtles lay eggs in the sand and leave them to hatch on their own. The young turtles make their way to the top of the sand and scramble to the water while trying to avoid predators.',
    'Sea turtles have special glands which help remove salt from the water they drink.',
    'The shell of a turtle is made up of 60 different bones all connected together.',
    'Turtles live on every continent except Antarctica.',
    'Turtles have good eyesight and an excellent sense of smell. Hearing and sense of touch are both good and even the shell contains nerve endings.',
    'While most turtles don\'t tolerate the cold well, the Blanding\'s turtle has been observed swimming under the ice in the Great Lakes region.',
    )

VAMPIRE_BAT_FACTS = (
    'Vampire bats are believed to be the only bats to “adopt” another young bat if something happens to the bat’s mother.',
    'Vampire bats typically gather in colonies of about 100 animals, but sometimes live in groups of 1,000 or more.',
    'In one year, a colony of 100 vampire bats can drink the blood of 25 cows.',
    'The common vampire bat has the fewest teeth of all bat species.',
    'The incisor teeth of the common vampire bat do not have any enamel which keeps them extremely sharp.',
    'The common vampire bat prefers to feed from horses rather than cattle, if given a choice.',
    'Vampire bats often remain in the colony in which they were born for their entire life.',
    'Vampire bats usually consume about one ounce of blood per night.',
    'A drug which uses the anticoagulant properties of the saliva of the common vampire bat, has been shown to increase blood flow in stroke victims.',
    'Vampire bats can live for up to 12 years in the wild, although captive individuals have been known to reach the age of 19.',
    'Young vampire bats feed on milk from the mother, not on blood. They cling tightly to their mothers, even in flight, until they are weaned at about 3 – 4 months.',
    'Vampire bats are not seasonal breeders and can mate all year round. They are pregnant for 3 – 4 months, which is a long gestation period compared to other small bats. The female gives birth to a single baby.',
    'The saliva of a vampire bat can be used to prevent blood from clotting.',
    )

VULTURE_FACTS = (
    'Vultures eat animals that have died in the wild. Without them, these animals would rot and smell.',
    'Vultures heads and necks are almost bare so they stay clean while feasting on rotten meat.',
    'Vultures also have strong immune systems so they don’t get sick from eating rotten meat.',
    'Vultures have wide, strong wings. They can glide in the air for hours looking for a meal.',
    'Vultures eat as much as they can at one meal. They never know when the next meal will come.',
    'Vultures live in every part of the world except Australia and the Antarctica.',
    'To eat their prey vultures have sharp hooked beaks and talons. They can also use tools.',
    'Vultures sometimes drop eggs to break them or hit them against rocks to open them for food.',
    'Vultures often appear when an animal is dying or dead. Egyptians and Native Americans used vultures in burial ceremonies.',
    'Unlike many raptors, vultures are relatively social and often feed, fly or roost in large flocks.',
    'Vultures have excellent senses of sight and smell to help them locate food, and they can find a dead animal from a mile or more away.',
    'While vultures eat mostly dead animals, they are capable of attacking and will often prey on extremely sick, wounded or infirm prey.',
    'Vultures urinate on their legs and feet to cool off on hot days, a process called urohydrosis.',
    'When threatened, vultures vomit to lighten their body weight so they can escape more easily into flight.',
    )

WALLABY_FACTS = (
    'Wallabies are members of the kangaroo clan found primarily in Australia and on nearby islands.',
    'Wallabies are marsupials or pouched mammals. Wallaby young are defenseless and develop in the pouch of their mother.',
    'The largest wallabies can reach 6 feet from head to tail.',
    'Wallabies have powerful hind legs they use to bound along at high speeds and jump great distances.',
    'Wallabies are herbivores and eat mainly roots, grass, tree leaves, and ferns. They rest during the day and are active mainly at night.',
    'Nail-tailed wallabies are so-named because of the sharp growth at the end of their tails.',
    'When wallabies fight, they use their hind legs to deliver powerful kicks.',
    'Four species of wallaby have already gone extinct. Many others are endangered, while others are considered vulnerable.',
    'Large species of wallaby tend to live in groups, but smaller species tend to live alone.',
    'A young wallaby is called Joey. The males are called Jack while the females are called Jill.',
    'There are 30 different species of wallabies and all are native to Australia and Tasmania.'
    'The average lifespan of a wallaby is from 9 - 15 years.',
    'A group of wallabies is known as a ‘mob’.',
    'A female typically gives birth to a single wallaby and in very rare cases, twins. The gestation period is one month.',
    'Wallabies have strong back legs that help them hop and move about powerfully. The forearms of the wallaby are small and used mainly for balancing or for feeding.',
    'An adult wallaby weighs about 15 – 26 kg. The males are 77-88 cm in height and the females are about 70-84 cm tall. Their tail is 80 cm long, which is almost the length of their entire body. They use their tail to balance and jump around. They also use it to prop into a sitting position.',
    'Wallabies are pink and furless at birth.',
    )

WALRUS_FACTS = (
    'The scientific name for a walrus is Odobenus Rosmarus. It is latin for tooth walking sea-horse.',
    'A male walrus is called a bull. A female walrus is called a cow. A baby walrus is called a calf.',
    'Walruses spend half their time on land and the other half in water.',
    'There are two sub-species of walruses. The Atlantic Walrus and the Pacific Walrus.',
    'Walruses live in the Northern Hemisphere in the Arctic.',
    'Atlantic walruses live near Northern Canada to Greenland.',
    'Walruses are grey or brown but turn a pinkish color as they age.',
    'Walruses have thick skin and then a layer of blubber. Their blubber keeps them warm in icy waters.',
    'Walruses grow to be 7.5 pounds to 11.5ft. Walruses can weigh up to 4,000 pounds',
    'Walruses whiskers are called vibrissae.',
    'Walruses have 450 whiskers. Their whiskers are very sensitive and are used to help them locate food.',
    'Walruses can hold their breath under water for up to 30 minutes.',
    'Walruses live between 30-40 years in the wild.',
    'Female walruses give birth to their babies on land or on ice floes.',
    'Baby walruses weigh between 100-165 pounds!',
    'There are around 250,000 walruses left in the wild.',
    'Walruses were hunted by humans for their blubber and ivory tusks.',
    'Walruses weigh from 600 to 1,500 kilograms (1,320 to 3,300 lbs.) and can be as long as 3.2 meters (10.5 feet).',
    'Walrus tusks can grow up to 3 feet (1 m). The tusks are canine teeth and stick out from either side of the animal’s mouth.',
    'Walruses use their tusks to break through ice, and to assist in climbing out of the water and onto the ice. The animals also use their tusks to defend themselves from larger predators and to establish dominance and a hierarchy among walruses.',
    'Walruses can swim on average around 4.35 mph (7 km/h) and as fast as 21.74 mph (35 km/h).',
    'A group of walruses is called a herd. They gather by the hundreds to sunbathe on the ice. During mating season, walruses amass by the thousands.',
    'Walruses are carnivores, but they aren’t ferocious hunters. The walrus’ favorite food is shellfish.',
    'There are three subspecies of walrus. Atlantic walruses live in the coastal areas along northeastern Canada to Greenland. Pacific walruses live in the northern seas near Russia and Alaska. Laptev walruses live in the Laptev Sea of Russia.',
    'In the 1950s, the population of walruses was almost eliminated due to commercial hunting, but the population was brought back to a thriving number in the 1980s.',
    'Native people of the Arctic hunt walruses for hides, food, ivory and bones. These natives are now the only people who are allowed to legally hunt walruses.',
    'Walruses have only two natural predators: the orca (or killer whale) and the polar bear. Both are more likely to hunt walrus calves than adults.',
    )

WARTHOG_FACTS = (
    'Warthogs get their name from the patches of skin on their face that look like warts. These “warts” are thick growths of skin that act as padding for when males fight during mating season.',
    'Did you know - during a dry season, a warthog can go months without water. Their bodies will conserve any moisture that would otherwise be used for cooling.',
    'Despite their appearance, warthogs are not aggressive (unless provoked or attacked) and don’t hunt prey. They are herbivores and use their long snouts and tusks to search the ground for roots, berries, bark, grass, or other plants.',
    'Warthogs can get out of a sticky situation fast - when threatened they can run up to 30 miles an hour.',
    'Female warthogs are called sows, and they live together in groups often as large as up to 40 members. Male warthogs live alone and often only join up with sow groups during mating season.',
    'A warthog’s average lifespan in the wild is about 15 years.',
    'Warthogs will often utilize empty dens they find (usually created by aardvarks). In a situation where they are being chased by a predator, warthogs will find these dens to back into - using their tusks to ward away prey from the front.',
    'A warthog is a member of the pig family and can be found in the savannas, open plains, and grasslands of Africa - south of Sahara.',
    'Warthogs don’t have sweat glads to cool themselves off so when it gets warm, a warthog will wallow in mud to cool off.',
    'Warthogs allow birds such as Oxpeckers or Yellow-Billed Hornbills to ride on their back. These birds will often eat insects on the warthog’s body.',
    )

WHALE_FACTS = (
    'Many whales are toothless. They use a plate of comb-like fibre called baleen to filter small crustaceans and other creatures from the water.',
    'There are 79 to 84 different species of whale. They come in many different shapes and sizes!',
    'A baby whale is called a calf. Whales form groups to look after calves and feed together. These groups are often made up of all female or all male whales.',
    'Whales that are found in both Northern and Southern hemisphere never meet or breed together. Their migration is timed so that they are never in breeding areas at the same time.',
    'The arched lower lip of a whale can often make it look like it is smiling! However, this isn’t a “real” smile as the blubber in the head of the whale prevents the muscles of the face from reaching the surface.',
    'You can tell the age of a whale by looking at the wax plug in its ear. This plug in the ear has a pattern of layers when cut lengthwise that scientists can count to estimate the age of the whale.',
    'Whales love to sing! They use this as a call to mates, a way to communicate and also just for fun! After a period of time they get bored of the same whale song and begin to sing a different tune.',
    'Sometimes whales make navigation mistakes during migrations. Although they may have made the mistake days before, they don’t realise it until they become stranded.',
    'Whales support many different types of life. Several creatures, such as barnacles and sea lice, attach themselves to the skin of whales and live there.',
    'Whales are mammals. They breathe air, give birth to live young, and nurse (i.e., feed milk to) their young.',
    'Whales sleep by resting half of their brain at a time. That means they can still surface to breathe while they are sleeping.',
    'Whales have excellent hearing, and can hear other whales from thousands of kilometers away.',
    'The blue whale is the largest animal to have ever lived on Earth; the largest on record was 100 ft. long.',
    'Blue whales are graceful swimmers. They cruise the ocean at over 8km/h and can reach speeds of over 30km/h.',
    'Various scientific studies have calculated life expectancy averages of various whale species to range anywhere from 30 to 70 years all the way up to 200 years.',
    'Blue whales mainly catch their food by diving and they can descend to depths of approximately 500m.',
    'Whales have few predators but are known to fall victim to attacks by sharks and killer whales, and many are injured or die each year from impacts with large ships.',
    'Females breed only once every three years and gestation is between 11-12 months. Females usually only have one young.',
    'A baby blue whale (calf) emerges weighing up to 3 tons and stretching to 25 feet.',
    'Intensive hunting in the 1900s by whalers seeking whale oil drove them to the brink of extinction. Hundreds of thousands of whales were killed.',
    'It is estimated that only 10,000-25,000 blue whales now swim the world’s oceans.',
    'Blue whale can produce the loudest sound of any animal. At 188 decibels, the noise can be detected over 800 kilometers (500 miles) away.',
    )

WILDEBEEST_FACTS = (
    'Wildebeest are one of the largest antelopes. They can reach 8 feet in length, 4.5 feet in height and weigh up to 600 pounds.',
    'Between January and March, half a million wildebeest are born each year in the Serengeti. February, is the month with the most babies, around 8,000 are born each day.',
    'During migration, wildebeests travel between 500 and 1000 miles. Timing of migration is determined by weather conditions, but it usually takes place during the months of May and June.',
    'When the Dutch settled in South Africa, they named this animal “wildebeest,” meaning “wild beast,” due to its untamed appearance and vigorous nature.',
    'Both males and females possess lengthy horns that spring outward from the base of their head and form curved semicircles, pointing slightly backward.',
    'Wildebeest live in massive herds of sometimes thousands, and many participate in the Great Migration, one of the most amazing spectacles in the animal kingdom.',
    'In East Africa, an estimated 300,000 - 500,000 wildebeest calves are born every year between January - February. New calves are able to walk on their own within minutes of being born!',
    'Wildebeest live in the plains and open woodlands in southern Africa. The biggest herds can be found in the Serengeti desert.',
    'Wildebeest trek around 30 miles every day and approximately 1,000 miles a year as the they follow the rains in order to find the best grass.',
    'Wildebeest are herbivorous animals and graze on grasses, leaves and shoots.',
    'When danger is spotted, the wildebeest warn each using groaning calls and then run together creating a stampede, both to escape approaching predators and also to intimidate them.',
    'Wildebeests look like a cross between a moose and a bull. They grow up to 4.5 feet (1.37 meters) tall, these animals have skinny legs, lean bodies, and a large head with two curved horns.',
    'There are 2 species of wildebeest which are the Black Wildebeest (Connochaetes gnou) and the Blue Wildebeest (Connochaetes taurinus), both are native to Africa.',
    'Wildebeest have a top speed of roughly 40 miles/hour, and will run together as herds to scare away and avoid predators.',
    'Mature male wildebeest will actively defend and mark their territory by means of poop and scent marking. They have modified glands in their eyes and feet and they will rub against trees or rake soil to leave their scent.',
    )

WOLF_FACTS = (
    'Wolves are excellent hunters and have been found to be living in more places in the world than any other land mammal except humans.',
    'The wolf is the ancestor of all breeds of domestic dog. It is part of a group of animals called the wild dogs which also includes the dingo and the coyote.',
    'Most wolves weigh about 40 kilograms but the heaviest wolf ever recorded weighed over 80 kilograms!',
    'Adult wolves have large feet. A fully grown wolf would have a paw print nearly 13 centimeters long and 10 centimeters wide.',
    'Wolves live and hunt in groups called a pack. A pack can range from two wolves to as many as 20 wolves depending on such factors as habitat and food supply. Most packs have one breeding pair of wolves, called the alpha pair, who lead the hunt.',
    'Wolf pups are born deaf and blind while weighing around 0.5 kg (1 lb). It takes about 8 months before they are old enough to actively join in wolf pack hunts.',
    'Wolves in the Arctic have to travel much longer distances than wolves in the forest to find food and will sometimes go for several days without eating.',
    'When hunting alone, the wolf catches small animals such as squirrels, hares, chipmunks, raccoons, or rabbits. However, a pack of wolves can hunt very large animals like moose, caribou and yaks.',
    'When a pack of wolves kill an animal, the alpha pair always eats first. As food supply is often irregular for wolves, they will eat up to 1/5th of their own body weight at a time to make up for days of missed food.',
    'Wolves have two layers of fur, an undercoat and a top coat, which allow them to survive in temperatures as low at minus 40 degrees fahrenheit! In warmer weather they flatten their fur to keep cool.',
    'A wolf can run at a speed of 40 miles per hour during a chase. Wolves have long legs and spend most of their time trotting at a speed of 7-10 miles per hour. They can keep up a reasonable pace for hours and have been known to cover distances of 55 miles in one night.',
    )

WOLVERINE_FACTS = (
    'A wolverine is a mammal which resembles a small bear, but it is actually the largest member of the weasel family.',
    'Wolverines live in the arctic and subarctic areas of North America, Canada, North Europe, Russia, and Siberia.',
    'Wolverines are nocturnal animals, which travel 15 to 20 miles each day in the search for food. They can pass even more (between 37 to 50 miles) when food sources are scarce.',
    'Wolverines are omnivores. They eat rabbits, mice, porcupines, squirrels, and they also hunt injured deer and caribou. During summer months, they expand their diet to feed on berries and roots.',
    'Wolverines feed on leftovers of dead animals. Due to their excellent sense of smell, they can detect carrion (decaying flesh of dead animals) hidden under 20 feet of snow. Wolverines will also dig snow if they sense the smell of the hibernating mammal.',
    'Wolverines are territorial animals who demand a lot of open space to roam. Males use a scent gland to mark the boundaries of his territory. Since they are polygamous, males will normally share their territory with multiple females.',
    'Since the substance secreted by a their anal gland has a very strong and unpleasant smell, wolverines are also known as "skunk bears".',
    'Female wolverines give birth to two to three babies each year, usually in the late winter or early spring. Young wolverines (kits) are born in an underground den.',
    'Young wolverines stay with their mother until they reach the age of two years. At that time, wolverines become sexually mature.',
    'The average lifespan of a wolverine in the wild is between 7 and 12 years.',
    'Wolverines sport heavy, attractive fur that once made them a prime trappers target in North America. Their fur was used to line parkas, though this practice is far less common today and the animals are protected in many areas.',
    'A wolverine can grow up to 42 inches (107 centimeters) long, though 32 to 34 inches (81 to 86 centimeters) is the more common length. It can also weigh up to 70 pounds (32 kilograms), with males being almost twice as heavy as females. Of all the mustelids, only the sea otter and the giant otter are larger.',
    'Wolverines are among the few animals that consume the bones of other animals, even the teeth. Because of this, wolverines have been likened to hyenas.',
    'Wolverines sleep, hunt, and give birth on the ground. However, they can climb trees just like some bears. They can do this because of their long, sharp hook-like claws, which they also use to climb sheer cliffs, icefalls, and snowy peaks.',
    )

YAK_FACTS = (
    'The yak is a long-haired bovid found throughout the Himalaya region of southern Central Asia, the Tibetan Plateau, and as far north as Mongolia and Russia.',
    'Most yaks are domesticated animals, though there is also a small, vulnerable wild yak population.',
    'Bos mutus is the scientific name for the wild yak and Bos grunniens for domesticated yak.',
    '90 percent of all known yaks can be found in Tibetan Plateau in the Himalayas.',
    'Yak is a close relative of buffalo and bison.',
    'The average lifespan of a yak is about 20 years in the wild and slightly longer when in captivity.',
    'The yak is a herd animal that tend to gather in herds from 10 to 100 yaks, most of which are females and their young.',
    'The yak is the third largest beast in Asia, after the elephant and rhino.',
    'Body of yak is covered with thick, wooly coat. It can be brown, black or white in color. Main purpose of the fur is preservation of the body heat and protection against low outer temperatures.Domesticated yak’s coat is less furry, but more diverse in color than the wild yak.',
    'Yaks have long, bushy tails which are used for the production of fake beards in certain Chinese theaters.',
    'Among domesticated animals, yaks are the highest dwelling animals of the world, living at 3,000–5,000 meters (9,800–16,400 feet).',
    'Yaks are herbivores. A great deal of a yaks time is spent on grassy plains in the mountains grazing on grasses, herbs, and wild flowers.',
    'Yaks grunt and, unlike cattle, are not known to produce the characteristic bovine lowing (mooing) sound.',
    )

ZEBRA_FACTS = (
    'Zebra are part of the equidae family along with horse and donkeys.',
    'Every zebra has a unique pattern of black and white stripes.',
    'There are a number of different theories which attempt to explain zebra’s unique stripes with most relating to camouflage.',
    'Common plain zebras have tails around half a meter in length (18 inches).',
    'Zebra crossings (pedestrian crossings) are named after the black and white stripes of zebras.',
    'Zebras run from side to side to being chased by a predator.',
    'Zebras have excellent eyesight and hearing.',
    'Zebras stand up while sleeping.',
    'Zebras eat mostly grass.',
    'The ears of a zebra show its mood.',
    'A zebra named Marty starred in the 2005 animated film Madagascar.',
    'Zebras are very fast animals, and can gallop at speeds of up to 65 km/h. This is fast enough to outrun many predators.',
    'Zebra foals can run within a few hours of birth.',
    'Zebras are one of the few mammals that scientists believe can see in color.',
    'Like horses, zebras sleep standing up, and usually only when in the safety of a group.',
    )

ZEBRAFISH_FACTS = (
    'The scientific name of Zebrafish is Danio rerio and it belongs to the minnow family, Cyprinidae. The fish got its common name from the presence of five uniform and pigmented horizontal stripes on the side of its body, that resemble the stripes of a zebra.',
    'Zebrafish are vertebrates, which means that they have a backbone like humans.',
    'The Zebrafish is perhaps one of the most frequently used model organisms for genetic and developmental studies. This tropical freshwater fish can be found in the rivers of northern India, northern Pakistan, Bhutan, and Nepal.',
    'A Zebrafish usually grows to a length of 6.4 cm. But in captivity, it rarely exceeds a length of 4 cm.',
    'Zebrafish embryos are nearly transparent which allows researchers to easily examine the development of internal structures.',
    'The male Zebrafish is usually slender with a torpedo-shaped body. It can be distinguished from the female by the presence of golden stripes in between the blue stripes. The female zebrafish, on the other hand, has a larger belly and silver stripes between its blue stripes',
    'Zebrafish are omnivorous and can eat anything smaller than them. They mainly feed on insects and insect larvae, phytoplankton, and zooplankton. But, they can also feast on worms and small crustaceans.',
    'Zebrafish can regenerate their fins, heart muscles, and retinal neurons.',
    'Zebrafish is one of the few species of fish that has been sent to space.',
    'Zebrafish have a similar genetic structure to humans. They share 70 per cent of genes with us.',
    'There are several varieties of Zebrafish, such as long-finned, short-finned, albino, pink, striped, and speckled. Zebrafish have also been modified to create several genetic variants of the same species, mainly for scientific research.',
    )

ALL_FACTS = (
    AARDVARK_FACTS,
    AARDWOLF_FACTS,
    AFRICAN_GREY_FACTS,
    ALBATROSS_FACTS,
    ALLIGATOR_FACTS,
    ALPACA_FACTS,
    ANACONDA_FACTS,
    ANGLERFISH_FACTS,
    ANT_FACTS,
    ANTEATER_FACTS,
    ANTELOPE_FACTS,
    ARMADILLO_FACTS,
    ATLANTIC_PUFFIN_FACTS,
    AVOCET_FACTS,
    AXOLOTL_FACTS,
    BADGER_FACTS,
    BARNACLE_FACTS,
    BEAR_FACTS,
    BEAVER_FACTS,
    BISON_FACTS,
    BLOBFISH_FACTS,
    BOBCAT_FACTS,
    BUFFALO_FACTS,
    BUTTERFLY_FACTS,
    CAMEL_FACTS,
    CAPYBARA_FACTS,
    CHAMELEON_FACTS,
    CHEETAH_FACTS,
    CHEVROTAIN_FACTS,
    CHICKEN_FACTS,
    CHIMPANZEE_FACTS,
    CHINCHILLA_FACTS,
    CHIPMUNK_FACTS,
    CLOWNFISH_FACTS,
    COBRA_FACTS,
    CONURE_FACTS,
    COUGAR_FACTS,
    COW_FACTS,
    COYOTE_FACTS,
    CRAB_FACTS,
    CRANE_FACTS,
    CRAYFISH_FACTS,
    CROCODILE_FACTS,
    CUTTLEFISH_FACTS,
    DEER_FACTS,
    DEGU_FACTS,
    DINGO_FACTS,
    DODO_FACTS,
    DOLPHIN_FACTS,
    DUGONG_FACTS,
    EAGLE_FACTS,
    EARTHWORM_FACTS,
    EARWIG_FACTS,
    ECHIDNA_FACTS,
    ELAND_FACTS,
    ELEPHANT_FACTS,
    ELEPHANT_SHREW_FACTS,
    ELK_FACTS,
    EMU_FACTS,
    FALCON_FACTS,
    FERRET_FACTS,
    FIRESALAMANDER_FACTS,
    FLAMINGO_FACTS,
    FLY_FACTS,
    FOX_FACTS,
    FROG_FACTS,
    GAZELLE_FACTS,
    GECKO_FACTS,
    GIBBON_FACTS,
    GIRAFFE_FACTS,
    GOAT_FACTS,
    GOOSE_FACTS,
    GOPHER_FACTS,
    GORILLA_FACTS,
    GRASSHOPPER_FACTS,
    HAMSTER_FACTS,
    HAWK_FACTS,
    HEDGEHOG_FACTS,
    HIPPO_FACTS,
    HONEYBADGER_FACTS,
    HONEYBEE_FACTS,
    HORSE_FACTS,
    HUMMINGBIRD_FACTS,
    HUSKY_FACTS,
    IBEX_FACTS,
    IGUANA_FACTS,
    JACKAL_FACTS,
    JELLYFISH_FACTS,
    JERBOA_FACTS,
    KANGAROO_FACTS,
    KIWI_FACTS,
    KOALA_FACTS,
    KOOKABURRA_FACTS,
    LADYBUG_FACTS,
    LAMPREY_FACTS,
    LEMUR_FACTS,
    LEOPARD_FACTS,
    LION_FACTS,
    LIZARD_FACTS,
    LLAMA_FACTS,
    LOBSTER_FACTS,
    LYNX_FACTS,
    MANATEE_FACTS,
    MANTIS_SHRIMP_FACTS,
    MARKHOR_FACTS,
    MEERKAT_FACTS,
    MINK_FACTS,
    MONGOOSE_FACTS,
    MONKEY_FACTS,
    MOOSE_FACTS,
    MOUSE_FACTS,
    NARWHAL_FACTS,
    NEWT_FACTS,
    NIGHTJAR_FACTS,
    OCELOT_FACTS,
    OCTOPUS_FACTS,
    OPOSSUM_FACTS,
    ORANGUTAN_FACTS,
    ORCA_FACTS,
    ORYX_FACTS,
    OSTRICH_FACTS,
    OTTER_FACTS,
    OWL_FACTS,
    PANDA_FACTS,
    PANGOLIN_FACTS,
    PANTHER_FACTS,
    PARROT_FACTS,
    PEACOCK_FACTS,
    PECCARY_FACTS,
    PENGUIN_FACTS,
    PIG_FACTS,
    PIGEON_FACTS,
    PLATYPUS_FACTS,
    PORCUPINE_FACTS,
    PUFFERFISH_FACTS,
    PUMA_FACTS,
    PRAYINGMANTIS_FACTS,
    QUOKKA_FACTS,
    RABBIT_FACTS,
    RACCOON_FACTS,
    RATTLESNAKE_FACTS,
    RAVEN_FACTS,
    REINDEER_FACTS,
    RHINO_FACTS,
    SALMON_FACTS,
    SCORPION_FACTS,
    SEAGULL_FACTS,
    SEAHORSE_FACTS,
    SEA_CUCUMBER_FACTS,
    SEA_URCHIN_FACTS,
    SHARK_FACTS,
    SHEEP_FACTS,
    SHRIMP_FACTS,
    SKUNK_FACTS,
    SLOTH_FACTS,
    SNAIL_FACTS,
    SNAKE_FACTS,
    SPIDER_FACTS,
    STARFISH_FACTS,
    STOAT_FACTS,
    STURGEON_FACTS,
    SQUIRREL_FACTS,
    STINGRAY_FACTS,
    SUNFISH_FACTS,
    TARANTULA_FACTS,
    TARDIGRADE_FACTS,
    TARSIER_FACTS,
    TASMANIAN_DEVIL_FACTS,
    TIGER_FACTS,
    TOAD_FACTS,
    TOUCAN_FACTS,
    TROUSER_SNAKE_FACTS,
    TROUT_FACTS,
    TUATARA_FACTS,
    TURTLE_FACTS,
    VAMPIRE_BAT_FACTS,
    VULTURE_FACTS,
    WALLABY_FACTS,
    WALRUS_FACTS,
    WARTHOG_FACTS,
    WHALE_FACTS,
    WILDEBEEST_FACTS,
    WOLF_FACTS,
    WOLVERINE_FACTS,
    YAK_FACTS,
    ZEBRA_FACTS,
    ZEBRAFISH_FACTS,
    )


def main():
    reddit = authenticate()
    while True:
        print(
            "Wait time after commenting will be " +
            str(wait_time) +
            " seconds.\n")
        animalfactsbot(reddit)


if __name__ == '__main__':
    main()
