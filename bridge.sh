#!/bin/bash
echo "--- AI Bridge Started ---"
while true; do
    echo "[Listening...]"
    # Listen for one message. We use -m 1 to exit grep after one match.
    # We redirect stderr to stdout because ggwave-rx logs there.
    MSG=$(./bin/ggwave-rx 2>&1 | grep --line-buffered -m 1 "Received sound data successfully:" | sed -u 's/.*successfully: //' | tr -d "'")
    
    if [ ! -z "$MSG" ]; then
        echo "Heard: $MSG"
        
        # Automatic response
        RESPONSE="Ack: $MSG"
        echo "Responding: $RESPONSE"
        echo "$RESPONSE" | ./bin/ggwave-cli -p0
    fi
    echo "--------------------------"
done
