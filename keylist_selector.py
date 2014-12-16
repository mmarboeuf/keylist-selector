"""
    This script selects the highest scoring keyword list from a list of input
    keywords utilizing a multi-factor scoring model.
    
    Input keywords and their metrics are read in from a file containing all
    relevant information (key,traffic,iphone_diff,iphone_apps,ipad_diff,
    ipad_apps).

    Keyword metrics used in multi-factor model
    difficulty: How hard to rank for a keyword (0=easy, 10=hard to rank for)
    traffic: How high is keyword serach volume (0=no traffic, 10=high traffic)
    apps: How many apps use a keyword (number >= 0)
    key length: Char length of a keyword    

    You can find a detailed description of how to select the right keywords
    for your app on my blog here:
    
    Part 1: How to find relevant keywords for your app
            http://blackboardmadness.com/blog/app-store-optimization-aso-selecting-the-right-keywords-part-1/
    Part 2: Description of a basic keyword selection process
            http://blackboardmadness.com/blog/app-store-optimization-aso-selecting-the-right-keywords-part-2/
    Part 3: Introduction to a multi-factor scoring model utilized in this script
            http://blackboardmadness.com/blog/app-store-optimization-aso-selecting-the-right-keywords-part-3/
    
    Sample data "in_sample_key_metrics.csv" and "in_sample_keypair_metrics.csv"
    is real Apple App Store data scraped from ASO sites as of Dec 2014.
    
    :copyright: (c) 2014 by Szilard Szasz-Toth.
    :license: MIT, see LICENSE for more details.
"""

import csv
import itertools
import time


class KeyDataStore(object):
    """Object to store keyword data.

    Attributes:
        keys: List of input keywords used for the selection.
        scores: Aggregated score of each input keyword, calculated as a weighted
            sum of the keyword metrics.
        traffic: Search volume for each input keyword.
        iphone_diff: iPhone difficulty metric for each input keyword.
        iphone_apps: Number of iPhone apps using each input keyword.
        ipad_diff: iPad difficulty metric for each input keyword.
        ipad_apps: Number of iPad apps using each input keyword.
        avg_diff: The average between iphone_diff and ipad_diff.
        avg_apps: The average between iphone_apps and ipad_apps.
        key_len: Char length of each input keyword.
    """
    
    keys = []
    scores = []
    traffic = []
    iphone_diff = []
    iphone_apps = []
    ipad_diff = []
    ipad_apps = []
    avg_diff = []
    avg_apps = []
    key_len = []

    def __init__(self):
        self.keys = []
        self.scores = []
        self.traffic = []
        self.iphone_diff = []
        self.iphone_apps = []
        self.ipad_diff = []
        self.ipad_apps = []    
        self.avg_diff = []
        self.avg_apps = []
        self.key_len = []

def read_in_keydata(file):
    """Read in keyword data from input file.
    
    Fetches list of keywords with corresponding keyword metrics and stores
    data in object KeyDataStore (keyword metrics are scraped from different 
    sources and processed in a separate script).

    Args:
        file: Name of csv input file holding all keyword data.

    Returns:
        A KeyDataStore object that stores all information of the input keys.
    """

    key_data = KeyDataStore()
    file_header = []

    try:
        csvfile = open(file, 'r', newline='', encoding='utf-8')
    except IOError as e:
        print('Exception: %s' % e)
        return key_data

    csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    
    for i, row in enumerate(csvreader):

        # Store header
        if (i == 0):
            file_header = row
        else:
            key = row[file_header.index("key")]
            key_data.keys.append(key)
            key_data.key_len.append(len(key))

            key_data.traffic.append(float(
                row[file_header.index("traffic")]))
            
            iphone_diff = float(row[file_header.index("iphone_diff")])
            iphone_apps = float(row[file_header.index("iphone_apps")])
            ipad_diff = float(row[file_header.index("ipad_diff")])
            ipad_apps = float(row[file_header.index("ipad_apps")])
            
            key_data.iphone_diff.append(iphone_diff)
            key_data.iphone_apps.append(iphone_apps)
            key_data.ipad_diff.append(ipad_diff)
            key_data.ipad_apps.append(ipad_apps)
            
            key_data.avg_diff.append(0.5 * (iphone_diff + ipad_diff))
            key_data.avg_apps.append(0.5 * (iphone_apps + ipad_apps))
        
    return key_data
            
def calc_keylist_permutations(keys, max_keylist_len, min_keylist_len, file=""):
    """Determine all possible keyword combinations.
    
    For a given set of input keywords, determines all possible keyword 
    combinations. Each keyword combination is a potential candidate to be 
    selected as the final keyword list, has to have at least min_keylist_len 
    chars and no more than max_keylist_len chars (separated by a comma).
    
    Args:
        keys: Set of input keywords to determine keyword combinations.
        max_keylist_len: Maximum allowed char length of a keyword combination.
            Keyword combinations exceeding max_keylist_len will skipped.
        min_keylist_len: Minimum allowed char length of a keyword combination.
            Keyword combinations with less than min_keylist_len will be skipped.
        file: Name of output file, where list of keyword combinations will be 
            stored to (optional. If left empty, no file stored).

    Returns:
        A list of all possible keyword lists that do not violate the min/ max
        char length restrictions.
    """

    print("input keys: ", keys, "\n")
    
    key_lists = []
    perms = []

    # Get composite key length (length of all input keys separated by a comma)
    keylist_len = len(",".join(keys))    

    if keylist_len > max_keylist_len:
        
        # Create keyword combinations
        for i in range(len(keys)+1):        
            for c in itertools.combinations(keys, i):
                cc = ','.join(c)
                if len(cc) >= min_keylist_len and len(cc) <= max_keylist_len:
                    perms.append(c)
        
        # Sort all permutations to delete duplicates
        sorted_perms = [sorted(p) for p in perms]
        
        # Delete duplicates
        unique_perms = [list(x) for x in set(tuple(x) for x in sorted_perms)]
        
        # Delete all permutation subsets, e.g. "add,math" is a subset of 
        # "add,math,calculate"
        no_subset_perms = unique_perms[:]
        for i,cur_perm in enumerate(unique_perms):
            for j,next_perm in enumerate(unique_perms):
                if set(cur_perm).issubset(set(next_perm)) and i!=j:
                    no_subset_perms.remove(cur_perm)
                    break
        
        key_lists = no_subset_perms[:]

    else:
        # Include all input keys, if composite key length below max key length
        print("Input keys below max char length. Including all keys.")
        key_lists = [keys[:]]

    # Write unique keyword lists without sublists to csv
    if file != "":
        with open(file, 'w', newline='', encoding='utf8') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', 
                quotechar='|', quoting=csv.QUOTE_MINIMAL)    
            for key_list in key_lists:
                csvwriter.writerow(key_list)        
        print("Keyword lists exported to file: %s" % file)

    return key_lists

# Calculate individual key scores as weighted sum over relevant factors
# factors: difficulty, traffic, number of apps, key length
def calc_key_scores(key_data, w_factors, apps_base, keylen_base, file=""):
    """Calculate individual keyword score for all input keywords.
    
    Calculates keyword score as the weighted sum over all keyword metrics, 
    traffic, average difficulty, average number of apps and keyword length. All
    individual keyword metrics are normalized to be in range [0,10], where 0 is
    the worst score and 10 the best score.
    
    Args:
        key_data: KeyDataStore object containing all keyword metrics.
        w_factors: Factor weights.
        apps_base: Integer value used to normalize key metric number of apps.
        keylen_base: Integer value used to normalize keyword length metric.
        file: Name of output file (optional. If left empty, no file stored).

    Returns:
        A list of scores for all input keywords.
    """

    w_sum = (w_factors['w_diff'] + w_factors['w_traffic'] + 
        w_factors['w_apps'] + w_factors['w_keylen'])
    if (w_sum != 1):
        print("Error: Factor weights don't add up to 100%.")
        return []

    # Reverse difficulty score to be in score range [0=worst, 10=best]. Scraped
    # values are in reverse order [0=best, 10=worst]
    norm_diff = [10 - diff for diff in key_data.avg_diff]
    norm_traffic = key_data.traffic[:]

    # Linearize number of apps to be in score range [0,10]. Keys with number of 
    # apps above twice the apps_base receive a score of 0.
    norm_apps = [10 - min(apps/(apps_base*2) * 10, 10) 
        for apps in  key_data.avg_apps]

    # Linearize keyword length to be in range [0,10]. Any key with key length 
    # above twice the keylen_base will receive 0 score.
    norm_keylen = [10 - min(key_len/(keylen_base*2) * 10, 10) 
        for key_len in key_data.key_len]

    # Calculate keyword score
    for i in range(len(key_data.keys)):
        score = (w_factors['w_diff'] * norm_diff[i] + 
            w_factors['w_traffic'] + norm_traffic[i] +
            w_factors['w_apps'] * norm_apps[i] +
            w_factors['w_keylen'] * norm_keylen[i])
        key_data.scores.append(score)


    if file != "":
        # write values to csv
        with open(file, 'w', newline='', encoding='utf8') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)

            csvwriter.writerow(['key', 'score', 'avg_difficulty', 'traffic', 
                'avg_apps', 'key_len', 'norm_diff', 'norm_traffic', 'norm_apps', 
                'norm_keylen'])

            for i in range(len(key_data.keys)):
                row_out = [key_data.keys[i], key_data.scores[i], 
                    key_data.avg_diff[i], key_data.traffic[i], key_data.avg_apps[i], 
                    key_data.key_len[i], norm_diff[i], norm_traffic[i], 
                    norm_apps[i], norm_keylen[i]]
                csvwriter.writerow(row_out)
            
        print("Key scores exported to file: %s" % file)

    return key_data.scores

def calc_keylist_scores(key_lists, key_data, max_keylist_len, file=""):
    """Calculate keylist scores.

    Calculates score of each input keyword list as the sum over all individual
    keyword scores. Normalize key score to be in score range [0,1] with
    norm_x = (x-min_score)/(max_score-min_score), where min_score equals 0 and
    max_score equals max_keylisy_len/2 * 10 (i.e. a keylist consisting of single 
    char keywords separated by a comma).
    
    Args:
        key_lists: A list of input keyword lists.
        key_data: KeyDataStore object containing all individual keyword scores.
        max_keylist_len: Maximum allowed char length of a keyword list.
        file: Name of output file (optional. If left empty, no file stored).

    Returns:
        A list of scores for all input keywords.
    """

    keylist_scores = []
    norm_scores = []

    # Maximum score of a keylist
    max_score = max_keylist_len/2 * 10
    
    # Calculate keylist score
    for keylist in key_lists:
        keylist_score = 0
        
        for key in keylist:
            key_score = get_key_score(key, key_data)
            
            if (key_score < 0):
                # Error getting key value
                keylist_score = -99
                break
            else:
                keylist_score += key_score

        # Normalize keylist score to be in range [0,1]
        norm_score = keylist_score/max_score
        
        keylist_scores.append(keylist_score)
        norm_scores.append(norm_score)

    if file != "":            
        # write to csv
        with open(file, 'w', newline='', encoding='utf8') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
        
            csvwriter.writerow(['keylist', 'score', 'norm_score', 'max_score', 
                'length', 'words'])    
            for i in range(len(key_lists)):
                keylist = ",".join(key_lists[i])
                row_out = [keylist, keylist_scores[i], norm_scores[i], max_score,
                    len(keylist), len(key_lists[i])]
                csvwriter.writerow(row_out)

        print("Keylist scores exported to file: %s" % file)

    return norm_scores

def get_key_score(key, key_data):
    """Returns score of a keyword."""
    try:
        return key_data.scores[key_data.keys.index(key)]
    except ValueError as e:
        print("Error: No score for key '%s'. Reason: %s." % (str(key), str(e)))
        return -99

def get_best_keylist(key_lists, keylist_scores):
    """Returns highest scoring keylist."""
    if len(keylist_scores)>0:
        i = keylist_scores.index(max(keylist_scores))
        return (key_lists[i], keylist_scores[i])
    else:
        print("Error: Provided empty keylist.")
        return ("", 0)

def get_keypair_combinations(keys):
    """Returns all dual key permutations.

    Example input keylist "math,physics,practice" returns dual key permutations
    "math physics, math practice, physics math, physics practice, practice math, 
    practice physics".

    Args:
        keys: A list of input keywords.

    Returns:
        A list dual key permutations.
    """
    return [" ".join(x) for x in itertools.permutations(keys, 2)]

def calc_keypair_scores(key_lists, keypair_data, max_keylist_len, file=""):
    """Calculates additional score for using key pairs as search phrase.

    Assume two keylists k1, k2, with same keylist score. Further assume that k1 
    includes keys "angry,birds" and k2 includes "game,birds". Search phrase 
    "angry birds" makes sense and has good search characteristics, whereas
    search phrase "game birds" makes no sense and has no traffic. Hence, k1 
    should have a higher overall keylist score than k2 due to the additional 
    benefit of including useful dual keyword combination "angry birds".

    Args:
        key_lists: A list of keyword lists.
        keypair_data: KeyDataStore object containing all search metrics of 
            relevant dual keyword serach phrases.
        max_keylist_len: Maximum allowed char length of a keyword list.
        file: Name of output file (optional. If left empty, no file stored).

    Returns:
        A list of scores for all dual keyword permutations for each input
        keyword list.
    """

    scores = []
    norm_scores = []
    keylist_perms = []

    # Maximum keypair scores of a keylist, i.e. all possible dual permutations 
    # of single char keywords with each permutation getting score 10
    max_keys = max_keylist_len/2
    max_perms = max_keys * (max_keys-1)
    max_score = max_perms * 10

    for key_list in key_lists:
        keypair_perms = get_keypair_combinations(key_list)
        
        keylist_score = 0
        for keypair in keypair_perms:
            keypair_score = get_key_score(keypair, keypair_data)
            
            if (keypair_score < 0):
                # Error getting key value
                keylist_score = -99
                break
            else:        
                keylist_score += keypair_score
        
        scores.append(keylist_score)
        keylist_perms.append(keypair_perms)

        # Normalize values
        norm_scores.append(keylist_score/max_score)

    # Write to csv
    if file != "":
        with open(file, 'w', newline='', encoding='utf8') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
        
            csvwriter.writerow(['keylist', 'score', 'norm_score', 'max_score', 
                'length', 'words', 'permutations'])
            for i in range(len(key_lists)):
                keylist = ",".join(key_lists[i])
                row_out = [keylist, scores[i], norm_scores[i], max_score,
                    len(keylist), len(key_lists[i]), keylist_perms[i]]
                csvwriter.writerow(row_out)

        print("Keylist keypair scores exported to file: %s" % file)

    return norm_scores

def process(key_data, keypair_data, include_dual_keys, max_keylist_len, 
            min_keylist_len, w_factors, apps_base, keylen_base):

    # Determine keylist permutations
    key_lists = calc_keylist_permutations(key_data.keys, max_keylist_len, 
        min_keylist_len, 'out_keylists.csv')

    # Calculate individual keyword scores
    key_scores = calc_key_scores(key_data, w_factors, apps_base, 
        keylen_base, 'out_key_scores.csv')

    # Calculate keylist scores
    keylist_scores = calc_keylist_scores(key_lists, key_data, max_keylist_len,
        'out_keylist_scores.csv')

    cumulative_scores = []
    if include_dual_keys:
        # Calculate additional score of dual key combinations of keylist
        keypair_scores = calc_key_scores(keypair_data, w_factors, apps_base, 
            keylen_base, 'out_keypair_scores.csv')
        keylist_keypair_scores = calc_keypair_scores(key_lists, keypair_data,
            max_keylist_len, "out_keylist_keypair_scores.csv")
            
        # Calculate cumulative keylist scores, which equals the sum of the 
        # individual keyword scores (twice as important) and the dual key 
        # combination score
        cumulative_scores = [score for score in map(lambda x,y:2/3*x + 1/3*y,
            keylist_scores, keylist_keypair_scores)]
    else:
        keylist_keypair_scores = [0 for score in keylist_scores]
        cumulative_scores = keylist_scores[:]

    with open("out_keylist_scores_cum.csv", 'w', 
        newline='', encoding='utf8') as csvfile:
        
        csvwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)

        csvwriter.writerow(['keylist', 'key_score', 'keypair_score',  
        'cumulative_score', 'length', 'words'])
        for i in range(len(key_lists)):
            keylist = ",".join(key_lists[i])
            row_out = [keylist, keylist_scores[i], keylist_keypair_scores[i],
                 cumulative_scores[i], len(keylist), len(key_lists[i])]
            csvwriter.writerow(row_out)

    # Get keylist with highest score
    (best_keylist, best_score) = get_best_keylist(key_lists, cumulative_scores)
    print("Woohoo, the keylist (%s) has the highest score with %.2f points!\n" 
        % (','.join(best_keylist), best_score))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Keyword selection")
    parser.add_argument("--key_data", default='in_sample_key_metrics.csv',
                        help="Keyword input data")
    parser.add_argument("--keypair_data",
                        default='in_sample_keypair_metrics.csv',
                        help="Key pair data for dual key permutation search " \
                            "phrase computation")
    parser.add_argument("--max_keylist_len", default=100, 
                        help="Max char length of keyword list")
    parser.add_argument("--min_keylist_len", default=90,
                        help="Min char length of keyword list")
    # Default value calculated as average of number of apps of the keys used by
    # the top 200 free apps
    parser.add_argument("--apps_base", default=3500,
                        help="Used to normalize score of number of apps factor")
    # Default value calculated as average keylength of the keys used by
    # the top 200 free apps
    parser.add_argument("--keylen_base", default=6,
                        help="Used to normalize score of keylength factor")
    parser.add_argument("--include_dual_keys", default=True,
                        help="Include score of dual key combinations to " \
                            "determine best keyword list")
                        
    args = parser.parse_args()

    # Start main procedure
    start_time = time.time()

    # Set factor weights
    w_factors = {'w_diff':0.55, 'w_traffic':0.35, 
                'w_apps':0.05, 'w_keylen':0.05}

    # Read in keyword data
    key_data = read_in_keydata(args.key_data)

    if not key_data.keys:
        # No input keywords
        print("Error: Please check input file and keywords.")
    else:
        # Read in dual keyword permutation data
        keypair_data = read_in_keydata(args.keypair_data)
        
        if not keypair_data.keys:
            # In case no  dual key permutations available, skip
            args.include_dual_keys = False
            print("Error: No dual keyword permutations found. Skipping ", 
                "score calculation step for dual key permutations.")

        process(key_data, keypair_data, args.include_dual_keys, 
                args.max_keylist_len, args.min_keylist_len, 
                w_factors, args.apps_base, args.keylen_base)

    print("Elapsed time: ", time.time() - start_time, "seconds")