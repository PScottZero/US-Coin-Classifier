from os import listdir

d = listdir('ebay_images/')
if '.DS_Store' in d:
    d.remove('.DS_Store')
d.sort()

with open('coin_classifier_labels.txt', 'w') as f:
    for coin_type in d:
        f.write('%s\n' % coin_type)
