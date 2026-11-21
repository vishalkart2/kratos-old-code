#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float64.hpp"
#include "std_msgs/msg/int32_multi_array.hpp"
#include "std_msgs/msg/float32_multi_array.hpp"
#include "sensor_msgs/msg/joy.hpp"
using std::placeholders::_1;
class MinimalSubscriber : public rclcpp::Node
{
  public:
    MinimalSubscriber()
    : Node("mapping_node")
    {
        publisher_1 = this->create_publisher<std_msgs::msg::Int32MultiArray>("mymotors", 10);
      subscription_1 = this->create_subscription<sensor_msgs::msg::Joy>(
      "joy", 10, std::bind(&MinimalSubscriber::topic_callback1, this, _1));
      motor_data.data.resize(9);
    }
/*{this}{
 *
} */
  private:
    void topic_callback1(sensor_msgs::msg::Joy msg)
    {      
      motor_data.data[0]=-msg.axes[0]*255;
      motor_data.data[1]=msg.axes[1]*255;

      motor_data.data[2]=msg.axes[3]*255;
      motor_data.data[3]=msg.axes[4]*255;
            if(msg.axes[2]!=1 && msg.axes[5]==1)
      {
          motor_data.data[5]=(255-msg.axes[2]*255)/2;
      }
      else if (msg.axes[2]==1 && msg.axes[5]!=1) {
          motor_data.data[5]=(msg.axes[5]*255 - 255)/2;
      }
      else {
          motor_data.data[5]=0;
      }
      motor_data.data[4]=msg.buttons[0];
      motor_data.data[6]=msg.buttons[1];
      motor_data.data[7]=msg.buttons[2];
      motor_data.data[8]=msg.buttons[3];
      publisher_1->publish(motor_data);
    }
    rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr subscription_1;
    rclcpp::Publisher<std_msgs::msg::Int32MultiArray>::SharedPtr publisher_1;
    std_msgs::msg::Int32MultiArray motor_data;

};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MinimalSubscriber>());
  rclcpp::shutdown();
  return 0;
}
