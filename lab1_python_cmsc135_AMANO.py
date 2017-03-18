def make_ing_form(word):
    specialE = ["be"]
    if word.endsWith("ie"):
        return word[: (len(word)- 2) ] + "ying"
    elif word.endsWith("ee"):
        return word[: (len(word)- 2) ] + "ing"
    elif word[(len(word)-3):].match("([bcdfghjklmnpqrstvwxz][aeiou][bcdfghjklmnpqrstvwxz])"):
        return word + word[: (len(word)- 1) ] + "ing"
    elif word[(len(word) - 1)] == "e":
        if word.lower() in withE:
            return word + "ing"
        else:
            return word[: (len(word) - 1) ] + "ing" + word[ (len(word) - 1) + 1:]
    else:
        return word + "ing"


def find_longest_word(words):
    longest = 0
    for word in words:
        longest = longest if longest >= len(words) else len(words)
    
    return longest


def  is_member(x, a):
    i = 0
    while i < len(a):
        if a[i] == x:
            return True
        i+=1
    return False



print(make_ing_form("able"))
