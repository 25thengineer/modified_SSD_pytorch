from __future__ import print_function
import torch
from torch.autograd import Variable
import cv2
import argparse
from data import TEST_ROOT
import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


from data import BaseTransform, VOC_CLASSES as labelmap
from ssd import build_ssd

parser = argparse.ArgumentParser(description='Single Shot MultiBox Detection')

parser.add_argument('--weights', default="/home/river/Graduation_Project/experiment/"
                                         "code/Python/ssd.pytorch-master/weights/ssd300_COCO_190000.pth",
                    type=str, help='Trained state_dict file path')
parser.add_argument('--cuda', default=False, type=bool,
                    help='Use cuda in live demo')
parser.add_argument('--fileName', default=None, type=str,
                    help='please input the name of test picture')

args = parser.parse_args()

COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
FONT = cv2.FONT_HERSHEY_SIMPLEX


def cv2_demo(net, transform):
    def predict(frame):
        height, width = frame.shape[:2]
        x = torch.from_numpy(transform(frame)[0]).permute(2, 0, 1)
        x = Variable(x.unsqueeze(0))
        y = net(x)  # forward pass
        detections = y.data
        # scale each detection back up to the image
        scale = torch.Tensor([width, height, width, height])
        for i in range(detections.size(1)):
            j = 0
            while detections[0, i, j, 0] >= 0.6: # 0.6
                score = float(detections[0, i, j, 0])
                pt = (detections[0, i, j, 1:] * scale).cpu().numpy()
                cv2.rectangle(frame,
                              (int(pt[0]), int(pt[1])),
                              (int(pt[2]), int(pt[3])),
                              COLORS[i % 3], 2)
                cv2.putText(frame, labelmap[i - 1] + '_' + str(score)[:4], (int(pt[0]), int(pt[1])),
                            FONT, 1, (255, 0, 255), 2, cv2.LINE_AA)
                j += 1
        return frame

    # picNum = "000001"
    # frame = cv2.imread(TEST_ROOT + "VOC2007/JPEGImages/" + picNum + ".jpg")

    # frame = cv2.imread("/home/river/data/self_test/u.jpg")
    frame = cv2.imread("/home/river/data/self_test/pictures__/00260.png")
    frame = predict(frame)
    window_name = 'Object detector'
    cv2.namedWindow(window_name, 0)
    cv2.resizeWindow(window_name, 300, 400)
    cv2.imshow(window_name, frame)


    '''
    # 2
    IMAGE_SIZE = (12, 8)
    plt.figure(figsize=IMAGE_SIZE)
    plt.imshow(frame)
    plt.show()
    '''

if __name__ == '__main__':
    net = build_ssd('test', 300, 21)  # initialize SSD
    net.load_state_dict(torch.load(args.weights))
    transform = BaseTransform(net.size, (104 / 256.0, 117 / 256.0, 123 / 256.0))

    cv2_demo(net.eval(), transform)
    # Press any key to close the image
    cv2.waitKey()
    # cleanup
    cv2.destroyAllWindows()

    # cv2_demo(net.eval(), transform) # 2
