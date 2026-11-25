#!/bin/bash
# Set before running: export ROBOT_SSH=ubuntu@<robot-ip>  ROBOT_PASS=<robot password>
# start_all.sh 로 띄운 프로세스 전부 종료

echo "=== 이 노트북 프로세스 종료 ==="
ps aux | grep -E "phone_cam_detector|bbox4|mission_manager|tracking/lib/tracking|explore_lite/lib|rosbridge_websocket|iriunwebcam|slam_toolbox|nav2_|lifecycle_manager|node_modules/.bin/vite" \
  | grep -v grep | awk '{print $2}' | xargs -r kill -9

echo "=== 로봇 파이 아두이노 슈터 종료 ==="
sshpass -p "$ROBOT_PASS" ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 "$ROBOT_SSH" \
  "ps aux | grep '[a]rduino_shooter_node' | awk '{print \$2}' | xargs -r kill -SIGINT"

sleep 1
echo "=== 완료 ==="
