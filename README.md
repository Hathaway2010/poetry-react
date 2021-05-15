# poetry-react

# Scansion

## Introduction

This is a remake of [poetry-scansion](https://github.com/Hathaway2010/poetry-scansion), Django (Python) web app with a SQLite database, using React and SCSS on the frontend. It allows students of metrical poetry to practice scansion on pre-scanned poems and, when their scansions prove reliable enough, to help train the app to scan poems by correcting its automatic scansions. This app was originally a final project for Harvard's CS50W MOOC, and it is one component of what I hope will become a larger suite of poetry-analysis and learning tools.

The app can be accessed at poetry-scansion.hathaway2010.repl.co

## How to Use

 If a user wants to see how their scansions stack up with mine (I will consider my scansions somewhat authoritative until the app finds multiple skilled users), they can look at the provided poem, click the symbols above the words until they match the user's guess at a scansion ("/" indicates an accented syllable, "u" an unaccented), adding and subtracting syllables using the "+" and "-" buttons below the words as needed. Then, when the user clicks the "submit scansion" button at the bottom of the poem, they will be notified whether they would have gained a point (agreed with an authoritative scansion in the scansions of 90% or more of the words), kept their current score (agreed with an authoritative scansion on 70% - 90% of the words), or lost a point (agreed on fewer words than that). Once they click "ok" on the alert giving them their score, they will see the words on which they disagreed highlighted in red and the words on which they agreed highlighted in green.
 
 The user can work from a "Blank Slate," in which all syllables are initially marked as unstressed, or from one of the machine scansions that appear on a dropdown menu; choose a different poem from the poet and poem dropdown menus; or input their own poem (if they are promoted and alter its machine scansion, the individual words and their scansions will be saved to the database, if any have not yet occurred, but the poem as a whole will not.)

 If the user logs in or registers, their scores will be recorded; if they reach a score of 10, they will be promoted and their altered scansions will overwrite the original scansions, though they'll still be informed of the locations of mismatches. They will also have the option of scanning poems that have not yet been scanned by a human (if any exist).

## About the Automated Scansion Process

At the moment, the app's scansion of a line of poetry depends upon the ratio between the number of times each syllable of each word has been marked (in a dictionary or by a user) as stressed to the number of times that syllable has been marked as unstressed.

The algorithm I first used to do this comparison was quite simple: the ratio for each syllable was compared to the ratio for the next syllable in the line (the last syllable was compared instead to the preceding syllable). While the program seemed to be steadily, albeit slowly, improving as it got more data on words' stress patterns, it was not close to being "promoted": usually it disagreed with my scansion of 20-40% of the words in a given poem.

The default algorithm I call the House Robber algorithm because it was based on [this](https://leetcode.com/problems/house-robber/discuss/156523/From-good-to-great.-How-to-approach-most-of-DP-problems) solution to the House Robber problem on LeetCode. The algorithm finds the combination of "houses" (in this case, syllables) that gives it the maximum sum of loot (here, defined as the stressed / unstressed ratio) without skipping more than two syllables in a row or accenting two adjacent syllables. Now, my somewhat limited experimentation so far suggests, the algorithm usually gets only 0.2- 0.02 of the words wrong — a massive improvement!

In addition, I've implemented a third algorithm, which I call Simple Scan: it guesses the stressed or unstressed status of a syllable based simply on the stressed/unstressed ratio, using no comparison. I hypothesize that this would do well for prose or verse that does not follow any particular metrical pattern.

The initial data on the words' patterns of stressed and unstressed syllables comes from Webster's Unabridged Dictionary from 1913, downloaded from Project Gutenberg and loaded into a database. Of course, this dictionary does not contain all words (especially plurals, different tenses, etc.), so it was also necessary to devise a means for attempting to count the syllables of words not included in that dictionary. In this I was inspired by Holtzscher's [syllapy](https://github.com/mholtzscher/syllapy), although I have added more sensitivity in a few areas, most notably regarding silent -ed and -es.

## About the Poems

All of the current poems available for practice except "Jabberwocky" by Lewis Carroll come from *The Golden Treasury*, a beloved nineteenth-century poetry anthology edited by Francis Turner Palgrave, found on Project Gutenberg; "Home-Bound" comes from a different Gutenberg anthology, *Anthology of Massachusetts Poets*, edited by William Braithwaite)

## How to Run the App Locally

Running this version of the app is considerably more complicated than the plain-JS version; expect an update later that will explain how to set up React and Sass. However, the [instructions from poetry-scansion](https://github.com/Hathaway2010/poetry-scansion/blob/main/README.md) hold good for the Django portion of the app.

## Tests

The tests at present are not up-to-date with the code. Expect updates soon.

## Future Directions
 - While the House Robber algorithm has improved my app's scansion ability enormously, I look forward to experimenting with more possibilities. I might want to: take into account words' positions in their lines, the grammatical role they play, the total number of ratings the word has received instead of just the ratio of one stress pattern to another, and the meter (if any) that the poem seems to obey (if the program could, for instance, observe that a poem was generally iambic, trochaic, anapestic, or dactylic and then apply that knowledge to scanning the apparently non-conforming parts of the poem, allowing the meter to take precedence in ambiguous cases while leaving unambiguous as they are, this might improve my program's scansion ability dramatically.)
 - I might add the ability to like poems and comment on them. Comments particularly could be helpful for discussing tricky metrical points. Scansion is an ambiguous art, and while some scansions are clearly wrong to the trained ear, which are right can be a matter of deep disagreement. (This is why I do not expect anyone's scansions to agree with mine exactly, and why I allow promoted users to override previous human scansions; their scansions may or may not be better than the previous human's, but they're unlikely to be absurd, and will benefit the computer's statistics by reinforcing points of agreement and adding ambiguity in areas of disagreement).
 - I will continue to add poems to the database.
 - The dictionary portion of the database has more than 100,000 entries, and updating it with the information from a given new scansion is slow. I suspect both that SQLite is not adequate to my needs here, and that my database structure and the code that updates the database could be more efficient. I plan to work on both of these issues.
 - Eventually I would like to teach my programs to analyze many other aspects of poetry as well (identify rhyme, alliteration, assonance, and specific poetic forms, for instance; and perhaps even something involving tone and subject matter!) and begin storing such information in the database so poets, periods, and poems can be compared in interesting and productive ways.
