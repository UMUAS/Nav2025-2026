import depthai as dai
import argparse

class Camera:
    def __init__(self):
        pass

def main(raw_args=None):
    parser = argparse.ArgumentParser(description="Runs DepthAI")
    parser.add_argument('-gui', action='store_true')
    args = parser.parse_args(raw_args)

    print('Running DepthAI with OpenCV')
    #TODO

if __name__ == '__main__':
    main()