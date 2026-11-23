import rclpy
from rclpy.node import Node
#from std_msgs.msg import String
from my_robot_interfaces.msg import TargetInfo
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class YoloPerceptionNode(Node):
    def __init__(self):
        super().__init__('yolo_detection_node')
        # gazebo kamerasından ham gorunduyu dinleyen subscriber.
        self.image_sub = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        
        # tespit ve yonelim bilgisini motor dugume topic ile bildiren publisher.
        self.detection_pub = self.create_publisher(TargetInfo, 'yolo_detections', 10)

        # ROS Image -> OpenCV donusumu:
        self.bridge = CvBridge()
        self.get_logger().info('Kamera akisi bekleniyor... (/camera/image_raw) ile.')

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        height, width, _ = frame.shape
        center_x = width // 2
        # --- BURASI MODEL / ALGILAMA KATMANI ---
        # İleride buraya doğrudan: results = model(frame) gelecek.
        # Şimdilik Gazebo'da eklediğimiz nesneyi (gri zeminden koyu/renkli piksel) maskeleyelim:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Gazebo zemini ~178 parlaklıktadır; daha koyu nesneleri yakalayalım
        # Binary inv: esik degerin ustunu 0(siyah), altini 255(beyaz) yapar.
        # zemin ~178 olduugundan zemin siyah olacak.
        _, mask = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)
        
        # contours ile ayni renkteki bitisik nesnelerin kontur cizgilerin kordinatlarini doner
        # cv2.RETR_EXTERNAL: sadece en distaki cizgileri alir.
        # cv2.CHAIN_APPROX_SIMPLE: sinir noktalari bellek dostu seklinde alir
        # ornegin dikdortgen varsa her bir ufak pixel degisimini degil de 4 kose.
        # ilk cikti sinir kordinatlarini liste seklinde tutar.
        # ikinci cikti nesnelerin ic ice olup olmadigini tutar, biz sadece disi aldik
        # 2. ciktiya ihtiyacimiz yok.
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out_msg = TargetInfo()

        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)

            if area > 500:  # Gürültüyü ele
                x, y, w, h = cv2.boundingRect(largest)
                obj_center_x = x + (w // 2)
                offset_x = obj_center_x - center_x  # (+) Sağda, (-) Solda
                
                # Nesne kameranın %35'inden fazlasını kaplıyorsa çok yakındır
                if area > (width * height * 0.35):
                    out_msg.status = "HEDEF_COK_YAKIN"
                    out_msg.offset_x = float(offset_x)
                else:
                    out_msg.status= "HEDEF_TAKIP"
                    out_msg.offset_x = float(offset_x)
            else:
                out_msg.status = "HEDEF_YOK"
                out_msg.offset_x = float(0)
        else:
            out_msg.status = "HEDEF_YOK"
            out_msg.offset_x = float(0)

        self.detection_pub.publish(out_msg) 

def main(args=None):
    rclpy.init(args=args)
    node = YoloPerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()