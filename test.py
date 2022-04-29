

if __name__ == '__main__':
    f = open('requirements.txt')
    line = f.readline()

    while line:
        line = line.split('==')[0]
        print('import ' + line)
        line = f.readline()


