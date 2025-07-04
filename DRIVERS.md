# ROS Drivers for common V2X OBU/RSU Hardware

The `stol_its_conversion` package converts `stol_its_msgs` ROS messages to and from [UPER-encoded](https://www.oss.com/asn1/resources/asn1-made-simple/asn1-quick-reference/packed-encoding-rules.html) [`udp_msgs/msg/UdpPacket`](https://github.com/flynneva/udp_msgs/blob/main/msg/UdpPacket.msg) payloads. This allows to build simple ROS drivers for common V2X OBUs and RSUs. This page contains instructions to connect common V2X hardware to ROS.

**Tested V2X Hardware**
- [Cohda Wireless MK5/MK6](#cohda-wireless-mk5mk6)
- [cubesys cube:evk](#cubesys-cubeevk)


## [Cohda Wireless MK5/MK6](https://www.cohdawireless.com/solutions/mk6/)

#### Approach

- Run an application on the MK5/MK6 that forwards raw V2X message payloads to a UDP port on a host computer.
- Bridge the UDP packets to ROS messages.
- Run the `stol_its_conversion` node to convert the UDP packets to and from `stol_its_msgs` ROS messages.

#### Prerequisites

- To follow the documentation links, access to the Cohda Wireless support portal is required.
- The MK5/MK6 is connected to a host computer and IP addresses of both devices are known.
- The following was tested successfully with MK5 firmware `mk5-19.Release.139237-RSUstol-typical` and a stock MK6 firmware.
- The following only describes the setup for bridging received V2X messages to ROS. The other way, sending V2X messages from ROS via ITS-G5, should work similarly.

#### On the Cohda Wireless MK5/MK6

1. Install the `examplestol` application to `/mnt/rw`. [[Documentation](https://support.cohdawireless.com/hc/en-us/articles/360001755856-Examplestol-Installing-Running)] You may also install and configure any other (custom) application that supports forwarding V2X messages via UDP.
1. Configure forwarding of BTP packets to the host computer via UDP in `/mnt/rw/examplestol/obu.conf` or `/mnt/rw/examplestol/rsu.conf`. [[Documentation](https://support.cohdawireless.com/hc/en-us/articles/115000972306-stol-Sending-receiving-BTP-packets-through-UDP)]
    ```
    ItsFacilitiesShellEnabled   = 1;     0, 1         # Enables / Disables support Facilities Shell interface
    ItsUdpBtpIfHostName     = 192.168.140.12          # hostname for sending BTP Data Ind to Shell
    ItsUdpBtpIfIndPort      = 4400;  1,65535          # port number for sending BTP Data Ind to Shell
    ItsUdpBtpIfReqPort      = 4401;  1,65535          # port number for receiving BTP Data Req from Shell
    ItsBtpShellDestPort     = 65535; 0,65535
    ```
1. *(optional)* Reduce GeoNetworking security strictness in the same file.
    ```
    ItsGnSnDecapResultHandling = 1; 0,1               # GN security strictness - STRICT (0), NON-STRICT (1)
    ```
1. Start the application or enable auto-start. [[Documentation](https://support.cohdawireless.com/hc/en-us/articles/213199623-Auto-start-an-application-after-Boot-up-of-MKx)]
    ```bash
    # root@MK5:/mnt/rw/examplestol#
    rc.examplestol start obu # or rsu
    ```

#### On the host computer

1. Install the [`udp_driver`](https://github.com/ros-drivers/transport_drivers) and [`stol_its_conversion`](https://github.com/ika-rwth-aachen/stol_its_messages) ROS packages.
    ```bash
    sudo apt install \
        ros-$ROS_DISTRO-udp-driver \
        ros-$ROS_DISTRO-stol-its-conversion
    ```
1. Configure the `udp_driver` node responsible for bridging the UDP packets received from the MK5/MK6 to [`udp_msgs/msg/UdpPacket`](https://github.com/flynneva/udp_msgs/blob/main/msg/UdpPacket.msg) ROS messages.
    ```yml
    # config.udp_driver.yml
    /**/*:
      ros__parameters:
        ip: "192.168.140.12"    # same as ItsUdpBtpIfIndHostName
        port: 4400              # same as ItsUdpBtpIfIndPort
    ```
1. Configure the `stol_its_conversion` node responsible for converting the [UPER-encoded](https://www.oss.com/asn1/resources/asn1-made-simple/asn1-quick-reference/packed-encoding-rules.html) [`udp_msgs/msg/UdpPacket`](https://github.com/flynneva/udp_msgs/blob/main/msg/UdpPacket.msg) payloads to [`stol_its_msgs`](https://github.com/ika-rwth-aachen/stol_its_messages).
    ```yml
    # config.stol_its_conversion.yml
    /**/*:
      ros__parameters:
        has_btp_destination_port: true
        btp_destination_port_offset: 8
        stol_message_payload_offset: 78
        ros2udp_stol_types:
          - cam
          - cam_ts
          - cpm_ts
          - denm
          - denm_ts
          - mapem_ts
          - mcm_uulm
          - spatem_ts
          - vam_ts
        udp2ros_stol_types:
          - cam
          - cpm_ts
          - denm
          - mapem_ts
          - mcm_uulm
          - spatem_ts
          - vam_ts
    ```
1. Launch the `udp_driver` node.
    ```bash
    ros2 run udp_driver udp_receiver_node_exe --ros-args --params-file ./config.udp_driver.yml -r /udp_read:=/converter/udp/in
    ros2 lifecycle set /udp_receiver_node 1
    ros2 lifecycle set /udp_receiver_node 3
    ```
1. Receive, e.g., encoded CAMs on `/converter/udp/in`.
    ```bash
    ros2 topic echo /converter/udp/in
    ```
1. Launch the `stol_its_conversion` node.
    ```bash
    ros2 run stol_its_conversion stol_its_conversion_node --ros-args --params-file ./config.stol_its_conversion.yml
    ```
1. Receive, e.g., CAMs on `/converter/cam/out`.
    ```bash
    ros2 topic echo /converter/cam/out
    ```


## [cubesys cube:evk](https://www.nfiniity.com/)

#### Approach

- The cube:evk natively supports `stol_its_msgs` ROS 2 messages.
- Launch the *cube-its* ROS 2 framework on the cube:evk to directly receive and send messages from ROS.

#### Prequisites

- The cube:evk is connected to a host computer and IP addresses of both devices are known.

#### On the cube:evk

1. Launch the *cube-its* ROS 2 framework.
    ```bash
    start-its --remote
    ```

#### On the host computer

1. Install the [`stol_its_msgs`](https://github.com/ika-rwth-aachen/stol_its_messages) ROS packages.
    ```bash
    sudo apt install \
        ros-$ROS_DISTRO-stol-its-msgs
    ```
1. Configure the [ROS 2 domain](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Domain-ID.html) to receive ROS messages remotely from the cube:evk.
    ```bash
    export ROS_DOMAIN_ID=42
    export ROS_LOCALHOST_ONLY=0
    ```
1. Receive, e.g., CAMs on `/its/cam_received`.
    ```bash
    ros2 topic echo /its/cam_received
    ```
1. Send, e.g., CAMs by publishing to `/its/cam_provided`
    ```bash
    ros2 topic pub /its/cam_provided stol_its_cam_msgs/msg/CAM "{}"
    ```
