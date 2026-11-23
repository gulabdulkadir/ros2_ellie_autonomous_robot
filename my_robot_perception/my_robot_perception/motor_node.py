import rclpy
from rclpy.node import Node
#from std_msgs.msg import String
from my_robot_interfaces.msg import TargetInfo
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data

class MotorControlNode(Node):
    def __init__(self):
        super().__init__('motor_control_node')
        self.subscription = self.create_subscription(TargetInfo, '/yolo_detections', self.listener_callback, 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # 1. Parametrelerin varsayılan değerlerini tanımla.
        self.declare_parameter('kp', 0.003)
        self.declare_parameter('linear_speed', 0.20)
        self.declare_parameter('search_angular_speed', 0.35)      
        self.declare_parameter('stop_distance', 0.45)
        
        # 2. Tanımlanan parametrelerin değerlerini oku.
        self.kp = self.get_parameter('kp').value
        self.linear_speed = self.get_parameter('linear_speed').value
        self.search_angular_speed = self.get_parameter('search_angular_speed').value
        self.stop_distance = self.get_parameter('stop_distance').value

        self.get_logger().info(
            f'Parametreler yüklendi -> Kp: {self.kp}, İleri Hız: {self.linear_speed}, Arama Hızı: {self.search_angular_speed}'
        )

        # LİDAR verisini alacak subscriber nodumuzu tanımlıyoruz.
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, qos_profile_sensor_data)

        # LİDAR için değişken tanımlıyoruz.
        self.min_front_dist = float('inf')

    def scan_callback(self, msg):
        self.front_ranges = msg.ranges[160:200]
        self.valid_ranges = [r for r in self.front_ranges if msg.range_min < r < msg.range_max]
        self.min_front_dist = min(self.valid_ranges) if self.valid_ranges else float('inf')


    def listener_callback(self, msg):
        status = msg.status
        offset_x = msg.offset_x
        twist = Twist()
        """
        # Gelen mesaj formatı DURUM|offset: değer şeklindeydi.
        parts = msg.data.split('|')
        status = parts[0]
        offset_x = float(parts[1].split(':')[1])
        """


        if self.min_front_dist < self.stop_distance:
            self.get_logger().warn(f'ENGEL ALGILANDI ({self.min_front_dist:.2f} m)! Güvenlik duruşu.')
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        elif status == 'HEDEF_COK_YAKIN':
            self.get_logger().warn('Hedefe ulaşıldı! Robot durduruluyor.')
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        elif status == 'HEDEF_TAKIP':
            # P-Kontrolcü ile açısal hız hesabı (Sağ el kuralı gereği eksi işareti)
            angular_z = -self.kp * offset_x

            # Maksimum dönüş hızını sınırla (-1.0 ile +1.0 rad/s arası)
            angular_z = max(min(angular_z, 1.0), -1.0)

            twist.linear.x = self.linear_speed     # Sabit ileri hız
            twist.angular.z = angular_z
            self.get_logger().info(f'Takip Ediliyor | Sapma: {offset_x:.0f}px | Dönüş: {angular_z:.2f}')

        else:  # HEDEF_YOK
            # Hedef görüş alanında değilse yavaşça dönerek ara
            twist.linear.x = 0.0
            twist.angular.z = self.search_angular_speed
            self.get_logger().info('Hedef aranıyor...')

        self.cmd_vel_pub.publish(twist)
        
def main(args=None):
    rclpy.init(args=args)
    node = MotorControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()