sudo iptables -t nat -I PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
sudo iptables -t nat -I PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8080
